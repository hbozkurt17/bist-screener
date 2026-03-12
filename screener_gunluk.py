import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import warnings
from datetime import datetime, date
from pathlib import Path

warnings.filterwarnings('ignore')

BOT_TOKEN = "8766976766:AAGCxR_ussy_n-vED6Jono-U5tvVQC2UPN0"
CHAT_ID   = "1019011392"

# ── Günlük Kriterler ──────────────────────────────────────
GUNLUK_DEGISIM_ESIK = 2.0    # Günlük % değişim (haftalık %5 → günlük %2)
ADR_ESIK            = 1.5    # Günlük ADR % (haftalık %2 → günlük %1.5)
HACIM_KAT_ESIK      = 1.5    # Günlük hacim, 20 günlük ort. kaç katı
RS_ESIK             = 1.02   # BIST100'e göre 20 günlük RS
BREAKOUT_GUN        = 20     # Kaç günlük zirve kırılımı
TREND_GUN           = 10     # Trend tutarlılık penceresi (gün)
TREND_MIN_POZ       = 6      # Bu günlerin kaçı pozitif olmalı
ATR_PERIOD          = 14
ATR_STOP_KAT        = 1.5
ATR_HEDEF_KAT       = 3.0
TOP_N               = 10
HISTORY_FILE        = "gecmis_gunluk.json"

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
    r = requests.post(url, json={
        "chat_id": CHAT_ID, "text": msg,
        "parse_mode": "HTML", "disable_web_page_preview": True
    })
    return r.status_code == 200

def load_history():
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}

def save_history(h):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(h, f, indent=2)

def update_history(history, liste):
    bugun = str(date.today())
    for t in liste:
        if t not in history:
            history[t] = {"streak": 1, "ilk": bugun, "son": bugun}
        else:
            history[t]["streak"] += 1
            history[t]["son"] = bugun
    for t in list(history.keys()):
        if t not in liste:
            history[t]["streak"] = 0
    return history

def get_ema(s, p):
    return s.ewm(span=p, adjust=False).mean().iloc[-1]

def calc_atr(high, low, close, period=14):
    h, l, c = high.values, low.values, close.values
    tr = np.maximum(h[1:]-l[1:], np.maximum(abs(h[1:]-c[:-1]), abs(l[1:]-c[:-1])))
    return float(np.mean(tr[-period:])) if len(tr) >= period else None

def calc_trend_suresi(closes, e21_series):
    ema21, cls = e21_series.values, closes.values
    count = 0
    for i in range(len(cls)-1, -1, -1):
        if cls[i] > ema21[i]: count += 1
        else: break
    return count

def calc_risk(adr, atr_pct):
    if adr is None or atr_pct is None: return "Orta", "🟡"
    if adr > 8 or atr_pct > 6:  return "Yüksek", "🔴"
    elif adr > 4 or atr_pct > 3: return "Orta", "🟡"
    return "Düşük", "🟢"

