from fundamentalist import webscraping, fundamentalist_filters
from technical_analysis import metodos
import pandas as pd

# Ja fez o webscraping?
webscrapin = True
df_full = webscraping(webscrapin)

use_defaults = input("Deseja usar os valores padrão fundamentalistas? (s/n): ").strip().lower() == 's'
df = fundamentalist_filters(df_full, use_defaults)
acao = df['Ativo']
'''
use_stochastic = input("Deseja usar o indicador estocastico lento? (s/n): ").strip().lower() == 's'
if use_stochastic == 's':
    use_stochastic = True
else:
    use_stochastic = False
use_atr = input("Deseja usar o indicador atr? (s/n): ").strip().lower() == 's'
if use_atr == 's':
    use_atr = True
else:
    use_atr = False
'''
use_stochastic = 's'
use_atr = 's'
for name in acao:
    banca_inicial = 1000
    novo_dado = metodos(name, banca_inicial, use_stochastic=use_stochastic, use_atr=use_atr)
    # Acrescente o dicionário na lista
    # dados.append(novo_dado)

df = pd.DataFrame(dados)
# Salvar DataFrame como JSON
df.to_json('dados_ativos.json', orient='records', lines=True)