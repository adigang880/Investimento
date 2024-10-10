import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

# Carregar dados do arquivo JSON
with open('dados_ativos.json', 'r') as f:
    data_json = [json.loads(line) for line in f]

# Converter de volta para DataFrame
df = pd.DataFrame(data_json)

# TODO para executar o codigo so colocar isso no terminal streamlit run D:\06_05_2022\Eletrica\MBA\Codigo\Projeto_aplicado\dddd.py
# Supondo que você tenha os dados em um formato similar a este:
data = {
    'Ativo': ['Ação A', 'Ação B', 'Ação C'],  # Liste os ativos aqui
    'Entradas': [1000, 2000, 1500],  # Valores das entradas correspondentes
    'Saídas': [1200, 1800, 1600],  # Valores das saídas correspondentes
    'Lucro/Perda Final': [200, -200, 100]  # Lucros ou perdas correspondentes
}

# Criação do DataFrame
df = pd.DataFrame(data)

# Título do dashboard
st.title("Dashboard de Ativos")

# Selecionar ativo
ativo_selecionado = st.selectbox("Selecione um ativo", df['Ativo'])

# Filtrar dados para o ativo selecionado
dados_ativo = df[df['Ativo'] == ativo_selecionado].iloc[0]

# Exibir resultados do ativo
st.write(f"**Entradas:** R$ {dados_ativo['Entradas']}")
st.write(f"**Saídas:** R$ {dados_ativo['Saídas']}")
st.write(f"**Lucro/Perda Final:** R$ {dados_ativo['Lucro/Perda Final']}")

# Gráfico de entradas e saídas
fig, ax = plt.subplots()
ax.bar(['Entradas', 'Saídas'], [dados_ativo['Entradas'], dados_ativo['Saídas']], color=['green', 'red'])
ax.set_ylabel('Valor em R$')
ax.set_title(f'Entradas e Saídas para {ativo_selecionado}')

# Exibir gráfico no Streamlit
st.pyplot(fig)

# Exibir todos os ativos e seus resultados
st.subheader("Resultados de Todos os Ativos")
st.write(df)
