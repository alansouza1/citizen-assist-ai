# Estudo Técnico — Soluções em Energias Renováveis e Sustentáveis (SERS)

> **Integração ao Citizen Assist AI — Global Solution 2026.2**
> **Aluno:** Alan Júnior Araújo de Souza | **RM:** 574112 | **Modalidade:** Individual

---

## 1. Público-Alvo e Necessidade Energética Real

- **Público-alvo:** jovens no primeiro emprego e famílias brasileiras de renda baixa a média (residência urbana padrão de **3 moradores**).
- **Necessidade energética abordada:** **aquecimento de água para banho diário** (3 banhos por dia, 30 dias/mês).
- **Por que esse problema é crítico:** segundo a Empresa de Pesquisa Energética (EPE) e o Procel, o consumo médio residencial brasileiro gira em torno de **177 a 180 kWh/mês**, e o chuveiro elétrico (potência típica entre **4.400 W e 7.600 W**) está entre os maiores responsáveis pela conta de luz doméstica, podendo representar **25% a 30% do consumo mensal**, além de sobrecarregar o sistema elétrico no horário de pico (17h às 20h).
- **Como o Citizen Assist AI contribui:** oferece recomendações acessíveis, fundamentadas em cálculos reais e transparentes, mostrando quando vale mais investir em **eficiência energética imediata** (baixo custo, ideal para quem mora de aluguel) ou em **fonte renovável** (aquecimento solar de água ou microgeração fotovoltaica), sempre informando custos, retorno e limitações.

---

## 2. Dados Públicos Reais vs. Premissas e Estimativas Justificadas

Para garantir rigor técnico, as premissas do estudo separam claramente o que é **dado público oficial** do que é **estimativa justificada**:

### 2.1. Dados Públicos Reais (Referências Oficiais)

| Parâmetro | Valor utilizado | Unidade | Origem / Justificativa | Fonte oficial |
| --- | --- | --- | --- | --- |
| **Tarifa residencial média (B1)** | `0,80` | `R$/kWh` | Valor de referência dentro da mediana nacional de R$ 0,79 a R$ 0,85/kWh divulgada pela ANEEL (sem bandeiras adicionais) | [ANEEL — Tarifas](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras) |
| **Fator médio de emissão do SIN** | `0,0461` | `kgCO2/kWh` | Fator médio anual consolidado de 2025 do Sistema Interligado Nacional (`0,0461 tCO2/MWh`) | [MCTI / SIRENE](https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao) |
| **Consumo médio residencial Brasil** | `177 a 180` | `kWh/mês` | Referência de consumo domiciliar brasileiro e faixa de potência de chuveiros (4.400 W a 7.600 W) | [EPE — Anuário Estatístico](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/anuario-estatistico-de-energia-eletrica) |

### 2.2. Estimativas Justificadas de Uso e Custos

- **Perfil familiar:** 3 moradores, 30 dias/mês, analisados em **três horizontes comuns**: **mensal (1 mês)**, **anual (12 meses)** e **5 anos (60 meses)**.
- **Cenário Base:** chuveiro elétrico tradicional de **5.500 W** (valor intermediário dentro da faixa de 4.400–7.600 W da EPE), 3 banhos de 12 minutos/dia (`0,60 h/dia`), sem custo inicial (`CAPEX = R$ 0,00`).
- **Alternativa 1 (Eficiência Energética e Conservação):** chuveiro eletrônico/multitemperatura ajustado para média de **3.800 W** + redutor de vazão + redução do banho para 8 minutos/pessoa (`0,40 h/dia`). Investimento inicial estimado (`CAPEX`) de **R$ 180,00** (aparelho eficiente + kit redutor de vazão).
- **Alternativa 2 (Fonte Renovável — Aquecimento Solar de Água / SAS):** sistema compacto acoplado de **200 litros** certificado pelo Selo Procel/Inmetro. Estima-se **fração solar anual de 80%** (o sol aquece a água gratuitamente na maior parte do ano e a resistência de apoio elétrico supre os **20%** restantes em períodos nublados/chuvosos). Investimento inicial estimado (`CAPEX`) de **R$ 3.200,00** (equipamento compacto + instalação hidráulica básica em casa térrea).

---

## 3. Fórmulas, Cálculos e Comparação dos 3 Cenários

Fórmulas executadas diretamente em [analise_energetica.py](analise_energetica.py):

$$\text{Energia}_{\text{mês}}\ (\text{kWh}) = \frac{\text{Potência (W)}}{1000} \times \text{horas/dia} \times 30 \times \text{fator elétrico}$$

