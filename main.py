from fundamentalist import webscraping, fundamentalist_filters

# Ja fez o webscraping?
webscrapin = True
df_full = webscraping(webscrapin)

use_defaults = input("Deseja usar os valores padrão fundamentalistas? (s/n): ").strip().lower() == 's'
df = fundamentalist_filters(df_full, use_defaults)
print(df)

x=1
