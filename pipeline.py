# pipeline.py
import pandas as pd
import yfinance as yf
from itertools import product
from indicadores import calcular_todos_indicadores
from tecnica_manual import gerar_sinais_tecnicos
from ml_models import testar_modelos_ml
from metrics import avaliar_estrategia
from signal_generator import salvar_sinais_json
import os
from fundamentalist import fundamentalist_filters, webscraping

# Configuração geral
#tickers = ["CPLE6.SA", "VALE3.SA", "BBAS3.SA"]

df = fundamentalist_filters(webscraping(True), 's')
tickers = df['Ativo'].tolist()

capital_total = 1000
capital_por_ativo = capital_total / len(tickers)
data_inicio = "2020-01-01"
data_fim = "2025-06-21"

# Parâmetros dinâmicos para testes
parametros_rsi = [20, 25, 30, 35, 40, 45]
parametros_macd = [(12, 26, 9), (10, 20, 5), (8, 17, 7)]
parametros_stoch = [(14, 3), (10, 3), (20, 4)]

melhores_sinais = []

for tickerst in tickers:
    ticker = tickerst + '.SA'
    print(f"Analisando ativo: {ticker}")
    try:
        df = yf.download(ticker, start=data_inicio, end=data_fim)
        df.columns = [col[0] for col in df.columns]
        df = calcular_todos_indicadores(df)

        melhores_estrategias = []

        for rsi in parametros_rsi:
            for macd_fast, macd_slow, macd_signal in parametros_macd:
                for k, d in parametros_stoch:
                    sinais = gerar_sinais_tecnicos(df.copy(), rsi, macd_fast, macd_slow, macd_signal, k, d)
                    resultado = avaliar_estrategia(df.copy(), sinais, capital_por_ativo)

                    melhores_estrategias.append({
                        'ticker': ticker,
                        'tipo': 'tecnica',
                        'params': {'rsi': rsi, 'macd': (macd_fast, macd_slow, macd_signal), 'stoch': (k, d)},
                        'resultado': resultado,
                        'sinais': sinais
                    })

        # Machine Learning (pode usar os mesmos indicadores como features)
        sinais_ml, resultado_ml = testar_modelos_ml(df.copy(), capital_por_ativo)
        melhores_estrategias.append({
            'ticker': ticker,
            'tipo': 'ml',
            'params': 'modelo_ml_padrao',
            'resultado': resultado_ml,
            'sinais': sinais_ml
        })

        # Seleciona a melhor estratégia com base no Sharpe Ratio
        melhores_estrategias.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
        melhor = melhores_estrategias[0]
        melhores_sinais.append(melhor)
        # Alocação proporcional ao Sharpe
        total_sharpe = sum(max(s['resultado']['sharpe'], 0.01) for s in melhores_sinais)  # evita zero

        for s in melhores_sinais:
            proporcao = max(s['resultado']['sharpe'], 0.01) / total_sharpe
            s['alocacao'] = round(proporcao * capital_total, 2)  # valor em reais para investir
    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")
        continue


# Salvar arquivo para envio no Telegram
salvar_sinais_json(melhores_sinais, 'sinais_telegram.json')
print("Arquivo de sinais gerado com sucesso!")
