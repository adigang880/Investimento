# relatorio_visual.py
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os
from datetime import datetime

# PARA RODAR FAÇA O COMAND OABAIXO
# python relatorio_visual.py

# Criar pasta de saída
os.makedirs("relatorios", exist_ok=True)

# Carregar sinais
df = pd.read_json("sinais_telegram.json")
df["data"] = pd.to_datetime(df["data"])
ativos = df["ativo"].unique()

# Gerar imagem por ativo
for ativo in ativos:
    dados = df[df["ativo"] == ativo].sort_values("data")
    if dados.empty:
        continue

    start = dados["data"].min()
    end = dados["data"].max()
    hist = yf.download(ativo, start=start, end=end)
    if hist.empty:
        continue

    plt.figure(figsize=(10, 6))
    plt.plot(hist["Close"], label="Preço Fechamento", alpha=0.6)

    # Marcar sinais
    for _, row in dados.iterrows():
        cor = "green" if row["tipo"] == "compra" else "red"
        plt.scatter(row["data"], row["preco"], color=cor, label=row["tipo"].capitalize())

    plt.title(f"{ativo} - {row['modelo'].upper()} | Sharpe: {row['sharpe']:.2f} | Retorno: {row['retorno']:.2f}% | Alocação: R$ {row['alocacao']:.2f}")
    plt.xlabel("Data")
    plt.ylabel("Preço (R$")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    nome_arquivo = f"relatorios/{ativo.replace('.SA','')}_{datetime.now().strftime('%Y%m%d')}.png"
    plt.savefig(nome_arquivo)
    plt.close()

print("Relatórios visuais gerados na pasta 'relatorios'.")