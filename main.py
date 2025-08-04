import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --- Titre de l'application ---
st.set_page_config(page_title="Simulateur ETFS", layout="centered")
st.title("📈 Simulateur pour atteindre 1 Million d'€")

st.markdown("""
Ce simulateur permet d'estimer en combien de temps vous pouvez atteindre **1 million d'euros** 
en investissant régulièrement dans un indice boursier, avec la possibilité de simuler des **frais annuels**.
""")

# --- Entrées utilisateur ---
st.sidebar.header("🎛️ Paramètres")
initial_investment = st.sidebar.number_input("💰 Investissement initial (€)", min_value=0, value=10000, step=1000)
monthly_contribution = st.sidebar.number_input("📆 Contribution mensuelle (€)", min_value=0, value=250, step=50)
target_value = st.sidebar.number_input("🎯 Objectif à atteindre (€)", min_value=10000, value=1_000_000, step=50000)
annual_fee_percent = st.sidebar.number_input("💼 Frais annuels (%)", min_value=0.0, max_value=5.0, value=0.3, step=0.1)

tickers = {
    "^GSPC": "S&P 500",
    "^NDX": "Nasdaq 100",
    "^DJI": "Dow Jones Industrial Average",
    "^RUT": "Russell 2000",
    "^GSPTSE": "S&P/TSX Composite",
    "^FTSE": "FTSE 100",
    "^STOXX50E": "Euro Stoxx 50",
    "^FCHI": "CAC 40 (France)",
    "^GDAXI": "DAX 40 (Allemagne)",
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

selected_ticker = st.sidebar.selectbox("📊 Choisissez un indice", options=list(tickers.keys()), format_func=lambda x: tickers[x])

# --- Téléchargement des données ---
@st.cache_data
def get_data(ticker):
    data = yf.download(ticker, start="1930-01-01", interval="1mo")['Close']
    return data.dropna()

data = get_data(selected_ticker)

@st.cache_data
def get_holdings(etf_ticker):
    try:
        etf = yf.Ticker(etf_ticker)
        holdings = etf.fund_holdings
        if holdings is not None and not holdings.empty:
            return holdings[['holdingName', 'holdingPercent']].head(10)
    except:
        return None
    return None

# --- Synthèse utilisateur ---
st.markdown("### 🧾 Synthèse de vos paramètres")
st.markdown(f"""
- **Investissement initial** : `{initial_investment:,.0f} €`
- **Contribution mensuelle** : `{monthly_contribution:,.0f} €`
- **Objectif à atteindre** : `{target_value:,.0f} €`
- **Frais annuels estimés** : `{annual_fee_percent:.2f} %`
- **Indice sélectionné** : `{tickers[selected_ticker]}`
""")

# --- Informations ETF ---
st.subheader(f"Simulation sur l’indice : **{tickers[selected_ticker]}**")

if selected_ticker == "^GSPC":
    st.markdown("**Top 10 des entreprises (via ETF SPY)**")
    holdings = get_holdings("SPY")
    if holdings is not None:
        st.dataframe(holdings)
    else:
        st.warning("Les données de composition ne sont pas disponibles actuellement.")

# --- Simulation ---
def simulate_growth(prices, start_idx, annual_fee):
    if isinstance(prices, pd.DataFrame):
        prices = prices.squeeze()

    prices = prices[start_idx:].reset_index(drop=True)
    portfolio_value = float(initial_investment)

    for i in range(len(prices)):
        if i > 0:
            growth = float(prices.iloc[i]) / float(prices.iloc[i - 1])
            portfolio_value *= growth
        monthly_fee = (1 - annual_fee / 100) ** (1 / 12)
        portfolio_value *= monthly_fee
        if i > 0:
            portfolio_value += monthly_contribution
        if isinstance(portfolio_value, (pd.Series, pd.DataFrame)):
            portfolio_value = float(portfolio_value)
        if portfolio_value >= target_value:
            return i / 12
    return None

def run_simulation(prices, annual_fee):
    results = []
    max_start = len(prices) - 12 * 5
    for start_idx in range(max_start):
        result = simulate_growth(prices, start_idx, annual_fee)
        if result:
            results.append(result)
    return results

# --- Exécution ---
with st.spinner("🔄 Simulation en cours..."):
    results = run_simulation(data, annual_fee_percent)

# --- Résultats ---
if results:
    avg = np.mean(results)
    med = np.median(results)

    st.markdown("### 📊 Résultats de la simulation")
    st.success(f"""
- 🟠 **Durée moyenne** pour atteindre l’objectif : **{avg:.1f} ans**
- 🟢 **Durée médiane** : **{med:.1f} ans**
""")

    fig, ax = plt.subplots()
    ax.hist(results, bins=20, color="skyblue", edgecolor="black")
    ax.axvline(avg, color="red", linestyle="--", label=f"Moyenne: {avg:.1f} ans")
    ax.axvline(med, color="green", linestyle="--", label=f"Médiane: {med:.1f} ans")
    ax.set_title(f"Temps pour atteindre {target_value:,.0f}€ ({tickers[selected_ticker]})")
    ax.set_xlabel("Années")
    ax.set_ylabel("Nombre de simulations")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("❗ L'objectif n’a jamais été atteint dans les simulations.")

st.caption("© Simulation basée sur les performances historiques mensuelles Yahoo Finance")
