import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
#from yahoo_fin import stock_info as si


def get_stock_fundamentals(stock_code):
    url = f'https://statusinvest.com.br/acoes/{stock_code}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'Error fetching data for {stock_code}')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    first = soup.find_all('div', class_='w-50 w-sm-33 w-md-25 w-lg-16_6 mb-2 mt-2 item')
    second = soup.find_all('div', class_='w-50 w-sm-33 w-md-25 w-lg-50 mb-2 mt-2 item')
    thirst = soup.find_all('div', class_='card rounded text-main-green-dark')
    data_cont = []

    # Função auxiliar para processar os valores encontrados
    def process_value(dado, regex_pattern):
        valor = dado.text
        match = re.search(regex_pattern, valor)
        if match:
            first_valor = match.group(1).strip().replace('.', '').replace(',', '.')
            return float(first_valor)  # Converte para float
        return None

    # Processar valores das seções capturadas
    for dado in first:
        data_cont.append(process_value(dado, r'\n\n(-?\d+,\d+)'))
    for dado in second:
        data_cont.append(process_value(dado, r'\n\n(-?\d+,\d+)'))
    for dado in thirst:
        data_cont.append(process_value(dado, r'R\$\s*([\d{1,3}\.]*\d+,\d{2})'))

    return data_cont


def data_name_ticker_b2():
    url = f'https://www.dadosdemercado.com.br/acoes'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'Error fetching data for DADOS DE MERCADO')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    datas = soup.find_all('strong')

    # Regex para extrair os nomes das ações
    regex = r">([A-Z0-9]+)<"

    # Lista para armazenar os nomes das ações
    nomes_acoes = []

    # Iterar sobre as tags encontradas
    for tag in datas:
        tag_str = str(tag)  # Converter o objeto 'Tag' para string
        match = re.search(regex, tag_str)
        if match:
            nomes_acoes.append(match.group(1))
    return nomes_acoes

def webscraping(webscraping):
    if not webscraping:
        acoes = data_name_ticker_b2()
        dados_acoes = []

        # Loop para buscar dados de cada ação e salvar no formato adequado
        for acao in acoes:
            valores = get_stock_fundamentals(acao)
            if valores:
                dados_acoes.append([acao] + valores)

        df = pd.DataFrame(dados_acoes, columns=['Ativo', 'D.Y', 'P/L', 'PEG RATIO', 'P/VP', 'EV/EBITDA', 'EV/EBIT', 'P/EBITDA',
                                                'P/EBIT', 'VPA', 'P/ATIVO', 'LPA', 'P/SR', 'P/CAP. GIRO', 'P/ATIVO CIRC. LIQ.',
                                                'DIV. LIQUIDA/PL', 'DIV. LIQUIDA/EBITDA', 'DIV. LIQUIDA/EBIT', 'PL/ATIVOS',
                                                'PASSIVOS/ATIVOS', 'LIQ. CORRENTE', 'M. BRUTA', 'M. EBITDA', 'M. EBIT',
                                                'M. LIQUIDA', 'ROE', 'ROA', 'ROIC', 'GIRO ATIVOS', 'CAGR RECEITA 5 ANOS',
                                                'CAGR LUCRO 5 ANOS', 'LIQUIDEZ DIA'])
        # Salvar o DataFrame em um arquivo Excel
        df.to_excel('dados_acoes.xlsx', index=False)
    else:
        df = pd.read_excel('dados_acoes.xlsx')
    return df