def analyze(ticker, df, benchmark):
    try:
        closes = df['Close'].dropna()
        highs  = df['High'].dropna()
        lows   = df['Low'].dropna()
        vols   = df['Volume'].dropna()
        if len(closes) < 30: return None

        cur  = float(closes.iloc[-1])
        prev = float(closes.iloc[-2])

        # C1: Günlük değişim > %2
        d_chg = (cur - prev) / prev * 100
        c1 = bool(d_chg > GUNLUK_DEGISIM_ESIK)

        # C2: Günlük ADR ≥ %1.5 (son 14 gün)
        n   = min(14, len(highs))
        dr  = (highs.iloc[-n:].values - lows.iloc[-n:].values) / lows.iloc[-n:].values * 100
        adr = float(np.mean(dr))
        c2  = bool(adr >= ADR_ESIK)

        # C3: Fiyat > günlük EMA21
        e21_series = closes.ewm(span=21, adjust=False).mean()
        e21 = float(e21_series.iloc[-1])
        c3  = bool(cur > e21)

        # C4: Fiyat > günlük EMA50
        e50 = get_ema(closes, 50) if len(closes) >= 50 else None
        c4  = bool(cur > e50) if e50 else None

        # C5: Günlük hacim, 20 günlük ort. 1.5x
        vol_oran_c5 = None
        if len(vols) >= 21:
            cv = float(vols.iloc[-1])
            av = float(vols.iloc[-21:-1].mean())
            if av > 0:
                vol_oran_c5 = cv / av
        c5 = bool(vol_oran_c5 is not None and vol_oran_c5 >= HACIM_KAT_ESIK)

        temel = sum(1 for x in [c1,c2,c3,c4,c5] if x is True)

        # P1: RS vs BIST100 (20 gün)
        rs_val, p1 = None, None
        try:
            aln = pd.concat([closes.rename('s'), benchmark.rename('b')], axis=1).dropna()
            if len(aln) >= 21:
                s_r = float(aln['s'].iloc[-1]) / float(aln['s'].iloc[-21])
                b_r = float(aln['b'].iloc[-1]) / float(aln['b'].iloc[-21])
                rs_val = s_r / b_r if b_r > 0 else None
                p1 = bool(rs_val is not None and rs_val > RS_ESIK)
        except: pass

        # P2: 20 günlük zirve kırılımı
        p2 = None
        if len(closes) >= BREAKOUT_GUN + 1:
            p2 = bool(cur > float(closes.iloc[-(BREAKOUT_GUN+1):-1].max()))

        # P3: Hacim teyidi (bugünkü hacim 10 günlük ort. 1.5x)
        vol_oran_p3, p3 = None, None
        if len(vols) >= 11:
            cv = float(vols.iloc[-1])
            av = float(vols.iloc[-11:-1].mean())
            if av > 0:
                vol_oran_p3 = cv / av
                p3 = bool(vol_oran_p3 >= HACIM_KAT_ESIK)

        # P4: Trend tutarlılığı — son 10 günün 6'sı pozitif
        poz_gun, p4 = None, None
        if len(closes) >= TREND_GUN + 1:
            deg = closes.iloc[-(TREND_GUN+1):].pct_change().dropna()
            poz_gun = int((deg > 0).sum())
            p4 = bool(poz_gun >= TREND_MIN_POZ)

        # P5: EMA21 > EMA50 (günlük)
        p5 = bool(e21 > e50) if e50 is not None else None

        pro    = sum(1 for x in [p1,p2,p3,p4,p5] if x is True)
        toplam = temel + pro

        # ATR & Stop/Hedef
        atr = calc_atr(highs, lows, closes, ATR_PERIOD)
        atr_pct   = round(atr / cur * 100, 2) if atr else None
        stop      = round(cur - ATR_STOP_KAT * atr, 2) if atr else None
        hedef     = round(cur + ATR_HEDEF_KAT * atr, 2) if atr else None
        stop_pct  = round((stop - cur) / cur * 100, 1) if stop else None
        hedef_pct = round((hedef - cur) / cur * 100, 1) if hedef else None

        trend_sure          = calc_trend_suresi(closes, e21_series)
        risk_label, risk_em = calc_risk(adr, atr_pct)

        return {
            'ticker': ticker, 'fiyat': round(cur, 2),
            'd_chg': round(d_chg, 2), 'adr': round(adr, 2),
            'rs': round(rs_val, 3) if rs_val else None,
            'atr_pct': atr_pct, 'stop': stop, 'stop_pct': stop_pct,
            'hedef': hedef, 'hedef_pct': hedef_pct,
            'trend_sure': trend_sure, 'risk_label': risk_label, 'risk_emoji': risk_em,
            'temel': temel, 'pro': pro, 'toplam': toplam,
        }
    except: return None

