# comparador_janelas.py
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tecnica_manual import gerar_sinais_tecnicos
from ml_models import testar_modelos_ml
from metrics import avaliar_estrategia
from indicadores import calcular_todos_indicadores
import os

# Configurações
ticker = "PETR4.SA"
capital = 10000
inicio = "2020-01-01"
fim = "2025-06-24"
periodo_janela = 180  # dias (~6 meses)

# Parâmetros técnicos fixos para exemplo
rsi = 30
macd_fast, macd_slow, macd_signal = 12, 26, 9
k_period, d_period = 14, 3
k_buy, k_sell = 30, 70
d_buy, d_sell = 30, 70

# Baixar dados e aplicar indicadores
df = yf.download(ticker, start=inicio, end=fim, auto_adjust=False)
df.columns = [col[0] for col in df.columns]
df = calcular_todos_indicadores(df)
df.dropna(inplace=True)

inicio_data = df.index.min()
fim_data = df.index.max()
janelas = []

while inicio_data + timedelta(days=periodo_janela) < fim_data:
    janela_fim = inicio_data + timedelta(days=periodo_janela)
    janela_df = df[(df.index >= inicio_data) & (df.index <= janela_fim)].copy()

    sinais_tecnica = gerar_sinais_tecnicos(janela_df, rsi, macd_fast, macd_slow, macd_signal,
                                           k_period, d_period, k_buy, k_sell, d_buy, d_sell)
    resultado_tec = avaliar_estrategia(janela_df.copy(), sinais_tecnica, capital)

    sinais_ml, resultado_ml = testar_modelos_ml(janela_df.copy(), capital)

    janelas.append({
        "Início": inicio_data.date(),
        "Fim": janela_fim.date(),
        "Ret_Técnica": round(resultado_tec["retorno_pct"], 2),
        "Sharpe_Técnica": round(resultado_tec["sharpe"], 2),
        "Ret_ML": round(resultado_ml["retorno_pct"], 2),
        "Sharpe_ML": round(resultado_ml["sharpe"], 2),
        "Modelo_ML": resultado_ml.get("modelo", "-")
    })

    inicio_data += timedelta(days=periodo_janela)

# Salvar resultado
df_janelas = pd.DataFrame(janelas)
os.makedirs("logs", exist_ok=True)
df_janelas.to_csv(f"logs/comparador_janelas_{ticker.replace('.SA','')}.csv", index=False)
print(df_janelas)
