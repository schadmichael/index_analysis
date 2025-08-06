import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from etfs_list import *
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.optimize as sco

# Configuration de la page
st.set_page_config(page_title="Indices & Ratios Financiers", layout="wide")
st.title("📈 Analyse & Comparaison des Indices Boursiers Mondiaux")

# Liste des indices enrichis
indices = etfs_enrich_list()

# Sélection des paramètres utilisateur
st.sidebar.header("⚙️ Paramètres")
selected = st.sidebar.multiselect(
    "Choisissez les indices à comparer",
    list(indices.keys()),
    default=["S&P 500 (USA)", "NASDAQ 100 (USA)"]
)
period = st.sidebar.selectbox("Période d'analyse", options=["1y", "3y", "5y", "10y", "15y", "20y", "25y", "30y", "35y", "40y"], index=2)
risk_free_rate = st.sidebar.slider("Taux sans risque (%) pour le Sharpe Ratio", 0.0, 5.0, 2.0) / 100

# Fonction pour récupérer les données
@st.cache_data
def get_data(ticker, period):
    df = yf.download(ticker, period=period)['Close']
    return df.dropna().squeeze()

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

    try:
        sharpe = (cagr - risk_free_rate) / float(volatility)
    except Exception:
        sharpe = np.nan

    # Max Drawdown
    drawdown_series = cum_return / cum_return.cummax() - 1
    max_drawdown = drawdown_series.min()

    # Recovery Time
    drawdown_end = drawdown_series[drawdown_series == 0].index
    max_dd_start = drawdown_series.idxmin()
    recovery_date = drawdown_end[drawdown_end > max_dd_start]
    if not recovery_date.empty:
        recovery_time = (recovery_date[0] - max_dd_start).days
    else:
        recovery_time = np.nan

    all_returns[name] = cum_return

    summary_metrics.append({
        "Indice": name,
        "Perf Cumulée": f"{(final_return - 1) * 100:.2f}%",
        "Rendement Annuel Moyen (CAGR)": f"{cagr * 100:.2f}%",
        "Volatilité": f"{volatility * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_drawdown * 100:.2f}%",
        "Recovery Time (jours)": f"{int(recovery_time) if not np.isnan(recovery_time) else 'N/A'}"
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

    **📊 Rendement Annuel Moyen (CAGR)** : Le taux de croissance moyen annuel des rendements, ajusté pour l'effet de la capitalisation. Il reflète un rendement annualisé régulier, comme si la croissance s’était produite de manière linéaire chaque année.

    **📉 Volatilité** : Mesure de la variation des rendements journaliers annualisée. Plus elle est élevée, plus l’actif est considéré comme risqué.

    **💡 Sharpe Ratio** : Indicateur de performance ajustée au risque. Il mesure le rendement excédentaire par unité de risque (volatilité).
    > *Formule : (CAGR – Taux sans risque) / Volatilité*

    **📉 Max Drawdown** : La perte maximale par rapport au pic historique de l’indice. Il représente le pire recul observé sur la période.

    **⏳ Recovery Time** : Nombre de jours nécessaires pour qu’un indice revienne à son plus haut après une perte maximale (Max Drawdown). Si la récupération n'a pas eu lieu, la valeur est "N/A".
    """)

# ----------------------------
# 🔗 MATRICE DE CORRÉLATION
# ----------------------------
st.subheader("🔗 Matrice de Corrélation des Rendements")

if not all_returns.empty and len(all_returns.columns) > 1:
    returns_daily = all_returns.pct_change().dropna()
    correlation_matrix = returns_daily.corr()

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
    plt.title("Corrélation entre les indices", fontsize=14)
    st.pyplot(fig)
else:
    st.info("Il faut sélectionner au moins deux indices avec des données valides pour afficher la matrice de corrélation.")

# ================================
# 🔧 Optimisation de portefeuille
# ================================
st.subheader("📊 Allocation Optimale de Portefeuille")

daily_return_matrix = pd.DataFrame()

for name in selected:
    symbol = indices[name]
    price = get_data(symbol, period)

    if price.empty:
        continue

    daily_returns = price.pct_change().dropna()
    daily_return_matrix[name] = daily_returns

if daily_return_matrix.empty or len(daily_return_matrix.columns) < 2:
    st.warning("Pas assez de données pour effectuer une allocation de portefeuille.")
else:
    mean_returns = daily_return_matrix.mean() * 252
    cov_matrix = daily_return_matrix.cov() * 252
    num_assets = len(mean_returns)
    assets = mean_returns.index.tolist()

    def portfolio_return(weights):
        return np.dot(weights, mean_returns)

    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def neg_sharpe_ratio(weights):
        port_return = portfolio_return(weights)
        port_vol = portfolio_volatility(weights)
        return -(port_return - risk_free_rate) / port_vol

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = num_assets * [1. / num_assets]

    def neg_return(weights):
        return -portfolio_return(weights)

    opt_ret = sco.minimize(neg_return, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    weights_ret = opt_ret.x

    opt_sharpe = sco.minimize(neg_sharpe_ratio, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    weights_sharpe = opt_sharpe.x

    alloc_df = pd.DataFrame({
        "Indice": assets,
        "Poids (max rendement)": [f"{w*100:.2f}%" for w in weights_ret],
        "Poids (max Sharpe)": [f"{w*100:.2f}%" for w in weights_sharpe]
    })

    st.dataframe(alloc_df)

    ret_return = portfolio_return(weights_ret)
    vol_return = portfolio_volatility(weights_ret)

    ret_sharpe = portfolio_return(weights_sharpe)
    vol_sharpe = portfolio_volatility(weights_sharpe)
    sharpe_max = (ret_sharpe - risk_free_rate) / vol_sharpe

    with st.expander("ℹ️ Détails des portefeuilles optimisés"):
        st.markdown(f"""
        **📈 Portefeuille Max Rendement**
        - Rendement attendu : `{ret_return*100:.2f}%`
        - Volatilité attendue : `{vol_return*100:.2f}%`

        **💡 Portefeuille Max Sharpe**
        - Rendement attendu : `{ret_sharpe*100:.2f}%`
        - Volatilité attendue : `{vol_sharpe*100:.2f}%`
        - Sharpe Ratio attendu : `{sharpe_max:.2f}`
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
