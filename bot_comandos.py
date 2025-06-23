# bot_comandos.py
from telegram import Update, InputFile
from telegram import ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd
import os
from datetime import datetime

#Agora seu bot responde no Telegram com os comandos:

#/saldo → mostra alocação por ativo

#/relatorio → envia o gráfico mais recente

#/video → envia o vídeo gerado para o ativo do dia

# PARA RODAR O CODIGO USE O COMANDO ABAIXO
#python bot_comandos.py

TOKEN = '7043331439:AAFg1xP3WlU-96qn1pDRtcRbKTFaDSV0vX4'
CHAT_ID = '6644531818'

df = pd.read_json("sinais_telegram.json")
df["data"] = pd.to_datetime(df["data"])

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resumo = df.groupby("ativo")["alocacao"].sum().reset_index()
    texto = "\u2709\ufe0f *Aloca\u00e7\u00e3o Atual por Ativo:*\n"
    for _, row in resumo.iterrows():
        texto += f"{row['ativo']}: R$ {row['alocacao']:.2f}\n"
    await update.message.reply_text(texto, parse_mode='Markdown')

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ativo = df.sort_values("data")["ativo"].iloc[-1].replace(".SA", "")
    path = f"relatorios/{ativo}_{datetime.now().strftime('%Y%m%d')}.png"
    if os.path.exists(path):
        await update.message.reply_photo(InputFile(path))
    else:
        await update.message.reply_text("Nenhum relatório encontrado para hoje.")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ativo = df.sort_values("data")["ativo"].iloc[-1].replace(".SA", "")
    path = f"videos/{ativo}_{datetime.now().strftime('%Y%m%d')}.mp4"
    if os.path.exists(path):
        await update.message.reply_video(InputFile(path))
    else:
        await update.message.reply_text("Nenhum vídeo encontrado para hoje.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("relatorio", relatorio))
app.add_handler(CommandHandler("video", video))

if __name__ == '__main__':
    print("Bot de comandos iniciado!")
    app.run_polling()
