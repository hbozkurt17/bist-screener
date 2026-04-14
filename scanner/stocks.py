# ============================================================
# BIST30 ve BIST100 Hisse Listeleri (Yahoo Finance formatı: .IS)
# Son güncelleme: 14 Nisan 2026 — kaynak: tr.investing.com
# ============================================================

BIST30 = [
    # Bankacılık & Finans
    "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "VAKBN.IS", "YKBNK.IS",
    "DESTK.IS",
    # Holding & Sanayi
    "KCHOL.IS", "SAHOL.IS", "ENKAI.IS", "ASTOR.IS",
    # Enerji & Kimya
    "PETKM.IS", "TUPRS.IS", "GUBRF.IS",
    # Demir-Çelik & Metal
    "EREGL.IS", "KRDMD.IS",
    # Otomotiv
    "FROTO.IS", "TOASO.IS",
    # Havacılık & Turizm
    "THYAO.IS", "PGSUS.IS", "TAVHL.IS",
    # Teknoloji & Telecom
    "ASELS.IS", "TCELL.IS", "TTKOM.IS",
    # Perakende & Gıda
    "BIMAS.IS", "MGROS.IS", "AEFES.IS",
    # GYO & Diğer
    "EKGYO.IS", "SISE.IS", "SASA.IS", "KOZAL.IS",
]

# BIST100 TAM LİSTE (BIST30 dahil)
_BIST100_FULL = [
    # ── BIST30 hisseleri ──────────────────────────────────────
    "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "VAKBN.IS", "YKBNK.IS",
    "DESTK.IS", "KCHOL.IS", "SAHOL.IS", "ENKAI.IS", "ASTOR.IS",
    "PETKM.IS", "TUPRS.IS", "GUBRF.IS", "EREGL.IS", "KRDMD.IS",
    "FROTO.IS", "TOASO.IS", "THYAO.IS", "PGSUS.IS", "TAVHL.IS",
    "ASELS.IS", "TCELL.IS", "TTKOM.IS", "BIMAS.IS", "MGROS.IS",
    "AEFES.IS", "EKGYO.IS", "SISE.IS",  "SASA.IS",  "KOZAL.IS",
    # ── Bankacılık & Finans (ex-30) ───────────────────────────
    "SKBNK.IS", "QNBFB.IS", "ICBCT.IS", "ALBRK.IS",
    "KLNMA.IS", "TSKB.IS",  "ENJSA.IS", "NTHOL.IS", "GSDHO.IS",
    # ── Eski BIST30 → şimdi BIST100 ──────────────────────────
    "ARCLK.IS", "DOHOL.IS", "HALKB.IS", "ODAS.IS",
    "OTKAR.IS", "TKFEN.IS",
    # ── Sanayi & Üretim (ex-30) ───────────────────────────────
    "AGESA.IS", "AKCNS.IS", "AKSA.IS",  "AKSEN.IS",
    "ALFAS.IS", "ALKIM.IS", "ASUZU.IS", "AVGYO.IS", "AYDEM.IS",
    "AYGAZ.IS", "BAGFS.IS", "BERA.IS",  "BIOEN.IS", "BRISA.IS",
    "BRYAT.IS", "BUCIM.IS", "CCOLA.IS", "CEMAS.IS", "CEMTS.IS",
    "CLEBI.IS", "CIMSA.IS", "CWENE.IS", "DEVA.IS",  "DYOBY.IS",
    "EGEEN.IS", "EGPRO.IS", "EUPWR.IS", "FENER.IS",
    "FLAP.IS",  "GENIL.IS", "GESAN.IS", "GOLTS.IS",
    "GWIND.IS", "HEKTS.IS", "ISGYO.IS", "IZENR.IS",
    "JANTS.IS", "KAREL.IS", "KAYSE.IS", "KMPUR.IS",
    "KONTR.IS", "KONYA.IS", "KORDS.IS", "KUTPO.IS", "LMKDC.IS",
    "LOGO.IS",  "LRSHO.IS", "MAVI.IS",  "NETAS.IS", "NUHCM.IS",
    "ORCAY.IS", "PARSN.IS", "PENGD.IS", "PRKME.IS", "RNPOL.IS",
    "SELEC.IS", "SILVR.IS", "SMART.IS", "SMRTG.IS", "SOKM.IS",
]

# BIST100 ex-BIST30 (BIST30 hisseleri çıkarılmış)
BIST100_EX_BIST30 = [t for t in _BIST100_FULL if t not in BIST30]

if __name__ == "__main__":
    print(f"BIST30 hisse sayısı   : {len(BIST30)}")
    print(f"BIST100 ex-30 sayısı  : {len(BIST100_EX_BIST30)}")
    print(f"Toplam taranacak      : {len(BIST30) + len(BIST100_EX_BIST30)}")
    overlap = set(BIST30) & set(BIST100_EX_BIST30)
    print(f"Çakışma               : {len(overlap)} hisse {overlap if overlap else '(yok)'}")
