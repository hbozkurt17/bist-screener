"""
Qullamaggie BIST Scanner  v4
=============================
Kristjan Kullamägi stratejisine göre BIST hisselerini tarar.
GitHub Actions tarafından her hafta içi 18:30 Türkiye saatinde çalıştırılır.

SİNYAL MANTIĞI:
  - AL   : EMA Fan ✅  +  ADR >= %4 ✅  +  Hacim >= 1.5x ✅
  - İZLE : EMA Fan ✅  +  ADR >= %4 ✅  (henüz hacim yok)
  - Sıkışma / ATR Squeeze → sadece bilgi, sinyale ETKİSİ YOK
  - "Yeni" = Dün bu koşul yoktu, bugün var (ilk mumda yakala)
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

from stocks import BIST

# ── Parametreler ──────────────────────────────────────────────────────────────
ADR_PERIOD      = 20
ADR_MIN_PCT     = 4.0
EMA_LENGTHS     = [10, 20, 50, 200]
VOL_MA_PERIOD   = 20
VOL_MULTIPLIER  = 1.5
LOOKBACK_DAYS   = 350

CONSOL_MIN_DAYS = 3
CONSOL_MAX_DAYS = 10
CONSOL_BAND_PCT = 5.0
ATR_PERIOD      = 10
ATR_RATIO_MAX   = 0.75


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def ema(s: pd.Series, p: int) -> pd.Series:
    return s.ewm(span=p, adjust=False).mean()

def adr_series(high, low, period=ADR_PERIOD):
    return ((high - low) / low * 100).rolling(period).mean()

def atr_series(high, low, close, period=ATR_PERIOD):
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def consolidation_info(close: pd.Series) -> tuple[bool, int]:
    for length in range(CONSOL_MIN_DAYS, CONSOL_MAX_DAYS + 1):
        w = close.iloc[-length:]
        lo, hi = w.min(), w.max()
        if lo > 0 and (hi - lo) / lo * 100 <= CONSOL_BAND_PCT:
            return True, length
    return False, 0

def squeeze_info(atr: pd.Series) -> bool:
    half = ATR_PERIOD // 2
    if len(atr.dropna()) < ATR_PERIOD + half:
        return False
    recent = atr.iloc[-half:].mean()
    base   = atr.iloc[-ATR_PERIOD:].mean()
    return base > 0 and (recent / base) <= ATR_RATIO_MAX

def fetch(ticker: str) -> pd.DataFrame | None:
    end   = datetime.now(tz=timezone.utc) + timedelta(days=1)
    start = end - timedelta(days=LOOKBACK_DAYS)
    try:
        df = yf.download(ticker, start=start, end=end,
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df if len(df) >= 210 else None
    except Exception as exc:
        print(f"  [HATA] {ticker}: {exc}", file=sys.stderr)
        return None


# ── Tek hisse analizi ─────────────────────────────────────────────────────────

def analyse(ticker: str) -> dict | None:
    df = fetch(ticker)
    if df is None:
        return None

    for p in EMA_LENGTHS:
        df[f"EMA{p}"] = ema(df["Close"], p)
    df["ADR"]   = adr_series(df["High"], df["Low"])
    df["ATR"]   = atr_series(df["High"], df["Low"], df["Close"])
    df["VolMA"] = df["Volume"].rolling(VOL_MA_PERIOD).mean()

    last = df.iloc[-1]

    adr_ok    = bool(last["ADR"] >= ADR_MIN_PCT)
    ema_fan   = bool(
        last["Close"]  > last["EMA10"]  and
        last["EMA10"]  > last["EMA20"]  and
        last["EMA20"]  > last["EMA50"]  and
        last["EMA50"]  > last["EMA200"]
    )
    vol_surge = bool(last["Volume"] >= last["VolMA"] * VOL_MULTIPLIER)

    al_today   = ema_fan and adr_ok and vol_surge
    izle_today = ema_fan and adr_ok and not vol_surge

    consol, consol_len = consolidation_info(df["Close"])
    squeeze            = squeeze_info(df["ATR"])

    if len(df) >= 3:
        df_p  = df.iloc[:-1]
        lp    = df_p.iloc[-1]
        adr_p = bool(lp["ADR"] >= ADR_MIN_PCT)
        fan_p = bool(
            lp["Close"]  > lp["EMA10"]  and
            lp["EMA10"]  > lp["EMA20"]  and
            lp["EMA20"]  > lp["EMA50"]  and
            lp["EMA50"]  > lp["EMA200"]
        )
        vol_p = bool(lp["Volume"] >= lp["VolMA"] * VOL_MULTIPLIER)
        al_p  = fan_p and adr_p and vol_p
        izle_p = fan_p and adr_p and not vol_p
    else:
        al_p = izle_p = False

    new_al   = al_today   and not al_p
    new_izle = izle_today and not izle_p and not al_today

    vol_ratio = float(last["Volume"] / last["VolMA"]) if last["VolMA"] > 0 else 0.0

    return {
        "ticker"    : ticker.replace(".IS", ""),
        "close"     : round(float(last["Close"]), 2),
        "adr_pct"   : round(float(last["ADR"]),   2),
        "vol_ratio" : round(vol_ratio,             2),
        "ema_fan"   : ema_fan,
        "vol_surge" : vol_surge,
        "consol"    : consol,
        "consol_len": consol_len,
        "squeeze"   : squeeze,
        "new_al"    : new_al,
        "new_izle"  : new_izle,
    }


# ── Tarama & rapor ────────────────────────────────────────────────────────────

def run_scan(tickers: list[str], label: str) -> dict:
    als    = []
    izles  = []
    errors = 0

    print(f"\n{'═'*64}")
    print(f"  {label}  ({len(tickers)} hisse)")
    print(f"  AL: EMA Fan + ADR≥{ADR_MIN_PCT}% + Hacim≥{VOL_MULTIPLIER}x")
    print(f"  IZLE: EMA Fan + ADR≥{ADR_MIN_PCT}%  |  Sikisma: sadece bilgi")
    print(f"{'═'*64}")

    for ticker in tickers:
        print(f"  → {ticker:<14}", end="", flush=True)
        result = analyse(ticker)
        if result is None:
            print("veri yok / atlandı")
            errors += 1
            continue

        status = []
        if result["new_al"]  : status.append("🚀 YENİ AL")
        if result["new_izle"]: status.append("👀 YENİ İZLE")
        if not status:         status.append("—")
        print(", ".join(status))

        if result["new_al"]  : als.append(result)
        if result["new_izle"]: izles.append(result)

    print(f"\n{'─'*64}")
    print(f"  ÖZET – {label}")
    print(f"{'─'*64}")

    if als:
        print(f"\n🚀  YENİ AL  ({len(als)} hisse)\n")
        print(f"  {'Hisse':<8} {'Fiyat':>8} {'ADR%':>6} {'Hacim/Ort':>10} {'Sikisma':>8} {'Squeeze':>8}")
        print(f"  {'─'*56}")
        for r in sorted(als, key=lambda x: x["vol_ratio"], reverse=True):
            c = str(r['consol_len'])+"g" if r["consol"] else "-"
            s = "VAR" if r["squeeze"] else "-"
            print(f"  {r['ticker']:<8} {r['close']:>8.2f} "
                  f"{r['adr_pct']:>6.2f}% {r['vol_ratio']:>9.2f}x "
                  f"{c:>8} {s:>8}")
    else:
        print("\n  🚀  Bugün yeni AL sinyali yok.")

    if izles:
        print(f"\n👀  YENİ İZLE  ({len(izles)} hisse)\n")
        print(f"  {'Hisse':<8} {'Fiyat':>8} {'ADR%':>6} {'Hacim/Ort':>10} {'Sikisma':>8} {'Squeeze':>8}")
        print(f"  {'─'*56}")
        for r in sorted(izles, key=lambda x: x["adr_pct"], reverse=True):
            c = str(r['consol_len'])+"g" if r["consol"] else "-"
            s = "VAR" if r["squeeze"] else "-"
            print(f"  {r['ticker']:<8} {r['close']:>8.2f} "
                  f"{r['adr_pct']:>6.2f}% {r['vol_ratio']:>9.2f}x "
                  f"{c:>8} {s:>8}")
    else:
        print("\n  👀  Bugün yeni İZLE sinyali yok.")

    print(f"\n  Hata/Veri yok: {errors} hisse")
    print(f"{'═'*64}\n")

    return {"als": als, "izles": izles}


# ── Telegram ──────────────────────────────────────────────────────────────────

def send_telegram(text: str) -> bool:
    token   = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id or not REQUESTS_OK:
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


def format_telegram(result: dict, now_tr: datetime) -> str:
    def fmt_row(r):
        c  = f" 🔄{r['consol_len']}g" if r["consol"]  else ""
        sq = " 📉sq"                   if r["squeeze"] else ""
        return (f"  • <code>{r['ticker']}</code>  {r['close']:.2f} TL"
                f"  ADR:{r['adr_pct']:.1f}%  H:{r['vol_ratio']:.1f}x{c}{sq}")

    lines = [f"⚡ <b>MOMENTUM BIST SCANNER</b>",
             f"📅 {now_tr.strftime('%d.%m.%Y %H:%M')} TR\n"]

    if result["als"]:
        lines.append("🚀 <b>YENİ AL</b>")
        lines += [fmt_row(r) for r in result["als"]]
    else:
        lines.append("🚀 AL sinyali yok")

    if result["izles"]:
        lines.append("\n👀 <b>YENİ İZLE</b>")
        lines += [fmt_row(r) for r in result["izles"]]
    else:
        lines.append("👀 İZLE sinyali yok")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now_tr = datetime.now(tz=timezone.utc) + timedelta(hours=3)
    print(f"\n{'═'*64}")
    print(f"  ⚡ MOMENTUM BIST SCANNER  v4")
    print(f"  {now_tr.strftime('%d.%m.%Y %H:%M')} TR")
    print(f"{'═'*64}")

    result = run_scan(BIST, "📊 BIST")

    msg  = format_telegram(result, now_tr)
    sent = send_telegram(msg)
    status = "✅ gönderildi" if sent else "ℹ️  TELEGRAM_TOKEN ayarlı değil"
    print(f"Telegram: {status}")


if __name__ == "__main__":
    main()
