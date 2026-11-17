"""
main.py
Ponto de entrada do Citizen Assist AI. Execute com:  python main.py

Projeto: Citizen Assist AI - Global Solution 2026.2 (PCP)
Autor:   Alan Júnior Araújo de Souza - RM 574112
Público: jovens no primeiro emprego e cidadãos em geral que buscam
         documentos, direitos básicos e economia de energia.
"""

import os

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento
from orientacao import AVISO
from sers_energia.analise_energetica import exibir_comparativo_sers

NOME_ASSISTENTE = "Citizen Assist AI"


def mostrar_boas_vindas(base):
    print("=" * 62)
    print(f"  {NOME_ASSISTENTE} - Assistente Digital de Orientação ao Cidadão")
    print("=" * 62)
    print("Orientações sobre documentos, trabalho, saúde, cidadania e energia,")
    print("sempre com a fonte oficial e a data em que a informação foi conferida.")
    print("Este assistente NUNCA pede nome, CPF, RG, telefone ou e-mail.")
    print(AVISO)
    if base.orientacoes:
        print(f"\n{len(base.orientacoes)} orientações carregadas em "
              f"{len(base.categorias())} categorias.")
    else:
        print("\nAtenção: a base de conhecimento não pôde ser carregada.")
    if base.erro:
        print(f"Aviso: {base.erro}")


def mostrar_menu():
    print("\n========== MENU PRINCIPAL ==========")
    print("1 - Fazer uma pergunta")
    print("2 - Navegar por categorias")
    print("3 - Ver indicadores de atendimento")
    print("4 - Exportar atendimentos para CSV")
    print("5 - Simulador e Comparativo de Energia Sustentável (SERS)")
    print("0 - Sair")


def sair(assistente):
    """Pede a nota de facilidade (1 a 5). Devolve True para encerrar."""
    print("\nAntes de sair, avalie o assistente.")
    nota = ler_opcao("De 1 (muito difícil) a 5 (muito fácil), quão fácil foi "
                     "usar o assistente? (0 para voltar ao menu): ", 0, 5)
    if nota == 0:
        return False
    if assistente.avaliar(nota):
        print(f"Nota {nota} registrada. Obrigado pela avaliação!")
    else:
        print(f"Obrigado pela nota {nota}! Como nenhum atendimento foi feito "
              "nesta sessão, ela não entra nos indicadores.")
    print(f"Até logo! - {NOME_ASSISTENTE}")
    return True


def main():
    # Garante que os caminhos "data/..." funcionem de qualquer pasta
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    base = BaseConhecimento(os.path.join("data", "base_conhecimento.json"))
    base.carregar()          # lê o JSON e cria os objetos Orientacao

    assistente = Assistente(NOME_ASSISTENTE, base)
    mostrar_boas_vindas(base)

    while True:
        mostrar_menu()
        opcao = ler_opcao("Escolha uma opção: ", 0, 5)
        if opcao == 1:
            assistente.perguntar()          # usa base.buscar() e orientacao.exibir()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.exibir_indicadores()
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == 4:
            quantidade = assistente.exportar_csv()
            if quantidade >= 0:
                print(f"\n{quantidade} atendimento(s) exportado(s) para "
                      f"{assistente.caminho_csv}")
        elif opcao == 5:
            exibir_comparativo_sers()
            input("\nPressione Enter para voltar ao menu...")
        elif opcao == 0:
            if sair(assistente):
                break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: encerra com educação, sem traceback
        print(f"\n\nAtendimento encerrado. Até logo! - {NOME_ASSISTENTE}")
