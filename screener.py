import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# ── Telegram Ayarları (GitHub Secrets'tan gelir) ──────────
BOT_TOKEN = "8766976766:AAGCxR_ussy_n-vED6Jono-U5tvVQC2UPN0"
CHAT_ID   = "1019011392"

# ── Kriterler ─────────────────────────────────────────────
HAFTALIK_ESIK  = 5.0
ADR_ESIK       = 2.0
HACIM_ESIK     = 10.0
RS_ESIK        = 1.05
BREAKOUT_HAFTA = 8
HACIM_KAT      = 1.5
TREND_HAFTA    = 6
TREND_MIN_POZ  = 4

TICKERS = [
    'ACSEL','ADANA','ADBGR','ADEL','ADESE','AFYON','AGESA','AGHOL','AGYO','AHGAZ',
    'AKBNK','AKCNS','AKENR','AKFGY','AKFYE','AKMGY','AKSA','AKSEN','AKSGY','AKSUE',
    'AKTK','ALARK','ALBRK','ALCAR','ALFAS','ALGYO','ALKIM','ALKLC','ALMAD','ALTNY',
    'ANELE','ANGYO','ANSGR','ANTGM','ANTTL','ARASE','ARCLK','ARDYZ','ARENA','ARFYO',
    'ARMDA','ARSAN','ARTMS','ASELS','ASGYO','ASTOR','ATAGY','ATATP','ATEKS','ATLAS',
    'AVGYO','AVHOL','AVISA','AVOD','AVPGY','AYCES','AYES','AYGAZ','AZTEK','BAGFS',
    'BAKAB','BANVT','BARMA','BAYDK','BBGYO','BERA','BEYAZ','BFREN','BIGCH','BIGGR',
    'BIMAS','BIOEN','BIZIM','BJKAS','BKFIN','BMSCH','BNTAS','BOSSA','BRISA','BRKO',
    'BRLSM','BRMEN','BRSAN','BSOKE','BTCIM','BUCIM','BURCE','BURVA','BVSAN','BYENO',
    'BYDNR','CANTE','CEOEM','CIMSA','CLEBI','CMBTN','CMENT','CONAS','CONSE','COSMO',
    'CRDFA','CRFSA','CUSAN','CVKMD','CWENE','DAGHL','DARDL','DENGE','DEVA','DGGYO',
    'DGNMO','DITAS','DNISI','DOAS','DOGUB','DOKTA','DOMB','DURDO','DYOBY','DZGYO',
    'EBEBK','ECILC','ECZYT','EGEEN','EGGUB','EGPRO','EGSER','EKGYO','ELITE','EMKEL',
    'ENERY','ENJSA','ENKAI','EPLAS','ERBOS','EREGL','ERGLI','ESCAR','ESCOM','ETILR',
    'EUPWR','EUHOL','EUREN','FENER','FLAP','FMIZP','FONET','FORMT','FROTO','GARAN',
    'GARFA','GEDZA','GENIL','GENTS','GILGZ','GLBMD','GLCVY','GLRYH','GLYHO','GMTAS',
    'GOBFN','GOKNR','GOLTS','GOZDE','GRSEL','GRTRK','GSDDE','GSDHO','GSRAY','GUBRF',
    'GVZGY','HALKB','HATEK','HDFGS','HEDEF','HEKTS','HLGYO','HOROZ','HTTBT','HUBVC',
    'HUNER','IDGYO','IEYHO','IHEVA','IHGZT','IHLAS','IHLGM','IKYHO','IMASM','INDES',
    'INFO','INGRM','INTEM','INVEO','IPEKE','ISATR','ISBTR','ISDMR','ISFIN','ISYAT',
    'IZENR','IZFAS','IZINV','IZMDC','IZOCM','JANTS','KAPLM','KAREL','KARSN','KATMR',
    'KAYSE','KBORU','KCAER','KCHOL','KENT','KERVT','KLGYO','KLKIM','KLMSN','KLRHO',
    'KMPUR','KNFRT','KOCMT','KOTON','KOZAA','KOZAL','KRDMA','KRDMB','KRDMD','KRGYO',
    'KRPLS','KRSTL','KRTEK','KSTUR','KTLEV','KTSKR','KUTPO','KUYAS','LIDFA','LKMNH',
    'LMKDC','LOGO','LRSHO','LUKSK','MAGEN','MAKIM','MAKTK','MANAS','MARKA','MARTI',
    'MAVI','MEDTR','MEGAP','MEPET','MERCN','MERIT','MERKO','METRO','MIATK','MIPAZ',
    'MMCAS','MNDRS','MNDTR','MOBTL','MPARK','MRGYO','MRPAS','MRSHL','MSGLD','MTRKS',
    'NATEN','NETAS','NIBAS','NILYT','NTHOL','NTTUR','NUGYO','NUHCM','OBAMS','ODAS',
    'ONCSM','ORCAY','ORGE','OSTIM','OTKAR','OYAKC','OYYAT','OZGYO','OZKGY','PAMEL',
    'PAPIL','PARSN','PASEU','PCILT','PETKM','PETUN','PGSUS','PINSU','PKART','PKENT',
    'PLTUR','PNLSN','POLHO','POLTK','PRKAB','PRKME','PRZMA','PSDTC','PSGYO','PTOFS',
    'RTALB','RUBNS','SAFKR','SAHOL','SAMAT','SANEL','SANFM','SANKO','SARKY','SASA',
    'SAYAS','SELEC','SELGD','SEYKM','SILVR','SISE','SKBNK','SKYLP','SMART','SNGYO',
    'SNKRN','SODSN','SOKM','SONME','SRVGY','SUNTK','SURGY','SUWEN','TABGD','TATGD',
    'TAVHL','TBORG','TCELL','TDGYO','TEKTU','TEZOL','THYAO','TLMAN','TMPOL','TOASO',
    'TRCAS','TRGYO','TRILC','TSGYO','TUCLK','TUPRS','TUREX','TURGG','TURSG','UCRET',
    'UFUK','ULKER','ULUFA','ULUSE','ULUUN','UNLU','USAK','USDM','VAKBN','VAKFN',
    'VAKKO','VERTU','VERUS','VESBE','VESTL','VKFYO','VKGYO','VKING','VRGYO','YEOTK',
    'YGYO','YKSLN','YONGA','YYLGD','ZEDUR','ZRGYO'
]


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })


