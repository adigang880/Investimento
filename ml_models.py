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
    y = df['target']
    y = y.astype(int)

    tscv = TimeSeriesSplit(n_splits=5)
    resultados_modelos = []

    for nome_modelo, modelo in modelos.items():
        sinais = []
        posicao = None
        lucro = 0
        banca = capital

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train = y.iloc[train_idx].values.ravel()
            y_test = y.iloc[test_idx].values.ravel()

            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            for i, pred in zip(test_idx, y_pred):
                if posicao is None and pred == 1:
                    sinais.append({'data': df.index[i], 'tipo': 'compra', 'preco': df['Close'].iloc[i]})
                    posicao = df['Close'].iloc[i]
                elif posicao is not None and pred == 0:
                    sinais.append({'data': df.index[i], 'tipo': 'venda', 'preco': df['Close'].iloc[i]})
                    lucro += (df['Close'].iloc[i] - posicao) * (banca / posicao)
                    posicao = None

        retorno_pct = (lucro / capital) * 100
        volatilidade = np.std(df['Close'].pct_change()) * 100
        retorno_decimal = retorno_pct / 100
        volatilidade_decimal = volatilidade / 100
        sharpe = retorno_decimal / (volatilidade_decimal + 1e-6)

        resultados_modelos.append({
            'modelo': nome_modelo,
            'sinais': sinais,
            'resultado': {
                'retorno_pct': retorno_pct,
                'sharpe': sharpe
            }
        })

    # Ordenar pelos melhores
    resultados_modelos.sort(key=lambda x: x['resultado']['sharpe'], reverse=True)
    melhor = resultados_modelos[0]
    return melhor['sinais'], melhor['resultado']
