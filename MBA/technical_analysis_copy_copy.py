'''
Ajustes e Melhorias
1- Validação Cruzada: Em vez de usar apenas uma divisão única, você pode implementar validação cruzada em várias divisões para maior robustez.
2- Ajuste da Proporção de Divisão: Dependendo da quantidade de dados, você pode ajustar split_ratio para garantir que o conjunto de teste seja representativo.
3- Métricas de Desempenho: Além do retorno, considere outras métricas, como a volatilidade e o drawdown, para uma análise mais completa.
4- Backtesting com Biblioteca: Considere usar uma biblioteca como backtrader para backtests mais completos, com relatórios e visualizações.
'''

import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from itertools import product


# Função para calcular o MACD
def calculate_macd(data, fast, slow, signal):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal


# Função para executar a estratégia
def strategy(data, macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell):
    data = data.copy()

    # Calcular o RSI usando a biblioteca `ta`
    data['RSI'] = RSIIndicator(close=data['Close'], window=rsi_period).rsi()

    # Calcular o MACD
    data['MACD'], data['MACD_signal'] = calculate_macd(data, macd_fast, macd_slow, macd_signal)

    # Sinais de compra e venda
    data['Buy_Signal'] = (data['RSI'] < rsi_buy) & (data['MACD'] > data['MACD_signal'])
    data['Sell_Signal'] = (data['RSI'] > rsi_sell) & (data['MACD'] < data['MACD_signal'])

    # Inicializar posições e calcular retorno
    position = 0  # 0: sem posição, 1: comprado
    returns = []

    for i in range(1, len(data)):
        if data['Buy_Signal'].iloc[i] and position == 0:
            buy_price = data['Close'].iloc[i]
            position = 1
        elif data['Sell_Signal'].iloc[i] and position == 1:
            sell_price = data['Close'].iloc[i]
            returns.append((sell_price - buy_price) / buy_price)
            position = 0

    # Calcular retorno acumulado
    if returns:
        cumulative_return = np.prod([1 + r for r in returns]) - 1
    else:
        cumulative_return = 0  # Nenhuma operação realizada

    return cumulative_return * 100  # Retorno em %


# Função de otimização para encontrar os melhores parâmetros
def optimize_strategy(data, macd_fast_values, macd_slow_values, macd_signal_values, rsi_period_values, rsi_buy_values,
                      rsi_sell_values):
    best_params = None
    best_return = -np.inf

    for params in product(macd_fast_values, macd_slow_values, macd_signal_values, rsi_period_values, rsi_buy_values,
                          rsi_sell_values):
        macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell = params

        # Evitar parâmetros de MACD inválidos
        if macd_fast >= macd_slow:
            continue

        cumulative_return = strategy(data, macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell)

        # Guardar o melhor retorno e parâmetros
        if cumulative_return > best_return:
            best_return = cumulative_return
            best_params = {
                'macd_fast': macd_fast,
                'macd_slow': macd_slow,
                'macd_signal': macd_signal,
                'rsi_period': rsi_period,
                'rsi_buy': rsi_buy,
                'rsi_sell': rsi_sell,
            }

    return best_params, best_return


# Função principal para carregar dados, otimizar e avaliar
def main(ticker):
    # Carregar dados do Yahoo Finance
    data = yf.download(ticker, start="2020-01-01", end="2023-01-01")

    # Dividir os dados em aprendizado e teste
    train_data = data.iloc[:int(0.7 * len(data))]
    test_data = data.iloc[int(0.7 * len(data)):]

    # Definir intervalos de parâmetros
    macd_fast_values = [12, 17]
    macd_slow_values = [26, 35]
    macd_signal_values = [9, 12]
    rsi_period_values = [10, 14, 21]
    rsi_buy_values = [25, 30, 35]
    rsi_sell_values = [65, 70, 75]

    # Otimizar a estratégia com os dados de aprendizado
    best_params, best_train_return = optimize_strategy(train_data, macd_fast_values, macd_slow_values,
                                                       macd_signal_values, rsi_period_values, rsi_buy_values,
                                                       rsi_sell_values)

    # Avaliar a estratégia otimizada com os dados de teste
    if best_params:
        test_return = strategy(test_data, **best_params)
        print(f"Melhores parâmetros: {best_params}")
        print(f"Retorno acumulado nos dados de aprendizado: {best_train_return:.2f}%")
        print(f"Retorno acumulado nos dados de teste: {test_return:.2f}%")
    else:
        print("Nenhum parâmetro otimizado encontrado.")


# Executar a função principal para uma ação específica
main("BBAS3.SA")


