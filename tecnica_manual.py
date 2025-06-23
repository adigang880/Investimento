# tecnica_manual.py
def gerar_sinais_tecnicos(df, rsi_thresh, macd_fast, macd_slow, macd_signal, k_period, d_period):
    sinais = []
    position = None

    for i in range(1, len(df)):
        cond_compra = (
            df['RSI'].iloc[i] < rsi_thresh and
            df['MACD'].iloc[i] > df['MACD_signal'].iloc[i] and
            df['%K'].iloc[i] < 30 and
            df['%D'].iloc[i] < 30
        )
        cond_venda = (
            df['RSI'].iloc[i] > (100 - rsi_thresh) and
            df['MACD'].iloc[i] < df['MACD_signal'].iloc[i] and
            df['%K'].iloc[i] > 70 and
            df['%D'].iloc[i] > 70
        )

        if position is None and cond_compra:
            sinais.append({
                'data': df.index[i],
                'tipo': 'compra',
                'preco': df['Close'].iloc[i]
            })
            position = 'comprado'

        elif position == 'comprado' and cond_venda:
            sinais.append({
                'data': df.index[i],
                'tipo': 'venda',
                'preco': df['Close'].iloc[i]
            })
            position = None

    return sinais
