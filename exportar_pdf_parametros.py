# exportar_pdf_parametros.py
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Carrega o relatório CSV mais recente
csv_path = sorted([f for f in os.listdir('.') if f.startswith("relatorio_parametros_") and f.endswith(".csv")])[-1]
df = pd.read_csv(csv_path)

# Inicializa PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Relatório de Estratégias por Ativo", ln=True, align='C')
pdf.ln(10)

# Cabeçalho
colunas = ["Ativo", "Modelo", "Sharpe", "Retorno (%)", "Alocação (R$)", "RSI", "MACD", "Stoch (K,D)", "K/D thresholds", "Sugestão"]
larguras = [20, 25, 20, 25, 30, 15, 30, 25, 25, 60]

for col, w in zip(colunas, larguras):
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(w, 10, col, border=1)
pdf.ln()

# Dados
for _, row in df.iterrows():
    for col, w in zip(colunas, larguras):
        texto = str(row[col])[:30] if isinstance(row[col], str) else f"{row[col]}"
        pdf.set_font("Arial", '', 9)
        pdf.cell(w, 10, texto, border=1)
    pdf.ln()

# Salvar
nome_arquivo = f"relatorio_parametros_{datetime.now().strftime('%Y%m%d')}.pdf"
pdf.output(nome_arquivo)
print(f"Relatório PDF salvo como {nome_arquivo}")
