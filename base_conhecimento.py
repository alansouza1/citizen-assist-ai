"""
base_conhecimento.py
Classe BaseConhecimento: o conjunto de todas as orientações.
Responsável por ler o JSON, listar categorias e buscar a melhor orientação.

Projeto: Citizen Assist AI - Global Solution 2026.2 (PCP)
Autor:   Alan Júnior Araújo de Souza - RM 574112
"""

import json
import re
import unicodedata

from orientacao import Orientacao

# Pesos e limites da busca por pontuação (explicados no README)
PONTOS_PALAVRA_CHAVE = 3      # palavra-chave da orientação encontrada na pergunta
PONTOS_PALAVRA_TITULO = 1     # palavra da pergunta (4+ letras) que aparece no título
TAMANHO_MINIMO_PALAVRA = 4    # só palavras com 4 letras ou mais pontuam no título
LIMITE_ALTA = 6               # 6 pontos ou mais  -> confiança ALTA
LIMITE_MEDIA = 3              # 3 a 5 pontos      -> confiança MÉDIA (abaixo: "Não encontrei")


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.

    Exemplo: "Como faço o Cartão do SUS?" -> " como faco o cartao do sus "
    Os espaços nas pontas permitem procurar palavras INTEIRAS
    (assim "sus" não é encontrado dentro de "suspenso").
    """
    texto = str(texto).lower().strip()
    # Separa letra e acento (ex.: "ã" -> "a" + "~") e descarta os acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    # Tudo o que não for letra ou número vira espaço (remove a pontuação)
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Guarda a lista de objetos Orientacao lidos do arquivo JSON."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []          # lista de objetos Orientacao (composição)
        self.erro = ""                 # mensagem do último problema ao carregar

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.

        Nunca trava: se o arquivo estiver ausente ou corrompido, mostra um
        aviso, deixa a base vazia e devolve False. Registros com campos
        faltando são ignorados (os demais continuam valendo).
        """
        self.orientacoes = []
        self.erro = ""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo '{self.caminho}' não encontrado."
            return False
        except json.JSONDecodeError as e:
            self.erro = (f"Arquivo '{self.caminho}' está corrompido "
                         f"(JSON inválido na linha {e.lineno}).")
            return False
        except (OSError, UnicodeDecodeError):
            self.erro = f"Não foi possível ler o arquivo '{self.caminho}'."
            return False

        if not isinstance(dados, list):
            self.erro = "A base de conhecimento deve ser uma lista de orientações."
            return False

        ignorados = 0
        for registro in dados:
            try:
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            except (KeyError, TypeError):
                ignorados += 1

        if ignorados:
            self.erro = f"{ignorados} registro(s) com campos faltando foram ignorados."
        if not self.orientacoes:
            self.erro = self.erro or "A base de conhecimento está vazia."
            return False
        return True

    def categorias(self):
        """Devolve a lista de categorias, sem repetição, na ordem do JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Calcula quantos pontos a orientação recebe para essa pergunta.

        +3 para cada palavra-chave da orientação encontrada na pergunta;
        +1 para cada palavra da pergunta (4+ letras) que aparece no título.
        """
        pergunta = normalizar(pergunta)
        titulo = normalizar(orientacao.titulo)
        pontos = 0

        # Regra 1: palavras-chave (procuradas como palavra/expressão inteira)
        for palavra_chave in orientacao.palavras_chave:
            chave = normalizar(palavra_chave)
            if chave.strip() and chave in pergunta:
                pontos += PONTOS_PALAVRA_CHAVE

        # Regra 2: palavras da pergunta que aparecem no título
        # (set evita contar duas vezes a mesma palavra repetida na pergunta)
        for palavra in set(pergunta.split()):
            if len(palavra) >= TAMANHO_MINIMO_PALAVRA and f" {palavra} " in titulo:
                pontos += PONTOS_PALAVRA_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a
        menor pontuação. Orientações com 0 ponto ficam de fora."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        # Maior pontuação primeiro; em caso de empate, menor id primeiro
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados

    @staticmethod
    def confianca(pontos):
        """Traduz a pontuação em nível de confiança ("ALTA", "MÉDIA" ou None)."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
