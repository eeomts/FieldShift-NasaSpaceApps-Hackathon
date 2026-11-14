# SRTM — Análise e documentação

## Elevação e relevo (30 m)

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
13. [Como e por que usar o SRTM no Field Shift](#13-como-e-por-que-usar-o-srtm-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `NASA_POWER.md`. Autenticação e AppEEARS em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Descrição, resolução, cobertura, datas, arquivos e acesso na página do dataset [1]; tamanho dos tiles, unidade e fontes de preenchimento no *SRTM Quick Guide* do LP DAAC [2], em 14/11/2026. ⚠️ O referencial vertical (geoide EGM96) não aparece nessas fontes. **Nenhum download executado ao vivo.**

**O que vem do contexto e o que foi acrescentado.** SRTM como obrigatório, no MVP, e o uso para baixadas sujeitas a geada vêm do repositório [8][9]. O restante foi acrescentado.

---

## 2. Visão geral

**SRTM** (*Shuttle Radar Topography Mission*) gerou um modelo digital de elevação quase global por **radar interferométrico**, a bordo do ônibus espacial **Endeavour** (missão STS-99, lançada em 11/02/2000, 11 dias) [1].

| Item | Valor | Fonte |
|---|---|---|
| Resolução | 1 segundo de arco (~30 m) | [1] |
| Cobertura | Terra entre 60°N e 56°S (~80% das terras emersas) | [1] |
| Data | 11 a 21/02/2000 (dado estático) | [1] |
| Unidade | **Metros** | [2] |
| Tiles | **1° × 1°** | [2] |
| Referencial vertical | Geoide EGM96 ⚠️ | — |
| Formato | `.HGT`; versão NetCDF4 (`SRTMGL1_NC`) | [1] |
| Distribuidor | LP DAAC (programa MEaSUREs) | [1] |

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | Duas antenas de radar (uma no ônibus espacial, outra num mastro) registram o mesmo terreno; a diferença de fase dá a altura | NASA/JPL, NGA | [1] |
| 2. Processamento | Média de todas as passagens dentro de cada tile | Equipe SRTM | [1] |
| 3. Preenchimento (V3) | Falhas preenchidas com **ASTER GDEM2, GMTED2010 e NED** ("SRTM Plus") | NASA (MEaSUREs) | [2] |
| 4. Fonte por pixel | Arquivo companheiro indica de onde veio cada pixel | NASA | [1] |
| 5. Distribuição | **LP DAAC** | LP DAAC | [1] |
| 6. Acesso | AppEEARS, Earthdata Search, earthaccess | Usuário | [1] |
| 7. Field Shift | Recorte, reprojeção, declividade, baixadas (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Em 2000, um radar no ônibus espacial mediu a altura do terreno do planeta. Com isso dá para saber onde o terreno é inclinado, para onde a água escorre e onde o ar frio se acumula."

---

## 4. Produtos

| Produto | Descrição | Fonte |
|---|---|---|
| **SRTMGL1 v003** | 30 m, falhas preenchidas ← recomendado | [1] |
| SRTMGL1N / `_NUMNC` | Fonte de cada pixel | [1][2] |
| SRTMGL1_NC | Mesmo dado em NetCDF4 | [1] |
| SRTMGL3 | ~90 m | [2] |
| NASADEM | Reprocessamento do SRTM com melhorias | [3] |

---

## 5. Formas de acesso

| Ferramenta | O que faz | Fonte |
|---|---|---|
| **AppEEARS** | Recorte por área (GeoTIFF) ou valor por ponto | [1][6] |
| **Earthdata Search** | Busca por tile | [1][4] |
| **earthaccess** | Busca e download | [7] |
| **LP DAAC** | User Guide, Quick Guide, guia de comparação de MDEs | [1][2] |

**Dica:** o SRTM não muda. **Baixe uma vez** o recorte da região da demo e guarde no projeto.

---

## 6. Parâmetros explicados

### 6.1 Pedido de área no AppEEARS

Campos gerais em `SMAP.md` (seção 6.2). Específico:

| Campo | Valor | Observação |
|---|---|---|
| `task_type` | `"area"` | Recorte raster |
| `layers[].product` | `SRTMGL1_NC.003` ou `NASADEM_NC.001` ⚠️ | Confirme com `GET /product` |
| `layers[].layer` | Camada de elevação ⚠️ | `GET /product/{id}` |
| `dates` | Qualquer intervalo que inclua fev/2000 ⚠️ | O produto é estático |
| `geo` | GeoJSON da fazenda (EPSG:4326) | — |
| `output.format.type` | `geotiff` | Abre em QGIS/rasterio |
| `output.projection` | `geographic` ou `native` | Reprojetar para UTM depois |

### 6.2 Nome dos tiles

Indica o canto sudoeste, ex.: `S19W047` cobre de 19°S a 18°S e de 47°W a 46°W (tiles de 1° [2]).

---

## 7. Estrutura dos dados

- Grade de altitudes em **metros** [2].
- Na V3, as falhas foram preenchidas; o arquivo de fonte (`NUM`) indica a origem do pixel [1][2].
- No GeoTIFF do AppEEARS: uma banda de elevação, georreferenciada.

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Recorte | AppEEARS `area` com o polígono da fazenda | Não baixar tiles inteiros |
| 2. Fonte do pixel | Verificar se a área usa pixels preenchidos (arquivo `NUM`) | Preenchimento tem qualidade diferente |
| 3. Reprojeção | Para UTM (ex.: SIRGAS 2000 / UTM 23S, EPSG:31983) ⚠️ confira a zona | Declividade exige distâncias em metros |
| 4. Suavização leve | Filtro de média 3 × 3 em áreas planas | Reduz declives falsos causados por ruído |
| 5. Declividade | Gradiente → % | Risco de erosão |
| 6. Orientação | Direção da encosta | Insolação e escoamento |
| 7. Baixadas | Pixels > 5 m abaixo da média do entorno (~300 m) | Acúmulo de ar frio (geada) |
| 8. Agregação | Média, máximo e % da área > 8% por talhão e por zona | Indicadores por talhão |
| 9. Integração | Altitude média do talhão → `site-elevation` do NASA POWER | Corrige a pressão no POWER |
| 10. Armazenamento | GeoTIFFs de declividade e baixadas + tabela por talhão | Mapas e reprodutibilidade |

```python
import numpy as np, rioxarray
from scipy.ndimage import uniform_filter

dem = rioxarray.open_rasterio("srtm_fazenda.tif", masked=True).squeeze()
dem_m = dem.rio.reproject("EPSG:31983")                                 # passo 3
z = uniform_filter(dem_m.values.astype(float), size=3)                  # passo 4
res = abs(dem_m.rio.resolution()[0])
dzdy, dzdx = np.gradient(z, res)
declividade = np.hypot(dzdx, dzdy) * 100                                # passo 5 (%)
orientacao = (np.degrees(np.arctan2(-dzdx, dzdy)) + 360) % 360          # passo 6
baixada = (z - uniform_filter(z, size=11)) < -5                          # passo 7
print("Área > 8%:", np.nanmean(declividade > 8) * 100, "%")             # passo 8
```

### Classes de declividade usadas como referência

Classificação de relevo amplamente usada no Brasil (Sistema Brasileiro de Classificação de Solos, Embrapa) ⚠️ confirme a classificação adotada pela equipe:

| Declividade | Relevo |
|---|---|
| 0–3% | Plano |
| 3–8% | Suave ondulado |
| 8–20% | Ondulado |
| 20–45% | Forte ondulado |
| > 45% | Montanhoso / escarpado |

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | Pedido de área no AppEEARS | GeoTIFF pequeno |
| 2 | Altitude de ponto conhecido | Diferença de poucos metros da altitude oficial |
| 3 | Declividade em graus geográficos sem reprojetar | Resultado absurdo (mostra a necessidade do passo 3) |
| 4 | Mapa de declividade | Maior perto de cursos d'água e encostas |
| 5 | Conferir com imagem | Vales coincidem com mata ciliar |
| 6 | SRTM × NASADEM | Diferenças pequenas |
| 7 | Altitude da fazenda × célula do POWER | Diferença de dezenas a centenas de metros |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução |
|---|---|---|
| AppEEARS 401 / 403 / 429 | Credencial, token, taxa | Ver `comunicacao-entre-apis.md` [6] |
| Declividade muito alta em todo lugar | Cálculo em graus sem reprojetar | Reprojetar para UTM |
| Faixas e "degraus" no mapa | Ruído e pixels preenchidos | Suavizar; checar o arquivo `NUM` |
| Mata com "morro" | Radar mede o topo das copas | Interpretar com cautela |

---

## 11. Limitações

1. **Superfície de 2000**, incluindo copas de árvores.
2. **30 m não capta microrrelevo** (terraços, curvas de nível, sulcos).
3. **Erros em relevo íngreme**; a V3 preenche falhas com outras fontes [2]; avaliação de desempenho em [5].
4. **Ruído em áreas planas**.
5. **Mudanças após 2000** não aparecem.
6. **Exige reprojeção** para declividade.

---

## 12. Boas práticas

1. **Reprojete para UTM**.
2. **Suavize levemente** em áreas planas.
3. Use o **recorte da fazenda**.
4. **Combine** com chuva extrema (IMERG) e cobertura (NDVI): declive sozinho não é risco.
5. Passe a altitude ao **NASA POWER**.
6. Compare com o **TOPODATA** (INPE), citado no repositório como equivalente nacional [8].

---

## 13. Como e por que usar o SRTM no Field Shift

> Contexto: **obrigatório** (D-002), no **MVP** (declividade) e usado para **baixadas** no risco de geada [8][9].

| Motivo | Por que importa |
|---|---|
| **Única camada obrigatória em escala de talhão** | POWER, SMAP e IMERG têm 10–55 km |
| **Explica a erosão** | Declive + chuva forte + solo descoberto |
| **Explica a geada localizada** | Ar frio se acumula nas baixadas |
| **Melhora outras fontes** | Altitude corrige o POWER e ajuda a interpretar o ECOSTRESS |
| **Termos do desafio** | "Zones of erosion risk" e "frost-prone areas" |

| Etapa | Papel |
|---|---|
| Indicadores | Declividade, % da área > 8%, baixadas |
| Diagnóstico | Zonas de risco de erosão e de geada |
| Pontuação | Critério **risco de erosão** |
| Mapa (extra) | Camadas de declividade e baixadas |

**Não resolve:** infiltração do solo (GAEZ/SoilGrids/Embrapa Solos, Q-07), práticas de conservação existentes (agricultor), temperatura real da baixada (sensor local).

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| Declividade média e máxima | Gradiente em % | Risco de erosão |
| % da área > 8% | Proporção de pixels | Comparar talhões |
| Baixadas | Altitude − média do entorno | Risco de geada |
| Orientação | Direção da encosta | Insolação, escoamento |
| Altitude média | Média do talhão | `site-elevation` do POWER |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `NASA_POWER.md` (seção 16).

**Dados usados:** SRTMGL1 v003 recortado pelo AppEEARS, tratado conforme a seção 8.

| Indicador | Valor |
|---|---|
| Altitude média do talhão | 950 m (célula do POWER: 880 m) |
| Declividade média | 4,5% (suave ondulado) |
| Área > 8% | **18%**, na **faixa norte** |
| Baixada junto ao córrego | ~12 ha, 15–20 m abaixo do entorno |

> ⛰️ **A faixa norte do talhão é mais inclinada.** Cerca de 18% da área passa de 8% de declive; é ali que a chuva escorre mais e aparecem os sulcos.
> *De onde vem: SRTM (NASA), pixels de 30 m.*

> ❄️ **A baixada perto do córrego pode gelar antes do resto.**
> *De onde vem: SRTM + NASA POWER. Só um termômetro no local mede a diferença real.*

**Efeito:** a faixa norte é inclinada (SRTM), mais quente na seca (ECOSTRESS) e mais fraca (Landsat): zona de manejo com cobertura permanente (estratégia B). Altitude passada ao POWER (`site-elevation=950`). Confiança **Alta** (declividade) e **Média** (geada na baixada).

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NASA Open Data. SRTM Global 1 arc second V003 (SRTMGL1): descrição, cobertura, datas, arquivos e acesso. <https://data.nasa.gov/dataset/nasa-shuttle-radar-topography-mission-global-1-arc-second-v003-e47e1>
2. NASA LP DAAC. SRTM Quick Guide: tiles, unidade e fontes de preenchimento da V3. <https://LPDAAC.USGS.GOV/documents/13/SRTM_Quick_Guide.pdf>
3. NASA LP DAAC. NASADEM User Guide V13. <https://lpdaac.usgs.gov/documents/2237/NASADEM_User_Guide_V13.pdf>
4. NASA Earthdata. SRTMGL1 v003. <https://www.earthdata.nasa.gov/data/catalog/lpcloud-srtmgl1-003>
5. Rodriguez, E., Morris, C. S., Belz, J. E. (2006). A global assessment of the SRTM performance. *Photogrammetric Engineering & Remote Sensing*. DOI do dataset: 10.5067/MEaSUREs/SRTM/SRTMGL1.003
6. NASA LP DAAC. AppEEARS API. <https://appeears.earthdatacloud.nasa.gov/api/>
7. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>

### 16.2 Base do projeto

8. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` (D-002, D-003: TOPODATA).
9. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md` (§7 geada com relevo, §13 MVP).

*Consulta das fontes: 14 de novembro de 2026.*
