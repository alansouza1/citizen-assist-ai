"""
orientacao.py
Classe Orientacao: representa UM registro da base de conhecimento (um item do JSON).

Projeto: Citizen Assist AI - Global Solution 2026.2 (PCP)
Autor:   Alan Júnior Araújo de Souza - RM 574112
"""

AVISO = "Aviso: este assistente NÃO é um canal oficial."


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave      # lista de strings
        self.resposta = resposta
        self.documentos = documentos              # lista de strings
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria um objeto Orientacao a partir de um dicionário lido do JSON.

        Lança KeyError se faltar algum campo obrigatório (tratado na
        BaseConhecimento, que ignora o registro inválido sem travar).
        """
        return cls(
            id=dados["id"],
            categoria=dados["categoria"],
            titulo=dados["titulo"],
            palavras_chave=list(dados["palavras_chave"]),
            resposta=dados["resposta"],
            documentos=list(dados["documentos"]),
            onde=dados["onde"],
            fonte=dados["fonte"],
            verificado_em=dados["verificado_em"],
        )

    def exibir(self):
        """Mostra a orientação formatada, SEMPRE com fonte, data e aviso."""
        print()
        print(f">> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        if self.documentos:
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("  - Nenhum documento específico.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO)

    def __str__(self):
        return f"{self.titulo} [{self.categoria}]"
