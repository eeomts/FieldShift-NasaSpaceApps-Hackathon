# GPM IMERG — Análise e documentação

## Precipitação global por satélite

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP (Field Shift Brasil) · 14 de novembro de 2026*

> ⚠️ Todos os números do caso hipotético (seção 15) são fictícios. As aplicações descrevem possibilidades para o projeto, não funcionalidades já implementadas.

---

## Sumário

1. [Como ler este documento](#1-como-ler-este-documento)
2. [Visão geral](#2-visão-geral)
3. [De onde vêm os dados](#3-de-onde-vêm-os-dados)
4. [Produtos e versões](#4-produtos-e-versões)
5. [Formas de acesso](#5-formas-de-acesso)
6. [Parâmetros explicados](#6-parâmetros-explicados)
7. [Estrutura dos dados](#7-estrutura-dos-dados)
8. [Tratamento dos dados no Field Shift](#8-tratamento-dos-dados-no-field-shift)
9. [Como testar](#9-como-testar)
10. [Códigos de erro e problemas comuns](#10-códigos-de-erro-e-problemas-comuns)
11. [Limitações](#11-limitações)
12. [Boas práticas](#12-boas-práticas)
13. [Como e por que usar o IMERG no Field Shift](#13-como-e-por-que-usar-o-imerg-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Segue o mesmo formato do `NASA_POWER.md`. A comunicação entre esta e as outras APIs (autenticação, padrões de requisição, orquestração) está no documento separado `comunicacao-entre-apis.md`.

**Referências.** Os números entre colchetes, como [1], apontam para a lista da seção 16. Para cada afirmação foi escolhida a fonte oficial mais completa.

**O que foi verificado.** Especificações, variáveis, cálculo diário, latências e formas de acesso foram conferidos nas páginas oficiais em 14/11/2026. **Nenhum download foi executado ao vivo**: o acesso exige Earthdata Login e o domínio não estava liberado no ambiente usado. Itens com ⚠️ precisam de confirmação antes de virar código.

**O que vem do contexto e o que foi acrescentado.** O escopo nacional (D-008, que substituiu o foco inicial em Minas Gerais), a classificação do IMERG como dataset obrigatório e o papel de validar a chuva do NASA POWER vêm do repositório da equipe [15][16]. As explicações técnicas, o tratamento dos dados e o caso hipotético foram acrescentados neste documento.

---

## 2. Visão geral

**IMERG** (*Integrated Multi-satellitE Retrievals for GPM*) é o algoritmo unificado dos EUA que gera o produto de precipitação multissatélite da missão **GPM** (NASA + JAXA) [3][6].

| Item | Valor | Fonte |
|---|---|---|
| Variável | Taxa e acumulado de precipitação | [1] |
| Resolução espacial | 0,1° × 0,1° (~10 × 10 km) | [1][3] |
| Resolução temporal | 30 minutos (base); diário e mensal derivados | [1][3] |
| Período | Desde junho de 2000 | [6] |
| Versão atual | **V07** (anteriores substituídas) | [1][6] |
| Login | NASA Earthdata Login (gratuito) | [2][11] |

---

## 3. De onde vêm os dados

A cadeia completa, do sensor até a ferramenta:

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação por micro-ondas | Radiômetros passivos de micro-ondas em vários satélites polares da constelação GPM medem a radiação emitida pelas gotas de chuva | NASA, JAXA e parceiros | [3] |
| 2. Conversão em chuva | Cada sensor é convertido em taxa de chuva pelo algoritmo **GPROF2021** | Equipe GPM | [3][6] |
| 3. Intercalibração | Todos os sensores são ajustados ao produto combinado radar-radiômetro (**CORRA**) | Equipe GPM | [3][6] |
| 4. Infravermelho | Satélites geoestacionários fornecem o topo das nuvens a cada meia hora; o algoritmo **PDIR** converte em chuva | NOAA CPC, PPS | [3][6] |
| 5. Morphing + filtro de Kalman | Áreas de chuva são movidas entre passagens usando vetores de vento do **MERRA-2** (Final) ou **GEOS FP** (Early/Late); o filtro de Kalman decide o peso do infravermelho, que ganha importância após ~90 min da passagem de micro-ondas | Equipe GPM | [6] |
| 6. Pluviômetros (só Final) | O acumulado mensal é ajustado com a análise mensal de pluviômetros; as meias-horas são reescaladas para somar o total mensal | Equipe GPM (análise GPCC) | [3][6] |
| 7. Produto diário | Média das meias-horas válidas × 24 = mm/dia | GES DISC | [1] |
| 8. Distribuição | Arquivos no **GES DISC** (NASA Goddard), com cópia no Earthdata Cloud e na AWS | GES DISC | [1][2][9] |
| 9. Acesso | Giovanni, OPeNDAP, earthaccess, Earthdata Search | Usuário | [1][7][13] |
| 10. Field Shift | Extração da célula do talhão, tratamento (seção 8) e indicadores | Equipe | — |

> **Resumo para o agricultor:** "Satélites medem a chuva várias vezes por dia; a NASA junta essas medições e corrige com pluviômetros. O resultado é a chuva estimada para quadrados de ~10 km."

---

## 4. Produtos e versões

| Versão | Latência | Morphing | Pluviômetros | Uso |
|---|---|---|---|---|
| **Early** | ~4 horas | Só "para frente" | Calibração climatológica | Alertas rápidos |
| **Late** | ~14 horas | Para frente e para trás | Calibração climatológica | Monitoramento quase em tempo real |
| **Final** | ~3,5 meses após o mês | Para frente e para trás | **Sim** (análise mensal) | **Análise histórica** |

Fonte: [3][6].

| Nome curto | Descrição |
|---|---|
| `GPM_3IMERGHH` | Final, meia-hora [6] |
| `GPM_3IMERGDF` | **Final, diário** ← recomendado [1] |
| `GPM_3IMERGM` | Final, mensal |
| `GPM_3IMERGDE` / `GPM_3IMERGDL` | Early e Late, diário ⚠️ |

**Latência do diário Final:** depende da entrega mensal das meias-horas Final (até 4 meses); os diários saem cerca de 24 horas depois. Exemplo oficial: os dias de janeiro só ficam disponíveis a partir de 2 de abril [1].

---

## 5. Formas de acesso

| Ferramenta | Endereço | O que faz | Fonte |
|---|---|---|---|
| **Giovanni** | `giovanni.gsfc.nasa.gov` | Mapas e séries **sem baixar arquivos**; sem login, há limite de passos de tempo | [7][10] |
| **GES DISC** | `disc.gsfc.nasa.gov/datacollection/GPM_3IMERGDF_07.html` | Página oficial, download e subconjunto | [2] |
| **Earthdata Search** | `search.earthdata.nasa.gov` (coleção `C2723754864-GES_DISC`) | Busca visual | [8] |
| **CMR Search API** | `cmr.earthdata.nasa.gov/search/granules` | Lista os arquivos por coleção, período e área | [12] |
| **Diretório virtual CMR** | `cmr.earthdata.nasa.gov/virtual-directory/collections/C2723754864-GES_DISC/temporal` | Navegar pelos arquivos por data | [1] |
| **earthaccess** | biblioteca Python | Login, busca, download e leitura | [13] |
| **AWS Open Data** | `registry.opendata.aws/nasa-gpm3imergdf/` | Cópia na nuvem | [9] |
| **NASA Worldview** | `worldview.earthdata.nasa.gov` | Camadas IMERG como imagem | enunciado do desafio |

> O IMERG **não está no AppEEARS**. Para um ponto, o caminho mais simples é o **Giovanni** (exploração) ou **earthaccess + xarray** (código).

---

## 6. Parâmetros explicados

### 6.1 Busca de arquivos na CMR (`GET /search/granules`)

| Parâmetro | Obrigatório | Formato | Explicação | Fonte |
|---|---|---|---|---|
| `short_name` | Sim* | Texto | Nome curto da coleção: `GPM_3IMERGDF` | [12] |
| `version` | Recomendado | Texto | Versão da coleção: `07` | [12] |
| `collection_concept_id` | Sim* | Texto | Alternativa a `short_name`: `C2723754864-GES_DISC` | [8][12] |
| `temporal` | Não | `AAAA-MM-DDTHH:MM:SSZ,AAAA-MM-DDTHH:MM:SSZ` | Período; limites inclusivos | [12] |
| `bounding_box` | Não | `oeste,sul,leste,norte` | Retângulo de busca | [12] |
| `point` | Não | `longitude,latitude` | Ponto (longitude primeiro) | [12] |
| `page_size` | Não | 1 a 2000 (padrão 10) | Itens por página | [12] |
| `sort_key[]` | Não | `-start_date` | Mais recentes primeiro | [12] |

\* A CMR **exige** que a busca de arquivos seja limitada a uma coleção (por `short_name`, `collection_concept_id` etc.) [12].

**Paginação:** cada resposta traz o cabeçalho `CMR-Search-After`; envie-o de volta para obter a próxima página. `CMR-Hits` informa o total [12].

### 6.2 Busca pelo earthaccess (`earthaccess.search_data`)

| Argumento | Exemplo | Explicação | Fonte |
|---|---|---|---|
| `short_name` | `"GPM_3IMERGDF"` | Coleção | [13] |
| `version` | `"07"` | Versão | [13] |
| `temporal` | `("2024-01-01", "2024-03-31")` | Período | [13] |
| `bounding_box` | `(lon_min, lat_min, lon_max, lat_max)` | Área | [13] |

O `earthaccess.login()` procura credenciais no `~/.netrc` ou nas variáveis `EARTHDATA_USERNAME` e `EARTHDATA_PASSWORD` [13].

### 6.3 Opções do Giovanni

| Opção | Escolha para o Field Shift |
|---|---|
| Variável | `IMERGDF` (precipitação diária Final) [7] |
| Tipo de gráfico | *Time Series, Area-Averaged* (série) ou *Time Averaged Map* (mapa) |
| Área | Caixa pequena em volta do talhão |
| Período | Até ~4 meses antes de hoje |

Sem login, o Giovanni limita o número de passos de tempo; logado, o limite some [10].

---

## 7. Estrutura dos dados

**Arquivo:** um por dia, cobrindo o globo inteiro. Formato NetCDF4 ⚠️ (a página do dataset não informa o formato) [1].

| Variável | Descrição | Unidade | Fonte |
|---|---|---|---|
| `precipitation` | Taxa média diária combinada (micro-ondas + infravermelho + pluviômetros). **A variável indicada para a maioria dos usuários** | mm/dia | [1][6] |
| `MWprecipitation` | Taxa média diária só de micro-ondas | mm/dia | [1] |
| `precipitation_cnt` | Número de meias-horas válidas no dia (combinado) | contagem | [1] |
| `MWprecipitation_cnt` | Número de meias-horas válidas (micro-ondas) | contagem | [1] |
| `randomError` | Erro aleatório diário | mm/dia | [1] |
| `lat`, `lon`, `time` | Coordenadas | graus / tempo | — |

**Como o valor diário é calculado [1]:**
1. Soma das taxas válidas de meia-hora (mm/h) da célula.
2. Divisão pelo número de meias-horas válidas.
3. Multiplicação por 24 → mm/dia.

Células sem nenhuma amostra válida recebem valor de preenchimento. **Zero conta como valor válido.** O erro diário é a raiz da média dos erros ao quadrado × 24. A V07 aplica esse método para reduzir o viés seco que as versões antigas tinham em dias com menos de 48 amostras.

No produto de meia-hora há ainda: erro aleatório, peso relativo dos pluviômetros, probabilidade de precipitação líquida e índice de qualidade [4].

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Busca | CMR/earthaccess lista os arquivos de `GPM_3IMERGDF` V07 no período | Saber o que existe antes de baixar |
| 2. Recorte | Via **OPeNDAP** ou subconjunto da GES DISC, só a célula do talhão (e vizinhas para mapas) | Cada arquivo global tem dezenas de MB; ~9.000 dias seriam inviáveis |
| 3. Seleção da célula | Célula de 0,1° que contém a coordenada (`method="nearest"`) | Não interpolar: o dado representa a célula inteira |
| 4. Valores ausentes | Converter o valor de preenchimento em nulo | Uma falha não pode virar "0 mm" |
| 5. Confiança diária | Marcar dias com `precipitation_cnt` < 48 ou `randomError` alto | Pesar menos esses dias e sinalizar na interface |
| 6. Versão | Usar **Final** até o último mês disponível; meses recentes com **Late**, marcados como provisórios | Late não tem correção por pluviômetro |
| 7. Agregação temporal | Somar em decêndios e meses; calcular climatologia mensal (média 2001–2025) | Dado diário é ruidoso; decisões agrícolas usam meses e decêndios |
| 8. Indicadores | Veranicos, dias > percentil 95, SPI, chuva no início da estação (seção 14) | Transformar chuva em informação de decisão |
| 9. Comparação | Mesmos indicadores com `PRECTOTCORR` do NASA POWER | Concordância entre fontes alimenta o selo de confiança |
| 10. Armazenamento | Série tratada em CSV/Parquet por talhão, com versão e data do download | Reprodutibilidade e cache |

```python
import earthaccess, xarray as xr, pandas as pd

earthaccess.login()
LAT, LON = -18.9, -46.9
res = earthaccess.search_data(short_name="GPM_3IMERGDF", version="07",
                              temporal=("2001-01-01", "2025-06-30"),
                              bounding_box=(LON-0.1, LAT-0.1, LON+0.1, LAT+0.1))
ds = xr.open_mfdataset(earthaccess.open(res))                # leitura remota
cel = ds.sel(lat=LAT, lon=LON, method="nearest")
df = cel[["precipitation", "precipitation_cnt", "randomError"]].to_dataframe()
df["baixa_confianca"] = df["precipitation_cnt"] < 48          # passo 5
mensal = df["precipitation"].resample("MS").sum()            # passo 7
clim = mensal.groupby(mensal.index.month).mean()
```
⚠️ Confirme os nomes das dimensões (`lat`/`lon`/`time`) no arquivo. Para séries muito longas, prefira recortar no servidor (OPeNDAP) em vez de `open_mfdataset` com milhares de arquivos.

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | `earthaccess.login()` | Autenticação sem erro |
| 2 | Busca de 1 dia | 1 arquivo |
| 3 | Busca dos últimos 3 meses | 0 arquivos (latência do Final) |
| 4 | CMR sem `short_name` nem coleção | Erro (busca precisa de escopo) [12] |
| 5 | `precipitation` em um ponto | Valor ≥ 0 em mm/dia |
| 6 | Soma mensal × `GPM_3IMERGM` | Valores próximos |
| 7 | Comparar com `PRECTOTCORR` do POWER | Mesma sazonalidade; picos maiores no IMERG |
| 8 | Comparar com estação do INMET | Boa correlação mensal; pior no diário |
| 9 | Série no Giovanni × série do código | Mesmos valores |
| 10 | Giovanni sem login, período longo | Erro de limite de passos [10] |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução | Fonte |
|---|---|---|---|
| HTTP 401 ao baixar | Sem Earthdata Login ou aplicativo da GES DISC não autorizado no perfil | Registrar-se e autorizar o aplicativo no Earthdata Login | [10][11] |
| "Too many redirects" | Cookies antigos ou corrompidos | Apagar o arquivo de cookies | [11] |
| "Concurrent connection limit reached" | Muitas conexões simultâneas | Limitar downloads em paralelo | [10] |
| Dados recentes ausentes | Latência do produto | Usar Late para os meses recentes | [1][10] |
| Giovanni: "all filled values" | Área só com preenchimento | Mudar a área | [10] |
| CMR HTTP 413 | URL longa demais | Usar POST | [12] |
| CMR HTTP 429 | Limite de taxa | Esperar o tempo do cabeçalho `retry-after` | [12] |
| CMR `CMR-Time-Out: true` | Consulta passou de 170 s; resultado parcial | Refinar a busca | [12] |

---

## 11. Limitações

1. **Latência de ~3,5 meses no Final** [3]. Os meses recentes só têm Early/Late, sem pluviômetros.
2. **Chuva convectiva localizada** (pancadas de verão) é suavizada numa célula de 10 km.
3. **É estimativa, não medição no chão**; longe das passagens de micro-ondas, depende mais do infravermelho, que é menos preciso [5][6].
4. **A correção com pluviômetros depende da densidade de estações**, baixa em partes do interior.
5. **Relevo complexo** reduz o acerto (registrado no repositório para as serras do Sudeste e do Sul e a Serra do Mar) [16].
6. **Arquivos globais**: baixar arquivo por arquivo para um ponto é ineficiente.

---

## 12. Boas práticas

1. **Final** para histórico; **Late** só para meses recentes, sempre sinalizado.
2. **Recorte no servidor** (OPeNDAP ou subconjunto) antes de baixar.
3. Use `precipitation_cnt` e `randomError` para **marcar dias de baixa confiança**.
4. **Agregue** em decêndios e meses antes de comparar fontes.
5. **Valide** com estações do INMET/CEMADEN (equivalentes do CoCoRaHS, conforme D-003) [15].
6. **Limite conexões simultâneas** ao baixar [10].
7. Registre a **versão (V07)** e a data do download.

---

## 13. Como e por que usar o IMERG no Field Shift

> Contexto: IMERG está entre os **6 obrigatórios** (D-002, proposto) [15]. O pipeline do `CONTEXTO-DESAFIO.md` usa a dispersão "chuva POWER vs. GPM" para calcular a incerteza [16].

### 13.1 Por que o IMERG

| Motivo | Por que importa |
|---|---|
| **Resolução ~5× melhor que o POWER** | ~10 km contra ~55 km; chuva é a variável que mais varia no espaço |
| **Observação de satélite + pluviômetros** | O POWER usa modelo (MERRA-2); o IMERG observa e, no Final, é corrigido em campo [3] |
| **Meia-hora** | Permite medir **intensidade**, base da erosividade |
| **Campos de erro** | `randomError` e `_cnt` alimentam o selo de confiança [1] |
| **Global, desde 2000** | Funciona no Brasil inteiro, com 25 anos de série |

### 13.2 Onde entra no produto

| Etapa do pipeline [16] | Papel |
|---|---|
| Indicadores | Veranicos, chuva extrema, SPI |
| Diagnóstico | Chuvas fortes caindo em solo descoberto |
| Pontuação | Critério **risco de erosão** (com SRTM e NDVI) |
| Incerteza | Comparação com o POWER |
| Cenários | Série base para o slider de chuva |

### 13.3 O que não resolve

- Água que fica no solo → SMAP.
- Quanto escorre → SRTM + solo.
- Chuva dentro do talhão → pluviômetro local.

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| Chuva mensal e climatologia | Soma mensal; média por mês 2001–2025 (a NASA também publica climatologias prontas do IMERG [14]) | Calendário agrícola |
| Veranico | Sequência de 10+ dias com < 1 mm dentro da estação chuvosa | Risco para a safrinha |
| Chuva extrema | Dias acima do percentil 95 da série | Risco de erosão |
| Início e fim da estação chuvosa | Primeiro/último decêndio acima de um limiar | Janelas de plantio |
| SPI 3 meses | Índice padronizado de precipitação (listado no repositório [16]) | Frequência de seca |
| Concordância POWER × IMERG | Diferença relativa por mês | Selo de confiança |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `NASA_POWER.md` (seção 16): produtor de sequeiro no Alto Paranaíba (MG), rotação soja → milho safrinha → pousio.

**Dados usados:** `GPM_3IMERGDF` V07, célula de 0,1° do talhão, 2001–2025, tratados conforme a seção 8.

| Indicador | NASA POWER (~55 km) | IMERG (~10 km) | Leitura |
|---|---|---|---|
| Chuva média de abril | 55 mm | 47 mm | IMERG 15% mais seco |
| Anos com veranico na safrinha | 6 em 10 | 7 em 10 | Fontes concordam: risco alto |
| Dias > 40 mm em out–nov | 2 por ano | 3 por ano | IMERG capta mais eventos fortes |
| Maior chuva diária | 78 mm | 112 mm | POWER suaviza o pico |

> 🌧️ **As primeiras chuvas são fortes.** Em média, 3 dias por ano em outubro e novembro passam de 40 mm, quando seu campo está sem cobertura.
> *De onde vem: satélites GPM (IMERG V07 Final), 2001–2025, quadrados de ~10 km. Confirmado pelo NASA POWER.*

**Efeito nas estratégias:** o risco de erosão da rotação atual sobe, reforçando a estratégia B (braquiária). Selo do critério de chuva: **Médio** (fontes concordam no padrão, divergem 15% no volume de abril).

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NASA Open Data. GPM IMERG Final Precipitation L3 1 day 0.1° V07 (GPM_3IMERGDF): variáveis, cálculo diário, latência e links. <https://data.nasa.gov/dataset/gpm-imerg-final-precipitation-l3-1-day-0-1-degree-x-0-1-degree-v07-gpm-3imergdf-at-ges-dis-13ed8>
2. GES DISC. Coleção GPM_3IMERGDF_07. <https://disc.gsfc.nasa.gov/datacollection/GPM_3IMERGDF_07.html>
3. NASA GPM. IMERG V07 Technical Documentation: execuções, latências e método. <https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation>
4. NASA GPM. IMERG V07 ATBD. <https://gpm.nasa.gov/resources/documents/imerg-v07-atbd>
5. NASA GPM. FAQ: diferenças entre TMPA e IMERG (morphing e filtro de Kalman). <https://gpm.nasa.gov/resources/faq/how-are-tmpa-and-imerg-algorithm-designs-same-and-different>
6. NASA Earthdata. GPM_3IMERGHH V07: descrição detalhada do algoritmo. <https://www.earthdata.nasa.gov/es/data/catalog/ges-disc-gpm-3imerghh-07>
7. NASA Giovanni. <https://giovanni.gsfc.nasa.gov/#dataKeyword=IMERGDF>
8. NASA Earthdata Search. Coleção C2723754864-GES_DISC. <https://search.earthdata.nasa.gov/search/granules?p=C2723754864-GES_DISC>
9. Registry of Open Data on AWS. GPM_3IMERGDF. <https://registry.opendata.aws/nasa-gpm3imergdf/>
10. Earthdata Forum. Problemas comuns de acesso a dados na GES DISC. <https://forum.earthdata.nasa.gov/viewtopic.php?p=12284>
11. Earthdata Login. Acesso a dados com curl e wget (.netrc, cookies, redirecionamento). <https://urs.earthdata.nasa.gov/documentation/for_users/data_access/curl_and_wget>
12. NASA CMR. Search API Documentation. <https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html>
13. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>
14. NASA GPM. IMERG V07 Daily and Grand Climatology Products Documentation. <https://gpm.nasa.gov/resources/documents/imerg-v07-daily-and-grand-climatology-products-documentation>

### 16.2 Base do projeto

15. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` (D-002, D-003).
16. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md` (§7 indicadores, §9.2 pipeline) e `docs/NasaSpaceApps-FieldShift/v1/.md/bancos-de-dados-field-shift-brasil.md`.

*Consulta das fontes: 14 de novembro de 2026. Versões, latências e endereços devem ser conferidos novamente no momento da implementação.*
