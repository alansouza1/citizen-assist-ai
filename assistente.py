"""
assistente.py
Classe Assistente: quem conversa com o cidadão.
Faz o atendimento, guarda o histórico, calcula os indicadores e exporta o CSV.

Projeto: Citizen Assist AI - Global Solution 2026.2 (PCP)
Autor:   Alan Júnior Araújo de Souza - RM 574112
"""

import csv
import json
import os
import re
import time
from datetime import datetime

from base_conhecimento import BaseConhecimento, LIMITE_MEDIA, normalizar

CAMINHO_HISTORICO = os.path.join("data", "historico.json")
CAMINHO_CSV = os.path.join("data", "atendimentos.csv")

# Colunas do CSV (as mesmas chaves de cada atendimento do historico.json)
CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo_segundos",
              "nota_facilidade"]

# 8 ou mais dígitos seguidos, mesmo separados por . - / ( ) ou espaço
# Ex.: 12345678 | 123.456.789-00 | 12.345.678-9 | (11) 91234-5678
PADRAO_DIGITOS = re.compile(r"\d(?:[\s.\-/()]*\d){7,}")

MAX_ALTERNATIVAS = 2


# --------------------------------------------------------------------------
# Funções de leitura do teclado: nunca deixam o programa quebrar
# --------------------------------------------------------------------------
def ler_texto(mensagem):
    """input() protegido: devolve o texto sem espaços nas pontas."""
    return input(mensagem).strip()


def ler_opcao(mensagem, minimo, maximo):
    """Pede um número inteiro entre minimo e maximo até ser válido."""
    while True:
        texto = ler_texto(mensagem)
        if texto == "":
            print("Entrada vazia. Digite um número.")
            continue
        try:
            numero = int(texto)
        except ValueError:
            print(f"'{texto}' não é um número. Digite apenas números.")
            continue
        if numero < minimo or numero > maximo:
            print(f"Opção fora da faixa. Escolha de {minimo} a {maximo}.")
            continue
        return numero


def ler_sim_nao(mensagem):
    """Pergunta s/n até receber uma resposta válida. Devolve True ou False."""
    while True:
        resposta = normalizar(ler_texto(mensagem)).strip()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao"):
            return False
        if resposta == "":
            print("Entrada vazia. Responda com s (sim) ou n (não).")
        else:
            print("Resposta inválida. Responda apenas com s (sim) ou n (não).")


def contem_dados_pessoais(texto):
    """True se o texto tiver 8+ dígitos (CPF, RG, telefone) ou @ (e-mail)."""
    return "@" in texto or PADRAO_DIGITOS.search(texto) is not None


AVISO_DADOS_PESSOAIS = (
    "Atenção: não digite CPF, RG, telefone, e-mail ou outros dados pessoais.\n"
    "Sua mensagem foi recusada e NÃO foi registrada. "
    "Reescreva a dúvida sem dados pessoais."
)


