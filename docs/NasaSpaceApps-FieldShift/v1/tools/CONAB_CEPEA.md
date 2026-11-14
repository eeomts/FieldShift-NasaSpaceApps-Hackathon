# CONAB e CEPEA no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar a CONAB e o CEPEA, como eles entram na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta a CONAB e o CEPEA aos outros datasets.

## O que são a CONAB e o CEPEA

A **CONAB** (Companhia Nacional de Abastecimento) é a empresa pública ligada ao Ministério da Agricultura que acompanha safras e mercados. Para o projeto, três produtos importam:

- **Acompanhamento da safra brasileira de grãos:** levantamentos ao longo do ano, com área, produtividade e produção por estado, e séries históricas.
- **Custos de produção:** planilhas por cultura, safra, município de referência e nível de tecnologia, com custo variável, custo fixo e custo total por hectare.
- **Preços agropecuários:** preços recebidos pelo produtor por estado e preços mínimos da política de garantia (PGPM).

O **CEPEA** (Centro de Estudos Avançados em Economia Aplicada, da Esalq/USP) calcula **indicadores diários de preço**. Os mais usados para grãos são o indicador do milho ESALQ/B3, com base em Campinas (SP), com série desde agosto de 2004, e o indicador da soja ESALQ/B3 no porto de Paranaguá (PR). Há indicadores também para trigo, algodão, boi, café e outros.

## Por que usar

**1. São o substituto brasileiro do AMS.** Nos EUA, o desafio usa o AMS Market News para preços. Aqui, CONAB e CEPEA cumprem esse papel (D-003).

**2. Uma boa rotação precisa caber no bolso.** Uma estratégia ótima para o solo que dá prejuízo não será adotada. Preço e custo transformam a nota de "renda" num número defensável.

**3. Mostram o risco de mercado.** A série longa do CEPEA mostra quanto o preço oscila. Uma cultura com preço muito volátil pesa mais para o pequeno produtor.

**4. O custo muda por região.** A CONAB tem planilhas para municípios de referência em vários estados. O custo do milho safrinha em Goiás não é o mesmo que no Paraná.

## Como entra no projeto

### Harmonização

- **Acesso:** portal da CONAB (planilhas de custos, séries históricas de safra e preços em XLS ou CSV); site do CEPEA, na consulta de séries de preços (planilha por indicador).
- **Processamento:** corrigir preços pela inflação (por exemplo, pelo IGP-DI ou IPCA), converter para R$ por saca ou por tonelada, calcular médias por mês da colheita e associar cada município ao custo de referência mais próximo, no mesmo estado e sistema de produção.

| Campo | O que é | Uso |
| --- | --- | --- |
| Indicador CEPEA (R$/saca) | Preço diário numa praça de referência | Preço típico e volatilidade |
| Preço recebido CONAB (por estado) | Preço pago ao produtor | Ajuste do preço para a região |
| Custo variável (R$/ha) | Sementes, adubo, defensivos, operações | Margem da estratégia |
| Custo total (R$/ha) | Variável mais fixo e remuneração de fatores | Comparação de longo prazo |
| Produtividade da planilha (sc/ha) | Rendimento assumido no custo | Ponto de equilíbrio |
| Preço mínimo (PGPM) | Preço de garantia do governo | Piso de referência |

> Confirmar nas páginas oficiais os municípios de referência de cada planilha de custo, as praças e a data de início de cada indicador, se o download no CEPEA exige cadastro e as condições de uso e citação dos dados. Nenhuma das duas fontes tem API pública documentada; o acesso previsto é por planilha.

### Indicadores calculados

- **Preço típico na colheita:** mediana real dos últimos 5 anos no mês de venda.
- **Volatilidade:** variação do preço entre anos (por exemplo, o intervalo entre os percentis 20 e 80).
- **Margem esperada:** preço × produtividade esperada − custo variável, por hectare.
- **Margem ajustada pelo risco:** a mesma conta usando a frequência de anos ruins (IBGE PAM, GLDAS, ZARC).
- **Ponto de equilíbrio:** produtividade mínima para cobrir o custo variável.

### Nível de confiança

Preço e custo são **referências regionais**. O frete até o comprador, o contrato do produtor e o pacote tecnológico mudam a conta. O mercado futuro de milho da B3 liquida pelo indicador do CEPEA, então os dois **não contam como confirmações independentes**. As estimativas de safra da CONAB e do IBGE PAM também usam informantes parecidos. A ferramenta mostra a margem como faixa, não como número exato.

## Onde o produtor vê isso

**Cartão da estratégia, em "Renda".** Uma faixa de margem por hectare, com o aviso "estimativa com preços e custos de referência".

**Etapa 4, ajuste de prioridades.** O produtor pode trocar o preço ou o custo pelo seu, e a nota de renda é recalculada.

**Glossário.** Explica indicador, praça de referência, custo variável e ponto de equilíbrio.

