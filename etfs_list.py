def etfs():
    return {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^DJI": "Dow Jones Industrial Average",
        "^RUT": "Russell 2000",
        "^GSPTSE": "S&P/TSX Composite",
        "^FTSE": "FTSE 100",
        "^STOXX50E": "Euro Stoxx 50",
        "^FCHI": "CAC 40 (France)",
        "^GDAXI": "DAX 40 (Allemagne)",
        # 🌍 Indices mondiaux et régionaux
        "URTH":"MSCI World Index",  # ETF représentant le MSCI World
        "ACWI":"ACWI (All Country World Index)",
        "^IBEX": "IBEX 35 (Espagne)",
        "^AEX": "AEX 25 (Pays-Bas)",
        "^SSMI": "SMI (Suisse)",
        "^N225": "Nikkei 225 (Japon)",
        "^HSI": "Hang Seng Index (Hong Kong)",
        "000001.SS": "SSE Composite (Chine)",
        "^TWII": "TSEC Weighted Index (Taïwan)",
        "^BSESN": "BSE Sensex (Inde)",
        "^AXJO": "ASX 200 (Australie)",
        "^BVSP": "IBOVESPA (Brésil)",
        "^MXX": "IPC Mexico",
        "^KS11": "KOSPI (Corée du Sud)",
        "^JKSE": "IDX Composite (Indonésie)",
        "^TA125.TA": "TA-125 (Israël)",
        "CL=F": "Pétrole brut (WTI)",
        "GC=F": "Or (Gold)",
        "SI=F": "Argent (Silver)",
        "BTC-EUR": "(Bitcoin)"
    }

def etfs_enrich_list():
    return {
    # 🇺🇸 USA
    "S&P 500 (USA)": "^GSPC",
    "NASDAQ 100 (USA)": "^NDX",
    "Dow Jones (USA)": "^DJI",
    "Russell 2000 (USA)": "^RUT",

    # 🇨🇦 Canada
    "S&P/TSX Composite (Canada)": "^GSPTSE",

    # 🇬🇧 Royaume-Uni
    "FTSE 100 (UK)": "^FTSE",

    # 🇩🇪 Allemagne
    "DAX (Germany)": "^GDAXI",

    # 🇫🇷 France
    "CAC 40 (France)": "^FCHI",

    # 🇪🇺 Europe
    "STOXX Europe 600": "^STOXX",
    "EURO STOXX 50": "^STOXX50E",

    # 🌍 Indices mondiaux et régionaux
    "MSCI World Index": "URTH",  # ETF représentant le MSCI World
    "MSCI Emerging Markets": "EEM",
    "MSCI EAFE (Europe, Australasia, Far East)": "EFA",
    "ACWI (All Country World Index)": "ACWI",

    # 🇯🇵 Japon
    "Nikkei 225 (Japan)": "^N225",

    # 🇨🇳 Chine
    "Shanghai Composite (China)": "000001.SS",
    "CSI 300 (China)": "000300.SS",

    # 🇭🇰 Hong Kong
    "Hang Seng (Hong Kong)": "^HSI",

    # 🇰🇷 Corée du Sud
    "KOSPI (South Korea)": "^KS11",

    # 🇮🇳 Inde
    "BSE Sensex (India)": "^BSESN",
    "Nifty 50 (India)": "^NSEI",

    # 🇧🇷 Brésil
    "Bovespa (Brazil)": "^BVSP",

    # 🇲🇽 Mexique
    "IPC Mexico": "^MXX",

    # 🇦🇺 Australie
    "S&P/ASX 200 (Australia)": "^AXJO",

    # 🇿🇦 Afrique du Sud
    "FTSE/JSE Top 40 (South Africa)": "J200.JO"
}
