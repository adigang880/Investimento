# backtest_janelas.py
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tecnica_manual import gerar_sinais_tecnicos
from metrics import avaliar_estrategia
from indicadores import calcular_todos_indicadores
import os

# Configurações
TICKER = "PETR4.SA"
CAPITAL = 10000
INICIO = "2020-01-01"
FIM = "2024-06-01"
PERIODO_JANELA = 180  # dias (~6 meses)

# Parâmetros fixos para exemplo
RSI = 30
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
K_PERIOD, D_PERIOD = 14, 3
K_BUY, K_SELL = 30, 70
D_BUY, D_SELL = 30, 70

# Baixar dados e indicadores
df = yf.download(TICKER, start=INICIO, end=FIM)
df.columns = [col[0] for col in df.columns]
df = calcular_todos_indicadores(df)
df.dropna(inplace=True)

# Janelas
inicio_data = df.index.min()
fim_data = df.index.max()
janelas = []

while inicio_data + timedelta(days=PERIODO_JANELA) < fim_data:
    janela_fim = inicio_data + timedelta(days=PERIODO_JANELA)
    janela_df = df[(df.index >= inicio_data) & (df.index <= janela_fim)].copy()
    sinais = gerar_sinais_tecnicos(janela_df, RSI, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
                                   K_PERIOD, D_PERIOD, K_BUY, K_SELL, D_BUY, D_SELL)
    resultado = avaliar_estrategia(janela_df, sinais, CAPITAL)

    janelas.append({
        "Início": inicio_data.date(),
        "Fim": janela_fim.date(),
        "Retorno (%)": round(resultado["retorno_pct"], 2),
        "Sharpe": round(resultado["sharpe"], 2),
        "Nº Sinais": len(sinais)
    })

    inicio_data += timedelta(days=PERIODO_JANELA)

# Salvar resultado
df_janelas = pd.DataFrame(janelas)
os.makedirs("logs", exist_ok=True)
df_janelas.to_csv(f"logs/backtest_janelas_{TICKER.replace('.SA','')}.csv", index=False)
print(df_janelas)
