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


dados_ativo = buscar_dados_por_ativo(acoes_disponiveis[0])
dados_ativo1 = pd.DataFrame(dados_ativo['Dados Historico'])

x=1
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
        style={'width': '200px', 'fontSize': '16px'} # Ajuste a largura e o tamanho da fonte
    ),

    html.Button('Atualizar Gráficos', id='botao-atualizar', n_clicks=0),

    html.Div(id='div-graficos',
             style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between'}),

    html.Div(id='div-resumo', style={'width': '100%'})
])


# Callback para atualizar os gráficos com base no ativo selecionado
@app.callback(
    [Output('div-graficos', 'children'),
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
    df = yf.download(tiker_name, start=dados_ativo['Data Inicio'], end=dados_ativo['Data Final'])
    cotacao_atual = df['Close'].iloc[-1] if not df.empty else None

    # Sinais de compra, venda, short e cover
    buy_signals = dados_ativo.get('Sinais Compra', [])
    sell_signals = dados_ativo.get('Sinais Venda', [])
    short_signals = dados_ativo.get('Sinais de Venda Descoberto', [])
    cover_signals = dados_ativo.get('Sinais de Compra Venda Descoberta', [])
    buy_open = dados_ativo.get('Entrada Aberta Compra', [])
    sell_open = dados_ativo.get('Entrada Aberta Venda Descoberto', [])

    # Gráfico da evolução da banca
    evolucao_banca_dados = dados_ativo["Evolucao Banca"]
    # Preparar listas para os valores de Y e X
    y_values = [evolucao_banca_dados[0]]  # Inicia com o primeiro valor (1000)
    x_values = [evolucao_banca_dados[1]]  # A primeira data
    for evolucao in evolucao_banca_dados[2:]:  # Começa da terceira posição
        y_values.append(evolucao[0])  # Extraindo os valores
        x_values.append(evolucao[1])  # Extraindo as datas

    candlestick = dcc.Graph(
        id='grafico-banca',
        figure={
            'data': [
                # Evolução da banca
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Candle'
                ),
                # Adicionando os sinais de compra (buy_signals)
                go.Scatter(
                    x=[signal[0] for signal in buy_signals],
                    y=[signal[1] for signal in buy_signals],
                    mode='markers',
                    name='Compras',
                    marker=dict(symbol='triangle-up', color='green', size=10),
                    showlegend=True
                ),
                # Adicionando os sinais de venda (sell_signals)
                go.Scatter(
                    x=[signal[0] for signal in sell_signals],
                    y=[signal[1] for signal in sell_signals],
                    mode='markers',
                    name='Vendas',
                    marker=dict(symbol='triangle-down', color='red', size=10),
                    showlegend=True
                ),
                # Adicionando sinais de short (short_signals)
                go.Scatter(
                    x=[signal[0] for signal in short_signals],
                    y=[signal[1] for signal in short_signals],
                    mode='markers',
                    name='Venda Descoberta',
                    marker=dict(symbol='triangle-down', color='black', size=10),
                    showlegend=True
                ),
                # Adicionando sinais de cover (cover_signals)
                go.Scatter(
                    x=[signal[0] for signal in cover_signals],
                    y=[signal[1] for signal in cover_signals],
                    mode='markers',
                    name='Compra Descoberta',
                    marker=dict(symbol='triangle-up', color='blue', size=10),
                    showlegend=True
                )
            ],
            
            'layout': go.Layout(
                title=f'Gráfico de Candle para {dados_ativo["Ativo"]}',
                xaxis={'title': 'Data'},
                yaxis={'title': 'Preço'},
                hovermode='closest'
            )
        }
    )

    evolucao_banca = dcc.Graph(
        id='grafico-banca',
        figure={
            'data': [
                go.Scatter(
                    x=x_values,
                    y=y_values,  # Simulando a banca como 5% acima do preço de fechamento
                    mode='lines+markers',
                    name='Banca (R$)',
                    marker=dict(color='blue')
                )
            ],
            'layout': go.Layout(
                title=f'Evolução da Banca para {dados_ativo["Ativo"]}',
                xaxis={'title': 'Data'},
                yaxis={'title': 'Banca (R$)'},
                hovermode='closest'
            )
        }
    )

    # Colocando os gráficos de candle e evolução da banca lado a lado
    div_graficos = html.Div([
        html.Div(candlestick, style={'flex': '1', 'marginRight': '10px'}),
        html.Div(evolucao_banca, style={'flex': '1'})
    ], style={'display': 'flex', 'width': '100%'})

    # Resumo Geral
    resumo_geral = [
        html.Div([
            html.H3("Banca Inicial", style={'textAlign': 'center'}),
            html.P(f"R$ {dados_ativo['Banca Inicial']:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Banca Final", style={'textAlign': 'center'}),
            html.P(f"R$ {dados_ativo['Banca Final']:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Lucro/Perda Total", style={'textAlign': 'center'}),
            html.P(f"R$ {dados_ativo['Lucro Perda']:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Número Total de Operações", style={'textAlign': 'center'}),
            html.P(str(dados_ativo['Numero Operacoes']), style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'})
    ]

    # Adicionando mais três blocos de resumo
    resumo_adicional = [
        html.Div([
            html.H3("Número de Operações Ganhas", style={'textAlign': 'center'}),
            html.P(str(dados_ativo['Numero Operacoes Ganhas']), style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Número de Operações Perdidas", style={'textAlign': 'center'}),
            html.P(str(dados_ativo['Numero Operacoes Perdas']), style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Porcentagem de Acerto", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Porcentagem Acerto'] * 100:.2f}%", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'})]

    resumo_adicional_1 = [
        html.Div([
            html.H3("Média de Ganhos", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Media Ganhos']:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Média de Perdas", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Media Perdas']:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Média de Operações", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Media Dias Operacao']:.2f} Dias", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Total de Dias Passados", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Total Dias Passados']:.0f} Dias", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Data de Inicio", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Data Inicio']}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Data Final", style={'textAlign': 'center'}),
            html.P(f"{dados_ativo['Data Final']}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'}),
        # Ajuste flex-basis

        html.Div([
            html.H3("Cotação Atual", style={'textAlign': 'center'}),
            html.P(f"R$ {cotacao_atual:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'})
    ]

    name = 'Sem Entrada em Aberto'
    data = ''
    valor = ''
    if len(dados_ativo['Entrada Aberta Compra']):
        name = 'Entrada em Aberto de Compra'
        data = dados_ativo['Entrada Aberta Compra'][0]
        valor = dados_ativo['Entrada Aberta Compra'][1]
    elif len(dados_ativo['Entrada Aberta Venda Descoberto']):
        name = 'Entrada em Aberto de Venda a Descoberto'
        data = dados_ativo['Entrada Aberta Venda Descoberto'][0]
        valor = dados_ativo['Entrada Aberta Venda Descoberto'][1]
    resumo_adicional_2 = [
            html.Div([
                html.H3(name, style={'textAlign': 'center'}),
                html.P(f"Data: {data} | Valor: {valor:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
            ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1', 'flex-basis': '25%'})
            # Ajuste flex-basis
    ]

    # Criando uma lista para o resumo completo
    resumo = html.Div(
[html.Div(resumo_geral + resumo_adicional, style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap',
                                          'justifyContent': 'space-around'}),
        html.Div(resumo_adicional_1 + resumo_adicional_2, style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap',
                                                'justifyContent': 'space-around'}),
        ],
        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
        # Centraliza os elementos
    )

    return div_graficos, resumo


# Executando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
