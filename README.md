# ⚽ Sistema Fuzzy de Scouting - Apoio à Decisão para Contratação de Jogadores

**Um Modelo de Apoio à Decisão para Contratação de Jogadores de Futebol Baseado em Inferência de Mamdani.**

Este repositório contém o código-fonte de um sistema especialista baseado em Lógica Fuzzy desenvolvido para auxiliar diretorias e equipes de *scouting* de clubes de futebol na avaliação e seleção de reforços. O projeto é fruto de pesquisa acadêmica apresentada no XV CONNEPI (Congresso Norte Nordeste de Pesquisa e Inovação).

---

## 📖 Sobre o Projeto

O *scouting* esportivo envolve decisões financeiras de alto risco em um ambiente de incerteza. Classificar um jogador como "caro" ou "experiente" não possui fronteiras nítidas e varia de clube para clube. 

Para resolver isso, este projeto utiliza **Lógica Fuzzy** (Motor de Inferência de Mamdani) para modelar raciocínios semelhantes aos de olheiros humanos. A principal inovação é a inclusão da variável de **Comprometimento Orçamentário**, que calcula o peso financeiro da contratação com base no orçamento real e atual do clube comprador. Assim, o mesmo jogador (ex: € 20 Milhões) pode ser uma oportunidade imperdível para um clube de elite ou um risco de falência para um clube menor.

## ✨ Funcionalidades

* **Motor de Inferência de Mamdani:** Implementação completa com Fuzzificação, aplicação de regras (operador mínimo), agregação (operador máximo) e Defuzzificação pelo método do Centroide.
* **Avaliação Dinâmica de Orçamento:** O sistema adapta as recomendações com base no orçamento total do clube inserido pelo usuário.
* **Base de Conhecimento Robusta:** 324 regras fuzzy geradas programaticamente que cobrem todas as combinações das cinco variáveis de entrada.
* **Geração de Gráficos:** Visualização das funções de pertinência trapezoidais de cada variável e plotagem das coordenadas de jogadores específicos utilizando `matplotlib`.
* **Banco de Dados Simulado:** Base gerada dinamicamente com 100 jogadores distribuídos em perfis realistas (Elite, Médios/Titulares e Baratos/Promessas).
* **Interface de Linha de Comando (CLI):** Menu interativo amigável para listar, pesquisar jogadores e alterar cenários de orçamento.

## 🧠 Variáveis do Modelo Fuzzy

### Entradas (Fuzzificação)
1.  **Comprometimento Orçamentário (%):** *Baixo, Médio, Alto.* (Calculado pela razão entre custo do atleta e orçamento do clube).
2.  **Custo Absoluto (€ Milhões):** *Barato, Médio, Caro.*
3.  **Volume de Jogos:** *Poucos, Médio, Muitos.*
4.  **Nota Média Técnica (0-10):** *Baixa, Média, Alta.*
5.  **Idade (Anos):** *Promessa (16-22), Consolidado (23-29), Experiente (30-34), Veterano (35+).*

### Saída (Defuzzificação)
* **Recomendação Final:** *Não contratar (0-40 pts), Observar (40-70 pts), Contratar (70-100 pts).*

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Bibliotecas:** * `matplotlib` (Geração de gráficos de pertinência)
  * `numpy` (Cálculos vetoriais e arrays para gráficos)
  * `dataclasses`, `re`, `unicodedata`, `random` (Bibliotecas padrão do Python)

## 🚀 Como Executar o Projeto

1. **Clone este repositório:**
   ```bash
   git clone git@github.com:22346-Andre/SISTEMA-FUZZY-DE-SCOUTING-UM-MODELO-DE-APOIO-DECIS-O-PARA-CONTRATA-O-DE-JOGADORES-DE-FUTEBOL-.git
   cd SISTEMA-FUZZY-DE-SCOUTING-UM-MODELO-DE-APOIO-DECIS-O-PARA-CONTRATA-O-DE-JOGADORES-DE-FUTEBOL-
