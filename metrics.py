# metrics.py
import numpy as np
import pandas as pd


def avaliar_estrategia(df, sinais, capital):
    df = df.copy()
    df["retorno_diario"] = 0.0
    posicao = None
    preco_entrada = 0
    quantidade = 0

    for sinal in sinais:
        data = pd.to_datetime(sinal["data"])
        preco = sinal["preco"]
        if sinal["tipo"] == "compra" and posicao is None:
            posicao = data
            preco_entrada = preco
            quantidade = capital / preco_entrada
        elif sinal["tipo"] == "venda" and posicao is not None:
            data_saida = data
            df_operacao = df.loc[posicao:data_saida]
            df_operacao = df_operacao.copy()
            df_operacao["retorno"] = df_operacao["Close"].pct_change().fillna(0)
            df_operacao["retorno"] *= quantidade
            df.loc[posicao:data_saida, "retorno_diario"] = df_operacao["retorno"]
            posicao = None

    df["retorno_diario"] = df["retorno_diario"].fillna(0)
    retorno_total = df["retorno_diario"].sum()
    retorno_pct = (retorno_total / capital) * 100
    volatilidade = df["retorno_diario"].std() * np.sqrt(252)
    sharpe = (df["retorno_diario"].mean() * 252) / volatilidade if volatilidade > 0 else 0

    return {
        "retorno_pct": retorno_pct,
        "sharpe": sharpe,
        "vol": df["retorno_diario"].std(),
        "lucro_total": retorno_total
    }
