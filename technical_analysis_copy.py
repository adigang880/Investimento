import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from itertools import product
import matplotlib.pyplot as plt


# Função para calcular o MACD
def calculate_macd(data, fast, slow, signal):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal


# Função para executar a estratégia
def strategy(data, macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell, initial_capital=10000):
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
    balance = initial_capital
    returns = []
    banca = [balance]  # Lista para armazenar a evolução da banca

    # Contar quantos sinais de compra e venda são gerados
    buy_signals = 0
    sell_signals = 0
    i_buy = None  # Variável para armazenar o índice de compra

    for i in range(1, len(data)):
        print(
            f"Dia {i}: RSI={data['RSI'].iloc[i]}, MACD={data['MACD'].iloc[i]}, MACD_signal={data['MACD_signal'].iloc[i]}")  # Debug
        if data['Buy_Signal'].iloc[i] and position == 0:
            buy_price = data['Close'].iloc[i]
            position = 1
            buy_signals += 1
            i_buy = i  # Armazenar o índice de compra
            print(f"Sinal de compra em {data.index[i]} a {buy_price}")  # Debug
        elif data['Sell_Signal'].iloc[i] and position == 1:
            sell_price = data['Close'].iloc[i]
            # Calcular o retorno da operação
            balance += (sell_price - buy_price) * (balance / buy_price)
            returns.append((sell_price - buy_price) / buy_price)
            position = 0
            sell_signals += 1
            print(f"Sinal de venda em {data.index[i]} a {sell_price}")  # Debug
        # Se já comprou, mas não teve sinal de venda, considerar forçar a venda após algum tempo
        elif position == 1 and i > (i_buy + 5):  # Forçar a venda após 5 dias da compra
            sell_price = data['Close'].iloc[i]
            balance += (sell_price - buy_price) * (balance / buy_price)
            returns.append((sell_price - buy_price) / buy_price)
            position = 0
            sell_signals += 1
            print(f"Venda forçada em {data.index[i]} a {sell_price} devido ao tempo")

        # Armazenar o valor da banca após cada operação
        banca.append(balance)

    # Calcular retorno acumulado
    cumulative_return = (balance - initial_capital) / initial_capital * 100

    print(f"Sinais de Compra: {buy_signals}, Sinais de Venda: {sell_signals}")

    return cumulative_return, banca  # Retorno e evolução da banca


# Testar com novos parâmetros
def main(ticker):
    # Carregar dados do Yahoo Finance
    data = yf.download(ticker, start="2017-01-01", end="2024-10-10")

    # Dividir os dados em aprendizado e teste
    train_data = data.iloc[:int(0.7 * len(data))]
    test_data = data.iloc[int(0.7 * len(data)):]

    # Definir intervalos de parâmetros
    macd_fast_values = [12, 17]
    macd_slow_values = [26, 35]
    macd_signal_values = [9, 12]
    rsi_period_values = [10, 14, 21]
    rsi_buy_values = [30, 35, 40]
    rsi_sell_values = [65, 70, 75]  # Aumentamos os valores de venda para testar

    # Otimizar a estratégia com os dados de aprendizado
    best_params, best_train_return, best_banca = optimize_strategy(train_data, macd_fast_values, macd_slow_values,
                                                                   macd_signal_values, rsi_period_values,
                                                                   rsi_buy_values, rsi_sell_values)

    # Avaliar a estratégia otimizada com os dados de teste
    if best_params:
        test_return, test_banca = strategy(test_data, **best_params)
        print(f"Melhores parâmetros: {best_params}")
        print(f"Retorno acumulado nos dados de aprendizado: {best_train_return:.2f}%")
        print(f"Retorno acumulado nos dados de teste: {test_return:.2f}%")

        # Plotar a evolução da banca
        plt.figure(figsize=(10, 6))
        plt.plot(test_banca, label='Evolução da Banca (Testes)', color='blue')
        plt.title('Evolução da Banca durante a Estratégia')
        plt.xlabel('Dias')
        plt.ylabel('Banca (R$)')
        plt.legend()
        plt.show()
    else:
        print("Nenhum parâmetro otimizado encontrado.")
# Função de otimização para encontrar os melhores parâmetros
def optimize_strategy(data, macd_fast_values, macd_slow_values, macd_signal_values, rsi_period_values, rsi_buy_values,
                      rsi_sell_values):
    best_params = None
    best_return = -np.inf
    best_banca = []

    for params in product(macd_fast_values, macd_slow_values, macd_signal_values, rsi_period_values, rsi_buy_values,
                          rsi_sell_values):
        macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell = params

        # Evitar parâmetros de MACD inválidos
        if macd_fast >= macd_slow:
            continue

        cumulative_return, banca = strategy(data, macd_fast, macd_slow, macd_signal, rsi_period, rsi_buy, rsi_sell)

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
            best_banca = banca

    return best_params, best_return, best_banca


# Executar a função principal para uma ação específica
main("BBAS3.SA")