def format_mesaj(top10, history, taranan, bugun, saat, guclu, gun_adi):
    msg = (
        f"📅 <b>BIST Günlük Momentum — {gun_adi}</b>\n"
        f"📆 {bugun}  |  🕖 {saat}\n"
        f"🔍 {taranan} hisse  |  💪 8+ skor: {guclu} hisse\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>GÜNÜN EN GÜÇLÜ {TOP_N} HİSSESİ</b>\n"
    )
    for i, row in enumerate(top10.itertuples(), 1):
        t      = row.ticker
        streak = history.get(t, {}).get("streak", 1)
        rozet  = f" 🔥x{streak}" if streak >= 3 else (" 🔁x2" if streak == 2 else "")
        w_sign = "+" if row.d_chg >= 0 else ""
        stop_s  = f"{row.stop} TL ({row.stop_pct}%)" if row.stop else "—"
        hedef_s = f"{row.hedef} TL (+{row.hedef_pct}%)" if row.hedef else "—"
        tv      = f"https://tr.tradingview.com/chart/?symbol=BIST:{t}"
        tb      = "🟩" * row.temel + "⬜" * (5 - row.temel)
        pb      = "🔵" * row.pro   + "⬜" * (5 - row.pro)
        msg += (
            f"\n{i}. <b>${t}</b>{rozet}  —  {row.fiyat} TL\n"
            f"   📈 {w_sign}{row.d_chg}%  |  ADR: {row.adr}%  |  RS: {row.rs or '—'}\n"
            f"   ⏱ Trendde: <b>{row.trend_sure} gün</b>  |  {row.risk_emoji} {row.risk_label} risk\n"
            f"   🛑 Stop: {stop_s}\n"
            f"   🎯 Hedef: {hedef_s}\n"
            f"   {tb} Temel {row.temel}/5\n"
            f"   {pb} Pro {row.pro}/5  —  <b>{row.toplam}/10</b>  |  <a href='{tv}'>📊 Grafik</a>\n"
        )
    msg += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥≥3 gün  🔁2 gün üst üste listede\n"
        f"⚠️ Yatırım tavsiyesi değildir."
    )
    return msg

def main():
    now    = datetime.now()
    bugun  = now.strftime('%d.%m.%Y')
    saat   = now.strftime('%H:%M')
    gunler = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar']
    gun_adi = gunler[now.weekday()]

    print(f"[{saat}] Günlük tarama başlıyor...")
    send_telegram(f"⏳ <b>Günlük screener başladı...</b> {gun_adi} {bugun}")

    # Benchmark (günlük)
    xu100 = yf.download('XU100.IS', period='1y', interval='1d',
                         auto_adjust=True, progress=False)
    if isinstance(xu100.columns, pd.MultiIndex):
        xu100.columns = xu100.columns.get_level_values(0)
    benchmark = xu100['Close'].squeeze().dropna()

    # Hisse verileri (günlük)
    stock_data = {}
    for i, ticker in enumerate(TICKERS):
        try:
            raw = yf.download(ticker + '.IS', period='1y', interval='1d',
                              auto_adjust=True, progress=False)
            if raw is None or len(raw) < 30: continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw = raw.dropna(subset=['Close'])
            if len(raw) >= 30:
                stock_data[ticker] = raw
        except: pass
        if (i + 1) % 75 == 0:
            print(f"  {i+1}/{len(TICKERS)} işlendi...")

    results = [r for r in (analyze(t, d, benchmark) for t, d in stock_data.items()) if r]
    if not results:
        send_telegram("⚠️ Bugün günlük tarama sonucu alınamadı.")
        return

    df_all = pd.DataFrame(results).sort_values('toplam', ascending=False)
    top10  = df_all.head(TOP_N)
    guclu  = len(df_all[df_all['toplam'] >= 8])

    history = load_history()
    history = update_history(history, top10['ticker'].tolist())
    save_history(history)

    mesaj = format_mesaj(top10, history, len(df_all), bugun, saat, guclu, gun_adi)
    send_telegram(mesaj)
    print("✅ Gönderildi.")

if __name__ == '__main__':
    main()