## Caso hipotético: CONAB e CEPEA junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Paulo planta grãos perto de Rio Verde, no sudoeste de Goiás, região de Cerrado com agroindústria de carnes e de milho.

- **Rotação atual:** soja (outubro a fevereiro) e milho safrinha (fevereiro a julho), todo ano.
- **Irrigação:** não tem.
- **Prioridades:** renda e água altas; solo médio.
- **Mercado:** soja, milho e sorgo, com compradores de ração na região.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **CONAB (custos)** | O custo variável do milho safrinha subiu 30% em 5 anos; o do sorgo é cerca de 35% menor por hectare. |
| **CONAB (preços)** | O sorgo é pago a cerca de 80% do preço do milho no estado. |
| **CEPEA** | O preço real do milho variou muito entre anos; em 2 dos últimos 5 anos ficou abaixo do ponto de equilíbrio da safrinha tardia. |
| IBGE PAM (tabela 839) | Milho 2ª safra com rendimento 25% abaixo da mediana em 3 dos últimos 10 anos. |
| GLDAS / SMAP L4 | Zona das raízes abaixo do normal em maio em 4 de cada 10 anos. |
| ZARC | Janela de menor risco do milho safrinha termina no fim de fevereiro. |
| HLS | Em 2 dos últimos 5 anos, o milho foi semeado em meados de março. |

### Onde os dados se completam

**O milho tardio é a parte cara do risco.** O HLS mostra plantios fora da janela do ZARC. O GLDAS mostra a água acabando em maio. A PAM confirma rendimentos baixos nesses anos. Juntando o custo da CONAB e o preço do CEPEA, o milho tardio dá margem negativa em boa parte dos anos.

**O sorgo perde em preço, mas ganha em custo.** Mesmo pago a 80% do milho, o sorgo custa menos e tolera melhor a seca. Para plantio depois da janela, a margem ajustada pelo risco fica parecida ou melhor.

### Regras ativadas

- **Margem negativa frequente no plantio tardio** aumenta o peso de uma regra condicional para a segunda cultura.
- **Déficit de água em maio** aumenta o peso das culturas tolerantes à seca.
- **Comprador de ração na região** mantém o sorgo como opção de venda.

### Comparação das estratégias

| Critério | A: atual (soja → milho safrinha) | B: soja → sorgo safrinha | C: soja → milho se semeado até o fim de fevereiro, sorgo depois |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●●○ | ●●●●○ |
| Solo | ●●○○○ | ●●●○○ | ●●●○○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●●○○ |
| Erosão | ●●○○○ | ●●●○○ | ●●●○○ |
| Forragem | ●○○○○ | ●●●○○ | ●●○○○ |
| Renda | ●●●●○ | ●●●○○ | ●●●●○ |

Com os pesos do Sr. Paulo (renda e água altas, solo médio), a **estratégia C** fica em primeiro. Ela empata com a B em água e com a A em renda. A B tem renda menor nos anos em que o milho entraria na janela.

### Cartão da estratégia C

> **Resumo:** uma opção é manter o milho safrinha quando a soja sai a tempo de semear até o fim de fevereiro e usar o sorgo quando a semeadura passaria dessa data.
>
> **Por que foi sugerida:** nos anos em que o milho foi semeado em março, a água acabou em maio e a margem estimada ficou negativa; o sorgo custa menos e tolera melhor a seca.
>
> **Evidências:** custos e preços regionais (CONAB e CEPEA, confiança média por serem referências regionais); falta de água em maio (GLDAS e SMAP L4, confiança alta); janela do ZARC; datas de plantio reais (HLS, confiança alta); rendimentos do município (IBGE PAM, confiança média).
>
> **Benefícios:** menos anos com prejuízo na segunda safra, custo menor quando o risco é maior e palhada nos dois casos.
>
> **Lacunas:** não sabemos o seu custo real, o frete até o comprador nem se há contrato de venda do sorgo.
>
> **Riscos para revisão local:** o preço do sorgo depende de comprador local; confirmar a demanda antes. Ajustar com o agrônomo a cultivar de sorgo e o manejo de pragas.

## Conclusão

CONAB e CEPEA trazem a **conta do bolso** para a ferramenta. Os dados de satélite e de clima dizem quando o risco é maior; o preço e o custo mostram quanto esse risco custa. Assim, a nota de renda deixa de ser opinião e passa a ser uma faixa com origem clara, que o produtor pode ajustar com os próprios números.

## Limitações

- **Preço de praça:** o indicador é de Campinas ou Paranaguá; o preço local depende do frete e do comprador.
- **Custo de referência:** a planilha descreve um sistema típico, não a fazenda.
- **Preço futuro é incerto:** a série passada mostra a variação, não o preço da próxima safra.
- **Sem API:** o acesso é por planilha, e o formato pode mudar.
- **Fontes ligadas:** B3 e CEPEA, e CONAB e IBGE PAM, não se confirmam de forma independente.
- **Tratamento:** corrigir pela inflação, mostrar a margem como faixa, deixar o produtor informar preço e custo próprios e citar a fonte de cada número.
