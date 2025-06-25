# metrics.py
import numpy as np
import pandas as pd


# Este módulo avalia o desempenho de uma estratégia de investimento com base nos sinais gerados.
def avaliar_estrategia(df, sinais, capital):
    """
    Avalia uma estratégia de compra e venda com base em sinais fornecidos.

    Parâmetros:
    - df: DataFrame com os dados históricos de preços (deve conter coluna 'Close')
    - sinais: lista de sinais no formato {'data': ..., 'tipo': 'compra' ou 'venda', 'preco': ...}
    - capital: valor disponível para aplicar nas operações

    Retorna:
    - Um dicionário com:
        - retorno_pct: retorno percentual total sobre o capital
        - sharpe: índice de Sharpe anualizado
        - vol: volatilidade diária
        - lucro_total: lucro em R$ no período
    """

    df = df.copy()  # Garante que não alteramos o DataFrame original
    df["retorno_diario"] = 0.0  # Inicializa coluna para armazenar retorno diário das operações

    posicao = None           # Marca se há uma posição aberta (comprado ou não)
    preco_entrada = 0        # Armazena o preço da compra
    quantidade = 0           # Quantidade de ativos comprados com o capital disponível

    # Itera sobre cada sinal para simular as operações
    for sinal in sinais:
        data = pd.to_datetime(sinal["data"])  # Converte a data do sinal para datetime
        preco = sinal["preco"]

        if sinal["tipo"] == "compra" and posicao is None:
            # Quando encontramos um sinal de compra, armazenamos os dados da posição
            posicao = data
            preco_entrada = preco
            quantidade = capital / preco_entrada  # Quantidade de ativos comprados

        elif sinal["tipo"] == "venda" and posicao is not None:
            # Finaliza uma operação de venda
            data_saida = data

            # Seleciona o período da operação entre entrada e saída
            df_operacao = df.loc[posicao:data_saida].copy()

            # Calcula o lucro total da operação com base na diferença de preços e quantidade
            lucro_total = (preco - preco_entrada) * quantidade

            # Distribui o lucro igualmente entre os dias da operação
            num_dias = len(df_operacao)
            if num_dias > 0:
                lucro_por_dia = lucro_total / num_dias
                df_operacao["retorno"] = lucro_por_dia
                df.loc[posicao:data_saida, "retorno_diario"] = df_operacao["retorno"]

            # Finaliza a posição
            posicao = None

    # Preenche valores nulos com zero (dias sem operação)
    df["retorno_diario"] = df["retorno_diario"].fillna(0)

    # Calcula o lucro total acumulado
    retorno_total = df["retorno_diario"].sum()

    # Calcula o retorno percentual sobre o capital alocado
    retorno_pct = (retorno_total / capital) * 100

    # Calcula a volatilidade anualizada
    volatilidade = df["retorno_diario"].std() * np.sqrt(252)

    # Calcula o índice de Sharpe anualizado (retorno médio dividido pela volatilidade)
    # TODO ENTENDER MELHOR ESSE CONCEITO E FAZER MELHOR
    sharpe = (df["retorno_diario"].mean() * 252) / volatilidade if volatilidade > 0 else 0

    return {
        "retorno_pct": retorno_pct,
        "sharpe": sharpe,
        "vol": df["retorno_diario"].std(),  # Volatilidade diária (sem anualizar)
        "lucro_total": retorno_total
    }
