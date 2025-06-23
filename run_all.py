# run_all.py
import os
from telegram_bot import enviar_sinais_para_telegram

if __name__ == '__main__':
    print("Executando o pipeline completo de investimentos...")
    os.system("python pipeline.py")
    print("Processo finalizado. Sinais prontos para envio.")
    enviar_sinais_para_telegram('sinais_telegram.json')
    print("Processo finalizado. Sinais enviados.")