class Assistente:
    """Atende o cidadão usando a base de conhecimento (composição)."""

    def __init__(self, nome, base: BaseConhecimento,
                 caminho_historico=CAMINHO_HISTORICO, caminho_csv=CAMINHO_CSV):
        self.nome = nome
        self.base = base                       # objeto BaseConhecimento
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.atendimentos_sessao = []          # atendimentos feitos nesta execução
        self.historico = self._carregar_historico()

    # ------------------------------------------------------------------
    # Arquivo de histórico
    # ------------------------------------------------------------------
    def _carregar_historico(self):
        """Lê o historico.json. Ausente ou corrompido -> começa vazio."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError):
            backup = self.caminho_historico + ".corrompido"
            try:
                os.replace(self.caminho_historico, backup)
                print(f"Aviso: histórico corrompido. Cópia salva em '{backup}'. "
                      "Um novo histórico será iniciado.")
            except OSError:
                print("Aviso: histórico corrompido. Um novo histórico será iniciado.")
            return []
        except OSError:
            print("Aviso: não foi possível ler o histórico. Começando vazio.")
            return []
        if not isinstance(dados, list):
            print("Aviso: formato do histórico inválido. Começando vazio.")
            return []
        return [item for item in dados if isinstance(item, dict)]

    def _salvar_historico(self):
        """Grava o histórico no JSON sem travar se der erro de disco."""
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=4)
        except OSError:
            print("Aviso: não foi possível salvar o histórico em disco.")

    # ------------------------------------------------------------------
    # Atendimento por pergunta livre
    # ------------------------------------------------------------------
    def _base_disponivel(self):
        if os.path.isfile(self.base.caminho):
            self.base.carregar()
        if not self.base.orientacoes:
            print("\nA base de conhecimento não está disponível no momento.")
            if self.base.erro:
                print(f"Motivo: {self.base.erro}")
            return False
        return True

    def _sugerir(self):
        """Mensagem de 'Não encontrei' com sugestões de palavras e categorias."""
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Dica: use palavras simples, como 'cartão SUS', 'carteira de trabalho',")
        print("'título de eleitor' ou 'tarifa social'.")
        print("Você também pode navegar pelas categorias (opção 2 do menu):")
        for categoria in self.base.categorias():
            print(f"  - {categoria}")

    def _mostrar_resultado(self, resultados):
        """Exibe a melhor orientação e até 2 alternativas.
        Devolve a lista de alternativas exibidas."""
        pontos, melhor = resultados[0]
        nivel = self.base.confianca(pontos)
        print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)")
        melhor.exibir()

        alternativas = [(p, o) for p, o in resultados[1:1 + MAX_ALTERNATIVAS]
                        if p >= LIMITE_MEDIA]
        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for numero, (p, orientacao) in enumerate(alternativas, start=1):
                print(f"  {numero}) {orientacao.titulo} [{orientacao.categoria}] "
                      f"- {p} pontos")
        return alternativas

    def perguntar(self):
        """Atendimento por pergunta em texto livre (usa base.buscar())."""
        if not self._base_disponivel():
            return
        print("\n=== FAZER UMA PERGUNTA ===")
        print("Escreva sua dúvida com suas palavras. Não digite dados pessoais.")

        while True:                                # cada volta = 1 atendimento
            inicio = time.time()
            tentativas = 0
            ultima = None     # (pergunta, id_orientacao, encontrou) da última tentativa
            concluido = False

            while not concluido:
                print()
                texto = ler_texto("Digite sua dúvida (0 para voltar): ")
                if texto == "0":
                    if ultima is not None:         # desistiu no meio: registra
                        self.registrar("pergunta", ultima[0], ultima[1], ultima[2],
                                       False, tentativas, inicio)
                    return
                if texto == "":
                    print("Entrada vazia. Digite sua dúvida ou 0 para voltar.")
                    continue
                if contem_dados_pessoais(texto):
                    print(AVISO_DADOS_PESSOAIS)
                    continue

                tentativas += 1
                if os.path.isfile(self.base.caminho):
                    self.base.carregar()
                resultados = self.base.buscar(texto)

                # ---- Não encontrou (menos de 3 pontos) ----
                if not resultados or resultados[0][0] < LIMITE_MEDIA:
                    ultima = (texto, None, False)
                    self._sugerir()
                    if ler_sim_nao("\nQuer tentar de novo com outras palavras? (s/n): "):
                        continue
                    self.registrar("pergunta", texto, None, False, False,
                                   tentativas, inicio)
                    concluido = True
                    continue

                # ---- Encontrou (confiança ALTA ou MÉDIA) ----
                melhor = resultados[0][1]
                ultima = (texto, melhor.id, True)
                alternativas = self._mostrar_resultado(resultados)

                if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    self.registrar("pergunta", texto, melhor.id, True, True,
                                   tentativas, inicio)
                    concluido = True
                    continue

                if alternativas:
                    escolha = ler_opcao("Digite o número de uma alternativa para "
                                        "vê-la (0 para não ver): ",
                                        0, len(alternativas))
                    if escolha != 0:
                        orientacao = alternativas[escolha - 1][1]
                        tentativas += 1
                        ultima = (texto, orientacao.id, True)
                        orientacao.exibir()
                        if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                            self.registrar("pergunta", texto, orientacao.id, True,
                                           True, tentativas, inicio)
                            concluido = True
                            continue

                if ler_sim_nao("Quer tentar de novo com outras palavras? (s/n): "):
                    continue
                self.registrar("pergunta", texto, ultima[1], True, False,
                               tentativas, inicio)
                concluido = True

    # ------------------------------------------------------------------
    # Atendimento por navegação nas categorias
    # ------------------------------------------------------------------
    def navegar(self):
        """Lista categorias e orientações numeradas, com 0 para voltar."""
        if not self._base_disponivel():
            return
        inicio = time.time()
        tentativas = 0
        pendente = None          # última orientação vista que não ajudou

        while True:
            categorias = self.base.categorias()
            print("\n=== NAVEGAR POR CATEGORIAS ===")
            for numero, categoria in enumerate(categorias, start=1):
                quantidade = len(self.base.por_categoria(categoria))
                print(f"  {numero}) {categoria} ({quantidade} orientações)")
            print("  0) Voltar")
            opcao = ler_opcao("Escolha uma categoria (0 para voltar): ",
                              0, len(categorias))
            if opcao == 0:
                if pendente is not None:   # viu orientações, nenhuma ajudou
                    self.registrar("categoria", pendente[0], pendente[1].id,
                                   True, False, tentativas, inicio)
                return

            categoria = categorias[opcao - 1]
            while True:
                orientacoes = self.base.por_categoria(categoria)
                print(f"\n--- {categoria} ---")
                for numero, orientacao in enumerate(orientacoes, start=1):
                    print(f"  {numero}) {orientacao.titulo}")
                print("  0) Voltar às categorias")
                escolha = ler_opcao("Escolha uma orientação (0 para voltar): ",
                                    0, len(orientacoes))
                if escolha == 0:
                    break

                orientacao = orientacoes[escolha - 1]
                tentativas += 1
                orientacao.exibir()
                descricao = f"[{categoria}] {orientacao.titulo}"

                if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    self.registrar("categoria", descricao, orientacao.id,
                                   True, True, tentativas, inicio)
                    inicio = time.time()           # começa um novo atendimento
                    tentativas = 0
                    pendente = None
                    break
                pendente = (descricao, orientacao)
                print("Tudo bem! Escolha outra orientação ou 0 para voltar.")

    # ------------------------------------------------------------------
    # Registro, indicadores e exportação
    # ------------------------------------------------------------------
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, inicio):
        """Salva um atendimento válido no historico.json."""
        if contem_dados_pessoais(pergunta):        # segunda barreira de proteção
            print(AVISO_DADOS_PESSOAIS)
            return None
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,                      # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,        # None quando não encontrou
            "encontrou": bool(encontrou),
            "ajudou": bool(ajudou),
            "tentativas": int(tentativas),
            "tempo_segundos": round(time.time() - inicio, 1),
            "nota_facilidade": None,               # preenchida ao sair
        }
        self.historico.append(atendimento)
        self.atendimentos_sessao.append(atendimento)
        self._salvar_historico()
        print(f"(Atendimento registrado: {atendimento['tempo_segundos']} s, "
              f"{atendimento['tentativas']} tentativa(s).)")
        return atendimento

    def avaliar(self, nota):
        """Guarda a nota de facilidade (1 a 5) nos atendimentos desta sessão."""
        if not self.atendimentos_sessao:
            return False
        for atendimento in self.atendimentos_sessao:
            atendimento["nota_facilidade"] = nota
        self._salvar_historico()
        return True

    def indicadores(self):
        """Calcula os 6 indicadores a partir do histórico. Devolve um dicionário."""
        total = len(self.historico)
        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]

        def percentual(parte, todo):
            return round(parte / todo * 100, 1) if todo else 0.0

        def media(valores):
            return round(sum(valores) / len(valores), 1) if valores else None

        # Facilidade: uma nota por sessão (pessoa/execução) que avaliou
        notas_por_sessao = {}
        for a in self.historico:
            nota = a.get("nota_facilidade")
            if isinstance(nota, (int, float)) and 1 <= nota <= 5:
                notas_por_sessao[a.get("sessao")] = nota

        # Dúvidas sem solução: atendimentos em que a pessoa não foi ajudada
        sem_solucao = []
        for a in self.historico:
            if not a.get("ajudou"):
                motivo = "não encontrada" if not a.get("encontrou") else "não ajudou"
                item = (a.get("pergunta", ""), motivo)
                if item not in sem_solucao:
                    sem_solucao.append(item)

        return {
            "total": total,
            "resposta_encontrada": percentual(len(encontrados), total),
            "tempo_medio": media([a.get("tempo_segundos", 0) for a in encontrados]),
            "facilidade": media(list(notas_por_sessao.values())),
            "avaliacoes": len(notas_por_sessao),
            "taxa_acerto": percentual(len(ajudaram), total),
            "tentativas_media": media([a.get("tentativas", 0) for a in self.historico]),
            "sem_solucao": sem_solucao,
        }

    def exibir_indicadores(self):
        """Mostra os indicadores calculados por indicadores()."""
        dados = self.indicadores()
        print("\n=== INDICADORES DE ATENDIMENTO ===")
        if dados["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return dados

        def ou_traco(valor, sufixo=""):
            return "-" if valor is None else f"{valor}{sufixo}"

        print(f"Total de atendimentos ........: {dados['total']}")
        print(f"Resposta encontrada ..........: {dados['resposta_encontrada']}%")
        print(f"Tempo médio para encontrar ...: {ou_traco(dados['tempo_medio'], ' s')}")
        print(f"Facilidade de uso (1 a 5) ....: {ou_traco(dados['facilidade'])}"
              f" ({dados['avaliacoes']} avaliação(ões))")
        print(f"Taxa de acerto (ajudou) ......: {dados['taxa_acerto']}%")
        print(f"Tentativas por atendimento ...: {ou_traco(dados['tentativas_media'])}")
        print("Dúvidas sem solução ..........:", end="")
        if dados["sem_solucao"]:
            print()
            for pergunta, motivo in dados["sem_solucao"]:
                print(f"  - {pergunta} ({motivo})")
        else:
            print(" nenhuma")
        return dados

    def exportar_csv(self):
        """Exporta todos os atendimentos para data/atendimentos.csv."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore", restval="")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
        except OSError:
            print("Não foi possível gravar o arquivo CSV.")
            return -1
        return len(self.historico)
