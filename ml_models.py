# ml_models.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
import numpy as np

def gerar_labels(df):
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()

def testar_modelos_ml(df, capital):
    df = gerar_labels(df)
    features = ['RSI', 'MACD', 'MACD_signal', '%K', '%D', 'ATR']
    df = df.dropna()
    X = df[features]
    y = df['target']

    tscv = TimeSeriesSplit(n_splits=5)
    preds = []
    posicao = None
    sinais = []
    lucro = 0
    banca = capital

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        for i, pred in zip(test_idx, y_pred):
            if posicao is None and pred == 1:
                sinais.append({'data': df.index[i], 'tipo': 'compra', 'preco': df['Close'].iloc[i]})
                posicao = df['Close'].iloc[i]
            elif posicao is not None and pred == 0:
                sinais.append({'data': df.index[i], 'tipo': 'venda', 'preco': df['Close'].iloc[i]})
                lucro += (df['Close'].iloc[i] - posicao) * (banca / posicao)
                posicao = None

    retorno_pct = (lucro / capital) * 100
    sharpe = retorno_pct / (np.std(df['Close'].pct_change()) * 100 + 1e-6)

    return sinais, {'retorno_pct': retorno_pct, 'sharpe': sharpe}
