import re
import unicodedata
import random
from dataclasses import dataclass
from typing import List, Optional, Dict

# ==========================================================
# 0. UTILITÁRIOS DE TEXTO
# ==========================================================
def normalizar(texto: str) -> str:
    if not texto: return ""
    texto = unicodedata.normalize("NFKD", texto.lower().strip())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto.replace("-", " ")).strip()

# ==========================================================
# 1. RÓTULOS E CONJUNTOS FUZZY TRAPEZOIDAIS
# ==========================================================
LABELS_COMP = ["Baixo", "Médio", "Alto"]
LABELS_CUSTO = ["Barato", "Médio", "Caro"]
LABELS_JOGOS = ["Poucos", "Médio", "Muitos"]
LABELS_NOTA = ["Baixa", "Média", "Alta"]
LABELS_IDADE = ["Promessa", "Consolidado", "Experiente", "Veterano"]
LABELS_SAIDA = ["Não contratar", "Observar", "Contratar"]

@dataclass
class FuncaoPertinencia:
    nome: str
    a: float
    b: float
    c: float
    d: float

    def calcular_pertinencia(self, x: float) -> float:
        if x < self.a or x > self.d: return 0.0
        if self.b <= x <= self.c: return 1.0
        if x < self.b: return (x - self.a) / (self.b - self.a)
        if self.d == self.c: return 1.0
        return (self.d - x) / (self.d - self.c)

# Universos de Discurso
COMPROMETIMENTO = [
    FuncaoPertinencia("Baixo", 0.0, 0.0, 20.0, 40.0),
    FuncaoPertinencia("Médio", 20.0, 40.0, 60.0, 80.0),
    FuncaoPertinencia("Alto", 60.0, 80.0, 100.0, 100.0),
]
CUSTO = [
    FuncaoPertinencia("Barato", 0.0, 0.0, 20.0, 40.0),
    FuncaoPertinencia("Médio", 20.0, 40.0, 60.0, 80.0),
    FuncaoPertinencia("Caro", 60.0, 80.0, 100.0, 100.0),
]
JOGOS = [
    FuncaoPertinencia("Poucos", 0.0, 0.0, 10.0, 20.0),
    FuncaoPertinencia("Médio", 10.0, 20.0, 30.0, 40.0),
    FuncaoPertinencia("Muitos", 30.0, 40.0, 50.0, 50.0),
]
NOTA = [
    FuncaoPertinencia("Baixa", 0.0, 0.0, 3.0, 5.0),
    FuncaoPertinencia("Média", 3.0, 5.0, 6.0, 8.0),
    FuncaoPertinencia("Alta", 6.0, 8.0, 10.0, 10.0),
]
# Idade: 16-22 Promessa | 23-29 Consolidado | 30-34 Experiente | 35+ Veterano
IDADE = [
    FuncaoPertinencia("Promessa", 16.0, 16.0, 20.0, 23.0),
    FuncaoPertinencia("Consolidado", 20.0, 23.0, 28.0, 31.0),
    FuncaoPertinencia("Experiente", 28.0, 30.0, 34.0, 36.0),
    FuncaoPertinencia("Veterano", 33.0, 35.0, 42.0, 42.0),
]
OUT_RECOMENDACAO = [
    FuncaoPertinencia("Não contratar", 0.0, 0.0, 20.0, 40.0),
    FuncaoPertinencia("Observar", 30.0, 45.0, 55.0, 70.0),
    FuncaoPertinencia("Contratar", 60.0, 80.0, 100.0, 100.0),
]

