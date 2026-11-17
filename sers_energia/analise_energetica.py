"""
sers_energia/analise_energetica.py
Análise energética e comparativo entre alternativas (Eficiência Energética vs.
Fonte Renovável) para a disciplina Soluções em Energias Renováveis e
Sustentáveis (SERS), integrada ao Citizen Assist AI.

Projeto: Citizen Assist AI - Global Solution 2026.2 (SERS)
Autor:   Alan Júnior Araújo de Souza - RM 574112
"""

import json
import os

CAMINHO_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dados_consumo_comparativo.json",
)


def carregar_dados_sers(caminho=CAMINHO_DADOS):
    """Lê os dados e premissas do estudo SERS a partir do JSON."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def calcular_comparativo(dados):
    """Calcula consumo, custo, economia, payback e emissões de cada cenário.

    Fórmula base:
      Energia mensal (kWh) = (Potência_W / 1000) * horas_dia * dias_mes * fator_eletrico
      Custo mensal (R$)    = Energia_mensal * tarifa_R$_kWh
      Emissão mensal (kg)  = Energia_mensal * fator_CO2_kg_kWh
    """
    periodos = dados["periodos_referencia"]
    dias_mes = periodos["mensal_dias"]
    meses_ano = periodos["anual_meses"]
    meses_5_anos = periodos["horizonte_meses"]

    tarifa = dados["dados_publicos_reais"]["tarifa_residencial_brl_kwh"]["valor"]
    fator_co2 = dados["dados_publicos_reais"]["fator_emissao_sin_kgco2_kwh"]["valor"]

    resultados = []
    base_ref = None

    for cenario in dados["cenarios"]:
        potencia_kw = cenario["potencia_w"] / 1000.0
        horas_dia = cenario["horas_uso_dia"]
        fator_eletrico = cenario["fator_consumo_eletrico"]
        capex = float(cenario["capex_brl"])

        kwh_mes = round(potencia_kw * horas_dia * dias_mes * fator_eletrico, 2)
        kwh_ano = round(kwh_mes * meses_ano, 2)
        kwh_5a = round(kwh_mes * meses_5_anos, 2)

        custo_mes = round(kwh_mes * tarifa, 2)
        custo_ano = round(kwh_ano * tarifa, 2)
        custo_5a = round(kwh_5a * tarifa, 2)

        co2_mes = round(kwh_mes * fator_co2, 2)
        co2_ano = round(kwh_ano * fator_co2, 2)
        co2_5a = round(kwh_5a * fator_co2, 2)

        item = {
            "id": cenario["id"],
            "nome": cenario["nome"],
            "categoria_sers": cenario["categoria_sers"],
            "potencia_w": cenario["potencia_w"],
            "horas_uso_dia": horas_dia,
            "fator_consumo_eletrico": fator_eletrico,
            "capex_brl": capex,
            "kwh_mes": kwh_mes,
            "kwh_ano": kwh_ano,
            "kwh_5a": kwh_5a,
            "custo_mes": custo_mes,
            "custo_ano": custo_ano,
            "custo_5a": custo_5a,
            "co2_mes": co2_mes,
            "co2_ano": co2_ano,
            "co2_5a": co2_5a,
            "viabilidade": cenario["viabilidade"],
            "limitacoes": cenario["limitacoes"],
        }
        if base_ref is None:
            base_ref = item
        resultados.append(item)

    # Calcula ganhos comparativos em relação ao Cenário Base
    for item in resultados:
        econ_kwh_mes = round(base_ref["kwh_mes"] - item["kwh_mes"], 2)
        econ_kwh_ano = round(base_ref["kwh_ano"] - item["kwh_ano"], 2)
        econ_kwh_5a = round(base_ref["kwh_5a"] - item["kwh_5a"], 2)
        reducao_pct = (
            round((econ_kwh_mes / base_ref["kwh_mes"]) * 100, 1)
            if base_ref["kwh_mes"] > 0
            else 0.0
        )

        econ_rs_mes = round(base_ref["custo_mes"] - item["custo_mes"], 2)
        econ_rs_ano = round(base_ref["custo_ano"] - item["custo_ano"], 2)
        econ_rs_5a = round(base_ref["custo_5a"] - item["custo_5a"], 2)

        co2_evitado_ano = round(base_ref["co2_ano"] - item["co2_ano"], 2)
        co2_evitado_5a = round(base_ref["co2_5a"] - item["co2_5a"], 2)

        if item["capex_brl"] > 0 and econ_rs_mes > 0:
            payback_meses = round(item["capex_brl"] / econ_rs_mes, 1)
        else:
            payback_meses = 0.0

        saldo_5a = round(econ_rs_5a - item["capex_brl"], 2)

        item.update({
            "economia_kwh_mes": econ_kwh_mes,
            "economia_kwh_ano": econ_kwh_ano,
            "economia_kwh_5a": econ_kwh_5a,
            "reducao_pct": reducao_pct,
            "economia_rs_mes": econ_rs_mes,
            "economia_rs_ano": econ_rs_ano,
            "economia_rs_5a": econ_rs_5a,
            "co2_evitado_ano": co2_evitado_ano,
            "co2_evitado_5a": co2_evitado_5a,
            "payback_meses": payback_meses,
            "saldo_liquido_5a": saldo_5a,
        })

    return resultados


def exibir_comparativo_sers(caminho=CAMINHO_DADOS):
    """Imprime no terminal o estudo comparativo de energia sustentável (SERS)."""
    try:
        dados = carregar_dados_sers(caminho)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as erro:
        print(f"\nNão foi possível carregar os dados do estudo SERS: {erro}")
        return None

    resultados = calcular_comparativo(dados)
    tarifa_info = dados["dados_publicos_reais"]["tarifa_residencial_brl_kwh"]
    co2_info = dados["dados_publicos_reais"]["fator_emissao_sin_kgco2_kwh"]
    moradores = dados["estimativas_justificadas_uso"]["moradores"]["valor"]
    dias = dados["periodos_referencia"]["mensal_dias"]

    print("\n" + "=" * 78)
    print("  SIMULADOR E COMPARATIVO ENERGÉTICO — SERS (AQUECIMENTO DE ÁGUA RESIDENCIAL)")
    print("=" * 78)
    print(f"Público-alvo : {dados['publico_alvo']}")
    print(f"Necessidade  : {dados['necessidade_energetica']}")
    print(f"Premissas    : {moradores} moradores | {dias} dias/mês | "
          f"Tarifa ref.: R$ {tarifa_info['valor']:.2f}/kWh (ANEEL)")
    print(f"Fator de CO2 : {co2_info['valor']:.4f} kgCO2/kWh "
          "(SIN/MCTI — ano base 2025)")

    print("\n--- TABELA COMPARATIVA (PERÍODO COMUM: MENSAL / ANUAL / 5 ANOS) ---")
    cabecalho = (
        f"{'Cenário':<26} | {'kWh/mês':>8} | {'R$/mês':>8} | "
        f"{'Econ./mês':>9} | {'CAPEX':>9} | {'Payback':>9} | {'CO2 evit/5a':>11}"
    )
    print("-" * len(cabecalho))
    print(cabecalho)
    print("-" * len(cabecalho))

    nomes_curtos = {
        "base": "Base (Chuveiro 5.500W)",
        "eficiencia": "Alt 1: Eficiência (3.800W)",
        "renovavel_sas": "Alt 2: Solar Térmico (SAS)",
    }

    for r in resultados:
        nome = nomes_curtos.get(r["id"], r["id"][:26])
        payback_str = "-" if r["payback_meses"] == 0 else f"{r['payback_meses']:.1f} m"
        print(
            f"{nome:<26} | {r['kwh_mes']:>8.1f} | {r['custo_mes']:>8.2f} | "
            f"{r['economia_rs_mes']:>9.2f} | {r['capex_brl']:>9.2f} | "
            f"{payback_str:>9} | {r['co2_evitado_5a']:>8.1f} kg"
        )
    print("-" * len(cabecalho))

    print("\n--- RESUMO EM 5 ANOS (60 MESES) ---")
    for r in resultados[1:]:
        print(f"* {r['nome']}")
        print(f"  - Redução de consumo : {r['reducao_pct']:.1f}% "
              f"({r['economia_kwh_5a']:.1f} kWh economizados em 5 anos)")
        print(f"  - Economia acumulada : R$ {r['economia_rs_5a']:.2f} | "
              f"Saldo líquido (após CAPEX): R$ {r['saldo_liquido_5a']:.2f}")
        print(f"  - Impacto ambiental  : {r['co2_evitado_ano']:.2f} kgCO2/ano "
              f"({r['co2_evitado_5a']:.2f} kgCO2 evitados em 5 anos)")
        print(f"  - Viabilidade        : {r['viabilidade']}")
        print(f"  - Limitações         : {r['limitacoes']}")

    print("\n--- FONTES E AVISO DE LIMITAÇÃO ---")
    print(f"- Tarifa ANEEL : {tarifa_info['fonte']}")
    print(f"- Fator MCTI   : {co2_info['fonte']}")
    print("- AVISO: Os valores acima são estimativas educacionais baseadas em premissas")
    print("  médias. Economia, geração solar e retorno financeiro variam conforme")
    print("  distribuidora, bandeira tarifária, clima local e hábitos de uso.")
    return resultados


if __name__ == "__main__":
    exibir_comparativo_sers()
