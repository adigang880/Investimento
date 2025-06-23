# telegram_bot.py
import json
import requests
from datetime import datetime

TOKEN = '7043331439:AAFg1xP3WlU-96qn1pDRtcRbKTFaDSV0vX4'
CHAT_ID = '6644531818'

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

if __name__ == '__main__':
    enviar_sinais_para_telegram('sinais_telegram.json')