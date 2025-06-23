# pipeline.py
from fundamentalist import webscraping, fundamentalist_filters
import pandas as pd
import yfinance as yf
from itertools import product
from indicadores import calcular_todos_indicadores
from tecnica_manual import gerar_sinais_tecnicos
from ml_models import testar_modelos_ml
from metrics import avaliar_estrategia
from signal_generator import salvar_sinais_json
from telegram_bot import enviar_sinais_para_telegram
import os
import datetime
from concurrent.futures import ThreadPoolExecutor

# Configuração geral
#df = fundamentalist_filters(webscraping(True), 's')
#tickers = df['Ativo'].tolist()
#tickers = [f"{ticker}.SA" for ticker in tickers]
tickers = ["PETR4.SA", "VALE3.SA", "BBAS3.SA"]
capital_total = 10000
data_inicio = "2020-01-01"
data_fim = "2025-06-23"

# Criar pasta de cache e logs se não existir
os.makedirs("cache", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Parâmetros dinâmicos para testes
parametros_rsi = [20, 25, 30, 35, 40, 45]
parametros_macd = [(12, 26, 9), (10, 20, 5), (8, 17, 7)]
parametros_stoch = [(14, 3), (10, 3), (20, 4)]
melhores_sinais = []


def processar_ativo(ticker):
    print(f"Analisando ativo: {ticker}")
    cache_path = f"cache/{ticker}.parquet"
    if os.path.exists(cache_path):
        df = pd.read_parquet(cache_path)
    else:
        df = yf.download(ticker, start=data_inicio, end=data_fim)
        df.columns = [col[0] for col in df.columns]
        #df.columns = [col[0] for col in df.columns] if isinstance(df.columns[0], tuple) else df.columns
        df.to_parquet(cache_path)

    df = calcular_todos_indicadores(df)
    melhores_estrategias = []

    for rsi in parametros_rsi:
        for macd_fast, macd_slow, macd_signal in parametros_macd:
            for k, d in parametros_stoch:
                sinais = gerar_sinais_tecnicos(df.copy(), rsi, macd_fast, macd_slow, macd_signal, k, d)
                resultado = avaliar_estrategia(df.copy(), sinais, capital_total / len(tickers))

                melhores_estrategias.append({
                    'ticker': ticker,
                    'tipo': 'tecnica',
                    'params': {'rsi': rsi, 'macd': (macd_fast, macd_slow, macd_signal), 'stoch': (k, d)},
                    'resultado': resultado,
                    'sinais': sinais,
                    'modelo': 'estrategia_tecnica'
                })

    sinais_ml, resultado_ml = testar_modelos_ml(df.copy(), capital_total / len(tickers))
    melhores_estrategias.append({
        'ticker': ticker,
        'tipo': 'ml',
        'params': 'modelo_ml_auto',
        'resultado': resultado_ml,
        'sinais': sinais_ml,
        'modelo': resultado_ml.get('modelo', 'desconhecido')
    })

    melhores_estrategias.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
    melhor = melhores_estrategias[0]

    # Log individual
    with open(f"logs/{ticker}.log", "w") as log:
        log.write(f"Ticker: {ticker}\n")
        log.write(f"Tipo: {melhor['tipo']}\n")
        log.write(f"Modelo: {melhor.get('modelo', 'n/a')}\n")
        log.write(f"Params: {melhor['params']}\n")
        log.write(f"Sharpe: {melhor['resultado']['sharpe']:.2f}\n")
        log.write(f"Retorno: {melhor['resultado']['retorno_pct']:.2f}%\n")
        log.write(f"Sinais: {len(melhor['sinais'])}\n")
        if melhor['sinais']:
            log.write(f"Último sinal: {melhor['sinais'][-1]['data']}\n")
        log.write(f"Atualizado em: {datetime.datetime.now()}\n")

    return melhor

# Processar com paralelismo
with ThreadPoolExecutor(max_workers=4) as executor:
    resultados = list(executor.map(processar_ativo, tickers))

# Alocação proporcional ao Sharpe Ratio (limitado entre 0.01 e 3 para evitar distorção)
for s in resultados:
    s['sharpe_truncado'] = min(max(s['resultado']['sharpe'], 0.01), 3)

total_sharpe = sum(s['sharpe_truncado'] for s in resultados)

for s in resultados:
    proporcao = s['sharpe_truncado'] / total_sharpe
    s['alocacao'] = round(proporcao * capital_total, 2)

melhores_sinais = resultados

# Log resumo geral
with open("logs/summary.log", "w") as resumo:
    resumo.write(f"Resumo gerado em {datetime.datetime.now()}\n")
    for s in melhores_sinais:
        resumo.write(f"{s['ticker']} - Modelo: {s.get('modelo', 'n/a')} - Sharpe: {s['resultado']['sharpe']:.2f}, Retorno: {s['resultado']['retorno_pct']:.2f}%, Alocação: R$ {s['alocacao']:.2f}\n")

# Salvar arquivo para envio no Telegram e Dashboard
salvar_sinais_json(melhores_sinais, 'sinais_telegram.json')
enviar_sinais_para_telegram('sinais_telegram.json')
print("Arquivo de sinais gerado e enviado para o Telegram!")