$$\text{Custo}_{\text{mês}}\ (\text{R\$}) = \text{Energia}_{\text{mês}} \times 0{,}80\qquad|\qquad \text{Emissão}_{\text{mês}}\ (\text{kgCO}_2) = \text{Energia}_{\text{mês}} \times 0{,}0461$$

$$\text{Payback simples (meses)} = \frac{\text{CAPEX (R\$)}}{\text{Economia mensal (R\$/mês)}}$$

### 3.1. Comparação Geral (Mesma Necessidade: 3 Banhos Diários)

| Indicador | Cenário Base (Chuveiro 5.500 W) | Alt. 1: Eficiência (3.800 W + 8 min) | Alt. 2: Renovável (Aquecedor Solar SAS 200 L) |
| --- | --- | --- | --- |
| **Consumo mensal** | `99,0 kWh/mês` | `45,6 kWh/mês` (**-53,9%**) | `19,8 kWh/mês` (**-80,0%**) |
| **Consumo anual** | `1.188,0 kWh/ano` | `547,2 kWh/ano` | `237,6 kWh/ano` |
| **Consumo em 5 anos** | `5.940,0 kWh` | `2.736,0 kWh` | `1.188,0 kWh` |
| **Economia de energia (5 anos)** | `0,0 kWh` | **`3.204,0 kWh`** | **`4.752,0 kWh`** |
| **Custo mensal na conta** | `R$ 79,20` | `R$ 36,48` | `R$ 15,84` |
| **Economia mensal** | `R$ 0,00` | **`R$ 42,72/mês`** | **`R$ 63,36/mês`** |
| **Economia anual** | `R$ 0,00` | `R$ 512,64/ano` | `R$ 760,32/ano` |
| **Economia bruta em 5 anos** | `R$ 0,00` | `R$ 2.563,20` | `R$ 3.801,60` |
| **CAPEX (investimento inicial)** | `R$ 0,00` | `R$ 180,00` | `R$ 3.200,00` |
| **Payback simples** | — | **`4,2 meses`** | **`50,5 meses` (~4,2 anos)** |
| **Saldo líquido em 5 anos** *(Econ. − CAPEX)* | `R$ 0,00` | **`+ R$ 2.383,20`** | **`+ R$ 601,60`** *(+10 anos de vida útil restante)* |
| **Emissões anuais** | `54,77 kgCO2/ano` | `25,23 kgCO2/ano` | `10,95 kgCO2/ano` |
| **CO2 evitado em 1 ano** | `0,00 kgCO2` | **`29,54 kgCO2/ano`** | **`43,82 kgCO2/ano`** |
| **CO2 evitado em 5 anos** | `0,00 kgCO2` | **`147,70 kgCO2`** | **`219,06 kgCO2`** |

---

## 4. Análise de Viabilidade, Custos e Impacto Ambiental

1. **Alternativa 1 (Eficiência Energética) — Melhor retorno no curto prazo:**
   - **Por que recomendar:** com apenas **R$ 180,00**, o cidadão recupera o investimento em **4,2 meses** e acumula **R$ 2.383,20 de saldo líquido positivo em 5 anos**. Funciona em **qualquer residência** (própria, alugada ou apartamento) e exige apenas a troca do chuveiro/redutor e ajuste de hábito.
2. **Alternativa 2 (Fonte Renovável — Aquecimento Solar SAS) — Maior impacto ambiental e economia no longo prazo:**
   - **Por que recomendar:** reduz em **80%** a eletricidade usada para banho (**4.752 kWh economizados** e **219,06 kgCO2 evitados em 5 anos**), além de aliviar o pico de carga da rede elétrica (17h–20h). Embora o retorno leve cerca de **4,2 anos** (`50,5 meses`), coletores solares certificados têm vida útil superior a 15 anos, gerando economia contínua após o payback.
   - **Comparação com Solar Fotovoltaica (Lei 14.300/2022):** um sistema fotovoltaico conectado à rede atende toda a casa (não apenas o banho), mas exige investimento inicial estimado entre **R$ 8.000 e R$ 14.000** (kit pequeno de ~1,5 a 2,5 kWp) e aprovação na distribuidora, com payback típico de 4 a 7 anos. Para quem quer atacar especificamente o gasto com banho, o aquecedor solar térmico (SAS) tem entrada financeira bem menor.
3. **Estratégia combinada recomendada ao usuário:** começar imediatamente pela **eficiência energética** (payback de 4 meses) e, caso more em imóvel próprio com telhado ensolarado, avaliar a **energia solar térmica ou fotovoltaica** para ganhos estruturais de longo prazo (além de verificar elegibilidade à **Tarifa Social de Energia Elétrica** se inscrito no CadÚnico).

---

