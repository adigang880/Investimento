import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf

# Inicializando o aplicativo Dash
app = dash.Dash(__name__)

# Data fixa para os gráficos
DATA_INICIO = '2023-01-01'
DATA_FIM = '2023-12-31'

# Lista de ações disponíveis
acoes_disponiveis = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX', 'FB', 'NVDA']

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Desempenho do Investimento"),

    html.Label("Selecione um Ativo:"),
    dcc.Dropdown(
        id='dropdown-ativo',
        options=[{'label': acao, 'value': acao} for acao in acoes_disponiveis],
        value='AAPL',  # Valor padrão
        multi=False  # Permite apenas uma seleção
    ),

    html.Button('Atualizar Gráficos', id='botao-atualizar', n_clicks=0),

    html.Div(id='div-graficos',
             style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between'}),

    html.Div(id='div-lucro-perda', style={'width': '100%'})
])


# Callback para atualizar os gráficos com base no ativo selecionado
@app.callback(
    [Output('div-graficos', 'children'),
     Output('div-lucro-perda', 'children')],
    [Input('botao-atualizar', 'n_clicks')],
    [Input('dropdown-ativo', 'value')]
)
def update_dashboard(n_clicks, ativo_selecionado):
    if n_clicks == 0:
        return [], []

    # Baixando dados do ativo selecionado usando yfinance
    df = yf.download(ativo_selecionado, start=DATA_INICIO, end=DATA_FIM)

    # Verificando se o DataFrame está vazio
    if df.empty:
        return [], [html.Div("Nenhum dado encontrado para este ativo.")]

    # Gráfico de Candle
    candlestick = dcc.Graph(
        id='grafico-candlestick',
        figure={
            'data': [
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Candle'
                )
            ],
            'layout': go.Layout(
                title=f'Gráfico de Candle para {ativo_selecionado}',
                xaxis={'title': 'Data'},
                yaxis={'title': 'Preço'},
                hovermode='closest'
            )
        }
    )

    # Gráfico da evolução da banca (simulando com dados aleatórios)
    evolucao_banca = dcc.Graph(
        id='grafico-banca',
        figure={
            'data': [
                go.Scatter(
                    x=df.index,
                    y=(df['Close'] * 1.05).tolist(),  # Simulando a banca como 5% acima do preço de fechamento
                    mode='lines+markers',
                    name='Banca (R$)',
                    marker=dict(color='blue')
                )
            ],
            'layout': go.Layout(
                title=f'Evolução da Banca para {ativo_selecionado}',
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

    # Gráfico de Lucro/Perda (simulando com dados aleatórios)
    lucro_perda = dcc.Graph(
        id='grafico-lucro-perda',
        figure={
            'data': [
                go.Bar(
                    x=list(range(len(df))),
                    y=(df['Close'].diff().dropna()).tolist(),  # Lucro/Perda baseado na variação do preço de fechamento
                    name='Lucro/Perda por Venda',
                    marker=dict(color='red')
                )
            ],
            'layout': go.Layout(
                title=f'Lucro/Perda para {ativo_selecionado}',
                xaxis={'title': 'Operações'},
                yaxis={'title': 'Lucro/Perda (R$)'},
                hovermode='closest'
            )
        }
    )

    # Resumo Geral
    resumo_geral = [
        html.Div([
            html.H3("Banca Inicial", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].iloc[0]:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Banca Final", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].iloc[-1]:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Lucro/Perda Total", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].diff().sum():.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Número Total de Operações", style={'textAlign': 'center'}),
            html.P(str(len(df) - 1), style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'})
    ]

    # Adicionando o gráfico de lucro/perda na parte inferior
    div_lucro_perda = html.Div([
        lucro_perda,
        html.Div(resumo_geral, style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})
    ])

    # Adicionando mais três blocos de resumo
    resumo_adicional = [
        html.Div([
            html.H3("Banca Inicial", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].iloc[0]:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Banca Final", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].iloc[-1]:.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Lucro/Perda Total", style={'textAlign': 'center'}),
            html.P(f"R$ {df['Close'].diff().sum():.2f}", style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'}),

        html.Div([
            html.H3("Número Total de Operações", style={'textAlign': 'center'}),
            html.P(str(len(df) - 1), style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'flex': '1'})
    ]

    # Combinando os dois resumos
    div_resumos = html.Div(resumo_geral + resumo_adicional,
                           style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})

    return div_graficos, html.Div([div_lucro_perda, div_resumos])


# Executando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
