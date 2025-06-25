# forward_test.py
import pandas as pd
import yfinance as yf
from tecnica_manual import gerar_sinais_tecnicos
from ml_models import testar_modelos_ml
from metrics import avaliar_estrategia
from indicadores import calcular_todos_indicadores
import datetime
import os

# Configurações
ticker = "PETR4.SA"
capital = 10000
inicio_treino = "2020-01-01"
fim_treino = "2022-12-31"
inicio_forward = "2023-01-01"
fim_forward = "2025-06-24"

# Parâmetros fixos (simulação como se escolhidos no treino)
rsi = 30
macd_fast, macd_slow, macd_signal = 12, 26, 9
k_period, d_period = 14, 3
k_buy, k_sell = 30, 70
d_buy, d_sell = 30, 70

# Baixar dados
df = yf.download(ticker, start=inicio_treino, end=fim_forward, auto_adjust=False)
df.columns = [col[0] for col in df.columns]
df = calcular_todos_indicadores(df)
df.dropna(inplace=True)

# Separar treino e forward
df_treino = df[(df.index >= inicio_treino) & (df.index <= fim_treino)].copy()
df_forward = df[(df.index >= inicio_forward) & (df.index <= fim_forward)].copy()

# Simular estratégia técnica no forward
t_sinais = gerar_sinais_tecnicos(df_forward.copy(), rsi, macd_fast, macd_slow, macd_signal,
                                  k_period, d_period, k_buy, k_sell, d_buy, d_sell)
t_result = avaliar_estrategia(df_forward.copy(), t_sinais, capital)

# Simular IA no forward
ml_sinais, ml_result = testar_modelos_ml(df_forward.copy(), capital)

# Comparar resultados
resultado = {
    "Ativo": ticker,
    "Treino até": fim_treino,
    "Forward": f"{inicio_forward} a {fim_forward}",
    "Técnica Retorno": round(t_result["retorno_pct"], 2),
    "Técnica Sharpe": round(t_result["sharpe"], 2),
    "ML Retorno": round(ml_result["retorno_pct"], 2),
    "ML Sharpe": round(ml_result["sharpe"], 2),
    "Modelo ML": ml_result.get("modelo", "-")
}

# Salvar
df_res = pd.DataFrame([resultado])
os.makedirs("logs", exist_ok=True)
df_res.to_csv("logs/forward_test.csv", index=False)
print(df_res)
