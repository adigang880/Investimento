# telegram_bot.py
import json
import requests
import pandas as pd
from datetime import datetime

TOKEN = ""
CHAT_ID = ""

CAMINHO_ALERTAS = 'logs/alertas_automaticos.csv'
#adigangBot
def enviar_sinais_para_telegram(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        sinais = json.load(f)

    hoje = datetime.now().date()

    for sinal in sinais:
        data_sinal = datetime.strptime(sinal['data'], '%Y-%m-%d %H:%M:%S').date()
        if data_sinal == hoje:
            modelo = sinal.get('modelo', 'n/a')
            mensagem = (
                f"\U0001F4C8 *Sinal de {sinal['tipo'].capitalize()}*\n"
                f"*Ativo:* {sinal['ativo']}\n"
                f"*Data:* {sinal['data']}\n"
                f"*Preço:* R$ {sinal['preco']:.2f}\n"
                f"*Modelo:* {modelo}\n"
                f"*Sharpe:* {sinal['sharpe']:.2f} | *Retorno:* {sinal['retorno']:.2f}%\n"
                f"*Alocação:* R$ {sinal['alocacao']:.2f}"
            )

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
            )

    print("Sinais enviados com sucesso para o Telegram!")

def enviar_alertas():
    try:
        df = pd.read_csv(CAMINHO_ALERTAS)
    except FileNotFoundError:
        print("Arquivo de alertas não encontrado.")
        return

    if df.empty:
        print("Nenhum alerta para enviar.")
        return

    for _, row in df.iterrows():
        mensagem = (
            f"🚨 *Alerta Automático!*"
            f"*Ativo:* {row['Ativo']}"
            f"*Data:* {row['Data']}"
            f"*Modelo:* {row['Modelo']}"
            f"*Sharpe:* {row['Sharpe']:.2f} | *Retorno:* {row['Retorno']:.2f}%"
            f"*Alocação:* R$ {row['Alocacao']:.2f}"
            f"*Gatilhos:* {' | '.join(eval(row['Alertas']) if isinstance(row['Alertas'], str) else row['Alertas'])}"
        )

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        )

    print("Alertas enviados para o Telegram!")


if __name__ == '__main__':
    enviar_sinais_para_telegram('sinais_telegram.json')
    enviar_alertas()
