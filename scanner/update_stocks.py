"""
BIST Hisse Listesi Haftalık Kontrol  v1
========================================
Her Pazartesi sabahı GitHub Actions tarafından çalıştırılır.
1. Tüm hisselerin yfinance'ten veri gelip gelmediğini kontrol eder
2. Delisted / veri gelmeyen hisseleri tespit eder
3. Sonuçları Telegram'a bildirir
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import yfinance as yf
import requests

from stocks import BIST30, BIST100_EX_BIST30


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def check_ticker(ticker: str) -> bool:
    """Hissenin son 5 günde veri döndürüp döndürmediğini kontrol eder."""
    try:
        df = yf.download(ticker, period="5d", progress=False, auto_adjust=True)
        if isinstance(df.columns, __import__("pandas").MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return len(df) > 0
    except Exception:
        return False


def send_telegram(text: str) -> bool:
    token   = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("[Telegram] Token/chat_id yok, konsola yazıldı.")
        print(text)
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram] Hata: {e}")
        return False


# ── Ana kontrol ───────────────────────────────────────────────────────────────

def main():
    now_tr = datetime.now(tz=timezone.utc) + timedelta(hours=3)

    bist30_bad   = []
    bist100_bad  = []

    print(f"\n{'═'*60}")
    print(f"  BIST Hisse Listesi Haftalık Kontrol")
    print(f"  {now_tr.strftime('%d.%m.%Y %H:%M')} TR")
    print(f"{'═'*60}")

    print(f"\n── BIST30 ({len(BIST30)} hisse) ──")
    for t in BIST30:
        ok = check_ticker(t)
        sym = t.replace(".IS", "")
        if ok:
            print(f"  ✅ {sym}")
        else:
            print(f"  ⚠️  {sym}  ← VERİ YOK")
            bist30_bad.append(sym)

    print(f"\n── BIST100 ex-30 ({len(BIST100_EX_BIST30)} hisse) ──")
    for t in BIST100_EX_BIST30:
        ok = check_ticker(t)
        sym = t.replace(".IS", "")
        if ok:
            print(f"  ✅ {sym}")
        else:
            print(f"  ⚠️  {sym}  ← VERİ YOK")
            bist100_bad.append(sym)

    total   = len(BIST30) + len(BIST100_EX_BIST30)
    problem = len(bist30_bad) + len(bist100_bad)

    # ── Telegram mesajı ────────────────────────────────────────────────────────
    lines = [
        f"📋 <b>BIST Hisse Listesi Haftalık Kontrol</b>",
        f"📅 {now_tr.strftime('%d.%m.%Y %H:%M')} TR",
        f"",
        f"Kontrol edilen: <b>{total}</b> hisse",
        f"Sorunlu: <b>{problem}</b> hisse",
    ]

    if bist30_bad:
        lines.append(f"\n⚠️ <b>BIST30 — veri yok ({len(bist30_bad)}):</b>")
        for s in bist30_bad:
            lines.append(f"  • <code>{s}</code>")
        lines.append("➡️ stocks.py → BIST30 listesinden kaldırın")

    if bist100_bad:
        lines.append(f"\n⚠️ <b>BIST100 ex-30 — veri yok ({len(bist100_bad)}):</b>")
        for s in bist100_bad:
            lines.append(f"  • <code>{s}</code>")
        lines.append("➡️ stocks.py → _BIST100_FULL listesinden kaldırın")

    if not problem:
        lines.append("\n✅ Tüm hisseler aktif — liste güncel görünüyor.")

    lines += [
        f"",
        f"🔗 Güncel endeks bileşenleri:",
        f"BIST30:  tr.investing.com/indices/ise-30-components",
        f"BIST100: tr.investing.com/indices/ise-100-components",
    ]

    msg = "\n".join(lines)
    sent = send_telegram(msg)
    print(f"\nTelegram: {'✅ gönderildi' if sent else 'ℹ️  Token yok'}")
    print(f"{'═'*60}\n")

    # Sorun varsa workflow'u fail et
    if problem > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
