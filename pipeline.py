# pipeline.py

# Esse script roda o pipeline completo: busca dados, testa estratégias, seleciona a melhor, aloca capital e envia
# sinais para o Telegram.
from MBA.fundamentalist import webscraping, fundamentalist_filters
import pandas as pd
import yfinance as yf
from indicadores import calcular_todos_indicadores
from tecnica_manual import gerar_sinais_tecnicos
from ml_models import testar_modelos_ml  # Importa função que testa modelos de machine learning
from metrics import avaliar_estrategia  # Importa função para calcular sharpe, retorno, etc.
from signal_generator import salvar_sinais_json  # Salva os sinais em formato JSON
from telegram_bot import enviar_sinais_para_telegram  # Envia sinais formatados ao Telegram
import os
import datetime
from concurrent.futures import ThreadPoolExecutor  # Permite paralelizar múltiplos ativos (opcional)

# ============================ CONFIGURAÇÃO ============================
# Configuração geral
# df = fundamentalist_filters(webscraping(True), 's') # (alternativo via filtros fundamentalistas)
# tickers = df['Ativo'].tolist()
# tickers = [f"{ticker}.SA" for ticker in tickers]
tickers = ["PETR4.SA", "VALE3.SA", "BBAS3.SA"] # Lista de ativos a analisar.
capital_total = 10000  # Capital inicial total para simulação
data_inicio = "2020-01-01"
data_fim = "2025-06-24"

# Criação de pastas para armazenar arquivos temporários e logs
os.makedirs("cache", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Parâmetros técnicos a serem testados dinamicamente (grid search)
parametros_rsi = [20, 25, 30, 35, 40, 45]
parametros_macd = [(12, 26, 9), (10, 20, 5), (8, 17, 7)]
parametros_stoch = [(14, 3), (10, 3), (20, 4)]
parametros_kd = [(30, 70), (25, 75), (20, 80)]

melhores_sinais = []  # Lista onde será armazenada a melhor estratégia por ativo


# ============================ FUNÇÃO PRINCIPAL ============================


def processar_ativo(ticker):
    """
    Executa o pipeline para um único ativo:
    - Baixa ou carrega dados
    - Calcula indicadores
    - Testa todas as combinações técnicas
    - Testa modelo de IA
    - Compara e escolhe a melhor estratégia
    """

    print(f"Analisando ativo: {ticker}")

    # Verifica se já existe cache salvo, senão faz download
    cache_path = f"cache/{ticker}.parquet"
    if os.path.exists(cache_path):
        df = pd.read_parquet(cache_path)
    else:
        df = yf.download(ticker, start=data_inicio, end=data_fim, auto_adjust=False)
        df.columns = [col[0] for col in df.columns]
        df.to_parquet(cache_path)

    # Aplica todos os indicadores técnicos
    df = calcular_todos_indicadores(df)
    melhores_estrategias = []  # Armazena todas as estratégias testadas (técnicas e ML)

    # Testa todas as combinações de parâmetros manuais
    for rsi in parametros_rsi:
        for macd_fast, macd_slow, macd_signal in parametros_macd:
            for k, d in parametros_stoch:
                for k_buy, k_sell in parametros_kd:
                    # Gera sinais com parâmetros específicos
                    sinais = gerar_sinais_tecnicos(df.copy(), rsi, macd_fast, macd_slow, macd_signal, k, d,
                                                   k_buy=k_buy, k_sell=k_sell, d_buy=k_buy, d_sell=k_sell)

                    # Avalia os sinais com base no capital proporcional
                    resultado = avaliar_estrategia(df.copy(), sinais, capital_total / len(tickers))

                    # Armazena a estratégia
                    melhores_estrategias.append({
                        'ticker': ticker,
                        'tipo': 'tecnica',
                        'params': {
                            'rsi': rsi,
                            'macd': (macd_fast, macd_slow, macd_signal),
                            'stoch': (k, d),
                            'kd_thresholds': (k_buy, k_sell)
                        },
                        'resultado': resultado,
                        'sinais': sinais,
                        'modelo': 'estrategia_tecnica'
                    })

    # Também testa a abordagem por machine learning
    sinais_ml, resultado_ml = testar_modelos_ml(df.copy(), capital_total / len(tickers))
    melhores_estrategias.append({
        'ticker': ticker,
        'tipo': 'ml',
        'params': 'modelo_ml_auto',
        'resultado': resultado_ml,
        'sinais': sinais_ml,
        'modelo': resultado_ml.get('modelo', 'desconhecido')
    })

    # Ordena pela métrica de Sharpe e seleciona a melhor
    melhores_estrategias.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
    melhor = melhores_estrategias[0]

    # Gera um log da melhor estratégia para esse ativo
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


# ============================ EXECUÇÃO DO PIPELINE ============================

# Versão paralela (opcional): processa múltiplos ativos simultaneamente
with ThreadPoolExecutor(max_workers=4) as executor:
    resultados = list(executor.map(processar_ativo, tickers))

# Versão sequencial
#resultados = processar_ativo(tickers)

# Aplica truncagem no Sharpe (para evitar pesos extremos na alocação)
for s in resultados:
    s['sharpe_truncado'] = min(max(s['resultado']['sharpe'], 0.01), 3)

# Calcula a proporção de alocação por ativo com base no Sharpe
total_sharpe = sum(s['sharpe_truncado'] for s in resultados)
for s in resultados:
    proporcao = s['sharpe_truncado'] / total_sharpe
    s['alocacao'] = round(proporcao * capital_total, 2)

# Define os sinais finais para uso posterior
melhores_sinais = resultados

# Gera um resumo consolidado
with open("logs/summary.log", "w") as resumo:
    resumo.write(f"Resumo gerado em {datetime.datetime.now()}\n")
    for s in melhores_sinais:
        resumo.write(
            f"{s['ticker']} - Modelo: {s.get('modelo', 'n/a')} - "
            f"Sharpe: {s['resultado']['sharpe']:.2f}, "
            f"Retorno: {s['resultado']['retorno_pct']:.2f}%, "
            f"Alocação: R$ {s['alocacao']:.2f}\n"
        )

# Exporta os sinais finais em formato JSON
salvar_sinais_json(melhores_sinais, 'sinais_telegram.json')

# Envia os sinais para o Telegram
enviar_sinais_para_telegram('sinais_telegram.json')
print("Arquivo de sinais gerado e enviado para o Telegram!")
