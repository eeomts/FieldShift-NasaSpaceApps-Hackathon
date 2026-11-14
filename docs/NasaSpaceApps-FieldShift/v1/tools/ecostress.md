# ECOSTRESS — Análise e documentação

## Temperatura da superfície e evapotranspiração em alta resolução

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP (Field Shift Minas) · 14 de novembro de 2026*

> ⚠️ Todos os números do caso hipotético (seção 15) são fictícios. As aplicações descrevem possibilidades para o projeto, não funcionalidades já implementadas.

---

## Sumário

1. [Como ler este documento](#1-como-ler-este-documento)
2. [Visão geral](#2-visão-geral)
3. [De onde vêm os dados](#3-de-onde-vêm-os-dados)
4. [Produtos (Collection 2)](#4-produtos-collection-2)
5. [Formas de acesso](#5-formas-de-acesso)
6. [Parâmetros explicados](#6-parâmetros-explicados)
7. [Estrutura dos dados](#7-estrutura-dos-dados)
8. [Tratamento dos dados no Field Shift](#8-tratamento-dos-dados-no-field-shift)
9. [Como testar](#9-como-testar)
10. [Códigos de erro e problemas conhecidos](#10-códigos-de-erro-e-problemas-conhecidos)
11. [Limitações](#11-limitações)
12. [Boas práticas](#12-boas-práticas)
13. [Como e por que usar o ECOSTRESS no Field Shift](#13-como-e-por-que-usar-o-ecostress-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `nasa-power-api-daily.md`. Autenticação e AppEEARS estão detalhados em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Camadas, unidades, cobertura, formato, nomes de arquivo e problemas conhecidos de `ECO_L2T_LSTE` e `ECO_L3T_JET` (v002) foram conferidos nas páginas oficiais em 14/11/2026 [1][2]. **Nenhum download executado ao vivo.**

**O que vem do contexto e o que foi acrescentado.** ECOSTRESS como fonte complementar e o uso para estresse no talhão vêm do repositório [10][11]. O restante foi acrescentado aqui.

---

## 2. Visão geral

**ECOSTRESS** é um radiômetro térmico instalado na **Estação Espacial Internacional (ISS)** que mede a temperatura da superfície e, a partir dela, estima evapotranspiração e estresse hídrico [1][6].

| Item | Valor | Fonte |
|---|---|---|
| Início dos dados | 09/07/2018 (LST) | [1] |
| Resolução | **70 m** | [1][2] |
| Cobertura | Coleta entre ~52°N e 52°S | [1][2] |
| Revisita | Variável (órbita da ISS) | [1][2] |
| Formato | Cloud Optimized GeoTIFF, uma camada por arquivo | [1][2] |
| Grade | Tiles de 109,8 × 109,8 km baseados no MGRS (código de 5 caracteres) | [1][2] |
| Login | NASA Earthdata Login | — |

**Princípio físico:** planta com água transpira e se resfria; quando falta água, os estômatos fecham, a transpiração cai e a folha esquenta [6].

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | Radiômetro térmico multiespectral a bordo da ISS mede a radiância emitida pela superfície | NASA/JPL | [6] |
| 2. Temperatura (L2) | Algoritmo de separação temperatura-emissividade (TES) gera LST e emissividade | Equipe ECOSTRESS | [1] |
| 3. Fusão (STARS) | Dados VIIRS e HLS são fundidos para fornecer insumos de alta resolução aos modelos de ET | Equipe ECOSTRESS | [2] |
| 4. Evapotranspiração (L3) | Modelos **PT-JPL-SM**, STIC, MOD16 e BESS estimam a ET | Equipe ECOSTRESS | [2] |
| 5. Estresse (L4) | Índice de estresse evaporativo (ESI) e eficiência no uso da água | Equipe ECOSTRESS | [3][4] |
| 6. Tiles | Reprojeção para tiles MGRS em COG | Equipe ECOSTRESS | [1][2] |
| 7. Distribuição | **LP DAAC** (Earthdata Cloud) | LP DAAC | [1][2] |
| 8. Acesso | AppEEARS, Earthdata Search, earthaccess | Usuário | [3][5] |
| 9. Field Shift | Filtro de nuvem e qualidade, conversões e indicadores (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Um sensor na estação espacial mede a temperatura do seu campo em quadrados de 70 m. Planta com sede esquenta; isso mostra onde a lavoura sofre mais."

---

## 4. Produtos (Collection 2)

| Produto | Nível | Conteúdo | Uso no projeto |
|---|---|---|---|
| **ECO_L2T_LSTE** | L2 | Temperatura da superfície e emissividade [1] | Pontos quentes |
| **ECO_L3T_JET** | L3 | Evapotranspiração por vários modelos [2] | Demanda de água |
| **ECO_L4T_ESI** | L4 | Índice de estresse evaporativo e ET potencial [3][4] | Estresse hídrico |
| ECO_L4T_WUE | L4 | Eficiência no uso da água [3] | Opcional |

O "T" (`L2T`, `L3T`, `L4T`) indica a versão em **tiles**. As versões tiled de ET, ESI e WUE estão disponíveis no **AppEEARS** [3].

---

## 5. Formas de acesso

| Ferramenta | O que faz | Fonte |
|---|---|---|
| **AppEEARS** | Ponto (CSV) ou área (GeoTIFF/NetCDF) | [3][5][9] |
| **Earthdata Search / CMR** | Busca por tile e data (CMR ID do ET: `C2076106409-LPCLOUD`) | [2] |
| **earthaccess** | Busca, download e leitura direta dos COG na nuvem | [7] |
| **Tutoriais oficiais** | AppEEARS e Python para dados tiled | [5][8] |

---

## 6. Parâmetros explicados

### 6.1 Pedido no AppEEARS

Os campos do `POST /task` são os mesmos descritos em `smap.md` (seção 6.2) e em `comunicacao-entre-apis.md`. Específico do ECOSTRESS:

| Campo | Valor | Observação |
|---|---|---|
| `layers[].product` | `ECO_L2T_LSTE.002`, `ECO_L3T_JET.002` ⚠️ | Confirme com `GET /product` |
| `layers[].layer` | `LST`, `cloud`, `QC`; `ETdaily`, `ETinstUncertainty` | Nomes conforme [1][2]; confirme com `GET /product/{id}` |
| `dates` | Período a partir de 07/2018 | Cenas em datas e horários irregulares |

### 6.2 Busca no earthaccess

| Argumento | Exemplo | Explicação |
|---|---|---|
| `short_name` | `"ECO_L2T_LSTE"` | Produto |
| `version` | `"002"` | Versão |
| `bounding_box` | `(-47.0, -19.0, -46.8, -18.8)` | Área do talhão |
| `temporal` | `("2024-04-01", "2024-06-30")` | Período |

### 6.3 Nome dos arquivos

`ECOv002_L3T_JET_[órbita]_[cena]_[tile MGRS]_[AAAAMMDDTHHMMSS]_[build]_[iteração]_[camada].tif` [2]. O trecho de data e hora permite **filtrar por horário** sem abrir o arquivo. ⚠️ Confirme se o horário está em UTC.

---

## 7. Estrutura dos dados

### 7.1 ECO_L2T_LSTE [1]

| Camada | Descrição | Unidade | Preenchimento |
|---|---|---|---|
| `LST` | Temperatura da superfície | **Kelvin** | NaN |
| `LST_err` | Erro da temperatura | Kelvin | NaN |
| `QC` | Qualidade (bits). Na v002, bits 1–0 indicam pixel produzido pelo TES, produzido com possível degradação, não definido ou não produzido | — | — |
| `cloud` | Máscara de nuvem | 0/1 | — |
| `water` | Máscara de água | 0/1 | — |
| `view_zenith` | Ângulo de visada | graus | NaN |
| `height` | Altitude | m | NaN |
| `EmisWB` | Emissividade de banda larga | 0–1 | NaN |

Sem fator de escala. **°C = K − 273,15.** A informação de nuvem da v001 **não está** no `QC` da v002: use a camada `cloud` [1].

### 7.2 ECO_L3T_JET [2]

| Camada | Descrição | Unidade |
|---|---|---|
| `ETdaily` | ET diária estimada | W/m² |
| `ETinstUncertainty` | Incerteza da ET | W/m² |
| `PTJPLSMinst` | ET instantânea total (PT-JPL-SM) | W/m² |
| `STICinst`, `MOD16inst`, `BESSinst` | ET instantânea por outros modelos | W/m² |
| `PTJPLSMcanopy` / `PTJPLSMsoil` / `PTJPLSMinterception` | Frações: transpiração / evaporação do solo / evaporação nas folhas | 0–1 |
| `cloud`, `water` | Máscaras | 0/1 (preenchimento 255) |

Camadas em ponto flutuante usam **NaN** como preenchimento [2].

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Busca | Cenas `ECO_L2T_LSTE` e `ECO_L3T_JET` do tile do talhão | Saber quantas cenas existem |
| 2. Filtro de horário | Manter passagens entre ~11h e 15h locais (pelo nome do arquivo) | Cenas de horários diferentes não são comparáveis |
| 3. Nuvem e água | Descartar pixels com `cloud` = 1 ou `water` = 1 | Nuvem esfria o pixel e falseia a LST |
| 4. Qualidade | Manter `QC` bits 1–0 indicando pixel produzido; descartar cenas com obstrução e geolocalização "suspect"/"poor" | Recomendações da página oficial [1] |
| 5. Períodos problemáticos | Marcar cenas de 15/05/2019–28/04/2023, jan–set/2023 e 15/05–01/07/2025 | Problemas conhecidos (seção 10) |
| 6. Conversão | LST: K → °C. ET: W/m² → mm/dia com `mm/dia ≈ W/m² × 0,0864 / 2,45` ⚠️ | Unidades que o agricultor entende |
| 7. Agregação espacial | Média por talhão e por zona de manejo; mapa por pixel | O ECOSTRESS enxerga dentro da fazenda |
| 8. Indicador relativo | LST − T2M (ar, NASA POWER) e diferença de cada zona para a média do talhão | Remove o efeito do dia mais quente ou mais frio |
| 9. Incerteza | Dispersão entre os 4 modelos de ET e `ETinstUncertainty` | Selo de confiança |
| 10. Armazenamento | GeoTIFF recortado por talhão + tabela de cenas usadas | Reprodutibilidade |

```python
import earthaccess, rioxarray

earthaccess.login()
res = earthaccess.search_data(short_name="ECO_L2T_LSTE", version="002",
                              bounding_box=(-47.0, -19.0, -46.8, -18.8),
                              temporal=("2024-04-01", "2024-06-30"))
for g in res:
    links = g.data_links()
    lst = next(l for l in links if l.endswith("_LST.tif"))
    cld = next(l for l in links if l.endswith("_cloud.tif"))
    t = rioxarray.open_rasterio(lst, masked=True) - 273.15        # passo 6
    c = rioxarray.open_rasterio(cld)
    t = t.where(c == 0)                                           # passo 3
    print(lst.split("_")[-4], float(t.mean()))                    # data/hora + média
```
⚠️ Confirme a posição do trecho de data no nome antes de usar o `split`.

**Sobre a conversão de ET:** 1 W/m² mantido por 24 h = 0,0864 MJ/m²/dia; dividindo pelo calor latente de vaporização (~2,45 MJ/kg), obtém-se kg/m²/dia = mm/dia. Confirme no guia do usuário se o `ETdaily` é um fluxo médio diário antes de aplicar.

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | Buscar cenas de 1 mês | Poucas cenas, em datas e horários irregulares |
| 2 | Ler `LST` e converter | 20–55 °C de dia |
| 3 | Aplicar `cloud` | Pixels nublados removidos |
| 4 | Cena da manhã × da tarde | Tarde mais quente |
| 5 | Talhão com cultura × pousio | Pousio mais quente no mesmo horário |
| 6 | Comparar os 4 modelos de ET | Mesma ordem de grandeza |
| 7 | Cena entre 2019 e 2023 | Bandas com preenchimento (modo de 3 bandas) |
| 8 | `LST_err` entre 16/12/2025 e 10/06/2026 | Camada ausente |

---

## 10. Códigos de erro e problemas conhecidos

**Erros de acesso:** os mesmos do AppEEARS e do Earthdata Login (401 credenciais, 403 token expirado, 429 limite de taxa) — ver `smap.md` seção 10 e `comunicacao-entre-apis.md`.

**Problemas registrados nas páginas oficiais [1][2]:**

| Período / tema | Problema | Ação |
|---|---|---|
| 15/05/2019 – 28/04/2023 | Coleta reduzida a 3 bandas; demais com preenchimento | Marcar e usar com cautela |
| 08–16/02/2020 | Listras na banda 4 (reprocessadas); sem dados em 17/02/2020 | — |
| Jan–set/2023 | Qualidade menor da ET (priors do STARS) | Usar com cautela |
| 15/05 – 01/07/2025 | Dados mais ruidosos | Usar com cautela |
| 16/12/2025 – 10/06/2026 | `LST_err` não gerada (reprocessamento previsto) | Não depender do erro nesse período |
| Painéis da ISS | Obstrução do campo de visão; campo não confiável antes de 24/10/2024 | Consultar a lista de cenas obstruídas |
| Geolocalização | Apontamento grosseiro da ISS | Usar só cenas "best" e "good" para análise espacial |
| ET | Artefatos de 500 m–1 km herdados do STARS | Interpretar como incerteza maior |

---

## 11. Limitações

1. **Revisita irregular**: não há série diária regular.
2. **Horário variável**: exige filtro.
3. **Nuvens** na estação chuvosa: poucas cenas limpas.
4. **Histórico curto** (desde 2018).
5. **Depende da ISS** para continuar.
6. **ET em W/m²**: exige conversão.

---

## 12. Boas práticas

1. Use as versões **tiled** e o **AppEEARS**.
2. **Filtre horário, nuvem e qualidade** em todas as cenas.
3. Use a **dispersão entre modelos de ET** como incerteza.
4. Compare com o **ar** (POWER) e com a **média do talhão**.
5. Trate como **evidência pontual**, não como série contínua.

---

## 13. Como e por que usar o ECOSTRESS no Field Shift

> Contexto: ECOSTRESS é **complementar** (D-002) [10]; no MVP aparece em "se sobrar tempo" (estresse em talhão) [11].

| Motivo | Por que importa |
|---|---|
| **70 m** | Único dado térmico do desafio na escala de talhão |
| **Mostra a resposta da planta** | Temperatura e ET, não só o clima |
| **Passagens à tarde** | Captura o pico do estresse diário |
| **ET observada** | Complementa a ET₀ teórica do POWER |
| **Termos do desafio** | "Hotspots of plant stress" e "field-level microclimate differences" |

| Etapa | Papel |
|---|---|
| Diagnóstico | Pontos quentes no talhão em períodos secos |
| Mapa (extra) | Camada de estresse térmico intra-talhão |
| Incerteza | Dispersão entre modelos de ET |

**Não resolve:** série contínua (use MODIS LST ou POWER), causa do ponto quente (exige campo), período chuvoso (poucas cenas).

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| LST − T do ar | LST (°C) − T2M do POWER no mesmo dia | Estresse relativo |
| Anomalia espacial | LST do pixel − média do talhão | Zonas que sofrem mais |
| ET diária | `ETdaily` convertida em mm/dia | Demanda real por cultura |
| Fração de transpiração | `PTJPLSMcanopy` | Quanto da água sai pela planta (e não do solo) |
| Incerteza | Desvio entre os 4 modelos | Selo de confiança |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `nasa-power-api-daily.md` (seção 16).

**Dados usados:** cenas ECO_L2T_LSTE e ECO_L3T_JET da safrinha (abr–jun) de 2019 a 2025, passagens entre 11h e 15h, sem nuvem e com qualidade aceitável, tratadas conforme a seção 8.

- 14 cenas úteis em 7 anos.
- Em maio de anos secos, a **faixa norte** ficou **4 a 6 °C mais quente** que o resto do talhão.
- ET ~30% menor nessa faixa; os 4 modelos concordaram na direção, divergiram no valor.

> 🌡️ **A parte norte do seu talhão sofre mais na seca.** Nas tardes secas de maio, ela fica até 6 °C mais quente e transpira menos. Pode ser solo mais raso, compactação ou mais escoamento.
> *De onde vem: ECOSTRESS (estação espacial), 14 imagens de 2019–2025, quadrados de 70 m.*
> *Por que confirmar: a ferramenta não sabe a causa.*

**Efeito:** reforça a estratégia B na faixa norte e gera a pergunta ao técnico sobre compactação. Confiança **Baixa a Média**.

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NASA Earthdata. ECO_L2T_LSTE v002: camadas, unidades, cobertura, formato e problemas conhecidos. <https://www.earthdata.nasa.gov/data/catalog/lpcloud-eco-l2t-lste-002>
2. NASA Earthdata. ECO_L3T_JET v002: camadas de ET, modelos, nomes de arquivo e problemas conhecidos. <https://www.earthdata.nasa.gov/data/catalog/lpcloud-eco-l3t-jet-002>
3. NASA Earthdata. Alerta: ET, ESI e WUE tiled disponíveis no AppEEARS. <https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-v2-level-3-et-level-4-esi-wue-tiled-data-now-available-appeears>
4. NASA Earthdata. Alerta: lançamento de ET e ESI v2 tiled. <https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-version-2-tiled-gridded-evapotranspiration-evaporative-stress-index>
5. NASA. Tutorial AppEEARS + ECOSTRESS. <https://nasa.github.io/ECOSTRESS-Data-Resources/guides/appeears_ecostress.html>
6. NASA/JPL. ECOSTRESS — missão. <https://www.jpl.nasa.gov/missions/ecosystem-spaceborne-thermal-radiometer-experiment-on-space-station-ecostress/>
7. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>
8. NASA. Tutorial: dados tiled do ECOSTRESS em Python. <https://nasa.github.io/ECOSTRESS-Data-Resources/python/tutorials/Working_with_ECOSTRESS_Tiled_data.html>
9. NASA LP DAAC. AppEEARS API. <https://appeears.earthdatacloud.nasa.gov/api/>

### 16.2 Base do projeto

10. Repositório da equipe, `docs/v1/.md/context/DECISOES.md` (D-002).
11. Repositório da equipe, `docs/v1/.md/context/CONTEXTO-DESAFIO.md` (§13 MVP) e `bancos-de-dados-field-shift-minas.md`.

*Consulta das fontes: 14 de novembro de 2026. Versões e problemas conhecidos mudam; confira novamente no momento da implementação.*
