"""
Qullamaggie BIST Scanner
========================
Kristjan Kullamägi stratejisine göre BIST hisselerini tarar.
GitHub Actions tarafından her hafta içi 18:30 Türkiye saatinde çalıştırılır.

Kriterler:
  1. ADR >= %4  (son 20 günün ortalama gün içi hareketi)
  2. EMA Fan    : fiyat > EMA10 > EMA20 > EMA50 > EMA200
  3. Sıkışma    : son 3–10 günde fiyat bandı <= %3
  4. Kırılım    : sıkışma yükseği kırıldı VE hacim >= 2× ortalama

Çıktı:
  - KIRILIM  : Bugün ilk kez kırılım sinyali oluşan hisseler
  - SIKIŞMADA: Henüz kırılım yok ama koşullar hazır (EMA fan + sıkışma + ADR)
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

from stocks import BIST30, BIST100_EX_BIST30

# ── Parametreler ────────────────────────────────────────────────────────────
ADR_PERIOD      = 20
ADR_MIN_PCT     = 4.0
EMA_LENGTHS     = [10, 20, 50, 200]
CONSOL_MIN_DAYS = 3
CONSOL_MAX_DAYS = 10
CONSOL_BAND_PCT = 3.0
VOL_MA_PERIOD   = 10
VOL_MULTIPLIER  = 2.0
LOOKBACK_DAYS   = 320   # EMA200 için yeterli geçmiş


# ── Yardımcı fonksiyonlar ────────────────────────────────────────────────────

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def adr(high: pd.Series, low: pd.Series, period: int = ADR_PERIOD) -> pd.Series:
    """Ortalama Günlük Hareket (%)"""
    return ((high - low) / low * 100).rolling(period).mean()


def tight_consolidation(high: pd.Series, low: pd.Series,
                         min_days: int = CONSOL_MIN_DAYS,
                         max_days: int = CONSOL_MAX_DAYS,
                         band_pct: float = CONSOL_BAND_PCT):
    """
    Verilen serinin SON barında sıkışma var mı?
    (min_days..max_days arası pencerede fiyat bandı <= band_pct)
    Döndürür: (bool, int)  →  (sıkışma_var_mı, kaç_gün)
    """
    for length in range(min_days, max_days + 1):
        window_high = high.iloc[-length:].max()
        window_low  = low.iloc[-length:].min()
        if window_low > 0 and (window_high - window_low) / window_low * 100 <= band_pct:
            return True, length
    return False, 0


def fetch(ticker: str, days: int = LOOKBACK_DAYS) -> pd.DataFrame | None:
    """Yahoo Finance'den OHLCV indir, hatalıysa None döndür."""
    end   = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=days)
    try:
        df = yf.download(ticker, start=start, end=end,
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if len(df) < 210:          # EMA200 için minimum bar
            return None
        return df
    except Exception as exc:
        print(f"  [HATA] {ticker}: {exc}", file=sys.stderr)
        return None


# ── Tek hisse analizi ────────────────────────────────────────────────────────

def analyse(ticker: str) -> dict | None:
    """
    Hisseyi analiz et; sonuç dict veya None döndür.

    Sonuç dict anahtarları:
        ticker, close, adr_pct, vol_ratio,
        ema_fan       : bool
        consol_today  : bool   – bugün sıkışmada mı
        consol_len    : int    – kaç gün
        breakout      : bool   – bugün kırılım sinyali var mı
        new_breakout  : bool   – dün yoktu, bugün var (YENİ kırılım)
        new_ready     : bool   – dün hazır değildi, bugün hazır (YENİ sıkışma)
    """
    df = fetch(ticker)
    if df is None:
        return None

    # EMA'lar
    for p in EMA_LENGTHS:
        df[f"EMA{p}"] = ema(df["Close"], p)

    df["ADR"]   = adr(df["High"], df["Low"])
    df["VolMA"] = df["Volume"].rolling(VOL_MA_PERIOD).mean()

    # ── Bugünkü bar ─────────────────────────────────────
    last = df.iloc[-1]

    adr_ok    = bool(last["ADR"] >= ADR_MIN_PCT)
    ema_fan   = bool(
        last["Close"]  > last["EMA10"]  and
        last["EMA10"]  > last["EMA20"]  and
        last["EMA20"]  > last["EMA50"]  and
        last["EMA50"]  > last["EMA200"]
    )
    vol_surge = bool(last["Volume"] >= last["VolMA"] * VOL_MULTIPLIER)

    # Bugün sıkışma
    consol_today, consol_len = tight_consolidation(df["High"], df["Low"])

    # Kırılım referansı: önceki barda sıkışma yükseği
    prev_consol, prev_len = tight_consolidation(
        df["High"].iloc[:-1], df["Low"].iloc[:-1]
    )
    if prev_consol and prev_len > 0:
        consol_high_prev = df["High"].iloc[-1 - prev_len:-1].max()
        breakout = bool(
            last["Close"] > consol_high_prev and
            prev_consol and vol_surge and adr_ok and ema_fan
        )
    else:
        breakout = False

    # ── Dünkü bar (yenilik tespiti) ─────────────────────
    if len(df) >= 3:
        df_prev = df.iloc[:-1]
        lp = df_prev.iloc[-1]

        adr_ok_p  = bool(lp["ADR"] >= ADR_MIN_PCT)
        ema_fan_p = bool(
            lp["Close"]  > lp["EMA10"]  and
            lp["EMA10"]  > lp["EMA20"]  and
            lp["EMA20"]  > lp["EMA50"]  and
            lp["EMA50"]  > lp["EMA200"]
        )
        vol_surge_p = bool(lp["Volume"] >= lp["VolMA"] * VOL_MULTIPLIER)
        prev2_consol, prev2_len = tight_consolidation(
            df_prev["High"].iloc[:-1], df_prev["Low"].iloc[:-1]
        )
        if prev2_consol and prev2_len > 0:
            cref = df_prev["High"].iloc[-1 - prev2_len:-1].max()
            breakout_p = bool(
                lp["Close"] > cref and
                prev2_consol and vol_surge_p and adr_ok_p and ema_fan_p
            )
        else:
            breakout_p = False

        consol_p, _ = tight_consolidation(df_prev["High"], df_prev["Low"])
        ready_p = bool(consol_p and ema_fan_p and adr_ok_p and not breakout_p)
    else:
        breakout_p = False
        ready_p    = False

    ready_today = bool(consol_today and ema_fan and adr_ok and not breakout)
    new_breakout = breakout and not breakout_p
    new_ready    = ready_today and not ready_p

    vol_ratio = float(last["Volume"] / last["VolMA"]) if last["VolMA"] > 0 else 0.0

    return {
        "ticker"      : ticker.replace(".IS", ""),
        "close"       : round(float(last["Close"]), 2),
        "adr_pct"     : round(float(last["ADR"]),   2),
        "vol_ratio"   : round(vol_ratio,             2),
        "ema_fan"     : ema_fan,
        "consol_today": consol_today,
        "consol_len"  : consol_len,
        "breakout"    : breakout,
        "new_breakout": new_breakout,
        "new_ready"   : new_ready,
    }


# ── Tarama & rapor ───────────────────────────────────────────────────────────

def run_scan(tickers: list[str], label: str) -> dict:
    """Verilen listeyi tara, kategorize et, raporla."""
    breakouts = []
    readys    = []
    errors    = 0

    print(f"\n{'═'*60}")
    print(f"  {label}  ({len(tickers)} hisse taranıyor…)")
    print(f"{'═'*60}")

    for ticker in tickers:
        print(f"  → {ticker:<14}", end="", flush=True)
        result = analyse(ticker)
        if result is None:
            print("veri yok / atlandı")
            errors += 1
            continue

        status = []
        if result["new_breakout"]: status.append("🚀 YENİ KIRILIM")
        if result["new_ready"]   : status.append("⏳ YENİ SIKIŞMA")
        if not status:             status.append("—")
        print(", ".join(status))

        if result["new_breakout"]:
            breakouts.append(result)
        elif result["new_ready"]:
            readys.append(result)

    # ── Özet rapor ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  ÖZET – {label}")
    print(f"{'─'*60}")

    if breakouts:
        print(f"\n🚀  YENİ KIRILIM  ({len(breakouts)} hisse)\n")
        header = f"  {'Hisse':<8} {'Fiyat':>8} {'ADR%':>6} {'Hacim/Ort':>10} {'Sıkışma':>8}"
        print(header)
        print(f"  {'-'*50}")
        for r in sorted(breakouts, key=lambda x: x["vol_ratio"], reverse=True):
            print(f"  {r['ticker']:<8} {r['close']:>8.2f} "
                  f"{r['adr_pct']:>6.2f}% {r['vol_ratio']:>9.2f}x "
                  f"{r['consol_len']:>6}g")
    else:
        print("\n  🚀  Bugün yeni kırılım yok.")

    if readys:
        print(f"\n⏳  YENİ SIKIŞMA (Hazır)  ({len(readys)} hisse)\n")
        header = f"  {'Hisse':<8} {'Fiyat':>8} {'ADR%':>6} {'Sıkışma':>8}"
        print(header)
        print(f"  {'-'*36}")
        for r in sorted(readys, key=lambda x: x["adr_pct"], reverse=True):
            print(f"  {r['ticker']:<8} {r['close']:>8.2f} "
                  f"{r['adr_pct']:>6.2f}% {r['consol_len']:>6}g")
    else:
        print("\n  ⏳  Bugün yeni sıkışmaya giren hisse yok.")

    print(f"\n  Hata/Veri yok: {errors} hisse")
    print(f"{'═'*60}\n")

    return {"breakouts": breakouts, "readys": readys}


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Qullamaggie BIST Scanner")
    parser.add_argument(
        "--mode",
        choices=["bist30", "bist100", "both"],
        default="both",
        help="Tarama modu: bist30 | bist100 (ex-30) | both"
    )
    args = parser.parse_args()

    now_tr = datetime.now(tz=timezone.utc) + timedelta(hours=3)
    print(f"\n{'═'*60}")
    print(f"  ⚡ QULLAMAGGIE BIST SCANNER")
    print(f"  Tarih/Saat (TR): {now_tr.strftime('%d.%m.%Y %H:%M')}")
    print(f"{'═'*60}")

    if args.mode in ("bist30", "both"):
        run_scan(BIST30, "📊 BIST30")

    if args.mode in ("bist100", "both"):
        run_scan(BIST100_EX_BIST30, "📊 BIST100 (BIST30 hariç)")


if __name__ == "__main__":
    main()
