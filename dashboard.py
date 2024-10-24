import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import json
import yfinance as yf
import datetime as dt


# Carregar dados do arquivo JSON
with open('dados_ativos.json', 'r') as f:
    data_json = [json.loads(line) for line in f]

data = pd.DataFrame(data_json)
# Inicializando o aplicativo Dash
app = dash.Dash(__name__)

# Data fixa para os gráficos
DATA_INICIO = '2022-01-01'
DATA_FIM = dt.datetime.now().strftime('%Y-%m-%d')

# Lista de ações disponíveis
acoes_disponiveis = data['Ativo']


def buscar_dados_por_ativo(nome_ativo):
    with open('dados_ativos.json', 'r') as f:
        data_json = [json.loads(line) for line in f]
    # Filtra os dados com base no nome do ativo
    for dados_ativo in data_json:
        if dados_ativo['Ativo'] == nome_ativo:
            return dados_ativo  # Retorna os dados do ativo encontrado
    return None  # Retorna None se o ativo não for encontrado


# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Desempenho do Investimento"),

    html.Label(
        "Selecione um Ativo:",
        style={'fontSize': '22px', 'fontWeight': 'bold'}  # Ajuste o tamanho e o peso da fonte
    ),
    dcc.Dropdown(
        id='dropdown-ativo',
        options=[{'label': acao, 'value': acao} for acao in acoes_disponiveis],
        value='CPLE6',  # Valor padrão
        multi=False,  # Permite apenas uma seleção
        style={'width': '200px', 'fontSize': '16px'}  # Ajuste a largura e o tamanho da fonte
    ),

    # Bloco para exibir a data de hoje e cotação
    html.Div(id='output-data'),

    html.Button('Atualizar Gráficos', id='botao-atualizar', n_clicks=0)
])


# Callback para atualizar os gráficos com base no ativo selecionado
@app.callback(
    [Output('output-data', 'children'),
     Output('div-graficos', 'children'),
     Output('div-resumo', 'children')],
    [Input('botao-atualizar', 'n_clicks')],
    [Input('dropdown-ativo', 'value')]
)
def update_dashboard(n_clicks, ativo_selecionado):
    if n_clicks == 0:
        return [], []

    # Obtendo dados do ativo selecionado
    dados_ativo = buscar_dados_por_ativo(ativo_selecionado)

    # Verificando se os dados estão disponíveis
    if dados_ativo is None:
        return [], [html.Div("Nenhum dado encontrado para este ativo.")]

    tiker_name = dados_ativo["Ativo"]+'.SA'
    df = yf.download(tiker_name, start=dados_ativo['Data Inicio'], end = dt.datetime.today().strftime('%Y-%m-%d'))

    # Sinais de compra, venda, short e cover
    buy_signals = dados_ativo.get('Sinais de Compra', [])
    sell_signals = dados_ativo.get('Sinais de Venda', [])
    short_signals = dados_ativo.get('Sinais de Venda Descoberto', [])
    cover_signals = dados_ativo.get('Sinais de Compra Venda Descoberta', [])
    buy_open = dados_ativo.get('Entrada Aberta Compra', [])
    sell_open = dados_ativo.get('Entrada Aberta Venda Descoberto', [])
    gain_loss = dados_ativo.get('Lucro/Perda Por Entrada Compra', [])

    #######################################################################################


    return


# Executando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
