# metrics.py
import numpy as np

def avaliar_estrategia(df, sinais, capital):
    lucro_total = 0
    posicao = None
    banca = capital

    for sinal in sinais:
        preco = sinal['preco']
        if sinal['tipo'] == 'compra' and posicao is None:
            posicao = preco
        elif sinal['tipo'] == 'venda' and posicao is not None:
            lucro = (preco - posicao) * (banca / posicao)
            lucro_total += lucro
            posicao = None

    retorno_pct = (lucro_total / capital) * 100
    volatilidade = np.std(df['Close'].pct_change()) * 100
    sharpe = (retorno_pct / volatilidade) / 100

    return {
        'retorno_pct': retorno_pct,
        'sharpe': sharpe
    }
