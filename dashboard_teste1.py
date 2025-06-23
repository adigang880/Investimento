# dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import datetime
import yfinance as yf
import numpy as np

# PARA EXECUTAR
# streamlit run dashboard_teste1.py

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Estratégias e Sinais")

@st.cache_data
def carregar_sinais():
    try:
        df = pd.read_json("sinais_telegram.json")
        df["data"] = pd.to_datetime(df["data"])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

sinais = carregar_sinais()
if sinais.empty:
    st.warning("Nenhum dado de sinal disponível.")
    st.stop()

ativos = sinais["ativo"].unique().tolist()
ativo_sel = st.sidebar.selectbox("Ativo", ["Todos"] + ativos)

if ativo_sel != "Todos":
    sinais = sinais[sinais["ativo"] == ativo_sel]

# Métricas gerais
total_alocado = sinais["alocacao"].sum()
lucro_estimado = (sinais["retorno"] / 100 * sinais["alocacao"]).sum()
sharpe_medio = sinais["sharpe"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Alocado", f"R$ {total_alocado:,.2f}")
col2.metric("📈 Lucro Estimado", f"R$ {lucro_estimado:,.2f}")
col3.metric("🤝 Sharpe Médio", f"{sharpe_medio:.2f}")

# Ranking de ativos
st.subheader("🏆 Ranking dos Ativos (Sharpe Ratio)")
ranking = sinais.groupby("ativo").agg({
    "sharpe": "mean",
    "retorno": "mean",
    "alocacao": "sum"
}).sort_values("sharpe", ascending=False)
st.dataframe(ranking.style.format("{:.2f}"))

# Gráfico comparativo com IBOV
st.subheader("🌎 Comparação com IBOV")
@st.cache_data
def carregar_ibov():
    ibov = yf.download("^BVSP", start=sinais["data"].min(), end=datetime.datetime.now())
    ibov = ibov["Close"].pct_change().fillna(0)
    ibov = (1 + ibov).cumprod()
    return ibov

ibov = carregar_ibov()

carteira = sinais.sort_values("data")
carteira["ret"] = sinais["retorno"] / 100
carteira["cum"] = (1 + carteira["ret"]).cumprod()

fig = go.Figure()
fig.add_trace(go.Scatter(x=carteira["data"], y=carteira["cum"], mode="lines", name="Carteira"))
fig.add_trace(go.Scatter(x=ibov.index, y=ibov.values, mode="lines", name="IBOV"))
fig.update_layout(title="Desempenho da Carteira vs IBOV", xaxis_title="Data", yaxis_title="Índice Acumulado")
st.plotly_chart(fig, use_container_width=True)

# Drawdown
st.subheader("📉 Análise de Drawdown")
def calcular_drawdown(serie):
    acumulado = serie.cummax()
    drawdown = (serie - acumulado) / acumulado
    return drawdown

carteira["dd"] = calcular_drawdown(carteira["cum"])
fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(x=carteira["data"], y=carteira["dd"], fill='tozeroy', name="Drawdown"))
fig_dd.update_layout(title="Drawdown da Carteira", xaxis_title="Data", yaxis_title="Drawdown")
st.plotly_chart(fig_dd, use_container_width=True)

# Detalhes por ativo
st.subheader("🔗 Detalhes Técnicos e Estratégicos")
cols = ["ativo", "data", "tipo", "preco", "modelo", "params", "sharpe", "retorno", "alocacao"]
detalhes = sinais[cols].sort_values("data", ascending=False)
colunas_formatadas = {
    "preco": "{:.2f}",
    "sharpe": "{:.2f}",
    "retorno": "{:.2f}",
    "alocacao": "{:.2f}"
}

st.dataframe(detalhes.reset_index(drop=True).style.format(colunas_formatadas))
