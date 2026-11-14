# IBGE PAM + API do SIDRA: análise, implementação e caso de uso

## Mercado local por município para o Field Shift

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Código: pasta `ibge-pam-exemplo/` (`pam_sidra.py`, `teste_offline.py`)
> Documentos relacionados: `relacao-nasa-power-harvest-portal.md`, `harvest-portal-api.md`, `arquitetura-completa-field-shift.md`

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [A pesquisa PAM](#2-a-pesquisa-pam)
3. [As APIs do IBGE usadas](#3-as-apis-do-ibge-usadas)
4. [API do SIDRA: anatomia da URL](#4-api-do-sidra-anatomia-da-url)
5. [Parâmetros, um por um](#5-parâmetros-um-por-um)
6. [Estrutura da resposta](#6-estrutura-da-resposta)
7. [Descobrindo códigos: API de Agregados e de Localidades](#7-descobrindo-códigos-api-de-agregados-e-de-localidades)
8. [Implementação em Python](#8-implementação-em-python)
9. [Indicadores para o Field Shift](#9-indicadores-para-o-field-shift)
10. [O fluxo no aplicativo](#10-o-fluxo-no-aplicativo)
11. [Exemplo: o agricultor](#11-exemplo-o-agricultor)
12. [Caso de uso UC-04](#12-caso-de-uso-uc-04)
13. [Testes realizados](#13-testes-realizados)
14. [Limitações](#14-limitações)
15. [Boas práticas](#15-boas-práticas)
16. [Referências](#16-referências)

---

## Nível de verificação

- Os fatos sobre a PAM vêm da **página oficial da pesquisa no IBGE**, de publicações e notas técnicas do IBGE e de metadados publicados pelo SNIF.
- A estrutura da API do SIDRA (`/t/`, `/n6/`, `/v/`, `/p/`, `/c/`, `allxp`, `last N`) vem da **documentação dos clientes oficiais e comunitários** (`sidrar`, `sidra`, `DadosAbertosBrasil`), que apontam para a ajuda oficial `apisidra.ibge.gov.br/home/ajuda`.
- Os **códigos das variáveis** (8331, 216, 214, 112, 215) vêm do código do pacote **`datazoom.amazonia`** (`R/pam.R`), que usa a PAM.
- **A página da PAM, o SIDRA e as APIs do IBGE não puderam ser acessados** diretamente no ambiente de pesquisa. **Nenhuma chamada foi feita à API real.**
- O código foi **testado offline** com uma resposta falsa no formato do SIDRA (seção 13).
- Itens marcados com ⚠️ devem ser confirmados com `python pam_sidra.py --descobrir`.
- **A PAM não está na lista oficial de recursos do desafio.** Ela entra como fonte complementar de mercado para o Brasil.

---

## 1. Visão geral

| Item | Valor |
|---|---|
| Pesquisa | **PAM — Produção Agrícola Municipal** (IBGE) |
| O que mede | Área plantada, área colhida, quantidade produzida, rendimento médio e valor da produção |
| Produtos | 64: 31 de lavouras temporárias e 33 de lavouras permanentes |
| Unidade | **Município** (agregável para microrregião, UF, Brasil) |
| Frequência | Anual (ano civil) |
| Série | Início oficial em 1974; tabelas do SIDRA a partir de 1974 ⚠️ (metadados do SNIF citam 1994–2024 para os painéis) |
| Último ano | **2024**, publicado em **11/09/2025** |
| Tabela principal no SIDRA | **5457** |
| Acesso | Site do IBGE, SIDRA (interface), **API do SIDRA**, API de Agregados v3 |
| Autenticação | Nenhuma |

**Papel no Field Shift:** substituir o dado de mercado **nacional** do Harvest Portal por dado **do município e da microrregião** do agricultor, no Brasil.

```
NASA POWER  → o que dá para plantar (clima do talhão)
PAM (IBGE)  → se vale a pena plantar (mercado e renda na região)
Harvest     → contexto nacional/global e chat com MCP
```

---

## 2. A pesquisa PAM

### 2.1 Variáveis

| Variável | Unidade | Uso no Field Shift |
|---|---|---|
| Área plantada ou destinada à colheita | ha | Tamanho da cultura na região |
| Área colhida | ha | Tamanho e perdas (plantada − colhida) |
| Quantidade produzida | t | Volume |
| Rendimento médio | kg/ha | Produtividade e variação entre anos |
| Valor da produção | mil R$ (nominal) | Renda por hectare |

### 2.2 Regras importantes da pesquisa

| Regra | Consequência |
|---|---|
| A unidade de investigação é o **município** | Não há dado por fazenda nem por talhão |
| Produto com menos de **1 ha** e **1 t** no município fica fora | Cultura muito pequena aparece como ausente |
| Para culturas de ciclo longo (cana, mandioca), soma-se o colhido mês a mês no ano civil | Comparar com culturas anuais com cuidado |
| Quando a colheita ultrapassa o ano civil, conta no ano em que se colheu a maior parte | Safrinha pode cair no ano seguinte ao plantio |
| Milho e feijão têm **1ª e 2ª safra** separados ⚠️ | Permite analisar a safrinha diretamente |
| Valor da produção é **nominal** | Corrigir pela inflação (IPCA, tabela 1737 do SIDRA) para comparar anos |

### 2.3 Números de 2024 (contexto para o pitch)

| Indicador | Valor |
|---|---|
| Valor da produção agrícola | R$ 783,2 bilhões (−3,9%) |
| Área colhida | 96,5 milhões de ha |
| Produção de cereais, leguminosas e oleaginosas | 292,5 milhões de t (−7,5%) |
| Soja + milho | Quase 88,7% da produção de grãos |

---

## 3. As APIs do IBGE usadas

| API | Endereço base | Para quê |
|---|---|---|
| **API do SIDRA** | `https://apisidra.ibge.gov.br/values` | **Baixar os dados** da tabela 5457 |
| **API de Agregados v3** | `https://servicodados.ibge.gov.br/api/v3/agregados` | **Metadados**: variáveis, classificações, códigos dos produtos, períodos |
| **API de Localidades v1** | `https://servicodados.ibge.gov.br/api/v1/localidades` | **Código IBGE** do município, microrregião e UF |
| **API de Malhas v3** (opcional) | `https://servicodados.ibge.gov.br/api/v3/malhas` | Contorno do município para o mapa |

Todas são abertas, sem login, e devolvem JSON.

---

## 4. API do SIDRA: anatomia da URL

```
https://apisidra.ibge.gov.br/values/t/5457/n6/3143104/v/8331,216,214,112,215/p/last%2010/c782/40124,40122
                                    └──┬──┘└────┬───┘└────────────┬────────┘└────┬─────┘└──────┬──────┘
                                    tabela  nível +     variáveis          período    classificação +
                                            localidade                                categorias
```

⚠️ O código do município e os códigos dos produtos acima são **ilustrativos**. Descubra os reais com a seção 7.

| Bloco | Significado | Exemplo |
|---|---|---|
| `/t/{tabela}` | Tabela do SIDRA | `/t/5457` |
| `/n{nível}/{localidades}` | Nível territorial e quais unidades | `/n6/3143104`, `/n6/all`, `/n9/31019` |
| `/v/{variáveis}` | Códigos das variáveis | `/v/214,112` ou `/v/allxp` |
| `/p/{períodos}` | Anos | `/p/last%2010`, `/p/2015-2024`, `/p/all` |
| `/c{classificação}/{categorias}` | Filtro de produto | `/c782/40124` ou `/c782/all` |
| `/h/n` (opcional) | Sem a linha de cabeçalho na resposta | `/h/n` |
| `/f/{formato}` e `/d/{decimais}` (opcionais) ⚠️ | Formato dos descritores e casas decimais | ver ajuda oficial |

---

## 5. Parâmetros, um por um

### 5.1 `/t/` — tabela

| Tabela | Conteúdo |
|---|---|
| **5457** | PAM: área plantada/destinada à colheita, área colhida, quantidade, rendimento e valor, **todos os produtos** (temporárias e permanentes) |
| 1612 | PAM: lavouras **temporárias** (usada no Anuário Estatístico) |
| 1613 ⚠️ | PAM: lavouras **permanentes** |
| 1737 | IPCA (para corrigir valores nominais) |

**Para o Field Shift:** use a **5457**.

### 5.2 `/n{nível}/` — nível territorial

| Código | Nível | Uso no projeto |
|---|---|---|
| `n1` | Brasil | Contexto nacional |
| `n3` | Unidade da Federação | Contexto estadual |
| `n6` | **Município** | Dado do município do talhão |
| `n9` | **Microrregião** | Mercado regional (mais estável que o município) |
| `n8` | Mesorregião | Contexto mais amplo |

Localidades: um código (`/n6/3143104`), vários (`/n6/3143104,3170206`) ou todos (`/n6/all`). ⚠️ Pedir `/n6/all` com muitas variáveis e anos pode estourar o limite de valores por consulta.

### 5.3 `/v/` — variáveis

| Código | Variável | Coluna no código |
|---|---|---|
| **8331** | Área plantada ou destinada à colheita (ha) | `area_plantada_ha` |
| **216** | Área colhida (ha) | `area_colhida_ha` |
| **214** | Quantidade produzida (t) | `quantidade_t` |
| **112** | Rendimento médio da produção (kg/ha) | `rendimento_kg_ha` |
| **215** | Valor da produção (mil R$) | `valor_mil_reais` |
| `allxp` | Todas, exceto as percentuais calculadas pelo SIDRA | — |
| `all` | Todas, inclusive percentuais | — |

### 5.4 `/p/` — período

| Valor | Significado |
|---|---|
| `last` | Último ano disponível |
| `last%2010` | Últimos 10 anos (`%20` é o espaço) |
| `first%205` | Primeiros 5 anos |
| `2015-2024` | Intervalo |
| `2021,2024` | Anos específicos |
| `all` | Todos |

### 5.5 `/c782/` — produto ⚠️

A classificação de produto da tabela 5457 é usada aqui como `c782`. Categorias: um código por produto, ou `all`. **Confirme o número da classificação e os códigos dos produtos** com a API de Agregados (seção 7).

---

## 6. Estrutura da resposta

A API devolve uma **lista JSON**. O **primeiro item é o cabeçalho**: ele diz o que cada chave significa. Os demais são as linhas.

```json
[
  {"NC": "Nível Territorial (Código)", "NN": "Nível Territorial",
   "MC": "Unidade de Medida (Código)", "MN": "Unidade de Medida",
   "V": "Valor",
   "D1C": "Município (Código)", "D1N": "Município",
   "D2C": "Variável (Código)", "D2N": "Variável",
   "D3C": "Ano (Código)", "D3N": "Ano",
   "D4C": "Produto das lavouras temporárias e permanentes (Código)",
   "D4N": "Produto das lavouras temporárias e permanentes"},
  {"NC": "6", "NN": "Município", "MN": "Toneladas", "V": "14800",
   "D1C": "<código>", "D1N": "<Município> - MG",
   "D2C": "214", "D2N": "Quantidade produzida",
   "D3C": "2024", "D3N": "2024",
   "D4C": "<código>", "D4N": "Sorgo (em grão)"}
]
```

> Valores ilustrativos. A ordem das dimensões (`D1`, `D2`...) segue a ordem dos blocos na URL ⚠️.

**Pontos importantes:**
- `V` (Valor) vem como **texto**. Converta para número.
- Símbolos especiais ⚠️: `-` costuma indicar zero absoluto; `..`, `...` e `X` indicam dado não disponível, não aplicável ou omitido por sigilo. **Nunca trate `..` ou `X` como zero.**
- Com `/h/n`, a resposta vem sem a linha de cabeçalho.

---

## 7. Descobrindo códigos: API de Agregados e de Localidades

### 7.1 Metadados da tabela 5457 (variáveis, produtos, períodos)

```
GET https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados
```

Retorna o nome da tabela, a periodicidade, os níveis territoriais, as **variáveis** e as **classificações** com suas **categorias** (os produtos e seus códigos).

```python
meta = requests.get("https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados").json()
for c in meta["classificacoes"]:
    print(c["id"], c["nome"])
    for cat in c["categorias"][:10]:
        print("   ", cat["id"], cat["nome"])
```

### 7.2 Código do município

```
GET https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios
```

```python
muns = requests.get(".../localidades/estados/MG/municipios").json()
codigo = next(m["id"] for m in muns if m["nome"] == "Monte Carmelo")
```

### 7.3 Microrregião do município

A resposta de municípios da API de Localidades traz a microrregião de cada município ⚠️ (campo `microrregiao`). Use o código dela com `/n9/`.

### 7.4 Comando pronto

```bash
python pam_sidra.py --descobrir
```

Imprime todos os produtos da tabela 5457 com seus códigos e o código de Monte Carmelo/MG.

---

## 8. Implementação em Python

**Arquivo:** `ibge-pam-exemplo/pam_sidra.py`

```bash
pip install requests pandas
```

### 8.1 Funções

| Função | O que faz | API |
|---|---|---|
| `codigo_municipio(nome, uf)` | Código IBGE do município | Localidades v1 |
| `produtos_da_tabela()` | `{nome do produto: código}` da tabela 5457 | Agregados v3 |
| `achar_codigo(produtos, "Sorgo")` | Código de um produto pelo nome | — |
| `montar_url(nivel, localidade, produtos, periodo)` | URL do SIDRA | — |
| `baixar(url)` | Baixa e converte em tabela | SIDRA |
| `para_tabela(json)` | Usa a 1ª linha como cabeçalho, converte valores, gira a tabela (uma coluna por variável) | — |
| `indicadores(tab, anos_secos)` | Área, tendência, R$/ha, variação do rendimento, quebra em anos secos, nota | — |
| `nota_mercado(ind)` | Nota 0–5 (proposta) | — |

### 8.2 Montar a URL

```python
VARIAVEIS = {8331: "area_plantada_ha", 216: "area_colhida_ha", 214: "quantidade_t",
             112: "rendimento_kg_ha", 215: "valor_mil_reais"}

def montar_url(nivel, localidade, codigos_produtos, periodo="last 10"):
    v = ",".join(str(k) for k in VARIAVEIS)
    c = ",".join(str(p) for p in codigos_produtos)
    p = periodo.replace(" ", "%20")
    return f"https://apisidra.ibge.gov.br/values/t/5457/n{nivel}/{localidade}/v/{v}/p/{p}/c782/{c}"
```

### 8.3 Converter a resposta

```python
def para_tabela(dados):
    cabecalho, linhas = dados[0], dados[1:]
    df = pd.DataFrame(linhas).rename(columns=cabecalho)
    df["Valor"] = pd.to_numeric(df["Valor"].replace({"-": "0"}), errors="coerce")  # ".." e "X" viram vazio
    ...
    return tabela  # colunas: produto, ano, area_plantada_ha, area_colhida_ha, quantidade_t, rendimento_kg_ha, valor_mil_reais
```

### 8.4 Fluxo completo

```python
produtos = produtos_da_tabela()
culturas = [achar_codigo(produtos, n) for n in ("Sorgo", "Milho", "Soja")]
mun = codigo_municipio("Monte Carmelo", "MG")
url = montar_url(nivel=6, localidade=mun, codigos_produtos=culturas, periodo="last 10")
tab = baixar(url)
anos_secos = [2021]          # vêm do NASA POWER
print(indicadores(tab, anos_secos))
```

### 8.5 Alternativas prontas

| Linguagem | Pacote | Exemplo |
|---|---|---|
| Python | `sidrapy` | `sidrapy.get_table(table_code="5457", territorial_level="6", ibge_territorial_code="<cód.>", period="last 10")` |
| Python | `DadosAbertosBrasil` | `ibge.sidra(5457, periodos="last 10", localidades={6: <cód.>})` |
| R | `sidrar` | `get_sidra(api = "/t/5457/n6/<cód.>/v/214/p/last%2010/c782/all")` |

---

## 9. Indicadores para o Field Shift

| Indicador | Cálculo | Pergunta que responde |
|---|---|---|
| **Área recente** | Média da área colhida nos últimos 3 anos | A cultura existe na região? Há escala? |
| **Tendência** | Área recente ÷ área dos 3 primeiros anos − 1 | O mercado local cresce ou encolhe? |
| **Valor por hectare** | Valor da produção × 1000 ÷ área colhida | Quanto costuma render em R$/ha? |
| **Variação do rendimento** | Desvio-padrão ÷ média do rendimento (%) | A produtividade é estável? |
| **Rendimento em anos secos** | Média nos anos secos ÷ média nos demais − 1 | Quanto a cultura perde quando falta chuva? (cruza com o NASA POWER) |
| **Nota de mercado (0–5)** | 50% área + 30% tendência + 20% R$/ha, normalizados entre as candidatas | Nota que entra no ranking |

**Os anos secos vêm do NASA POWER:** por exemplo, anos em que a chuva acabou antes de abril no talhão. É aqui que a PAM e o POWER se cruzam.

A fórmula da nota é **proposta** e deve ser revisada pela equipe.

---

## 10. O fluxo no aplicativo

```
 1. Agricultor cadastra                (talhão, soja + milho safrinha, pesos)
              │
              ▼
 2. NASA POWER · clima                 (elimina feijão e trigo)
              │  culturas aprovadas
              ▼
 3. PAM (IBGE) · mercado local  ◄─ ─ ─ Harvest Portal (contexto nacional, complemento)
              │  área, tendência, R$/ha no município/microrregião
              ▼
 4. PAM × NASA POWER                   (quebra de rendimento nos anos secos)
              │
              ▼
 5. Ranking com evidências             (sorgo 1º · milho 2º · milheto 3º)
              │
              ▼
 6. Decisão do agricultor              (com técnico e cooperativa)
```

### 10.1 Comunicação por passo

| Passo | Chamada |
|---|---|
| 3a | `GET servicodados.ibge.gov.br/api/v1/localidades/estados/{UF}/municipios` → código do município e da microrregião |
| 3b | `GET servicodados.ibge.gov.br/api/v3/agregados/5457/metadados` → códigos dos produtos (uma vez, em cache) |
| 3c | `GET apisidra.ibge.gov.br/values/t/5457/n9/{microrregião}/v/8331,216,214,112,215/p/last%2010/c782/{produtos}` |
| 4 | Cálculo local: rendimento (PAM) × anos secos (NASA POWER) |

---

## 11. Exemplo: o agricultor

> ⚠️ Números **fictícios**.

**Passo 1 — cadastro.** Talhão perto de Monte Carmelo/MG. Rotação: soja (out–fev) → milho safrinha (fev–jul). Pesos: clima 4, mercado 3.

**Passo 2 — NASA POWER.** Chuva acaba em meados de abril; geada em junho em 3 de cada 10 anos. Descarta feijão (geada) e trigo (pouca chuva). Aprova sorgo, milho e milheto.

**Passo 3 — PAM, microrregião, 2015–2024:**

| Cultura | Área recente | Tendência | R$/ha | Nota de mercado |
|---|---|---|---|---|
| Milho | 120 mil ha | +20% | 5.800 | 4,5 |
| Sorgo | 8 mil ha | +60% | 3.900 | 3,5 |
| Milheto | 300 ha | Estável | 1.500 | 1,0 |

**Passo 4 — PAM × NASA POWER.** Nos 3 anos em que a chuva acabou antes de abril (NASA POWER), o rendimento do milho no município caiu **30%**; o do sorgo, **10%** (PAM).

**Passo 5 — ranking:**

| Posição | Cultura | Clima | Mercado local | Final |
|---|---|---|---|---|
| 1º | Sorgo | 4,5 | 3,5 | 4,1 |
| 2º | Milho | 2,5 | 4,5 | 3,4 |
| 3º | Milheto | 4,8 | 1,0 | 3,2 |

**O que o agricultor vê:**

> 📈 **Sorgo: melhor equilíbrio para você.** Aguenta melhor o fim de chuva em abril. Na sua microrregião, o sorgo já ocupa 8 mil hectares, essa área cresceu 60% em 10 anos, e nos anos secos ele perdeu só 10% de produtividade, contra 30% do milho.
> *Clima: NASA POWER (grade de ~55 km). Mercado e produtividade: IBGE/PAM 2015–2024 (microrregião).*
> ⚠️ Confirme com sua cooperativa preço e demanda nesta safra.

**Passo 6 — decisão.** O agricultor leva o relatório ao técnico, confirma comprador e decide testar sorgo em um talhão.

---

## 12. Caso de uso UC-04

### 12.1 Ficha

| Item | Descrição |
|---|---|
| **Nome** | UC-04 · Avaliar o mercado local das culturas aprovadas com a PAM do IBGE |
| **Ator principal** | Agricultor |
| **Ator de sistema** | Back-end do Field Shift |
| **Sistemas externos** | API do SIDRA, API de Agregados v3, API de Localidades v1 |
| **Objetivo** | Dar a cada cultura aprovada no filtro climático uma nota de mercado **regional**, com evidência de produtividade em anos secos |
| **Gatilho** | O filtro climático (NASA POWER) termina |
| **Pré-condições** | 1) Talhão no Brasil. 2) Culturas aprovadas no filtro. 3) Anos secos identificados pelo NASA POWER. 4) Códigos dos produtos em cache (seção 7) |
| **Sucesso** | Cada cultura tem nota de mercado local e os cartões de evidência citam "IBGE/PAM" e a escala |
| **Falha** | Usa a nota nacional do Harvest Portal, ou "mercado não verificado" |

### 12.2 Fluxo principal

| # | Quem | O que acontece |
|---|---|---|
| 1 | Back-end | Recebe as culturas aprovadas e a coordenada do talhão |
| 2 | Back-end | Descobre o município e a microrregião (Localidades, em cache) |
| 3 | Back-end | Traduz as culturas para os códigos de produto da tabela 5457 (cache) |
| 4 | Back-end | Chama a API do SIDRA para a microrregião, últimos 10 anos, 5 variáveis |
| 5 | Back-end | Converte a resposta, trata `..`/`X` como ausente |
| 6 | Back-end | Calcula área, tendência, R$/ha, variação e quebra nos anos secos |
| 7 | Back-end | Calcula a nota de mercado e combina com a nota de clima |
| 8 | Agricultor | Vê o ranking com evidências do IBGE e do NASA POWER |

### 12.3 Fluxos alternativos

| Código | Situação | O que acontece |
|---|---|---|
| **A1** | Cultura sem dado na microrregião (abaixo de 1 ha/1 t) | "Não é plantada na sua região"; nota de mercado baixa e aviso |
| **A2** | Dado da microrregião com `X` (sigilo) | Sobe para mesorregião ou UF e informa a escala |
| **A3** | Talhão fora do Brasil | Pula a PAM e usa o Harvest Portal |
| **A4** | Agricultor muda os pesos | Recalcula o ranking sem chamar a API |

### 12.4 Fluxos de exceção

| Código | Situação | O que acontece |
|---|---|---|
| **E1** | API do SIDRA fora do ar ou lenta | Usa cache; sem cache, usa o Harvest Portal |
| **E2** | Consulta excede o limite de valores | Divide em várias consultas (por produto ou por período) |
| **E3** | Código de produto mudou | Recarrega os metadados da tabela 5457 |

### 12.5 Critérios de aceite

| # | Dado que... | Quando... | Então... |
|---|---|---|---|
| 1 | Sorgo, milho e milheto aprovados | O UC-04 roda | Cada um tem área, tendência, R$/ha e nota |
| 2 | O NASA POWER marcou 2021 como ano seco | O UC-04 roda | A evidência mostra a perda de rendimento em 2021 |
| 3 | Milheto não aparece na microrregião | O UC-04 roda | Aparece "não é plantado na sua região", sem nota inventada |
| 4 | SIDRA fora do ar e sem cache | O UC-04 roda | Ranking usa o Harvest Portal ou "mercado não verificado" |
| 5 | Valor `X` na resposta | O UC-04 roda | Não vira zero; sobe de escala |

---

## 13. Testes realizados

| Teste | Resultado |
|---|---|
| `py_compile` de `pam_sidra.py` | ✅ |
| `teste_offline.py`: resposta falsa no formato do SIDRA (cabeçalho na 1ª linha, `D1`…`D4`) | ✅ Converteu para tabela com uma coluna por variável |
| Indicadores com dados fictícios (milho e sorgo; 2021 como ano seco) | ✅ Milho: área 48 mil ha, +20%, R$ 5.792/ha, −33% em ano seco. Sorgo: 4 mil ha, +60%, R$ 3.900/ha, −10% em ano seco |
| URL gerada | ✅ `.../values/t/5457/n6/0000000/v/8331,216,214,112,215/p/last%2010/c782/1,2` |
| Chamada às APIs reais do IBGE | ❌ Não testada (sem acesso de rede) |

**Para testar:**

```bash
cd ibge-pam-exemplo
python teste_offline.py          # sem internet
python pam_sidra.py --descobrir  # com internet: confirma códigos
python pam_sidra.py              # com internet: indicadores reais de Monte Carmelo
```

---

## 14. Limitações

| Limitação | Consequência |
|---|---|
| **Fora da lista oficial do desafio** | Complemento, não fonte principal |
| **Escala municipal** | Não diferencia fazendas; usar microrregião para estabilidade |
| **Só 64 produtos** | Culturas de cobertura (braquiária, crotalária) provavelmente não aparecem |
| **Corte de 1 ha / 1 t** | Culturas pequenas aparecem como ausentes |
| **Valor nominal** | Corrigir pelo IPCA para comparar anos |
| **Defasagem** | O ano mais recente sai em setembro do ano seguinte |
| **Ano civil** | Safrinha pode cair no ano seguinte ao plantio |
| **Só Brasil** | Fora do Brasil, usar o Harvest Portal |
| **Instabilidade do site** | O portal do IBGE exibia aviso de instabilidade; usar cache |

---

## 15. Boas práticas

1. **Baixe e guarde antes da demo** (cache por microrregião e produto).
2. **Use microrregião** como padrão e mostre o município como detalhe.
3. **Confirme os códigos** com `--descobrir` e com os metadados da tabela 5457.
4. **Nunca trate `..` ou `X` como zero.**
5. **Corrija o valor pela inflação** antes de comparar anos.
6. **Cite sempre "IBGE/PAM" e a escala** ao lado do número.
7. **Peça só as variáveis e os produtos necessários** para não estourar o limite da API.

---

## 16. Referências

**IBGE — PAM**
- Página da pesquisa: https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html
- Tabelas da PAM no SIDRA: https://sidra.ibge.gov.br/pesquisa/pam/tabelas
- Tabela 5457: https://sidra.ibge.gov.br/tabela/5457
- PAM 2024 — Informativo: https://biblioteca.ibge.gov.br/visualizacao/periodicos/66/pam_2024_v51_br_informativo.pdf
- PAM 2024 — Notas técnicas: https://biblioteca.ibge.gov.br/visualizacao/periodicos/66/pam_2024_v51_br_notas_tecnicas.pdf
- PAM 2023 — Apresentação de resultados: https://agenciadenoticias.ibge.gov.br/media/com_mediaibge/arquivos/3e44fdaa85766c6fa1e8aad80b7626eb.pdf
- Agência IBGE — PAM 2024: https://agenciadenoticias.ibge.gov.br/pt/agencia-noticias/44465-pam-2024-com-queda-nos-precos-e-na-safra-de-graos-valor-da-producao-agricola-cai-pelo-segundo-ano-seguido.html
- Metadados da PAM (SNIF, 2025): https://dados.florestal.gov.br/pt_BR/dataset/2e0b7844-0039-4a23-a2ed-14f353fe4b29/resource/b89cbe41-121f-4ce4-9b02-bcde32b8391c/download/metadados_pam_ibge_2025.pdf

**APIs do IBGE**
- Ajuda da API do SIDRA: https://apisidra.ibge.gov.br/home/ajuda
- API de Agregados v3: https://servicodados.ibge.gov.br/api/docs/agregados?versao=3
- API de Localidades: https://servicodados.ibge.gov.br/api/docs/localidades
- API de Malhas v3: https://servicodados.ibge.gov.br/api/docs/malhas?versao=3

**Clientes e códigos**
- `sidrar` (R): https://cran.r-project.org/web/packages/sidrar/sidrar.pdf
- `sidra` (R, Agregados v3): https://github.com/rodrigoesborges/sidra
- `DadosAbertosBrasil` (Python): https://www.gustavofurtado.com/DadosAbertosBrasil/referencia/ibge/
- `datazoom.amazonia` — códigos de variáveis da PAM: https://rdrr.io/cran/datazoom.amazonia/src/R/pam.R