def process_data(data):
    fill_values = {
        'D.Y': 0,
        'P/L': -0.1,
        'PEG RATIO': 0,
        'P/VP': 0,
        'EV/EBITDA': 0,
        'EV/EBIT': 0,
        'P/EBITDA': 0,
        'P/EBIT': 0,
        'VPA': 0,
        'P/ATIVO': 0,
        'LPA': 0,
        'P/SR': 0,
        'P/CAP. GIRO': 0,
        'P/ATIVO CIRC. LIQ.': 0,
        'DIV. LIQUIDA/PL': 0,
        'DIV. LIQUIDA/EBITDA': 0,
        'DIV. LIQUIDA/EBIT': 0,
        'PL/ATIVOS': 0,
        'PASSIVOS/ATIVOS': 0,
        'LIQ. CORRENTE': 0,
        'M. BRUTA': 0,
        'M. EBITDA': 0,
        'M. EBIT': 0,
        'M. LIQUIDA': 0,
        'ROE': 0,
        'ROA': 0,
        'ROIC': 0,
        'GIRO ATIVOS': 0,
        'CAGR RECEITA 5 ANOS': 0,
        'CAGR LUCRO 5 ANOS': 0,
        'LIQUIDEZ DIA': 0
    }
    for col, value in fill_values.items():
        data[col] = data[col].fillna(value)
    return data


def get_input_with_default(prompt, default_value):
    """Função para obter entrada do usuário com valor padrão."""
    user_input = input(prompt)
    if user_input.strip() == "":
        return default_value
    return float(user_input)


def filter_dataframe(df, use_defaults=True):
    """Função para aplicar filtros ao DataFrame com ou sem a opção de valores padrão."""

    if not use_defaults:
        # Pergunta ao usuário os valores para as métricas
        liq_corrente_min = get_input_with_default("Informe o valor mínimo para 'LIQ. CORRENTE' (padrão 1.2): ", 1.2)
        liquidez_dia_min = get_input_with_default("Informe o valor mínimo para 'LIQUIDEZ DIA' (padrão 1E6): ", 1E6)
        pl_min = get_input_with_default("Informe o valor mínimo para 'P/L' (padrão 0): ", 0)
        pl_max = get_input_with_default("Informe o valor máximo para 'P/L' (padrão 15): ", 15)
        p_vp_min = get_input_with_default("Informe o valor mínimo para 'P/VP' (padrão 0): ", 0)
        p_vp_max = get_input_with_default("Informe o valor máximo para 'P/VP' (padrão 1.5): ", 1.5)
        div_liquida_pl_max = get_input_with_default("Informe o valor máximo para 'DIV. LIQUIDA/PL' (padrão 2): ", 2)
        cagr_lucro_min = get_input_with_default("Informe o valor mínimo para 'CAGR LUCRO 5 ANOS' (padrão 2): ", 2)
        cagr_receita_min = get_input_with_default("Informe o valor mínimo para 'CAGR RECEITA 5 ANOS' (padrão 2): ",
                                                  2)
        roe_min = get_input_with_default("Informe o valor mínimo para 'ROE' (padrão 2): ", 2)
    else:
        # Valores padrão sem perguntar ao usuário
        liq_corrente_min = 1.2
        liquidez_dia_min = 1E6
        pl_min = 0
        pl_max = 15
        p_vp_min = 0
        p_vp_max = 1.5
        div_liquida_pl_max = 2
        cagr_lucro_min = 2
        cagr_receita_min = 2
        roe_min = 2

    # Aplicando os filtros ao DataFrame
    df_filtered = df[df['LIQ. CORRENTE'] > liq_corrente_min]
    df_filtered = df_filtered[df_filtered['LIQUIDEZ DIA'] > liquidez_dia_min]
    df_filtered = df_filtered[(df_filtered['P/L'] >= pl_min) & (df_filtered['P/L'] <= pl_max)]
    df_filtered = df_filtered[(df_filtered['P/VP'] >= p_vp_min) & (df_filtered['P/VP'] <= p_vp_max)]
    df_filtered = df_filtered[df_filtered['DIV. LIQUIDA/PL'] <= div_liquida_pl_max]
    df_filtered = df_filtered[df_filtered['CAGR LUCRO 5 ANOS'] >= cagr_lucro_min]
    df_filtered = df_filtered[df_filtered['CAGR RECEITA 5 ANOS'] >= cagr_receita_min]
    df_filtered = df_filtered[df_filtered['ROE'] >= roe_min]

    return df_filtered


def fundamentalist_filters(data, use_defaults):
    df_acao = process_data(data)
    df2 = filter_dataframe(df_acao, use_defaults)

    return df2
