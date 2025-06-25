# ml_models.py
# Este módulo aplica diferentes modelos de machine learning para prever sinais de compra e
# venda usando indicadores técnicos.

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

# Dicionário com os modelos de ML que serão testados
modelos = {
    'random_forest': RandomForestClassifier(n_estimators=100),
    'logistic_regression': LogisticRegression(max_iter=1000),
    'gradient_boosting': GradientBoostingClassifier(n_estimators=100),
    'xgboost': XGBClassifier(eval_metric='logloss')
}


def gerar_labels(df):
    """
    Cria o rótulo 'target' para o modelo supervisionado:
    - 1 se o preço de fechamento seguinte for maior que o atual (sinal de compra)
    - 0 caso contrário
    """

    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()


def testar_modelos_ml(df, capital):
    """
    Testa múltiplos modelos de ML para prever sinais de compra e venda.
    Usa validação por séries temporais e escolhe o melhor modelo com base no Sharpe Ratio.

    Parâmetros:
    - df: DataFrame com indicadores técnicos calculados
    - capital: valor em R$ disponível para operar

    Retorna:
    - sinais: lista com os sinais do melhor modelo
    - resultado: dicionário com sharpe, retorno, lucro total e volatilidade
    """

    # Gera os rótulos binários (comprar ou não)
    df = gerar_labels(df)

    # Define os indicadores usados como features para o modelo
    features = ['RSI', 'MACD', 'MACD_signal', '%K', '%D', 'ATR', 'SMA', 'EMA', 'OBV', 'ROC']
    df = df.dropna()
    X = df[features]
    y = df['target'].astype(int)

    tscv = TimeSeriesSplit(n_splits=5)  # Validação temporal
    resultados_modelos = []  # Lista para armazenar resultados de cada modelo

    for nome_modelo, modelo in modelos.items():
        sinais = []          # Lista de sinais gerados por esse modelo
        posicao = None       # Se estamos comprados ou não
        quantidade = 0       # Quantidade de ativos comprados
        df['retorno_diario'] = 0.0  # Inicializa coluna de retorno

        for train_idx, test_idx in tscv.split(X):
            # Treina o modelo com uma parte dos dados e testa com outra (seguindo o tempo)
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train = y.iloc[train_idx]
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            preco_entrada = 0

            # Gera sinais com base na predição
            for i, pred in zip(test_idx, y_pred):
                preco = df['Close'].iloc[i]
                data = df.index[i]

                if posicao is None and pred == 1:
                    # Compra se não estivermos posicionados e o modelo indicar alta
                    sinais.append({'data': data, 'tipo': 'compra', 'preco': preco})
                    posicao = data
                    preco_entrada = preco
                    quantidade = capital / preco

                elif posicao is not None and pred == 0:
                    # Cálculo do lucro real
                    retorno_pct_individual = ((preco - preco_entrada) / preco_entrada) * 100
                    sinais.append({'data': data, 'tipo': 'venda', 'preco': preco, 'retorno': retorno_pct_individual})
                    lucro_total = (preco - preco_entrada) * quantidade
                    df_operacao = df.loc[posicao:data].copy()
                    num_dias = len(df_operacao)

                    if num_dias > 1:
                        df_operacao['retorno'] = df_operacao['Close'].pct_change().fillna(0) * quantidade
                    else:
                        df_operacao['retorno'] = lucro_total

                    df.loc[posicao:data, 'retorno_diario'] = df_operacao['retorno']
                    posicao = None

            # FECHAMENTO FORÇADO da posição se ainda aberta no final do split
            if posicao is not None:
                # Usa o último índice do bloco de teste como data de venda
                data_fechamento = df.index[test_idx[-1]]
                preco_fechamento = df['Close'].iloc[test_idx[-1]]
                retorno_pct_individual = ((preco_fechamento - preco_entrada) / preco_entrada) * 100

                sinais.append({'data': data_fechamento, 'tipo': 'venda', 'preco': preco_fechamento, 'retorno': retorno_pct_individual})

                # Calcula o lucro da operação pendente
                lucro_total = (preco_fechamento - preco_entrada) * quantidade
                df_operacao = df.loc[posicao:data_fechamento].copy()
                num_dias = len(df_operacao)
                if num_dias > 1:
                    df_operacao['retorno'] = df_operacao['Close'].pct_change().fillna(0) * quantidade
                else:
                    df_operacao['retorno'] = lucro_total

                df.loc[posicao:data_fechamento, 'retorno_diario'] = df_operacao['retorno']
                posicao = None # Garante que não fique posição aberta para o próximo split


        # Preenche valores nulos com zero (dias sem operação)
        df["retorno_diario"] = df["retorno_diario"].fillna(0)

        # Calcula o lucro total acumulado
        retorno_total = df["retorno_diario"].sum()

        # Calcula o retorno percentual sobre o capital alocado
        retorno_pct = (retorno_total / capital) * 100

        # Calcula a volatilidade anualizada
        vol_anual = df["retorno_diario"].std() * np.sqrt(252)

        # Calcula o índice de Sharpe anualizado (retorno médio dividido pela volatilidade)
        # TODO ENTENDER MELHOR ESSE CONCEITO E FAZER MELHOR
        sharpe = (df["retorno_diario"].mean() * 252) / vol_anual if vol_anual > 0 else 0

        # Armazena os resultados do modelo
        resultados_modelos.append({
            'modelo': nome_modelo,
            'sinais': sinais,
            'resultado': {
                'retorno_pct': retorno_pct,
                'sharpe': sharpe,
                'lucro_total': retorno_total,
                'vol': vol_anual
            }
        })

    # Seleciona o modelo com maior Sharpe Ratio
    resultados_modelos.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
    melhor = resultados_modelos[0]

    return melhor['sinais'], melhor['resultado']
