import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from etfs_list import *

st.set_page_config(page_title="Montants Obtenus", layout="centered")
st.title("📊 Simulation de Montants Obtenus (sans objectif)")

st.markdown("""
Simulez l'évolution de votre portefeuille **sans objectif à atteindre**, simplement pour observer 
les **résultats finaux** selon les performances historiques d’un indice.
""")

# --- Entrées utilisateur ---
st.sidebar.header("🎛️ Paramètres")
initial_investment = st.sidebar.number_input("💰 Investissement initial (€)", min_value=0, value=10000, step=1000)
monthly_contribution = st.sidebar.number_input("📆 Contribution mensuelle (€)", min_value=0, value=250, step=50)
investment_duration_years = st.sidebar.slider("⏳ Durée de l'investissement (années)", 5, 40, 20)
annual_fee_percent = st.sidebar.number_input("💼 Frais annuels (%)", min_value=0.0, max_value=5.0, value=0.3, step=0.1)

tickers = etfs()

selected_ticker = st.sidebar.selectbox("📊 Choisissez un indice", options=list(tickers.keys()), format_func=lambda x: tickers[x])

# --- Téléchargement des données ---
@st.cache_data
def get_data(ticker):
    data = yf.download(ticker, start="1930-01-01", interval="1mo")['Close']
    return data.dropna()

data = get_data(selected_ticker)

# --- Simulation des montants finaux ---
def simulate_final_amount(prices, start_idx, annual_fee, years):
    months = years * 12
    if isinstance(prices, pd.DataFrame):
        prices = prices.squeeze()

    if start_idx + months >= len(prices):
        return None

    prices = prices[start_idx:start_idx + months].reset_index(drop=True)
    portfolio_value = float(initial_investment)

    for i in range(len(prices)):
        if i > 0:
            growth = float(prices.iloc[i]) / float(prices.iloc[i - 1])
            portfolio_value *= growth
        monthly_fee = (1 - annual_fee / 100) ** (1 / 12)
        portfolio_value *= monthly_fee
        if i > 0:
            portfolio_value += monthly_contribution

    return portfolio_value

def run_simulation(prices, annual_fee, years):
    results = []
    max_start = len(prices) - years * 12
    for start_idx in range(max_start):
        result = simulate_final_amount(prices, start_idx, annual_fee, years)
        if result:
            results.append(result)
    return results

# --- Synthèse utilisateur ---
st.markdown("### 🧾 Synthèse de vos paramètres")
st.markdown(f"""
- **Investissement initial** : `{initial_investment:,.0f} €`
- **Contribution mensuelle** : `{monthly_contribution:,.0f} €`
- **Durée simulée** : `{investment_duration_years} ans`
- **Frais annuels estimés** : `{annual_fee_percent:.2f} %`
- **Indice sélectionné** : `{tickers[selected_ticker]}`
""")

# --- Lancer simulation ---
with st.spinner("🔄 Simulation en cours..."):
    results = run_simulation(data, annual_fee_percent, investment_duration_years)

# --- Affichage des résultats ---
if results:
    avg = np.mean(results)
    med = np.median(results)

    st.markdown("### 📈 Montants obtenus après simulation")
    st.success(f"""
- 💰 **Montant moyen obtenu** : **{avg:,.0f} €**
- 💎 **Montant médian** : **{med:,.0f} €**
""")

    fig, ax = plt.subplots()
    ax.hist(results, bins=30, color="lightgreen", edgecolor="black")
    ax.axvline(avg, color="red", linestyle="--", label=f"Moyenne: {avg:,.0f} €")
    ax.axvline(med, color="blue", linestyle="--", label=f"Médiane: {med:,.0f} €")
    ax.set_title(f"Distribution des montants finaux sur {investment_duration_years} ans\n({tickers[selected_ticker]})")
    ax.set_xlabel("Montant final (€)")
    ax.set_ylabel("Nombre de simulations")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("❗ Les données historiques sont insuffisantes pour cette durée.")

st.caption("© Simulation basée sur les performances historiques mensuelles Yahoo Finance")