## 5. Integração Funcional ao Citizen Assist AI

A análise de SERS está integrada ao sistema de duas formas:

1. **Base de Conhecimento (`data/base_conhecimento.json`):** a categoria `"Energia e Sustentabilidade"` reúne orientações sustentadas diretamente pelos cálculos acima (IDs `13` a `17`, incluindo o comparativo direto entre chuveiro eficiente, aquecedor solar térmico e geração fotovoltaica), com custos estimados, payback, impacto ambiental, fontes oficiais e avisos de limitação.
2. **Simulador no Menu Principal (`main.py` — opção `5`):** chama `exibir_comparativo_sers()` de `sers_energia/analise_energetica.py`, exibindo a tabela comparativa mensal/anual/5 anos e os avisos diretamente no terminal sem alterar as opções `1` a `4` e `0` da disciplina PCP.

---

## 6. Testes de Compreensão e Utilidade com Usuários (SERS)

Foram realizados testes de leitura e compreensão das orientações de energia com **3 perfis anônimos** (sem coleta de nome, CPF, telefone ou e-mail), avaliando se os cidadãos entendiam as recomendações, os custos e as limitações das estimativas:

| Perfil anônimo | Situação testada | Comentário recebido sobre clareza e limitações | Ajuste realizado nas orientações |
| --- | --- | --- | --- |
| **Perfil E1** *(Jovem morando de aluguel)* | Perguntou como gastar menos no chuveiro e analisou o comparativo da opção 5 | Achou útil ver o retorno de ~4 meses no chuveiro eficiente, mas ficou em dúvida se compensava instalar aquecedor solar em casa alugada | Deixado explícito na orientação 17 e no simulador que o **aquecedor solar (SAS)** exige imóvel próprio ou autorização do proprietário e adaptação hidráulica, reforçando a **Alternativa 1** para quem aluga |
| **Perfil E2** *(Família interessada em energia solar)* | Consultou as orientações 16 (fotovoltaica) e 17 (comparativo banho) | Confundiu **aquecedor solar de água** com **painel solar fotovoltaico** e pensou que a economia de 80% se aplicava à conta inteira da casa | Diferenciado claramente no texto da orientação 16 e 17 que o **SAS aquece apenas água** (~80% do consumo do chuveiro) enquanto o **fotovoltaico gera eletricidade para a casa toda**, com faixas de investimento distintas |
| **Perfil E3** *(Cidadão comparando valores na conta)* | Avaliou os valores em reais (`R$ 42,72/mês` e `R$ 63,36/mês`) exibidos nas respostas | Perguntou se a economia de R$ 42 ou R$ 63 era garantida na cidade dele, já que a tarifa local era diferente de R$ 0,80/kWh | Inserido destaque explícito de **premissas e limitação** (`R$ 0,80/kWh`, 3 moradores, clima e bandeira tarifária variam) deixando claro que estimativas **não são resultados garantidos** |

---

## 7. Limitações Explícitas das Estimativas

- **As estimativas de consumo, economia, geração solar e retorno financeiro NÃO são resultados garantidos.**
- A tarifa residencial varia fortemente entre distribuidoras brasileiras (conforme ranking B1 da ANEEL, há concessionárias com tarifa menor e outras acima de R$ 1,00/kWh), além da incidência de impostos estaduais (ICMS) e bandeiras tarifárias.
- O fator de emissão de CO2 do SIN (`0,0461 kgCO2/kWh` em 2025) oscila mensal e anualmente conforme o despacho de hidrelétricas e termelétricas (condições hidrológicas).
- O desempenho de sistemas solares térmicos (SAS) e fotovoltaicos depende da irradiação solar da região, orientação/inclinação do telhado, sombreamento e manutenção.
- Os preços de equipamentos e instalação (`CAPEX`) são estimativas médias de mercado sujeitas a variação regional.

---

## 8. Fontes Verificáveis

- **ANEEL — Tarifas e Informações Econômico-Financeiras:** https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras
- **ANEEL — Tarifa Social de Energia Elétrica:** https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social
- **ANEEL — Micro e Minigeração Distribuída (Lei 14.300/2022):** https://www.gov.br/aneel/pt-br/assuntos/geracao-distribuida
- **EPE — Anuário Estatístico de Energia Elétrica:** https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/anuario-estatistico-de-energia-eletrica
- **EPE — Atlas da Eficiência Energética Brasil:** https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/atlas-da-eficiencia-energetica-brasil
- **MCTI / SIRENE — Fatores de Emissão de CO2 (Inventários Corporativos / SIN):** https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao
- **Selo Procel (Eficiência Energética):** https://smartseloprocel.procelinfo.com.br/selo-procel
