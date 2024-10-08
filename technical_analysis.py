# ifr https://www.youtube.com/watch?v=hmTOQbgpGJA&pp=ygUNaW5kaWNhZG9yIGlmcg%3D%3D divergencia
# https://www.youtube.com/watch?v=J4F09C3EnWs
# https://www.youtube.com/watch?v=m2kGFXWghTU&t=9s semanal e diario

# macd https://www.youtube.com/watch?v=6htExpkRL5w
# estocastico lento  https://www.youtube.com/watch?v=6zDREMYERmI
# Volume
# indicador que mede a volatilidade de cada ação, uma vez que cada setor varia diferente dando pesos diferente para cada uma https://www.youtube.com/watch?v=Xc70DVCKPrE
# true range para colcoar com metica na volatilidade acima
# testar aestrategia do trezoitão se um ativo desvia 2x o desvio padrão ver se pode comprar ou vender aquele ativo, ver a taxa de acetividade disso e o lucro ou perda


import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

###################################################################################################
# Parâmetros de entrada
ticker = 'AZUL4.SA'  # Exemplo para ação da Azul (B3)
start_date = '2022-01-01'
end_date = '2024-09-30'
period = 20  # Período para a média móvel (padrão é 20)
window = 50  # Período para cálculo da volatilidade
df = yf.download(ticker, start=start_date, end=end_date)


###################################################################################################
# Função para calcular a volatilidade diária
def calculate_volatility(df, window=10):
    # Calcular os retornos diários: (Preço de hoje / Preço de ontem) - 1
    df['Returns'] = df['Close'].pct_change()

    # Calcular a volatilidade diária como o desvio padrão dos retornos
    df['Volatility'] = df['Returns'].rolling(window=window).std() * np.sqrt(
        window)  # Multiplicado pela raiz quadrada para anualizar

    # Calcular a média móvel da volatilidade
    df['Volatility_Moving_Avg'] = df['Volatility'].rolling(window=window).mean()

    return df


# Função para calcular o True Range (TR) e o Average True Range (ATR)
def calculate_atr(data, window=14):
    data['high-low'] = data['High'] - data['Low']
    data['high-close_prev'] = abs(data['High'] - data['Adj Close'].shift(1))
    data['low-close_prev'] = abs(data['Low'] - data['Adj Close'].shift(1))

    # True Range é o maior valor entre essas três diferenças
    data['TR'] = data[['high-low', 'high-close_prev', 'low-close_prev']].max(axis=1)

    # ATR é a média móvel exponencial do True Range
    data['ATR'] = data['TR'].rolling(window=window).mean()

    return data


# Função para calcular o MACD
def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    data['EMA_fast'] = data['Adj Close'].ewm(span=fast_period, adjust=False).mean()
    data['EMA_slow'] = data['Adj Close'].ewm(span=slow_period, adjust=False).mean()
    data['MACD'] = data['EMA_fast'] - data['EMA_slow']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    data['Histograma'] = data['MACD'] - data['Signal_Line']
    return data


