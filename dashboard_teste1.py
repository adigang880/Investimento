# dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import datetime
import yfinance as yf
import numpy as np
import os

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
    ibov.columns = [col[0] for col in ibov.columns]
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
colunas_formatadas = {
    "preco": "{:.2f}",
    "sharpe": "{:.2f}",
    "retorno": "{:.2f}",
    "alocacao": "{:.2f}"
}

colunas_visiveis = ["ativo", "data", "tipo", "preco", "modelo", "params", "sharpe", "retorno", "alocacao"]
if set(colunas_visiveis).issubset(sinais.columns):
    detalhes = sinais[colunas_visiveis].sort_values("data", ascending=False)
    st.dataframe(detalhes.reset_index(drop=True).style.format(colunas_formatadas))
else:
    st.warning("Algumas colunas esperadas não estão presentes no arquivo de sinais.")

# Relatório de parâmetros
st.subheader("📊 Relatório de Parâmetros e Sugestões")
relatorio_path = max([f for f in os.listdir('.') if f.startswith("relatorio_parametros_") and f.endswith(".csv")], default=None)
if relatorio_path:
    df_parametros = pd.read_csv(relatorio_path)
    st.dataframe(df_parametros)
else:
    st.info("Gere o relatório de parâmetros executando o script 'relatorio_parametros.py'")

# Backtest por janelas
st.subheader("📅 Desempenho por Janelas Temporais")
backtests = [f for f in os.listdir("logs") if f.startswith("backtest_janelas_") and f.endswith(".csv")]
if backtests:
    for file in backtests:
        st.markdown(f"**{file.replace('backtest_janelas_', '').replace('.csv', '')}**")
        df_bt = pd.read_csv(os.path.join("logs", file))
        st.dataframe(df_bt)
else:
    st.info("Nenhum backtest por janelas encontrado. Execute 'backtest_janelas.py'.")

# Comparador técnica vs ML
st.subheader("🔄 Comparação Estratégia Técnica vs IA por Janela")
comp_path = max([f for f in os.listdir("logs") if f.startswith("comparador_janelas_") and f.endswith(".csv")], default=None)
if comp_path:
    df_comp = pd.read_csv(os.path.join("logs", comp_path))
    st.dataframe(df_comp)

    # Gráfico de retorno
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_comp["Início"], y=df_comp["Ret_Técnica"], name="Técnica"))
    fig.add_trace(go.Scatter(x=df_comp["Início"], y=df_comp["Ret_ML"], name="ML"))
    fig.update_layout(title="Retorno por Janela: Técnica vs ML", xaxis_title="Início da Janela", yaxis_title="Retorno (%)")
    st.plotly_chart(fig, use_container_width=True)

    # Estatísticas resumidas
    st.markdown("### 🔢 Resumo da Competição por Janela")
    tecnica_vitorias = (df_comp["Ret_Técnica"] > df_comp["Ret_ML"]).sum()
    ml_vitorias = (df_comp["Ret_ML"] > df_comp["Ret_Técnica"]).sum()
    st.write(f"🔧 Técnica venceu em: {tecnica_vitorias} janelas")
    st.write(f"🤖 ML venceu em: {ml_vitorias} janelas")

    media_tec = df_comp["Ret_Técnica"].mean()
    media_ml = df_comp["Ret_ML"].mean()
    st.write(f"Média de retorno Técnica: {media_tec:.2f}%")
    st.write(f"Média de retorno ML: {media_ml:.2f}%")

    # Recomendação final
    melhor = "ML" if media_ml > media_tec else "Técnica"
    st.markdown(f"### 🔹 Estratégia Recomendável: **{melhor}** com base no desempenho médio das janelas")
else:
    st.info("Nenhum comparador de janelas encontrado. Execute 'comparador_janelas.py'.")

# Comparador Multiativo
st.subheader("📊 Comparador Multiativo Técnica vs ML")
multi_path = "logs/comparador_multiativo.csv"
if os.path.exists(multi_path):
    df_multi = pd.read_csv(multi_path)
    st.dataframe(df_multi)

    # Ranking por ativo: qual estratégia venceu mais vezes?
    df_multi["Vencedor"] = df_multi.apply(
        lambda x: "Técnica" if x["Ret_Técnica"] > x["Ret_ML"] else "ML", axis=1
    )
    ranking = df_multi.groupby(["Ativo", "Vencedor"]).size().unstack(fill_value=0)
    ranking["Total"] = ranking.sum(axis=1)
    ranking["% ML"] = (ranking.get("ML", 0) / ranking["Total"] * 100).round(1)
    ranking["% Técnica"] = (ranking.get("Técnica", 0) / ranking["Total"] * 100).round(1)

    st.markdown("### 🏅 Ranking de Estratégias por Ativo")
    st.dataframe(ranking)

    st.markdown("### 📈 Gráfico de Vitória por Estratégia")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=ranking.index, y=ranking["% Técnica"], name="Técnica"))
    fig_bar.add_trace(go.Bar(x=ranking.index, y=ranking["% ML"], name="ML"))
    fig_bar.update_layout(barmode="group", title="Vitórias por Estratégia (%)", xaxis_title="Ativo", yaxis_title="% Vitórias")
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Execute 'comparador_multiativo.py' para visualizar comparações por ativo.")

# Forward Test
st.subheader("🚀 Simulação Forward Test (Futuro Real)")
if os.path.exists("logs/forward_test.csv"):
    df_fwd = pd.read_csv("logs/forward_test.csv")
    st.dataframe(df_fwd)

    fig_fw = go.Figure()
    fig_fw.add_trace(go.Bar(x=["Técnica"], y=df_fwd["Técnica Retorno"], name="Técnica"))
    fig_fw.add_trace(go.Bar(x=["ML"], y=df_fwd["ML Retorno"], name="ML"))
    fig_fw.update_layout(title="Retorno no Forward Test", yaxis_title="Retorno (%)")
    st.plotly_chart(fig_fw, use_container_width=True)
else:
    st.info("Execute 'forward_test.py' para gerar a simulação do período futuro.")

# Alertas Automáticos
st.subheader("🚨 Gatilhos Automáticos por Métricas")
alerta_path = "logs/alertas_automaticos.csv"
if os.path.exists(alerta_path):
    df_alertas = pd.read_csv(alerta_path)
    st.dataframe(df_alertas)
else:
    st.info("Nenhum alerta disponível. Execute 'gatilhos_automaticos.py' para gerar.")
