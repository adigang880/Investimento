# ml_models.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

modelos = {
    'random_forest': RandomForestClassifier(n_estimators=100),
    'logistic_regression': LogisticRegression(max_iter=1000),
    'gradient_boosting': GradientBoostingClassifier(n_estimators=100),
    'xgboost': XGBClassifier(eval_metric='logloss')
}


def gerar_labels(df):
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()


def testar_modelos_ml(df, capital):
    df = gerar_labels(df)
    features = ['RSI', 'MACD', 'MACD_signal', '%K', '%D', 'ATR', 'SMA', 'EMA', 'OBV', 'ROC']
    df = df.dropna()
    X = df[features]
    y = df['target'].astype(int)

    tscv = TimeSeriesSplit(n_splits=5)
    resultados_modelos = []

    for nome_modelo, modelo in modelos.items():
        sinais = []
        posicao = None
        quantidade = 0
        df['retorno_diario'] = 0.0

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train = y.iloc[train_idx]
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            for i, pred in zip(test_idx, y_pred):
                preco = df['Close'].iloc[i]
                data = df.index[i]

                if posicao is None and pred == 1:
                    sinais.append({'data': data, 'tipo': 'compra', 'preco': preco})
                    posicao = data
                    preco_entrada = preco
                    quantidade = capital / preco
                elif posicao is not None and pred == 0:
                    sinais.append({'data': data, 'tipo': 'venda', 'preco': preco})
                    df_operacao = df.loc[posicao:data].copy()
                    df_operacao['retorno'] = df_operacao['Close'].pct_change().fillna(0) * quantidade
                    df.loc[posicao:data, 'retorno_diario'] = df_operacao['retorno']
                    posicao = None

        df['retorno_diario'] = df['retorno_diario'].fillna(0)
        retorno_total = df['retorno_diario'].sum()
        retorno_pct = (retorno_total / capital) * 100
        vol_diaria = df['retorno_diario'].std()
        sharpe = (df['retorno_diario'].mean() * 252) / vol_diaria if vol_diaria > 0 else 0

        resultados_modelos.append({
            'modelo': nome_modelo,
            'sinais': sinais,
            'resultado': {
                'retorno_pct': retorno_pct,
                'sharpe': sharpe,
                'lucro_total': retorno_total,
                'vol': vol_diaria
            }
        })

    resultados_modelos.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
    melhor = resultados_modelos[0]
    return melhor['sinais'], melhor['resultado']