def get_ema(series, period):
    return series.ewm(span=period, adjust=False).mean().iloc[-1]


def analyze(ticker, df, benchmark):
    try:
        closes = df['Close'].dropna()
        highs  = df['High'].dropna()
        lows   = df['Low'].dropna()
        vols   = df['Volume'].dropna()
        if len(closes) < 20:
            return None

        cur  = float(closes.iloc[-1])
        prev = float(closes.iloc[-2])

        # Temel kriterler
        w_chg = (cur - prev) / prev * 100
        c1 = bool(w_chg > HAFTALIK_ESIK)

        n   = min(14, len(highs))
        dr  = (highs.iloc[-n:].values - lows.iloc[-n:].values) / lows.iloc[-n:].values * 100
        adr = float(np.mean(dr))
        c2  = bool(adr >= ADR_ESIK)

        e21 = get_ema(closes, 21)
        c3  = bool(cur > e21)

        e50 = get_ema(closes, 50) if len(closes) >= 50 else None
        c4  = bool(cur > e50) if e50 else None

        vol_chg = None
        if len(vols) >= 8:
            rv = float(vols.iloc[-4:].mean())
            pv = float(vols.iloc[-8:-4].mean())
            if pv > 0:
                vol_chg = (rv - pv) / pv * 100
        c5 = bool(vol_chg is not None and vol_chg > HACIM_ESIK)

        temel = sum(1 for x in [c1, c2, c3, c4, c5] if x is True)

        # Pro kriterler
        rs_val = None
        p1 = None
        try:
            aln = pd.concat([closes.rename('s'), benchmark.rename('b')], axis=1).dropna()
            if len(aln) >= 13:
                s_r = float(aln['s'].iloc[-1]) / float(aln['s'].iloc[-13])
                b_r = float(aln['b'].iloc[-1]) / float(aln['b'].iloc[-13])
                rs_val = s_r / b_r if b_r > 0 else None
                p1 = bool(rs_val is not None and rs_val > RS_ESIK)
        except:
            pass

        p2 = None
        if len(closes) >= BREAKOUT_HAFTA + 1:
            prev_high = float(closes.iloc[-(BREAKOUT_HAFTA + 1):-1].max())
            p2 = bool(cur > prev_high)

        vol_oran = None
        p3 = None
        if len(vols) >= 11:
            cv = float(vols.iloc[-1])
            av = float(vols.iloc[-11:-1].mean())
            if av > 0:
                vol_oran = cv / av
                p3 = bool(vol_oran >= HACIM_KAT)

        poz_hafta = None
        p4 = None
        if len(closes) >= TREND_HAFTA + 1:
            degisimler = closes.iloc[-(TREND_HAFTA + 1):].pct_change().dropna()
            poz_hafta = int((degisimler > 0).sum())
            p4 = bool(poz_hafta >= TREND_MIN_POZ)

        p5 = bool(e21 > e50) if e50 is not None else None

        pro    = sum(1 for x in [p1, p2, p3, p4, p5] if x is True)
        toplam = temel + pro

        return {
            'ticker':  ticker,
            'fiyat':   round(cur, 2),
            'w_chg':   round(w_chg, 2),
            'adr':     round(adr, 2),
            'rs':      round(rs_val, 3) if rs_val else None,
            'temel':   temel,
            'pro':     pro,
            'toplam':  toplam,
            'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4, 'c5': c5,
            'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5,
        }
    except:
        return None


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Tarama başlıyor...")
    send_telegram("⏳ <b>BIST Momentum Taraması başladı...</b>")

    # Benchmark
    xu100 = yf.download('XU100.IS', period='2y', interval='1wk',
                         auto_adjust=True, progress=False)
    if isinstance(xu100.columns, pd.MultiIndex):
        xu100.columns = xu100.columns.get_level_values(0)
    benchmark = xu100['Close'].squeeze().dropna()

    # Hisse verileri
    stock_data = {}
    for i, ticker in enumerate(TICKERS):
        try:
            raw = yf.download(ticker + '.IS', period='2y', interval='1wk',
                              auto_adjust=True, progress=False)
            if raw is None or len(raw) < 15:
                continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw = raw.dropna(subset=['Close'])
            if len(raw) >= 15:
                stock_data[ticker] = raw
        except:
            pass
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(TICKERS)} hisse işlendi...")

    print(f"  {len(stock_data)} hisse verisi alındı.")

    # Analiz
    results = []
    for ticker, df in stock_data.items():
        r = analyze(ticker, df, benchmark)
        if r:
            results.append(r)

    if not results:
        send_telegram("⚠️ Bugün tarama sonucu alınamadı.")
        return

    df = pd.DataFrame(results).sort_values('toplam', ascending=False)
    taranan = len(df)

    # İlk 5 — en yüksek toplam skor
    top5 = df.head(5)

    bugun = datetime.now().strftime('%d.%m.%Y')
    saat  = datetime.now().strftime('%H:%M')

    mesaj = f"""📊 <b>BIST Momentum Screener</b>
📅 {bugun} | 🕕 {saat}
🔍 {taranan} hisse tarandı

🏆 <b>GÜNÜN EN GÜÇLÜ 5 HİSSESİ</b>
━━━━━━━━━━━━━━━━━━━━━━━"""

    semboller = {
        True:  '✅',
        False: '❌',
        None:  '—'
    }

    for i, row in enumerate(top5.itertuples(), 1):
        temel_bar = '🟩' * row.temel + '⬜' * (5 - row.temel)
        pro_bar   = '🔵' * row.pro   + '⬜' * (5 - row.pro)
        w_sign    = '+' if row.w_chg >= 0 else ''

        mesaj += f"""

{i}. <b>${row.ticker}</b> — {row.fiyat} TL
   Haftalık: <b>{w_sign}{row.w_chg}%</b> | ADR: {row.adr}% | RS: {row.rs if row.rs else '—'}
   Temel {row.temel}/5: {temel_bar}
   Pro    {row.pro}/5: {pro_bar}
   Toplam: <b>{row.toplam}/10</b>"""

    # Kaç hisse 8+ aldı
    guclu = len(df[df['toplam'] >= 8])
    mesaj += f"""

━━━━━━━━━━━━━━━━━━━━━━━
💪 8+ skor alan: <b>{guclu} hisse</b>
⚠️ Bu mesaj yatırım tavsiyesi değildir."""

    send_telegram(mesaj)
    print("✅ Telegram mesajı gönderildi.")
    print(mesaj)


if __name__ == '__main__':
    main()