# Função para calcular o RSI
def calculate_rsi(data, period=14):
    delta = data['Adj Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calcula a média exponencial para ganho e perda
    avg_gain = gain.ewm(span=period, min_periods=period).mean()
    avg_loss = loss.ewm(span=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data


# Função para calcular o Estocástico Lento
def calculate_stochastic(data, k_period=14, d_period=3):
    data['L14'] = data['Low'].rolling(window=k_period).min()
    data['H14'] = data['High'].rolling(window=k_period).max()
    data['%K'] = 100 * ((data['Adj Close'] - data['L14']) / (data['H14'] - data['L14']))
    data['%D'] = data['%K'].rolling(window=d_period).mean()
    return data


# Função para calcular o Volume Oscillator (VO)
def calculate_volume_oscillator(data, fast_period=5, slow_period=20):
    data['Volume_EMA_fast'] = data['Volume'].ewm(span=fast_period, adjust=False).mean()
    data['Volume_EMA_slow'] = data['Volume'].ewm(span=slow_period, adjust=False).mean()
    data['VO'] = ((data['Volume_EMA_fast'] / data['Volume_EMA_slow']) - 1) * 100
    return data


# Função para calcular o Volume Delta com EWMA
def calculate_volume_delta_ewm(data, fast_period=14, slow_period=28):
    # Calcula o Volume Delta como a diferença do volume em relação ao período anterior
    data['Volume_Delta'] = data['Volume'].diff()

    # Aplica médias móveis exponenciais (EWMA) para suavizar as variações de volume
    data['Volume_Delta_EMA_fast'] = data['Volume_Delta'].ewm(span=fast_period, adjust=False).mean()
    data['Volume_Delta_EMA_slow'] = data['Volume_Delta'].ewm(span=slow_period, adjust=False).mean()

    # Opcional: Você pode calcular uma diferença entre os EMAs rápido e lento, similar ao MACD
    data['Volume_Delta_MACD'] = data['Volume_Delta_EMA_fast'] - data['Volume_Delta_EMA_slow']

    return data


# Calculando os indicadores
data = calculate_macd(df)
data = calculate_rsi(df)
data = calculate_stochastic(df)
data = calculate_volume_oscillator(df)
data = calculate_atr(df)
data = calculate_volume_delta_ewm(df)
data = calculate_volatility(df, window)


def trading_strategy(data, banca, rsi_threshold=20, use_rsi=True, use_macd=True, use_stochastic=False, use_atr=False):
    buy_signals = []
    sell_signals = []
    position = None  # Rastreamos a posição atual ('buy', 'sell', ou None)
    total_profit = 0  # Para acumular o lucro/prejuízo total
    successful_trades = 0  # Para contar os trades lucrativos
    total_trades = 0  # Para contar o número total de trades
    short_signals = []  # Sinais para vendas descobertas
    cover_signals = []  # Sinais para cobrir (fechar) vendas descobertas
    data_start = []

    # Itera sobre os dados para verificar as condições
    for i in range(1, len(data)):
        current_rsi = data['RSI'].iloc[i] if use_rsi else None
        previous_rsi = data['RSI'].iloc[i - 1] if use_rsi else None
        current_macd = data['MACD'].iloc[i] if use_macd else None
        current_signal = data['Signal_Line'].iloc[i] if use_macd else None
        current_k = data['%K'].iloc[i] if use_stochastic else None
        current_d = data['%D'].iloc[i] if use_stochastic else None
        current_atr = data['ATR'].iloc[i] if use_atr else None

        # Condição base de compra usando RSI e MACD
        if position is None:
            buy_condition = (
                        use_rsi and previous_rsi is not None and previous_rsi < rsi_threshold and current_rsi > previous_rsi)
            macd_condition = (use_macd and current_macd < current_signal)

            # Condição extra de compra usando Stochastic
            if use_stochastic:
                stochastic_condition = (current_k < 30 and current_d < 30)  # Exemplo de condição com Stochastic
            else:
                stochastic_condition = True  # Ignorado se não estiver ativo

            # Condição extra de compra usando ATR
            if use_atr:
                atr_condition = current_atr > data['ATR'].rolling(window=14).mean().iloc[i]  # Exemplo de uso do ATR
            else:
                atr_condition = True  # Ignorado se não estiver ativo

            # Verifica se todas as condições para compra são atendidas
            if buy_condition and macd_condition and stochastic_condition and atr_condition:
                buy_signals.append((data.index[i].strftime('%Y-%m-%d'), round(float(data['Adj Close'].iloc[i]), 2)))  # Marca um sinal de compra
                position = 'buy'  # Atualiza a posição como 'comprado'
                buy_price = data['Adj Close'].iloc[i]  # Armazena o preço de compra
                data_start = data.index[i]
                print(f"Compra em: {data.index[i].strftime('%Y-%m-%d')} | Preço: {buy_price:.2f}")

        # Condição base de venda usando RSI e MACD
        # Compra de ativo
        elif position == 'buy':
            sell_condition = (use_rsi and current_rsi > 70)
            macd_condition_sell = (use_macd and current_macd > current_signal)

            # Condição extra de venda usando Stochastic
            if use_stochastic:
                stochastic_condition_sell = (current_k > 70 and current_d > 70)  # Exemplo de condição com Stochastic
            else:
                stochastic_condition_sell = True  # Ignorado se não estiver ativo

            # Condição extra de venda usando ATR
            if use_atr:
                atr_condition_sell = current_atr < data['ATR'].rolling(window=14).mean().iloc[
                    i]  # Exemplo de uso do ATR
            else:
                atr_condition_sell = True  # Ignorado se não estiver ativo

            # Verifica se todas as condições para venda são atendidas
            if sell_condition and macd_condition_sell and stochastic_condition_sell and atr_condition_sell:
                sell_price = data['Adj Close'].iloc[i]  # Armazena o preço de venda
                sell_signals.append((data.index[i].strftime('%Y-%m-%d'), round(float(sell_price), 2)))  # Marca um sinal de venda
                position = None  # Reseta a posição após a venda
                numero_acoes = banca / buy_price
                trade_profit = (sell_price - buy_price) * numero_acoes  # Calcula o lucro da operação
                banca += trade_profit
                porcentagem = (sell_price / buy_price - 1) * 100
                total_profit += trade_profit  # Acumula o lucro/prejuízo total
                total_trades += 1  # Incrementa o número de trades
                datafinal = (data.index[i] - data_start).days

                # Verifica se a operação foi lucrativa
                if trade_profit > 0:
                    successful_trades += 1  # Incrementa o número de trades lucrativos

                print(
                    f"Venda em: {data.index[i].strftime('%Y-%m-%d')} | Dias: {datafinal} | Preço: {sell_price:.2f} | Lucro: R${trade_profit:.2f} | Retorno {porcentagem:.2f}%")

        # **Venda Descoberta** (short selling) - Vender antes de comprar
        if position is None:
            short_condition = (
                        use_rsi and current_rsi > 70)  # Condição para iniciar uma venda descoberta (RSI alto)

            macd_condition_short = (use_macd and current_macd > current_signal)

            # Condições adicionais (Stochastic e ATR) - Venda Descoberta
            if use_stochastic:
                stochastic_condition_short = (current_k > 80 and current_d > 80)
            else:
                stochastic_condition_short = True  # Ignorado se não estiver ativo

            # Condição extra de compra usando ATR
            if use_atr:
                atr_condition_short = (current_atr < data['ATR'].rolling(window=14).mean().iloc[i])
            else:
                atr_condition_short = True  # Ignorado se não estiver ativo

            # Verifica se todas as condições para venda descoberta são atendidas
            if short_condition and macd_condition_short and stochastic_condition_short and atr_condition_short:
                short_price = data['Adj Close'].iloc[i]  # Preço de venda na venda descoberta
                short_signals.append((data.index[i].strftime('%Y-%m-%d'), round(float(short_price), 2)))  # Marca o sinal de venda descoberta
                position = 'sell'  # Abre posição de venda descoberta
                data_start = data.index[i]
                print(f"Venda Descoberta em: {data.index[i].strftime('%Y-%m-%d')} | Preço: {short_price:.2f}")

        # **Cobrir Venda Descoberta** (buy to cover) - Comprar para fechar a venda
        elif position == 'sell':
            cover_condition = (use_rsi and current_rsi < rsi_threshold)  # Condição para fechar a venda descoberta
            macd_condition_cover = (use_macd and current_macd < current_signal)

            # Condições adicionais (Stochastic e ATR) - Cobertura da Venda Descoberta
            if use_stochastic:
                stochastic_condition_cover = (current_k < 20 and current_d < 20)
            else:
                stochastic_condition_cover = True  # Ignorado se não estiver ativo

            # Condição extra de venda usando ATR
            if use_atr:
                atr_condition_cover = (current_atr > data['ATR'].rolling(window=14).mean().iloc[i])
            else:
                atr_condition_cover = True  # Ignorado se não estiver ativo

            # Verifica se todas as condições para cobertura da venda descoberta são atendidas
            if cover_condition and macd_condition_cover and stochastic_condition_cover and atr_condition_cover:
                cover_price = data['Adj Close'].iloc[i]
                cover_signals.append((data.index[i].strftime('%Y-%m-%d'), round(float(cover_price), 2)))  # Marca o sinal de cobertura
                position = None  # Fecha a posição de venda descoberta
                numero_acoes = banca / short_price
                trade_profit = (short_price - cover_price) * numero_acoes  # Lucro da venda descoberta
                banca += trade_profit
                porcentagem = (short_price / cover_price - 1) * 100
                total_profit += trade_profit
                total_trades += 1
                datafinal = (data.index[i] - data_start).days

                if trade_profit > 0:
                    successful_trades += 1

                print(
                    f"Cobertura em: {data.index[i].strftime('%Y-%m-%d')} | Dias: {datafinal} | Preço: {cover_price:.2f} | Lucro: R${trade_profit:.2f} | Retorno {porcentagem:.2f}%")

    # Calcula a probabilidade de acerto
    if total_trades > 0:
        win_rate = successful_trades / total_trades
    else:
        win_rate = 0

    return buy_signals, sell_signals, total_profit, win_rate, banca

# Define a banca inicial
banca_inicial = 1000  # Valor inicial para operar

# Usando apenas RSI e MACD
buy_signals, sell_signals, total_profit, win_rate, banca_final = trading_strategy(data, banca_inicial)
# Exibe os resultados
print("Sinais de Compra:", buy_signals)
print("Sinais de Venda:", sell_signals)
print(f"Lucro Total: {total_profit}")
print(f"Taxa de Sucesso: {win_rate * 100}%")
print(f"Banca Final: {banca_final}")
print(f"Porcentagem de Banca Final: {(total_profit/banca_final)*100}%")

# Usando RSI, MACD, e Stochastic
buy_signals, sell_signals, total_profit, win_rate, banca_final = trading_strategy(data, banca_inicial, use_stochastic=True)
# Exibe os resultados
print("Sinais de Compra:", buy_signals)
print("Sinais de Venda:", sell_signals)
print(f"Lucro Total: {total_profit}")
print(f"Taxa de Sucesso: {win_rate * 100}%")
print(f"Banca Final: {banca_final}")
print(f"Porcentagem de Banca Final: {(total_profit/banca_final)*100}%")

# Usando RSI, MACD, ATR, e Stochastic
buy_signals, sell_signals, total_profit, win_rate, banca_final = trading_strategy(data, banca_inicial, use_stochastic=True, use_atr=True)

# Exibe os resultados
print("Sinais de Compra:", buy_signals)
print("Sinais de Venda:", sell_signals)
print(f"Lucro Total: {total_profit}")
print(f"Taxa de Sucesso: {win_rate * 100}%")
print(f"Banca Final: {banca_final}")
print(f"Porcentagem de Banca Final: {(total_profit/banca_final)*100}%")