# ==========================================================
# 2. GERAÇÃO PROGRAMÁTICA DAS REGRAS (3x3x3x3x4 = 324 combinações)
# ==========================================================
def inicializar_matriz_regras() -> List:
    # Dimensões: [comprometimento][custo][jogos][nota][idade]
    matriz = [[[[[0] * 4 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]

    BONUS_IDADE = [0.5, 1.0, 0.0, -1.0]

    for comp in range(3):
        for cust in range(3):
            for jg in range(3):
                for nt in range(3):
                    for idd in range(4):
                        score_est = (nt * 2.0) + (jg * 1.0) - (cust * 1.5) - (comp * 1.0)
                        score_est += BONUS_IDADE[idd]

                        consequente = 1
                        if score_est >= 2.5: consequente = 2
                        elif score_est < 0.0: consequente = 0

                        if nt == 0: consequente = 0  # Nota baixa = Não contrata
                        if cust == 2 and nt < 2: consequente = 0  # Caro sem nota alta = Não contrata
                        if comp == 2: consequente = 0  # Quebra o orçamento do clube = Não contrata
                        if idd == 3 and cust == 2: consequente = 0  # Veterano + caro = risco alto, não contrata
                        if nt == 2 and cust == 0 and comp == 0 and idd in (0, 1):
                            consequente = 2  # Bom, barato e jovem/em pico = Contrata

                        matriz[comp][cust][jg][nt][idd] = consequente
    return matriz

MATRIZ_REGRAS = inicializar_matriz_regras()

# ==========================================================
# 3. ENTIDADES
# ==========================================================
@dataclass
class Clube:
    orcamento: float

@dataclass
class Jogador:
    nome: str
    valor_mercado: float
    numero_jogos: float
    nota_media: float
    idade: float
    score_final: float = 0.0
    recomendacao_perfil: str = ""
    termo_comprometimento: str = ""
    termo_idade: str = ""
    perc_comprometimento: float = 0.0

    def _termo_max(self, funcoes, labels, valor) -> str:
        melhor_u, melhor_i = -1.0, 0
        for i, f in enumerate(funcoes):
            u = f.calcular_pertinencia(valor)
            if u > melhor_u: melhor_u, melhor_i = u, i
        return labels[melhor_i]

    def t_nota(self) -> str: return self._termo_max(NOTA, LABELS_NOTA, self.nota_media)
    def t_jogos(self) -> str: return self._termo_max(JOGOS, LABELS_JOGOS, self.numero_jogos)
    def t_custo(self) -> str: return self._termo_max(CUSTO, LABELS_CUSTO, self.valor_mercado)
    def t_idade(self) -> str: return self._termo_max(IDADE, LABELS_IDADE, self.idade)

# ==========================================================
# 4. MOTOR DE INFERÊNCIA MAMDANI
# ==========================================================
def avaliar_jogador_mamdani(j: Jogador, c: Clube) -> None:
    # Calcula o impacto do jogador no orçamento do clube (Trava em 100% no máximo)
    j.perc_comprometimento = min(100.0, (j.valor_mercado / c.orcamento) * 100.0)

    u_comp = [f.calcular_pertinencia(j.perc_comprometimento) for f in COMPROMETIMENTO]
    u_custo = [f.calcular_pertinencia(j.valor_mercado) for f in CUSTO]
    u_jogos = [f.calcular_pertinencia(j.numero_jogos) for f in JOGOS]
    u_nota = [f.calcular_pertinencia(j.nota_media) for f in NOTA]
    u_idade = [f.calcular_pertinencia(j.idade) for f in IDADE]

    atv_saida = [0.0, 0.0, 0.0]

    for comp in range(3):
        if u_comp[comp] == 0: continue
        for cust in range(3):
            if u_custo[cust] == 0: continue
            for jg in range(3):
                if u_jogos[jg] == 0: continue
                for nt in range(3):
                    if u_nota[nt] == 0: continue
                    for idd in range(4):
                        if u_idade[idd] == 0: continue

                        ativacao = min(u_comp[comp], u_custo[cust], u_jogos[jg], u_nota[nt], u_idade[idd])
                        if ativacao > 0:
                            consequente = MATRIZ_REGRAS[comp][cust][jg][nt][idd]
                            atv_saida[consequente] = max(atv_saida[consequente], ativacao)

    soma_num, soma_den = 0.0, 0.0
    for z in range(0, 101):
        mu_agregado = max([min(atv_saida[i], OUT_RECOMENDACAO[i].calcular_pertinencia(z)) for i in range(3)])
        soma_num += mu_agregado * z
        soma_den += mu_agregado

    j.score_final = 50.0 if soma_den == 0 else (soma_num / soma_den)

    melhor_u, melhor_i = -1.0, 0
    for i, u in enumerate(u_comp):
        if u > melhor_u: melhor_u, melhor_i = u, i
    j.termo_comprometimento = LABELS_COMP[melhor_i]

    melhor_u, melhor_i = -1.0, 0
    for i, u in enumerate(u_idade):
        if u > melhor_u: melhor_u, melhor_i = u, i
    j.termo_idade = LABELS_IDADE[melhor_i]

    if j.score_final <= 40.0: j.recomendacao_perfil = LABELS_SAIDA[0]
    elif j.score_final <= 70.0: j.recomendacao_perfil = LABELS_SAIDA[1]
    else: j.recomendacao_perfil = LABELS_SAIDA[2]

# ==========================================================
# 5. GERADOR DO BANCO DE 100 JOGADORES (Dados Realistas)
# ==========================================================
def gerar_banco_100_jogadores() -> List[Jogador]:
    elite = ["Lionel Messi", "Kylian Mbappé", "Erling Haaland", "Vinícius Júnior", "Jude Bellingham", "Kevin De Bruyne", "Rodri", "Harry Kane", "Bukayo Saka", "Phil Foden", "Lamine Yamal", "Florian Wirtz", "Jamal Musiala", "Declan Rice", "Martin Ødegaard", "Robert Lewandowski", "Mohamed Salah", "Antoine Griezmann", "Lautaro Martínez", "Victor Osimhen", "Alisson Becker", "Thibaut Courtois", "Rúben Dias", "Virgil van Dijk", "Trent Alexander-Arnold"]
    medios = ["Achraf Hakimi", "Alphonso Davies", "Pedri", "Gavi", "Rafael Leão", "Khvicha Kvaratskhelia", "Son Heung-min", "Neymar Jr", "Bruno Fernandes", "Marcus Rashford", "Gabriel Martinelli", "Luis Díaz", "Darwin Núñez", "Julián Álvarez", "Enzo Fernández", "Alexis Mac Allister", "Emiliano Martínez", "Ronald Araújo", "Marquinhos", "Eder Militão", "Federico Valverde", "Eduardo Camavinga", "Aurélien Tchouaméni", "Toni Kroos", "Luka Modrić", "Joshua Kimmich", "Leroy Sané", "Serge Gnabry", "Kingsley Coman", "Ousmane Dembélé", "Raphinha", "Frenkie de Jong", "Matthijs de Ligt", "Xavi Simons", "Jeremie Frimpong", "Alejandro Grimaldo", "Granit Xhaka", "Ollie Watkins", "Alexander Isak", "Bruno Guimarães", "Lucas Paquetá", "Douglas Luiz", "Gabriel Magalhães", "William Saliba", "John Stones", "Kyle Walker", "Rodrygo", "João Félix", "João Cancelo", "Diogo Jota"]
    baratos = ["Endrick", "Vitor Roque", "Cristiano Biraghi", "Federico Chiesa", "Nicolò Barella", "Alessandro Bastoni", "Hakan Çalhanoğlu", "Marcus Thuram", "Dusan Vlahovic", "Milan Škriniar", "Gianluigi Donnarumma", "Mike Maignan", "Theo Hernández", "Fikayo Tomori", "Christian Pulisic", "Weston McKennie", "Alvaro Morata", "Dani Carvajal", "Alejandro Garnacho", "Kobbie Mainoo", "Cole Palmer", "Arda Güler", "Pau Cubarsí", "Rico Lewis", "Warren Zaïre-Emery"]

    elenco = []
    random.seed(42)  # Seed fixa para manter os mesmos valores em testes

    for nome in elite:
        custo = round(random.uniform(70.0, 100.0), 1)
        jogos = round(random.uniform(35, 50))
        nota = round(random.uniform(7.5, 10.0), 1)
        idade = round(random.uniform(21, 37))
        elenco.append(Jogador(nome, custo, jogos, nota, idade))

    for nome in medios:
        custo = round(random.uniform(30.0, 69.9), 1)
        jogos = round(random.uniform(20, 45))
        nota = round(random.uniform(5.0, 7.9), 1)
        idade = round(random.uniform(19, 36))
        elenco.append(Jogador(nome, custo, jogos, nota, idade))

    for nome in baratos:
        custo = round(random.uniform(2.0, 29.9), 1)
        jogos = round(random.uniform(5, 30))
        nota = round(random.uniform(3.0, 7.0), 1)
        idade = round(random.uniform(17, 29))
        elenco.append(Jogador(nome, custo, jogos, nota, idade))

    return elenco

# ==========================================================
# 6. GRÁFICOS (matplotlib)
# ==========================================================
def exibir_graficos(jogador_destaque: Jogador):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[Aviso] As bibliotecas 'matplotlib' e 'numpy' são necessárias para ver os gráficos.")
        print("Instale-as executando: pip install matplotlib numpy")
        return

    valores_jogador = {
        "Comprometimento Orçamentário (%)": jogador_destaque.perc_comprometimento,
        "Custo Absoluto (€ Milhões)": jogador_destaque.valor_mercado,
        "Volume de Jogos (Partidas)": jogador_destaque.numero_jogos,
        "Nota Média Técnica (0-10)": jogador_destaque.nota_media,
        "Idade do Jogador (anos)": jogador_destaque.idade,
        "Saída: Recomendação Final (Pontos)": jogador_destaque.score_final
    }

    conjuntos = [
        ("Comprometimento Orçamentário (%)", COMPROMETIMENTO, 100.0),
        ("Custo Absoluto (€ Milhões)", CUSTO, 100.0),
        ("Volume de Jogos (Partidas)", JOGOS, 50.0),
        ("Nota Média Técnica (0-10)", NOTA, 10.0),
        ("Idade do Jogador (anos)", IDADE, 42.0),
        ("Saída: Recomendação Final (Pontos)", OUT_RECOMENDACAO, 100.0),
    ]

    fig, eixos = plt.subplots(2, 3, figsize=(15, 8))
    eixos = eixos.flatten()

    for i, (titulo, funcoes, x_max) in enumerate(conjuntos):
        ax = eixos[i]
        xs = np.linspace(0, x_max, 400)

        for f in funcoes:
            ys = [f.calcular_pertinencia(x) for x in xs]
            ax.plot(xs, ys, label=f.nome)

        # Plota a linha e o X no gráfico do jogador
        x_val = valores_jogador[titulo]
        y_val = max([f.calcular_pertinencia(x_val) for f in funcoes])

        ax.axvline(x=x_val, color='red', linestyle='--', alpha=0.6, label=f'{jogador_destaque.nome}')
        ax.scatter(x_val, y_val, color='red', marker='X', s=120, zorder=5)

        ax.set_title(titulo, fontsize=10)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)

    fig.tight_layout()
    plt.show()

# ==========================================================
# 7. MENU INTERATIVO PRINCIPAL
# ==========================================================
def main():
    print("=" * 70)
    print(" SISTEMA FUZZY DE SCOUTING (COM CÁLCULO DE ORÇAMENTO E IDADE)")
    print("=" * 70)

    try:
        orcamento = float(input("💰 Digite o orçamento total do seu Clube (€ Milhões): "))
    except ValueError:
        print("Valor inválido. Usando orçamento padrão de 150.0 Milhões.")
        orcamento = 150.0

    clube_comprador = Clube(orcamento)

    print("\n⏳ Carregando banco de dados de 100 jogadores...")
    elenco = gerar_banco_100_jogadores()

    # Avalia todos os jogadores com base no orçamento inserido
    for j in elenco:
        avaliar_jogador_mamdani(j, clube_comprador)

    print(f"✅ Jogadores avaliados com base no orçamento de {orcamento}M.")

    while True:
        print("\n" + "-"*40)
        print("MENU PRINCIPAL:")
        print("1 - Listar todos os jogadores (Resumo)")
        print("2 - Buscar Jogador por Nome e Gerar Gráfico Fuzzy")
        print("3 - Alterar orçamento do Clube")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            # Ordena por score final decrescente para mostrar os mais recomendados primeiro
            elenco_ordenado = sorted(elenco, key=lambda x: x.score_final, reverse=True)
            print(f"\nLista de Jogadores (Orçamento do Clube: {clube_comprador.orcamento}M)")
            for j in elenco_ordenado:
                print(f"{j.nome:20} | Idade: {j.idade:4.0f} ({j.termo_idade:11}) | Nota: {j.nota_media:4.1f} | "
                      f"Custo: {j.valor_mercado:4.1f}M | "
                      f"Comprometimento: {j.perc_comprometimento:5.1f}% ({j.termo_comprometimento:5}) -> {j.recomendacao_perfil}")

        elif opcao == "2":
            busca = normalizar(input("\nDigite o nome (ou parte do nome) do jogador: "))
            encontrados = [j for j in elenco if busca in normalizar(j.nome)]

            if not encontrados:
                print("❌ Jogador não encontrado no banco de dados.")
            else:
                alvo = encontrados[0]
                print(f"\n✅ Gerando Gráficos e Coordenadas para: {alvo.nome}")
                print(f"Idade: {alvo.idade:.0f} ({alvo.termo_idade}) | Custo: {alvo.valor_mercado}M | "
                      f"Jogos: {alvo.numero_jogos} | Nota: {alvo.nota_media}")
                print(f"Impacto no Orçamento do Clube: {alvo.perc_comprometimento:.1f}% ({alvo.termo_comprometimento})")
                print(f"Score Final: {alvo.score_final:.2f} -> {alvo.recomendacao_perfil}")
                exibir_graficos(alvo)

        elif opcao == "3":
            try:
                novo_orc = float(input("\n💰 Novo orçamento do Clube (€ Milhões): "))
                clube_comprador.orcamento = novo_orc
                # Reavalia todo o elenco com o novo orçamento
                for j in elenco:
                    avaliar_jogador_mamdani(j, clube_comprador)
                print(f"✅ Orçamento atualizado para {novo_orc}M e elenco reavaliado!")
            except ValueError:
                print("Valor inválido.")

        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()