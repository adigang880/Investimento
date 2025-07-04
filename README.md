# 🧠 Investimentos

Este projeto tem como objetivo desenvolver um sistema automatizado (bot) para identificar oportunidades 
de compra e venda de ativos financeiros na Bolsa de Valores brasileira, com foco em atingir um rendimento 
anual superior a 25%. O sistema será responsável por gerar sinais de entrada e saída, gerenciar o capital 
alocado e informar, via Telegram, quanto investir ou resgatar em cada operação, com base em uma estratégia 
quantitativa.
---
## 🎯 Objetivo
```bash
Criar um robô de investimentos que:

Monitore ativos de renda fixa e variável;

Gere sinais baseados em algoritmos com alta probabilidade de sucesso;

Faça gestão ativa do capital inicial de R$ 10.000,00;

Alcance rentabilidade superior a 25% ao ano com controle de risco.
```
---

## 🔬 Metodologia
```bash
# Seleção dos Ativos:

Renda Variável: Ações, ETFs e FIIs.

Renda Fixa: CDB, LCI, LCA, CRI, CRA, Tesouro Direto, todos operados por marcação a mercado.

# Critérios de Operação:

Renda Variável: Swing trade com permanência mínima de 2 dias.

Renda Fixa: Compra e venda antes do vencimento visando lucros na oscilação dos preços.

# Algoritmos e Estratégias:

Serão aplicados modelos quantitativos para identificar padrões de entrada e saída com alta probabilidade estatística de ganho.

Ajustes periódicos serão feitos com base no histórico de performance.

# Gestão do Capital:

O sistema calculará automaticamente a alocação ideal por operação.

Será enviada uma notificação via Telegram com o valor exato a investir ou resgatar.

# Análise de Resultados:

Todas as operações serão registradas em planilhas.

Haverá análise contínua para otimização das estratégias.

# Marketing e Educação:

Criação de conteúdos para redes sociais (Instagram e TikTok) explicando:

Por que o ativo foi selecionado.

Qual critério técnico foi utilizado.

O racional por trás da operação.
```
---

## 📈 Resultados Esperados
```bash
Rentabilidade média anual superior a 25%.

Sistema automatizado e escalável.

Engajamento do público com conteúdo educativo.

Gestão de risco ativa e capital sempre alocado de forma estratégica.
```
---

## 📁 Web Scraping e Filtros Fundamentalistas:
```bash
fundamentalist.py realiza a coleta de dados de sites como statusinvest e aplica filtros baseados 
em indicadores, como liquidez e P/L.
A função webscraping obtém os dados das ações (linhas 69‑90) e filter_dataframe aplica os critérios 
de seleção (linhas 140‑178).

```
---

## 📁 Cálculo de Indicadores Técnicos:
```bash
technical_analysis.py define funções para volatilidade, ATR, MACD, RSI, Estocástico e Volume, 
entre outros (linhas 23‑92).
```
---

## 📁 Estratégia de Trading:
```bash
O core da estratégia está em trading_strategy, que gera sinais de compra e venda (linhas 189‑460) 
e calcula lucros, stop‑loss e estatísticas de desempenho.

A função metodos orquestra a análise de cada ticker, baixando dados do Yahoo Finance, aplicando 
os indicadores e retornando um dicionário com os resultados (linhas 463‑556).
```
---

## 📁 Pipeline Principal:
```bash
main.py integra tudo: executa o web scraping, pergunta se o usuário deseja usar valores padrão 
de filtros, define se indicadores como Estocástico ou ATR serão usados, e então processa cada ação 
retornando um JSON com o resumo dos trades (linhas 1‑33).
```
---

## 📁 Dashboard:
```bash
dashboard.py (usando Streamlit) lê o JSON gerado, exibe métricas de cada ativo e plota gráficos 
de candles e evolução da banca.
```
---


## 📁 Etapa 1: Criar seu projeto local

```bash
mkdir meu-projeto
cd meu-projeto

echo "# Meu Projeto" > README.md

echo "__pycache__/
.env
.venv/
*.pyc
*.log
node_modules/
.vscode/
.idea/" > .gitignore

echo "numpy
pandas
matplotlib" > requirements.txt

git init

git add .
git commit -m "commit inicial do projeto"

git remote add origin https://github.com/usuario/nome-do-repo.git
git branch -M main
git push -u origin main
```

---

## ✏️ Etapa 2: Subir alterações futuras

```bash
git add .
git commit -m "mensagem explicando a alteração"
git push
```

---

## 🌿 Etapa 3: Criar e trabalhar com branches

```bash
# Criar nova branch
git checkout -b nome-da-branch

# Voltar para a main
git checkout main

# Subir a nova branch
git push -u origin nome-da-branch
```

---

## 🔀 Etapa 4: Fazer merge da branch na main

```bash
git checkout main
git merge nome-da-branch
git push
```

---

## 💻 Etapa 5: Clonar o projeto em outro computador

```bash
git clone https://github.com/usuario/nome-do-repo.git
cd nome-do-repo

python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

## 🔄 Etapa 6: Puxar atualizações do projeto

```bash
git pull
```

Ou, se estiver em uma branch específica:

```bash
git pull origin nome-da-branch
```

---

## ✅ Pronto!

