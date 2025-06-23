# signal_generator.py
import json

def salvar_sinais_json(lista_sinais, caminho):
    saida = []
    for item in lista_sinais:
        for sinal in item['sinais']:
            saida.append({
                'ativo': item['ticker'],
                'data': str(sinal['data']),
                'tipo': sinal['tipo'],
                'preco': round(float(sinal['preco']), 2),
                'modelo': item['tipo'],
                'params': item['params'],
                'sharpe': round(item['resultado']['sharpe'], 2),
                'retorno': round(item['resultado']['retorno_pct'], 2),
                'alocacao': item['alocacao']
            })
    with open(caminho, 'w') as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)