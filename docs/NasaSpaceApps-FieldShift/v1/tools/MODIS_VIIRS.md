# MODIS e VIIRS — Análise e documentação

## Índices de vegetação em séries longas (250–1000 m)

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP (Field Shift Brasil) · 14 de novembro de 2026*

> ⚠️ Todos os números do caso hipotético (seção 15) são fictícios. As aplicações descrevem possibilidades para o projeto, não funcionalidades já implementadas.

---

## Sumário

1. [Como ler este documento](#1-como-ler-este-documento)
2. [⚠️ Alerta: transição MODIS → VIIRS](#2-️-alerta-transição-modis--viirs)
3. [De onde vêm os dados](#3-de-onde-vêm-os-dados)
4. [Produtos](#4-produtos)
5. [Formas de acesso](#5-formas-de-acesso)
6. [Parâmetros explicados](#6-parâmetros-explicados)
7. [Estrutura dos dados](#7-estrutura-dos-dados)
8. [Tratamento dos dados no Field Shift](#8-tratamento-dos-dados-no-field-shift)
9. [Como testar](#9-como-testar)
10. [Códigos de erro e problemas comuns](#10-códigos-de-erro-e-problemas-comuns)
11. [Limitações](#11-limitações)
12. [Boas práticas](#12-boas-práticas)
13. [Como e por que usar MODIS/VIIRS no Field Shift](#13-como-e-por-que-usar-modisviirs-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `NASA_POWER.md`. Autenticação e AppEEARS em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Camadas, escalas e preenchimentos do **MOD13Q1 v061** e do **VJ113A1 v002** nas páginas do Earthdata [1][3]; significado do *pixel reliability*, bits do *VI Quality* e método de compósito no **guia do usuário MOD13 C6.1** [2]; situação das missões no alerta oficial de transição [4], em 14/11/2026. **Nenhum download executado ao vivo.**

**O que vem do contexto e o que foi acrescentado.** MODIS NDVI como obrigatório e o limiar de NDVI 0,25 para solo exposto vêm do repositório [10][11]. O restante foi acrescentado.

---

## 2. ⚠️ Alerta: transição MODIS → VIIRS

| Fato | Fonte |
|---|---|
| **Terra e Aqua (MODIS) devem começar a ser desligados no fim de 2026 ou início de 2027** | [4] |
| Os dois satélites já estão saindo da órbita original (muda o horário de passagem) | [4] |
| Haverá um reprocessamento final dos dados MODIS | [4] |
| **Suomi NPP (VIIRS) não terá novas observações a partir de 02/11/2026** | aviso no site do Earthdata, citado em [4] |
| A NASA recomenda migrar para produtos VIIRS | [4][5] |

**Consequência:** o **histórico MODIS (2000–2026)** continua ótimo para diagnóstico. Para dados novos, use o VIIRS do **NOAA-20** (`VJ113A1`).

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | MODIS (Terra/Aqua) e VIIRS (NOAA-20) medem a refletância em várias bandas, com revisita quase diária | NASA, NOAA | [4] |
| 2. Refletância de superfície | Correção atmosférica diária | Equipes de terra MODIS/VIIRS | [2] |
| 3. Compósito de 16 dias | Após filtros de qualidade, nuvem e geometria, o método **CV-MVC** compara as duas observações de maior NDVI e escolhe a mais próxima do nadir; se as condições forem ruins, usa o maior NDVI (MVC) | Equipe MODIS | [2] |
| 4. Índices e qualidade | NDVI, EVI, camadas *VI Quality* e *pixel reliability* | Equipe MODIS | [2] |
| 5. Distribuição | **LP DAAC** (Earthdata Cloud), grade senoidal em tiles | LP DAAC | [1][3] |
| 6. Acesso | AppEEARS, Earthdata Search, earthaccess, Worldview | Usuário | [1][9] |
| 7. Field Shift | Filtro de qualidade, escala, suavização, curva típica (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Satélites passam todo dia; a NASA escolhe, a cada 16 dias, a melhor imagem de cada pedaço do mapa. Assim dá para ver, ano após ano, quando o campo está verde e quando está descoberto."

O compósito pode criar descontinuidades espaciais, porque pixels vizinhos podem vir de dias diferentes [2].

---

## 4. Produtos

| Nome curto | Satélite | Conteúdo | Resolução | Período | Fonte |
|---|---|---|---|---|---|
| **MOD13Q1** v061 | Terra | NDVI, EVI, 16 dias | **250 m** | 18/02/2000 – fim da missão | [1] |
| MYD13Q1 v061 | Aqua | NDVI, EVI, 16 dias | 250 m | 2002 – fim da missão | — |
| **VJ113A1** v002 | **NOAA-20** | NDVI, EVI, EVI2, 16 dias | **500 m** | 01/01/2018 – presente | [3] |
| VNP13A1 v002 | Suomi NPP | NDVI, EVI, EVI2, 16 dias | 500 m | sem dados novos após 11/2026 | [4][6] |

A versão 6 do MOD13A1 foi descontinuada; use a **6.1 (061)** [7].

---

## 5. Formas de acesso

| Ferramenta | O que faz | Fonte |
|---|---|---|
| **AppEEARS** | Série por ponto (CSV) ou área; decodifica a qualidade | [8][9] |
| **AppEEARS — serviço de qualidade** | `GET /quality/{produto}/{camada}/{valor}` traduz um valor de qualidade em texto | [8] |
| **Earthdata Search / earthaccess** | Busca e download | [1] |
| **NASA Worldview** | Visualizar camadas | — |
| **LAADS DAAC** | Planejamento da transição MODIS → VIIRS | [5] |

---

## 6. Parâmetros explicados

### 6.1 Pedido no AppEEARS

Campos do `POST /task` iguais aos de `SMAP.md` (seção 6.2). Específico:

| Campo | Valor | Observação |
|---|---|---|
| `layers[].product` | `MOD13Q1.061`, `VJ113A1.002` ⚠️ | Confirme com `GET /product` |
| `layers[].layer` | NDVI, pixel reliability, composite day of the year | Ex.: `_250m_16_days_NDVI` ⚠️ (padrão de nome visto no serviço de qualidade [8]); confirme com `GET /product/{id}` |
| `dates` | 02-18-2000 até a data desejada | Uma linha a cada 16 dias |

### 6.2 Serviço de qualidade do AppEEARS [8]

| Chamada | Retorna |
|---|---|
| `GET /quality` | Camadas que têm qualidade associada |
| `GET /quality/{produto}` | Pares camada → camada de qualidade do produto |
| `GET /quality/{produto}/{camada_qualidade}` | Significado de cada valor de cada campo de bits, com indicação `Acceptable` |
| `GET /quality/{produto}/{camada_qualidade}/{valor}` | Decodifica um inteiro (ex.: 4160 → "VI produced, good quality") |

O tutorial usa o endereço antigo da API (`lpdaacsvc.cr.usgs.gov`); hoje a base é `appeears.earthdatacloud.nasa.gov/api` [8][9].

---

## 7. Estrutura dos dados

### 7.1 MOD13Q1 v061 [1]

| Camada | Escala | Preenchimento | Faixa válida | Tipo |
|---|---|---|---|---|
| `250m 16 days NDVI` | **0,0001** | **−3000** | −2000 a 10000 | int16 |
| `250m 16 days EVI` | 0,0001 | −3000 | −2000 a 10000 | int16 |
| `250m 16 days VI Quality` | bits | 65535 | 0 a 65534 | uint16 |
| `250m 16 days pixel reliability` | — | −1 | 0 a 3 | int8 |
| `250m 16 days composite day of the year` | — | −1 | 1 a 366 | int16 |
| `250m 16 days red / NIR / blue / MIR reflectance` | 0,0001 | −1000 | 0 a 10000 | int16 |
| `250m 16 days view / sun zenith angle` | 0,01 | −10000 | 0 a 18000 | int16 |
| `250m 16 days relative azimuth angle` | 0,01 | −4000 | −18000 a 18000 | int16 |

Formato HDF-EOS2 [1].

### 7.2 Pixel reliability (MOD13Q1) [2]

| Valor | Significado | Uso |
|---|---|---|
| −1 | Preenchimento / não processado | Descartar |
| **0** | **Dado bom** — usar com confiança | Manter |
| **1** | **Marginal** — útil, mas ver outras informações de qualidade | Manter com cautela |
| 2 | Neve/gelo | Descartar |
| 3 | Nuvem — alvo não visível | Descartar |

### 7.3 VI Quality (bits) [2]

| Bits | Campo | Valores |
|---|---|---|
| 0–1 | Qualidade VI (MODLAND) | 00 boa; 01 produzido, ver outras QA; 10 provavelmente nublado; 11 não produzido |
| 2–5 | Utilidade do VI | 0000 (melhor) a 1100 (pior); 1101 qualidade baixa demais; 1110 L1B com falha; 1111 não útil |
| 6–7 | Quantidade de aerossol | 00 climatologia; 01 baixa; 10 intermediária; 11 alta |
| 8 | Nuvem adjacente | 1 = sim |
| 10 | Nuvens mistas | 1 = algum pixel de 250 m agregado tinha nuvem |
| 11–13 | Máscara terra/água | 7 classes |
| 14 | Possível neve/gelo | 1 = sim |
| 15 | Possível sombra | 1 = sim |

### 7.4 VJ113A1 v002 [3]

| Camada | Escala | Preenchimento | Faixa válida |
|---|---|---|---|
| NDVI, EVI, EVI2 | ÷ 10000 | −15000 | −10000 a 10000 |
| Pixel reliability | — | −4 | 0 a 11 |

Formato HDF-EOS5 (`.h5`). **Preenchimento e escala do pixel reliability diferem do MODIS** [3].

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Pedido | AppEEARS `point`: NDVI, pixel reliability e composite day of the year do MOD13Q1 (2000–2026) e do VJ113A1 (2018–hoje) | CSV pronto, sem HDF |
| 2. Ausentes | Remover −3000 (MODIS) e −15000 (VIIRS) | Não confundir com NDVI baixo |
| 3. Escala | Multiplicar por 0,0001 (ou dividir por 10000), se o CSV não vier escalado ⚠️ | NDVI real entre −1 e 1 |
| 4. Qualidade | Manter pixel reliability 0 e 1 (MODIS) [2]; para o VIIRS, usar a tabela própria do produto ⚠️ | Remover nuvem e neve |
| 5. Data real | Usar o *composite day of the year* como data da observação | O pixel vem de um dia específico dentro dos 16 |
| 6. Emenda MODIS/VIIRS | Comparar 2018–2026, quando os dois existem; aplicar ajuste linear se houver viés | Sensores diferentes |
| 7. Suavização | Mediana móvel ou Savitzky-Golay | Curva sazonal estável |
| 8. Curva típica | Mediana por período de 16 dias do ano | Climatologia de NDVI |
| 9. Indicadores | Duração do solo exposto (NDVI < 0,25), picos, anomalia por ano | Diagnóstico |
| 10. Armazenamento | Série tratada por talhão, com sensor de origem de cada data | Rastreabilidade |

```python
import pandas as pd

df = pd.read_csv("MOD13Q1-061-results.csv", parse_dates=["Date"])
ndvi = [c for c in df.columns if c.endswith("NDVI")][0]                # ⚠️ ajuste
rel  = [c for c in df.columns if "pixel_reliability" in c.lower()][0]
doy  = [c for c in df.columns if "composite_day" in c.lower()][0]

df = df[(df[ndvi] > -0.3) & (df[rel].isin([0, 1]))]                    # passos 2–4
df["data_obs"] = pd.to_datetime(df["Date"].dt.year.astype(str), format="%Y") \
                 + pd.to_timedelta(df[doy] - 1, unit="D")              # passo 5
s = df.set_index("data_obs")[ndvi].sort_index().rolling(3, center=True, min_periods=1).median()
exposto = s[s < 0.25]
print(exposto.groupby(exposto.index.month).size())                    # meses de solo exposto
```
⚠️ Confira se o AppEEARS já entregou o NDVI escalado (valores entre −1 e 1) e ajuste o passo 2 conforme a escala. Cuidado com compósitos na virada do ano ao calcular a data real.

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | `GET /product/MOD13Q1.061` | Camadas da tabela 7.1 |
| 2 | Pedido de 1 ano | ~23 linhas |
| 3 | NDVI | Entre −0,2 e 1 após escala |
| 4 | Filtro de reliability | Remove pontos do verão chuvoso |
| 5 | Curva de soja + safrinha | Dois picos e um vale em ago–out |
| 6 | MOD13Q1 × VJ113A1 (2018–2026) | Mesma forma, valores próximos |
| 7 | Decodificar 4160 no serviço de qualidade | "VI produced, good quality" [8] |
| 8 | Ponto sobre represa | NDVI negativo ou ~0 |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução |
|---|---|---|
| AppEEARS 401 / 403 / 429 | Credencial, token expirado, taxa | Ver `comunicacao-entre-apis.md` [9] |
| Série termina em 2026 | Fim do MODIS | Continuar com VJ113A1 [4] |
| Série VNP13A1 sem dados novos | Fim do Suomi NPP | Usar VJ113A1 [4] |
| Salto entre MODIS e VIIRS | Sensores diferentes | Passo 6 (emenda) |
| NDVI −0,3 em vários pontos | Preenchimento não removido | Passo 2 |

---

## 11. Limitações

1. **250 m (MODIS) e 500 m (VIIRS)** misturam talhões e bordas de mata.
2. **Fim do MODIS** e deriva de órbita [4].
3. **Suomi NPP encerrado** [4].
4. **Diferenças entre sensores**.
5. **Compósito de 16 dias** atrasa a detecção de eventos curtos; pixels vizinhos podem vir de dias diferentes [2].
6. **Nuvens persistentes** geram pixels marginais.
7. **NDVI satura** em vegetação densa (use EVI) [1].
8. **Palhada** tem NDVI parecido com solo nu.

---

## 12. Boas práticas

1. **MODIS para o histórico, VIIRS NOAA-20 para o presente**, indicando o sensor de cada trecho.
2. **Filtre a qualidade** (reliability 0–1) [2].
3. Use o **composite day of the year**.
4. Calcule **curva típica** e **anomalia**.
5. Complemente com **Landsat/HLS** no talhão.
6. Avise que **palhada pode parecer solo nu**.

---

## 13. Como e por que usar MODIS/VIIRS no Field Shift

> Contexto: **MOD13Q1** está entre os **6 obrigatórios** (D-002) [10]; o §14 do `CONTEXTO-DESAFIO.md` usa "NDVI abaixo de 0,25" como evidência de solo exposto [11].

| Motivo | Por que importa |
|---|---|
| **25 anos de série regular** | "Em 20 de 25 anos o campo ficou descoberto de agosto a outubro" |
| **Compósito sem falhas** | Valor a cada 16 dias, mesmo no verão |
| **Responde ao desafio** | "Times when fields are typically bare" e "seasonal transitions" |
| **AppEEARS** | CSV pronto com qualidade decodificada |
| **Continuidade com VIIRS** | A ferramenta segue funcionando após o MODIS |

| Etapa | Papel |
|---|---|
| Diagnóstico | Solo exposto, datas de plantio e colheita, anos de baixo vigor |
| Candidatas | Janelas vazias onde cabe cultura de cobertura |
| Pontuação | Critério **proteção do solo** |
| Telas | Curva de NDVI no fundo do calendário de 12 meses |

**Não resolve:** detalhe no talhão (Landsat/HLS), palhada × solo nu (SWIR ou agricultor), cultura plantada (MapBiomas ou agricultor).

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| Curva típica de NDVI | Mediana por período de 16 dias do ano | Calendário de cobertura |
| Duração do solo exposto | Dias com NDVI suavizado < 0,25 | Proteção do solo |
| Pico de vigor por safra | Máximo do NDVI por ciclo | Comparar anos |
| Anomalia de NDVI | Valor − curva típica no mesmo período | Anos de estresse |
| Datas de plantio/colheita | Subida e queda da curva (com o *composite day of the year*) | Calendário real |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `NASA_POWER.md` (seção 16).

**Dados usados:** MOD13Q1 v061 (2001–2025) e VJ113A1 v002 (2018–2025), pixel reliability 0–1, tratados conforme a seção 8.

| Indicador | Valor |
|---|---|
| Pico da soja | 0,82 (meados de janeiro) |
| Pico da safrinha | 0,68 (meados de abril) |
| NDVI médio ago–out | **0,19** |
| Anos (de 25) com NDVI < 0,25 por mais de 60 dias | **20** |
| Anos com pico da safrinha 20% abaixo do normal | 6 (coincidem com os veranicos do POWER) |

> 🟫 **Seu campo fica descoberto cerca de 3 meses por ano.**
> *De onde vem: satélites MODIS (2001–2025) e VIIRS (2018–2025), pixels de 250–500 m.*
> *Atenção: palhada seca também aparece assim.*

**Efeito:** evidência principal da estratégia B; POWER, SMAP e MODIS contam a mesma história nos anos ruins (confiança **Alta**). A ressalva da palhada vira pergunta ao Sr. José na ferramenta.

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NASA Earthdata. MOD13Q1 v061: descrição, cobertura, formato e tabela de camadas (escala, preenchimento, faixas). <https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13q1-061>
2. NASA LP DAAC. MOD13 User Guide C6.1: pixel reliability, bits do VI Quality, método CV-MVC. <https://LPDAAC.USGS.GOV/documents/621/MOD13_User_Guide_V61.pdf>
3. NASA Earthdata. VJ113A1 v002 (VIIRS NOAA-20): camadas, escala, preenchimento, período. <https://www.earthdata.nasa.gov/data/catalog/lpcloud-vj113a1-002>
4. NASA Earthdata. Alerta: transição de MODIS para VIIRS. <https://www.earthdata.nasa.gov/data/alerts-outages/transition-from-modis-viirs>
5. NASA LAADS DAAC. MODIS to VIIRS Transition. <https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition/>
6. NASA Earthdata. Alerta: VIIRS Version 2 Vegetation Indices. <https://www.earthdata.nasa.gov/data/alerts-outages/viirs-version-2-vegetation-indices-products-released>
7. NASA Earthdata. MOD13A1 v006 (descontinuado; recomenda a 6.1). <https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13a1-006>
8. NASA Earthdata. Tutorial: serviço de qualidade do AppEEARS para camadas MODIS. <https://www.earthdata.nasa.gov/learn/tutorials/use-appeears-quality-service-extract-information-from-modis-quality-layers>
9. NASA LP DAAC. AppEEARS API. <https://appeears.earthdatacloud.nasa.gov/api/>

### 16.2 Base do projeto

10. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` (D-002).
11. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md` (§14) e `bancos-de-dados-field-shift-brasil.md`.

*Consulta das fontes: 14 de novembro de 2026. A situação das missões muda rapidamente; confira o alerta [4] antes da implementação.*
