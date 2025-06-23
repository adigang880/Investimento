# gerar_video.py
import os
import pandas as pd
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from datetime import datetime

# PARA RODAR FAÇA O COMAND OABAIXO
# python gerar_video.py

# Criar pasta de saída
os.makedirs("videos", exist_ok=True)

# Carregar sinais
df = pd.read_json("sinais_telegram.json")
df["data"] = pd.to_datetime(df["data"])
df = df.sort_values("data")

for i, row in df.iterrows():
    ativo = row["ativo"].replace(".SA", "")
    nome_img = f"relatorios/{ativo}_{datetime.now().strftime('%Y%m%d')}.png"
    nome_audio = f"videos/{ativo}_audio.mp3"
    nome_video = f"videos/{ativo}_{datetime.now().strftime('%Y%m%d')}.mp4"

    if not os.path.exists(nome_img):
        continue

    texto = (f"Sinal de {row['tipo']} em {ativo}. Modelo utilizado: {row['modelo']}. "
             f"Sharpe de {row['sharpe']:.2f}, retorno esperado de {row['retorno']:.2f}%. "
             f"Valor sugerido para alocação: R$ {row['alocacao']:.2f}.")

    tts = gTTS(text=texto, lang='pt-br')
    tts.save(nome_audio)

    imagem = ImageClip(nome_img).with_duration(10).resized(height=720)
    audio = AudioFileClip(nome_audio)
    video = imagem.with_audio(audio)
    video.write_videofile(nome_video, fps=24)

print("Vídeos gerados com sucesso na pasta 'videos'.")
