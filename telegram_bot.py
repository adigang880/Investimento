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

    hoje = datetime.today().date()
    hoje = datetime.strptime('2025-06-20', '%Y-%m-%d').date()
    for sinal in sinais:
        data_sinal = datetime.strptime(sinal['data'], '%Y-%m-%d %H:%M:%S').date()
        if data_sinal == hoje:  # Só envia sinais do dia atual
            mensagem = (
                f"📈 *Sinal de {sinal['tipo'].capitalize()}*\n"
                f"*Ativo:* {sinal['ativo']}\n"
                f"*Data:* {sinal['data']}\n"
                f"*Preço:* R$ {sinal['preco']:.2f}\n"
                f"*Modelo:* {sinal['modelo']}\n"
                f"*Sharpe:* {sinal['sharpe']} | *Retorno:* {sinal['retorno']}%\n"
                f"*Alocação:* R$ {sinal['alocacao']:.2f}"
            )

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": mensagem,
                    "parse_mode": "Markdown"
                }
            )

    print("Sinais de hoje enviados com sucesso!")


if __name__ == '__main__':
    enviar_sinais_para_telegram('sinais_telegram.json')
