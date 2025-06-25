# signal_generator.py
# Este módulo converte os sinais gerados para um formato JSON padronizado e salva em disco.

import json


def salvar_sinais_json(lista_sinais, caminho):
    """
    Salva os sinais gerados (técnicos ou ML) em um arquivo JSON formatado para envio ou visualização.

    Parâmetros:
    - lista_sinais: lista de dicionários com os dados dos melhores modelos por ativo.
        Cada item deve conter:
            - 'ticker': ativo analisado
            - 'sinais': lista de sinais com 'data', 'tipo' e 'preco'
            - 'tipo': modelo utilizado ('tecnica' ou 'ml')
            - 'params': parâmetros utilizados
            - 'resultado': métricas como sharpe e retorno
            - 'alocacao': valor em R$ alocado no ativo

    - caminho: caminho de saída do arquivo JSON (ex: 'sinais_telegram.json')
    """

    saida = []  # Lista final que conterá todos os sinais no formato plano

    for item in lista_sinais:
        for sinal in item['sinais']:
            saida.append({
                'ativo': item['ticker'],  # Código do ativo (ex: PETR4.SA)
                'data': str(sinal['data']),  # Data do sinal (convertida para string)
                'tipo': sinal['tipo'],  # Tipo de sinal: 'compra' ou 'venda'
                'preco': round(float(sinal['preco']), 2),  # Preço do ativo arredondado
                'modelo': item['tipo'],  # Origem do modelo: 'tecnica' ou 'ml'
                'params': item['params'],  # Parâmetros usados para gerar esse sinal
                'sharpe': round(item['resultado']['sharpe'], 2),  # Índice de Sharpe da estratégia
                'retorno': round(item['resultado']['retorno_pct'], 2),  # Retorno percentual da estratégia
                'alocacao': item['alocacao']  # Valor alocado no ativo
            })

    # Salva a lista no formato JSON, com indentação e suporte a acentos (UTF-8)
    with open(caminho, 'w') as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)
