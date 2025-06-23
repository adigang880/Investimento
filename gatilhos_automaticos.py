# gatilhos_automaticos.py
import pandas as pd
import json
import datetime

# Configurações de alerta
LIMIAR_SHARPE = 0.5
LIMIAR_RETORNO = 0.0
LIMIAR_DRAWDOWN = -0.15

# Carrega sinais finais
df = pd.read_json("sinais_telegram.json")
df["data"] = pd.to_datetime(df["data"])

# Gatilhos
alertas = []
for i, row in df.iterrows():
    gatilhos = []
    if row["sharpe"] < LIMIAR_SHARPE:
        gatilhos.append("🔻 Sharpe muito baixo")
    if row["retorno"] < LIMIAR_RETORNO:
        gatilhos.append("📉 Retorno negativo")
    if "drawdown" in row and row["drawdown"] < LIMIAR_DRAWDOWN:
        gatilhos.append("⚠️ Drawdown elevado")

    if gatilhos:
        alertas.append({
            "Ativo": row["ativo"],
            "Data": row["data"].date(),
            "Modelo": row["modelo"],
            "Alocacao": row["alocacao"],
            "Sharpe": row["sharpe"],
            "Retorno": row["retorno"],
            "Alertas": gatilhos
        })

# Salvar alertas
if alertas:
    pd.DataFrame(alertas).to_csv("logs/alertas_automaticos.csv", index=False)
    print("Alertas gerados em logs/alertas_automaticos.csv")
else:
    print("Nenhum alerta gerado. Tudo sob controle!")
