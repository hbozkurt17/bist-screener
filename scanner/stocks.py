# ============================================================
# BIST30 ve BIST100 Hisse Listeleri (Yahoo Finance formatı: .IS)
# ============================================================

BIST30 = [
    "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "DOHOL.IS",
    "EKGYO.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", "HALKB.IS",
    "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "KRDMD.IS", "MGROS.IS",
    "ODAS.IS",  "OTKAR.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS",
    "SASA.IS",  "SISE.IS",  "TAVHL.IS", "TCELL.IS", "THYAO.IS",
    "TKFEN.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "YKBNK.IS",
]

# BIST100 - BIST30 hariç 70 hisse
_BIST100_FULL = [
    # Bankacılık & Finans
    "VAKBN.IS", "SKBNK.IS", "QNBFB.IS", "ICBCT.IS", "ALBRK.IS",
    "KLNMA.IS", "TSKB.IS",  "ENJSA.IS", "NTHOL.IS", "GSDHO.IS",
    # Sanayi & Üretim
    "AEFES.IS", "AGESA.IS", "AKCNS.IS", "AKSA.IS",  "AKSEN.IS",
    "ALFAS.IS", "ALKIM.IS", "ASUZU.IS", "AVGYO.IS", "AYDEM.IS",
    "AYGAZ.IS", "BAGFS.IS", "BERA.IS",  "BIOEN.IS", "BRISA.IS",
    "BRYAT.IS", "BUCIM.IS", "CCOLA.IS", "CEMAS.IS", "CEMTS.IS",
    "CLEBI.IS", "CIMSA.IS", "CWENE.IS", "DEVA.IS",  "DYOBY.IS",
    "EGEEN.IS", "EGPRO.IS", "ENKAI.IS", "EUPWR.IS", "FENER.IS",
    "FLAP.IS",  "GENIL.IS", "GESAN.IS", "GOLTS.IS", "GUBRF.IS",
    "GWIND.IS", "HEKTS.IS", "IPEKE.IS", "ISGYO.IS", "IZENR.IS",
    "JANTS.IS", "KAREL.IS", "KAYSE.IS", "KERVT.IS", "KMPUR.IS",
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
