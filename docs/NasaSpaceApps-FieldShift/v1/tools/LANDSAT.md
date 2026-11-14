# Landsat (e HLS) — Análise e documentação

## Refletância e índices de vegetação a 30 m

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP (Field Shift Brasil) · 14 de novembro de 2026*

> ⚠️ Todos os números do caso hipotético (seção 15) são fictícios. As aplicações descrevem possibilidades para o projeto, não funcionalidades já implementadas.

---

## Sumário

1. [Como ler este documento](#1-como-ler-este-documento)
2. [Visão geral](#2-visão-geral)
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
13. [Como e por que usar o Landsat no Field Shift](#13-como-e-por-que-usar-o-landsat-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `NASA_POWER.md`. Autenticação e AppEEARS em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Processamento, fatores de escala, faixas válidas, bits de qualidade, disponibilidade por satélite e limitações foram conferidos nas páginas oficiais do USGS; o HLS, na página do produto no Earthdata, em 14/11/2026. **Nenhum download executado ao vivo.**

**O que vem do contexto e o que foi acrescentado.** Landsat como complementar e a inconsistência I-2 (Landsat × MODIS no exemplo do "seu Antônio") vêm do repositório [12]. O restante foi acrescentado.

---

## 2. Visão geral

**Landsat** é a série NASA/USGS de imagens da superfície terrestre com registro contínuo mais longo. O produto recomendado é o **Collection 2 Level-2**, com refletância de superfície já corrigida da atmosfera [1].

| Item | Valor | Fonte |
|---|---|---|
| Satélites em operação | Landsat 8 (desde 04/2013) e Landsat 9 (desde 10/2021) | [1] |
| Histórico em Level-2 | Landsat 4 (1982–1993), 5 (1984–2012), 7 (1999–04/2022) | [1] |
| Resolução | 30 m | [1] |
| Revisita | 16 dias por satélite; 8 dias com 8 e 9 | enunciado do desafio, [11] |
| Disponibilidade | Novos produtos SR em geral até 24 h após o processamento Tier 1/2 | [1] |
| Formato | Cloud Optimized GeoTIFF | [1] |

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | Sensores OLI/OLI-2 (óptico) e TIRS (térmico) medem a luz refletida e o calor emitido | Landsat 8/9 (NASA/USGS) | [1] |
| 2. Level-1 | Correção geométrica e radiométrica; cenas classificadas em Tier 1/Tier 2 | USGS EROS | [1] |
| 3. Refletância de superfície | Algoritmo **LaSRC** (v1.5.0) remove o efeito da atmosfera usando aerossóis e dados auxiliares MODIS/VIIRS | USGS EROS | [1] |
| 4. Qualidade | Bandas `QA_PIXEL`, `QA_RADSAT`, `SR_QA_AEROSOL` | USGS EROS | [3] |
| 5. Distribuição | **USGS EROS** (EarthExplorer, nuvem) | USGS | [1] |
| 5b. Harmonização (HLS) | Landsat e Sentinel-2 harmonizados na mesma grade de 30 m (MGRS), com correção BRDF | NASA (distribuído pelo **LP DAAC**) | [5] |
| 6. Acesso | EarthExplorer; HLS por AppEEARS, earthaccess, CMR | Usuário | [1][5] |
| 7. Field Shift | Escala, máscara de nuvem, NDVI, compósitos (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Satélites fotografam seu campo a cada poucos dias, em pixels de 30 m. A NASA corrige a influência da atmosfera, e o verde da lavoura vira um índice que mostra onde ela está mais forte ou mais fraca."

---

## 4. Produtos

| Produto | O que é | Quando usar | Fonte |
|---|---|---|---|
| **C2 Level-2 Surface Reflectance** | Refletância por banda | Índices de vegetação; histórico antes de 2013 | [1][6] |
| **C2 Level-2 Surface Temperature** | Temperatura da superfície | Calor da superfície | [4] |
| **HLS v2.0** (`HLSL30`, `HLSS30`) | Landsat + Sentinel-2 harmonizados, 30 m, revisita combinada de ~1,6 dia | **Séries temporais recentes** | [5] |

---

## 5. Formas de acesso

| Ferramenta | Oferece | Login | Fonte |
|---|---|---|---|
| **USGS EarthExplorer** | Landsat. Caminho: *Data Sets* → *Landsat* → *Landsat Collection 2 Level-2* | Conta USGS | [1][8] |
| **USGS M2M API** | Download automatizado ⚠️ exige conta USGS e pedido de acesso | Conta USGS | — |
| **AppEEARS** | HLS por ponto ou área | Earthdata | [9] |
| **Earthdata Search / earthaccess / CMR** | HLS direto da nuvem (COG) | Earthdata | [5][10] |

**Recomendado:** HLS via AppEEARS (ponto) ou earthaccess (área), com a mesma conta Earthdata das outras fontes.

---

## 6. Parâmetros explicados

### 6.1 AppEEARS (HLS por ponto)

Campos do `POST /task` iguais aos de `SMAP.md` (seção 6.2). Específico:

| Campo | Valor | Observação |
|---|---|---|
| `layers[].product` | `HLSL30.020` e `HLSS30.020` ⚠️ | Confirme com `GET /product` |
| `layers[].layer` | Vermelho, NIR e `Fmask` | No HLSL30, vermelho = `B04` e NIR = `B05`; no HLSS30, NIR = `B8A` ⚠️ |

### 6.2 earthaccess (HLS por área)

| Argumento | Exemplo |
|---|---|
| `short_name` | `"HLSL30"` ou `"HLSS30"` |
| `version` | `"2.0"` |
| `bounding_box` | `(-47.0, -19.0, -46.8, -18.8)` |
| `temporal` | `("2024-08-01", "2024-08-31")` |

### 6.3 EarthExplorer (Landsat C2 L2)

| Filtro | Escolha |
|---|---|
| Área | Polígono ou coordenada |
| Período | Datas desejadas |
| Data set | Landsat 8–9 OLI/TIRS C2 L2 |
| Cobertura de nuvem | Filtro por percentual (critério adicional) |

---

## 7. Estrutura dos dados

### 7.1 Bandas do Landsat 8/9 para vegetação

| Banda | Faixa | Uso |
|---|---|---|
| B2 | Azul | EVI |
| **B4** | **Vermelho** | **NDVI** |
| **B5** | **NIR** | **NDVI** |
| B6, B7 | SWIR | Água na vegetação, palhada × solo |
| B10 | Térmica | Temperatura |

O USGS recomenda **não usar as bandas 1 e 2 do OLI** em análises [1].

### 7.2 Escala (Collection 2 Level-2) [2]

| Produto | Fórmula | Preenchimento | Faixa válida (DN) | Tipo |
|---|---|---|---|---|
| Refletância | `DN × 0,0000275 − 0,2` | 0 | 7273–43636 | uint16 |
| Temperatura | `DN × 0,00341802 + 149,0` (K) | 0 | 293–65535 | uint16 |

Exemplo oficial: DN 18.639 → **0,313** de refletância; DN 44.947 → **302,6 K** [2].

### 7.3 Bits do `QA_PIXEL` (Landsat 8/9) [3]

| Bit | Significado (quando = 1) |
|---|---|
| 0 | Preenchimento |
| 1 | Nuvem dilatada |
| 2 | Cirros (alta confiança) |
| 3 | **Nuvem** (alta confiança) |
| 4 | **Sombra de nuvem** (alta confiança) |
| 5 | Neve |
| 6 | **Céu limpo** (nem nuvem nem nuvem dilatada) |
| 7 | Água |
| 8–9 | Confiança de nuvem (00 não definido, 01 baixa, 10 média, 11 alta) |
| 10–11 | Confiança de sombra |
| 12–13 | Confiança de neve/gelo |
| 14–15 | Confiança de cirros |

`SR_QA_AEROSOL` (L8/9): bits 6–7 indicam o nível de aerossol (00 climatologia, 01 baixo, 10 médio, 11 alto). O USGS recomenda evitar pixels com aerossol alto [1][3].

### 7.4 HLS [5]

| Item | Valor |
|---|---|
| Escala das bandas espectrais | 0,0001 |
| Escala das bandas de ângulo | 0,01 |
| Qualidade | `Fmask` (bits, uint8, preenchimento 255) |
| Bandas do HLSS30 | 13, incluindo 3 de *red edge* |
| Arquivo | Um COG por banda; nome com o tile (ex.: `T17SLU`) |

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Busca | Cenas HLS (L30 + S30) do tile do talhão | Mais imagens do que o Landsat sozinho |
| 2. Recorte | Só a área da fazenda | Um tile tem ~110 × 110 km |
| 3. Escala | Bandas × 0,0001 (HLS) ou `DN × 0,0000275 − 0,2` (Landsat C2) | Sem isso, o NDVI sai errado |
| 4. Máscara | Descartar nuvem, sombra, cirros, neve, água (`Fmask` ou bits 1, 2, 3, 4 do `QA_PIXEL`) e aerossol alto | Nuvem e sombra falseiam o índice |
| 5. Índices | NDVI = (NIR − V)/(NIR + V); NDMI com SWIR | Vigor e água na vegetação |
| 6. Compósito | Mediana mensal (ou de 16 dias) por pixel | Reduz ruído e falhas |
| 7. Suavização | Média móvel ou Savitzky-Golay na série do talhão | Detectar datas com estabilidade |
| 8. Eventos | Solo exposto: NDVI < ~0,25 por 30+ dias; zonas fracas recorrentes | Diagnóstico do talhão |
| 9. Comparação | Mesma curva com MODIS | Concordância alimenta a confiança |
| 10. Armazenamento | GeoTIFF mensal por talhão + série em CSV | Mapas e reprodutibilidade |

```python
import earthaccess, rioxarray, numpy as np

earthaccess.login()
res = earthaccess.search_data(short_name="HLSL30", version="2.0",
                              bounding_box=(-47.0, -19.0, -46.8, -18.8),
                              temporal=("2024-08-01", "2024-08-31"))
g = res[0]
link = lambda b: next(l for l in g.data_links() if l.endswith(f".{b}.tif"))
red  = rioxarray.open_rasterio(link("B04"), masked=True) * 0.0001     # passo 3
nir  = rioxarray.open_rasterio(link("B05"), masked=True) * 0.0001
fmask = rioxarray.open_rasterio(link("Fmask")).astype("uint8")
# passo 4: bits 1 (nuvem), 2 (adjacente), 3 (sombra) do Fmask ⚠️ confirme no guia do HLS
ruim = ((fmask >> 1) & 1) | ((fmask >> 2) & 1) | ((fmask >> 3) & 1)
ndvi = ((nir - red) / (nir + red)).where(ruim == 0)                    # passo 5
```
⚠️ A ordem dos bits do `Fmask` do HLS difere da do `QA_PIXEL` do Landsat; confirme no guia do usuário do HLS.

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | Buscar cenas HLS de 1 mês | Várias cenas L30 e S30 |
| 2 | NDVI com escala | Entre −1 e 1 |
| 3 | NDVI sem escala (Landsat C2) | Valores errados |
| 4 | Aplicar máscara | Nuvens viram nulo |
| 5 | Série de 1 ano | Picos de soja e milho; vale em ago–out |
| 6 | Comparar com MODIS | Mesma curva, mais detalhe |
| 7 | Cenas limpas em jan × jul | Muito menos em janeiro |
| 8 | Conferir exemplo do USGS (DN 18.639) | 0,313 |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução |
|---|---|---|
| AppEEARS/earthaccess 401 | Earthdata Login ausente ou errado | Configurar `.netrc` [10] |
| AppEEARS 403 | Token expirado | Novo login [9] |
| EarthExplorer exige login | Download Landsat precisa de conta USGS | Criar conta |
| NDVI fora de −1 a 1 | Escala não aplicada ou preenchimento não removido | Revisar passos 3 e 4 |
| Série com saltos | Mistura de L30 e S30 sem harmonização ou sem máscara | Usar HLS v2.0 e máscara |

---

## 11. Limitações

1. **Nuvens** no verão chuvoso.
2. **Revisita de 8 dias** (Landsat sozinho).
3. **Escala diferente** entre Landsat C2 e HLS.
4. **Correção atmosférica pior** com sol baixo (ângulo zenital > 76° não é processado), em áreas hiperáridas, costeiras e com muita nuvem [1].
5. **Máscara de nuvem pode errar** com contrastes de temperatura extremos [1].
6. **Volume de dados**.
7. **Landsat 7 encerrado** em 2022 [1].

---

## 12. Boas práticas

1. **HLS** para séries recentes; **Landsat C2 L2** para antes de 2013.
2. **Escala → máscara → índice**, sempre.
3. **Compósitos** mensais e **suavização**.
4. MODIS para série longa; Landsat/HLS para detalhe.

---

## 13. Como e por que usar o Landsat no Field Shift

> Contexto: Landsat é **complementar** (D-002) [12]. Solução proposta para a **I-2**: MODIS para série histórica e diagnóstico; Landsat/HLS para detalhe do talhão.

| Motivo | Por que importa |
|---|---|
| **30 m** | Diferenças dentro da área |
| **Histórico desde os anos 1980** | Mudanças de uso e manejo |
| **HLS** | Mais chances de captar plantio, colheita e solo exposto |
| **Visual** | Mapas fáceis de mostrar ao agricultor |

| Etapa | Papel |
|---|---|
| Diagnóstico | Confirmar no talhão o solo exposto detectado pelo MODIS |
| Mapa (extra) | NDVI mensal; zonas fracas recorrentes |
| Incerteza | Concordância MODIS × Landsat |

**Não resolve:** série contínua no verão (MODIS), qual cultura está plantada (MapBiomas ou agricultor, conforme D-003), causa da zona fraca (campo).

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| NDVI | (NIR − V)/(NIR + V) [7] | Vigor |
| NDMI | (NIR − SWIR1)/(NIR + SWIR1) | Água na vegetação; ajuda a separar palha seca |
| Dias de solo exposto | Duração com NDVI < ~0,25 | Proteção do solo |
| Zona fraca recorrente | Pixels abaixo da média do talhão em X de Y anos | Zonas de manejo |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `NASA_POWER.md` (seção 16).

**Dados usados:** HLS v2.0 (L30 + S30) de 2019 a 2025, tratados conforme a seção 8.

- 210 cenas; **96 limpas** (9 em dez–jan, 30 em jul–ago).
- Setembro: NDVI médio de **0,18**.
- **Faixa norte** com NDVI 15% menor na fase de enchimento do milho, em todos os anos secos.

> 🟫 **Em setembro, quase não há palha cobrindo o solo.**
> *De onde vem: Landsat 8/9 e Sentinel-2 (HLS), pixels de 30 m, 2019–2025.*

> 🗺️ **A faixa norte rende menos todo ano seco.**
> *De onde vem: Landsat/HLS; mesmo padrão observado pelo ECOSTRESS.*

**Efeito:** evidência visual para a estratégia B e sugestão de zona de manejo. Confiança **Alta** (solo exposto) e **Média** (causa da faixa fraca).

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. USGS. Landsat Collection 2 Surface Reflectance: processamento, disponibilidade, download e limitações. <https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance>
2. USGS. Como usar o fator de escala dos produtos Level-2 (SR e ST, com exemplos). <https://www.usgs.gov/faqs/how-do-i-use-scale-factor-landsat-level-2-science-products>
3. USGS. Landsat Collection 2 Quality Assessment Bands (`QA_PIXEL`, `QA_RADSAT`, `SR_QA_AEROSOL`). <https://www.usgs.gov/Landsat-missions/Landsat-collection-2-quality-assessment-bands>
4. USGS. Landsat Collection 2 Surface Temperature. <https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature>
5. NASA Earthdata. HLSS30 v2.0: bandas, escala, Fmask, tiles e revisita. <https://www.earthdata.nasa.gov/es/data/catalog/lpcloud-hlss30-2.0>
6. USGS. Landsat Collection 2 Level-2 Science Products. <https://www.usgs.gov/land-resources/nli/landsat/landsat-collection-2-level-2-science-products>
7. USGS. Landsat NDVI: fórmula e especificações. <https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index>
8. USGS EarthExplorer. <https://earthexplorer.usgs.gov>
9. NASA LP DAAC. AppEEARS API. <https://appeears.earthdatacloud.nasa.gov/api/>
10. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>
### 16.2 Base do projeto

11. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/.md/bancos-de-dados-field-shift-brasil.md` (revisita de 8 dias com Landsat 8 e 9).
12. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` (D-002, D-003, I-2).

*Consulta das fontes: 14 de novembro de 2026. Confira versões e endereços no momento da implementação.*
