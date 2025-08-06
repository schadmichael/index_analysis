import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from etfs_list import *

# Configuration de la page
st.set_page_config(page_title="Indices & Ratios Financiers", layout="wide")
st.title("📈 Analyse & Comparaison des Indices Boursiers Mondiaux")

# Liste des indices (tu peux remplacer cette liste par un appel à ta fonction etfs() si elle est utile)
indices = {
    "S&P 500 (USA)": "^GSPC",
    "NASDAQ 100 (USA)": "^NDX",
    "Dow Jones (USA)": "^DJI",
    "FTSE 100 (UK)": "^FTSE",
    "DAX (Germany)": "^GDAXI",
    "CAC 40 (France)": "^FCHI",
    "Nikkei 225 (Japan)": "^N225",
    "Hang Seng (Hong Kong)": "^HSI",
    "Shanghai Composite (China)": "000001.SS",
    "S&P/ASX 200 (Australia)": "^AXJO",
}
indices=etfs_enrich_list()
# Sélection des paramètres utilisateur
st.sidebar.header("⚙️ Paramètres")
selected = st.sidebar.multiselect(
    "Choisissez les indices à comparer",
    list(indices.keys()),
    default=["S&P 500 (USA)", "NASDAQ 100 (USA)"]
)
period = st.sidebar.selectbox("Période d'analyse", options=["1y", "3y", "5y", "10y","15y","20y","25y","30y","35y","40y"], index=2)
risk_free_rate = st.sidebar.slider("Taux sans risque (%) pour le Sharpe Ratio", 0.0, 5.0, 2.0) / 100

# Fonction pour récupérer les données
@st.cache_data
def get_data(ticker, period):
    df = yf.download(ticker, period=period)['Close']
    return df.dropna().squeeze()  # Squeeze pour convertir DataFrame → Series si applicable

# Conteneurs
all_returns = pd.DataFrame()
summary_metrics = []

st.subheader(f"📊 Performance cumulée sur {period}")

for name in selected:
    symbol = indices[name]
    price = get_data(symbol, period)

    if price.empty:
        continue

    daily_returns = price.pct_change().dropna()
    cum_return = (1 + daily_returns).cumprod()

    if cum_return.empty:
        continue

    years = int(period.replace("y", ""))
    final_return = cum_return.iloc[-1]
    cagr = (final_return) ** (1 / years) - 1
    volatility = daily_returns.std() * np.sqrt(252)

    # Sécuriser le calcul du Sharpe Ratio
    try:
        sharpe = (cagr - risk_free_rate) / float(volatility)
    except Exception:
        sharpe = np.nan

    max_drawdown = ((cum_return / cum_return.cummax()) - 1).min()

    all_returns[name] = cum_return

    summary_metrics.append({
        "Indice": name,
        "Perf Cumulée": f"{(final_return - 1) * 100:.2f}%",
        "CAGR": f"{cagr * 100:.2f}%",
        "Volatilité": f"{volatility * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_drawdown * 100:.2f}%"
    })

# Affichage graphique
if not all_returns.empty:
    st.line_chart(all_returns)
else:
    st.warning("Aucune donnée disponible pour les indices sélectionnés.")

# Tableau des ratios
st.subheader("📋 Ratios Financiers par Indice")
df_metrics = pd.DataFrame(summary_metrics)
st.dataframe(df_metrics)
with st.expander("ℹ️ Description des métriques financières"):
    st.markdown("""
    **📈 Perf Cumulée** : Représente l’évolution totale du prix de l’indice sur la période sélectionnée, exprimée en pourcentage. Elle ne tient pas compte des intérêts composés.

    **📊 CAGR (Taux de croissance annuel composé)** : Le taux de croissance moyen annuel des rendements, ajusté pour l'effet de la capitalisation. Il reflète un rendement annualisé régulier, comme si la croissance s’était produite de manière linéaire chaque année.

    **📉 Volatilité** : Mesure de la variation des rendements journaliers annualisée. Plus elle est élevée, plus l’actif est considéré comme risqué.

    **💡 Sharpe Ratio** : Indicateur de performance ajustée au risque. Il mesure le rendement excédentaire par unité de risque (volatilité). Plus il est élevé, mieux l’actif a compensé le risque pris.  
    > *Formule : (CAGR – Taux sans risque) / Volatilité*

    **📉 Max Drawdown** : La perte maximale par rapport au pic historique du portefeuille ou de l'indice. Il représente le pire recul observé sur la période.
    """)

# Téléchargement CSV
st.subheader("📥 Export des Données")

csv_metrics = df_metrics.to_csv(index=False).encode()
csv_returns = all_returns.to_csv().encode()

col1, col2 = st.columns(2)
with col1:
    st.download_button("📊 Télécharger les Ratios (CSV)", csv_metrics, "ratios_indices.csv", "text/csv")
with col2:
    st.download_button("📈 Télécharger les Performances (CSV)", csv_returns, "performances_indices.csv", "text/csv")

st.caption("📡 Données issues de Yahoo Finance – mises à jour automatiquement.")
