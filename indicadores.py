# indicadores.py
import pandas as pd
import numpy as np


# RSI (Índice de Força Relativa): mede a força do movimento dos preços e identifica sobrecompra ou sobrevenda.

def calcular_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


# MACD (Moving Average Convergence Divergence): mostra a direção e a força da tendência com duas médias móveis exponenciais.

def calcular_macd(df, fast=12, slow=26, signal=9):
    df['EMA_fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    return df


# Estocástico (%K e %D): compara o preço atual com a faixa de preços passada, útil para detectar reversões.

def calcular_estocastico(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df


# ATR (Average True Range): mede a volatilidade média dos preços, útil para ajuste de stop loss.

def calcular_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period).mean()
    return df


# SMA e EMA: médias móveis simples e exponenciais para identificar tendências de curto e longo prazo.

def calcular_sma_ema(df, short=9, long=21):
    df['SMA'] = df['Close'].rolling(window=short).mean()
    df['EMA'] = df['Close'].ewm(span=long, adjust=False).mean()
    return df


# Bandas de Bollinger: cria faixas de desvio padrão ao redor da média, útil para detectar momentos de reversão.

def calcular_bollinger(df, window=20, std_mult=2):
    df['Bollinger_MA'] = df['Close'].rolling(window=window).mean()
    std = df['Close'].rolling(window=window).std()
    df['Bollinger_Upper'] = df['Bollinger_MA'] + std_mult * std
    df['Bollinger_Lower'] = df['Bollinger_MA'] - std_mult * std
    return df


# OBV (On Balance Volume): indicador de volume acumulado que sugere pressão compradora ou vendedora.

def calcular_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df


# ROC (Rate of Change): mede a variação percentual do preço em relação a um período anterior.

def calcular_roc(df, period=10):
    df['ROC'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100
    return df


def calcular_todos_indicadores(df):
    df = calcular_rsi(df)
    df = calcular_macd(df)
    df = calcular_estocastico(df)
    df = calcular_atr(df)
    df = calcular_sma_ema(df)
    df = calcular_bollinger(df)
    df = calcular_obv(df)
    df = calcular_roc(df)
    return df
