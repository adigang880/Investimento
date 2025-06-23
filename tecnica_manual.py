# tecnica_manual.py
from indicadores import calcular_macd, calcular_estocastico


def gerar_sinais_tecnicos(df, rsi_thresh, macd_fast, macd_slow, macd_signal, k_period, d_period,
                          k_buy=30, k_sell=70, d_buy=30, d_sell=70):

    # Recalcula MACD e Estocástico com os parâmetros passados
    df = calcular_macd(df, fast=macd_fast, slow=macd_slow, signal=macd_signal)
    df = calcular_estocastico(df, k_period=k_period, d_period=d_period)

    sinais = []
    position = None

    for i in range(1, len(df)):
        cond_compra_rsi_macd = (
            df['RSI'].iloc[i] < rsi_thresh and
            df['MACD'].iloc[i] > df['MACD_signal'].iloc[i] and
            df['%K'].iloc[i] < k_buy and
            df['%D'].iloc[i] < d_buy
        )

        cond_venda_rsi_macd = (
            df['RSI'].iloc[i] > (100 - rsi_thresh) and
            df['MACD'].iloc[i] < df['MACD_signal'].iloc[i] and
            df['%K'].iloc[i] > k_sell and
            df['%D'].iloc[i] > d_sell
        )

        cond_bollinger_buy = df['Close'].iloc[i] < df['Bollinger_Lower'].iloc[i]
        cond_bollinger_sell = df['Close'].iloc[i] > df['Bollinger_Upper'].iloc[i]

        media = df['Close'].rolling(window=20).mean().iloc[i]
        desvio = df['Close'].rolling(window=20).std().iloc[i]
        cond_trezoitao_buy = df['Close'].iloc[i] < media - 2 * desvio
        cond_trezoitao_sell = df['Close'].iloc[i] > media + 2 * desvio

        obv_momentum = df['OBV'].iloc[i] > df['OBV'].rolling(window=5).mean().iloc[i]
        roc_positive = df['ROC'].iloc[i] > 0
        cond_momentum_buy = obv_momentum and roc_positive
        cond_momentum_sell = not obv_momentum and df['ROC'].iloc[i] < 0

        if position is None and (cond_compra_rsi_macd or cond_bollinger_buy or cond_trezoitao_buy or cond_momentum_buy):
            sinais.append({
                'data': df.index[i],
                'tipo': 'compra',
                'preco': df['Close'].iloc[i]
            })
            position = 'comprado'

        elif position == 'comprado' and (
                cond_venda_rsi_macd or cond_bollinger_sell or cond_trezoitao_sell or cond_momentum_sell):
            sinais.append({
                'data': df.index[i],
                'tipo': 'venda',
                'preco': df['Close'].iloc[i]
            })
            position = None

    return sinais
