# relatorio_parametros.py
import pandas as pd
import json
import os
from datetime import datetime

# Carregar sinais
df = pd.read_json("sinais_telegram.json")
df["data"] = pd.to_datetime(df["data"])

# Agrupar por ativo
relatorio = []
agrupado = df.groupby("ativo")

for ativo, grupo in agrupado:
    modelo = grupo["modelo"].iloc[-1]
    sharpe = grupo["sharpe"].mean()
    retorno = grupo["retorno"].mean()
    alocacao = grupo["alocacao"].sum()
    params = grupo["params"].iloc[-1] if isinstance(grupo["params"].iloc[-1], dict) else {}

    sugestao = ""
    if sharpe < 1:
        sugestao = "🔧 Testar ajustes nos thresholds de RSI e %K para melhorar entrada"
    elif retorno < 5:
        sugestao = "📉 Baixo retorno. Tente aumentar os filtros de MACD ou mudar o modelo"
    else:
        sugestao = "✅ Parâmetros parecem bons. Continue monitorando."

    relatorio.append({
        "Ativo": ativo,
        "Modelo": modelo,
        "Sharpe": round(sharpe, 2),
        "Retorno (%)": round(retorno, 2),
        "Alocação (R$)": round(alocacao, 2),
        "RSI": params.get("rsi", "-"),
        "MACD": params.get("macd", "-"),
        "Stoch (K,D)": params.get("stoch", "-"),
        "K/D thresholds": params.get("kd_thresholds", "-"),
        "Sugestão": sugestao
    })

# Exportar para CSV e exibir
df_relatorio = pd.DataFrame(relatorio)
saida = f"relatorio_parametros_{datetime.now().strftime('%Y%m%d')}.csv"
df_relatorio.to_csv(saida, index=False)
print(f"Relatório salvo como {saida}")
print(df_relatorio)
