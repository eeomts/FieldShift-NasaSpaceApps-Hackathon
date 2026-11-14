# GRACE e GRACE-FO — Análise e documentação

## Tendência de água armazenada (contexto regional)

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
13. [Como e por que usar o GRACE no Field Shift](#13-como-e-por-que-usar-o-grace-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `NASA_POWER.md`. Autenticação e orquestração em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Produto, resolução, variáveis, formato e acesso na página do PO.DAAC [1]; tamanho dos mascons, filtro CRI, período de referência, fatores de ganho e incertezas na página do JPL GRACE Tellus [2]; ferramenta de download em lote no tutorial do PO.DAAC [5], em 14/11/2026. **Nenhum download executado ao vivo.**

**O que vem do contexto e o que foi acrescentado.** GRACE como complementar e a decisão **D-005 ("só como contexto regional")** vêm do repositório [9][10]. O restante foi acrescentado.

---

## 2. Visão geral

**GRACE** (2002–2017) e **GRACE-FO** (desde 2018) são pares de satélites que medem variações do campo gravitacional; daí se calculam **variações da água total armazenada** (rios, lagos, solo, aquíferos, gelo) [1][2].

| Item | Valor | Fonte |
|---|---|---|
| Variável | Anomalia de água armazenada, em **cm de água equivalente** | [1][2] |
| Resolução temporal | Mensal | [1] |
| Resolução espacial real | **Mascons de 3°** (4.551 blocos de área igual) | [1][2] |
| Grade distribuída | 0,5° (720 × 360 pontos); células vizinhas **não são independentes** | [2] |
| Período | Abril de 2002 – presente | [1] |
| Referência das anomalias | Média de **2004,0 a 2009,999** | [2] |
| Formato | NetCDF-4, **um arquivo único** atualizado a cada novo mês | [1][2] |
| Login | Earthdata Login (buckets protegidos e downloads) | [1] |

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | Dois satélites medem continuamente a distância entre si; variações de massa abaixo deles alteram essa distância | GRACE (NASA/DLR) e GRACE-FO (NASA/GFZ) | [3] |
| 2. Campo gravitacional | Medidas viram campos gravitacionais mensais | Centros JPL, CSR e GFZ | [1][4] |
| 3. Solução mascon | O JPL estima a massa em 4.551 blocos de 3°, com restrições geofísicas; não precisa de suavização posterior | JPL | [1][2] |
| 4. Remoção de efeitos | Oceano e atmosfera removidos (variável `GAD`) | JPL | [1] |
| 5. Filtro CRI (opcional) | Separa massa de terra e oceano nos mascons costeiros | JPL | [2] |
| 6. Grade de 0,5° | Valores do mascon repetidos na grade para facilitar o uso | JPL | [2] |
| 7. Distribuição | **PO.DAAC** (JPL), também em AWS S3 | PO.DAAC | [1] |
| 8. Acesso | PO.DAAC, Earthdata Search, OPeNDAP, podaac-data-downloader, earthaccess | Usuário | [1][5] |
| 9. Field Shift | Média regional, fatores de ganho, remoção do ciclo sazonal, tendência (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Dois satélites sentem o 'peso' da água na região. Quando há mais água no solo e nos aquíferos, a gravidade muda um pouquinho. Isso mostra se a reserva de água da região está subindo ou descendo ao longo dos anos."

---

## 4. Produtos

| Produto | Descrição | Para quem | Fonte |
|---|---|---|---|
| **JPL Mascon RL06.3 v04** (`TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4`) | Mascons sem filtro CRI | **"Uso especializado"**; não corrige vazamento costeiro | [1][8] |
| **JPL Mascon RL06.3 com filtro CRI** | Com correção de linha de costa | **Indicado para os demais usuários**, com os fatores de ganho de hidrologia | [1][2] |
| CSR / GFZ TELLUS Level-3 Land RL06.3 v04 | Grades de anomalia sobre o continente, de outros centros | Comparar soluções | [4] |

**Para o Field Shift:** JPL Mascon com **filtro CRI** + **fatores de ganho** (o Brasil tem um litoral extenso, e o CRI corrige o vazamento de sinal entre oceano e continente nas bacias costeiras; também é a versão para a qual os ganhos foram feitos [2]).

---

## 5. Formas de acesso

| Ferramenta | O que faz | Fonte |
|---|---|---|
| **PO.DAAC** (página do dataset) | Descrição, documentos e links | [1] |
| **Earthdata Search / CMR** | Busca e download | [1] |
| **OPeNDAP** (`opendap.earthdata.nasa.gov`) | Ler só a região e o período | [1] |
| **podaac-data-downloader** | Linha de comando, recomendado para lote | [1][5] |
| **AWS S3 (us-west-2)** | Acesso direto na nuvem | [1] |
| **earthaccess** | Busca e download com a mesma conta | [6] |
| **GRACE Tellus** (JPL) | Explicações e visualizações | [2][3] |

> O GRACE **não está no AppEEARS**. Por ser **um único arquivo**, baixe uma vez e recorte localmente.

---

## 6. Parâmetros explicados

### 6.1 podaac-data-downloader [5]

| Argumento | Obrigatório | Explicação |
|---|---|---|
| `-c` / `--collection-shortname` | Sim | Nome curto da coleção |
| `-d` / `--data-dir` | Sim | Pasta de destino |
| `-sd` / `--start-date`, `-ed` / `--end-date` | Um deles | Datas ISO, ex.: `2002-04-01T00:00:00Z` |
| `-b` / `--bounds` | Não | `oeste,sul,leste,norte` sem espaços; use a forma `-b="..."`. **Filtra por metadado; baixa o arquivo inteiro** |

Requer `.netrc` com `machine urs.earthdata.nasa.gov login ... password ...` [5][7].

```bash
pip install podaac-data-subscriber
podaac-data-downloader -c TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4 -d ./grace --start-date 2002-04-01T00:00:00Z
```
⚠️ Para o arquivo com filtro CRI, confirme o nome curto da coleção no PO.DAAC.

### 6.2 earthaccess

| Argumento | Exemplo |
|---|---|
| `short_name` | `"TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4"` (ou a versão CRI) |

---

## 7. Estrutura dos dados

| Variável | Descrição | Unidade | Fonte |
|---|---|---|---|
| `lwe_thickness` | Espessura de água líquida equivalente (anomalia) | cm | [1] |
| `uncertainty` | Incerteza | cm | [1] |
| `GAD` | Modelo de remoção de oceano/atmosfera | cm | [1] |
| `mascon_ID` | Identificador do bloco de 3° | — | [1] |
| `lat`, `lon`, `lat_bounds`, `lon_bounds` | Coordenadas | graus | [1] |
| `time`, `time_bounds` | Mês | — | [1] |
| Fatores de ganho | Variável dentro do arquivo (versão CRI) | adimensional | [2] |

**Sobre a incerteza [2]:** é fornecida na grade de 0,5°, mas cada valor vale para o **mascon inteiro** (só 4.551 valores independentes). É estimada de forma conservadora e é um pouco maior no início e no fim da série.

**Sobre os fatores de ganho [2]:** **ainda não estão aplicados** aos dados; o usuário deve multiplicá-los. Valem só para hidrologia continental, foram feitos para a versão CRI e são dominados pelo ciclo anual, **podendo não ser confiáveis para tendências**.

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Download | Arquivo único da versão CRI (podaac-data-downloader ou earthaccess) | Série inteira num arquivo |
| 2. Longitude | Conferir se vai de 0 a 360 (−46,9° → 313,1°) | Erro comum de recorte |
| 3. Região | Média sobre um bloco de ≥ 3° × 3° em torno da fazenda | Resolução real de 3° [2] |
| 4. Ganho | Multiplicar pelo fator de ganho; calcular a tendência **com e sem** ganho | Ganho recomendado, mas pode não servir para tendência [2] |
| 5. Meses faltantes | Manter como nulo; marcar o intervalo GRACE → GRACE-FO no gráfico | Não interpolar uma lacuna de meses |
| 6. Ciclo sazonal | Subtrair a média de cada mês do ano | Separar tendência da oscilação chuva/seca |
| 7. Tendência | Mann-Kendall + Sen (listado no repositório [10]) | Robusto a valores extremos |
| 8. Incerteza | Propagar `uncertainty` e mostrar a faixa | Transparência |
| 9. Tradução | "cm de água equivalente na região", sempre com aviso de escala | Linguagem do agricultor |
| 10. Uso na pontuação | **Nenhum** no talhão (D-005); só contexto e sugestão de peso | Decisão da equipe [9] |

```python
import earthaccess, xarray as xr, numpy as np

earthaccess.login()
res = earthaccess.search_data(short_name="TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4")
ds = xr.open_dataset(earthaccess.download(res, "./grace")[0])

lon = -46.9 % 360                                                     # passo 2
reg = ds["lwe_thickness"].sel(lat=slice(-20.4, -17.4),
                              lon=slice(lon-1.5, lon+1.5)).mean(["lat", "lon"])  # passo 3
s = reg.to_series().dropna()
anom = s - s.groupby(s.index.month).transform("mean")                # passo 6
t = (anom.index - anom.index[0]).days / 365.25
print(f"Tendência: {np.polyfit(t, anom.values, 1)[0]:.2f} cm/ano")   # passo 7 (versão simples)
```

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | Buscar o dataset | 1 arquivo NetCDF |
| 2 | Listar variáveis | `lwe_thickness`, `uncertainty`, `time` |
| 3 | Série numa região do Brasil (ex.: bacia do São Francisco) | Valores em cm, positivos e negativos |
| 4 | Ciclo anual | Máximo no fim da estação chuvosa, mínimo no fim da seca |
| 5 | Média de 2004–2009 | Próxima de zero (é a referência [2]) |
| 6 | Meses faltantes | Intervalo entre as missões e meses isolados |
| 7 | Dois pontos a 50 km | Praticamente iguais |
| 8 | Anos secos (ex.: 2014–2015 no Sudeste) | Quedas visíveis |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução | Fonte |
|---|---|---|---|
| Downloader pede usuário e senha | `.netrc` ausente | Criar `.netrc` | [5] |
| HTTP 401 | Credencial errada | Corrigir `.netrc` | [7] |
| "Too many redirects" | Cookies corrompidos | Apagar o arquivo de cookies | [7] |
| Recorte vazio | Longitude em 0–360 | Converter (passo 2) | — |
| Tendência muda muito com o ganho | Ganhos dominados pelo ciclo anual | Reportar as duas versões | [2] |

---

## 11. Limitações

1. **Mascons de 3° (~300 km)**: nunca diferencia fazendas [1][2].
2. **Soma tudo** (solo, aquífero, rio, represa).
3. **Mensal**: não capta veranicos.
4. **Intervalo entre GRACE e GRACE-FO** (2017–2018) e meses isolados faltando ⚠️ datas exatas a confirmar.
5. **Anomalia, não total**: relativa a 2004–2009 [2].
6. **Versão sem CRI é "para uso especializado"** [1].
7. **Ganhos podem não servir para tendência** [2].

---

## 12. Boas práticas

1. **Contexto regional apenas** (D-005).
2. **Média sobre ≥ 3° × 3°**.
3. **Remova o ciclo sazonal** antes da tendência.
4. **Mostre a incerteza** e o intervalo entre missões.
5. Reporte a tendência **com e sem ganho**.

---

## 13. Como e por que usar o GRACE no Field Shift

> Contexto: complementar (D-002) e **D-005: GRACE só como contexto regional** [9]. O desafio cita "long-term water trends" e "water‑storage declines".

| Motivo | Por que importa |
|---|---|
| **Único dado do desafio que inclui aquíferos** | Chuva e umidade do solo não mostram a reserva subterrânea |
| **Mais de 20 anos** | Quantifica o que o agricultor percebe ("o poço está mais baixo") |
| **Contexto para estratégias de água** | Região perdendo água valoriza culturas de menor demanda |

| Etapa | Papel |
|---|---|
| Diagnóstico | Cartão de contexto regional |
| Pontuação | **Não altera a nota do talhão** (D-005); pode sugerir peso maior para "economizar água" |
| Linha do tempo (extra) | Série regional com ciclo e tendência |

**Não resolve:** diferenças entre fazendas, nível do poço (ANA HidroWeb, equivalente do NWIS conforme D-003), disponibilidade para irrigação.

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| Tendência regional | Sen da anomalia sem ciclo sazonal (cm/ano) | Cartão de contexto |
| Queda acumulada | Tendência × anos | Comunicação simples |
| Amplitude sazonal | Máximo − mínimo da climatologia mensal | Variação chuva/seca |
| Anos de déficit | Anomalia anual abaixo de −1 desvio | Relacionar com secas |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `NASA_POWER.md` (seção 16).

**Dados usados:** JPL Mascon RL06.3 com filtro CRI, bloco de 3° × 3°, 2002–2025, tratado conforme a seção 8.

- Tendência: **−0,6 cm/ano** (±0,3) sem ganho; −0,7 cm/ano com ganho.
- Queda forte em 2014–2015 e recuperação parcial.
- Amplitude sazonal de ~25 cm.

> 🌎 **Na sua região, a água guardada no solo e nos aquíferos vem diminuindo devagar.** Desde 2002, a reserva média caiu o equivalente a cerca de 14 cm de água espalhados pela região.
> *De onde vem: satélites GRACE e GRACE-FO, média de uma área de ~300 × 300 km.*
> *Importante: dado da região, não da sua fazenda. Não indica o nível do seu poço.*

**Efeito:** não altera a pontuação (D-005); aparece como contexto na estratégia C (sorgo) e pode sugerir aumentar o peso de "reduzir risco de falta de água".

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NASA PO.DAAC. JPL GRACE/GRACE-FO Mascon RL06.3 v04: descrição, variáveis, formato, acesso e ressalvas. <https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4>
2. NASA/JPL GRACE Tellus. O que são mascons: tamanho, CRI, período de referência, fatores de ganho e incertezas. <https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/>
3. NASA PO.DAAC. GRACE-FO — página da missão. <https://podaac.jpl.nasa.gov/GRACE-FO>
4. NASA PO.DAAC. CSR TELLUS GRACE-FO Level-3 Land RL06.3 v04. <https://podaac.jpl.nasa.gov/dataset/TELLUS_GRFO_L3_CSR_RL06.3_LND_v04>
5. NASA PO.DAAC. Tutorial do Data Subscriber/Downloader. <https://podaac.github.io/tutorials/quarto_text/DataSubscriberDownloader.html>
6. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>
7. Earthdata Login. Acesso com curl e wget. <https://urs.earthdata.nasa.gov/documentation/for_users/data_access/curl_and_wget>
8. Citação do dataset: Wiese, D. N. et al. (2023). JPL GRACE and GRACE-FO Mascon RL06.3Mv04. PO.DAAC. DOI 10.5067/TEMSC-3MJ634. Método: Watkins et al. (2015), JGR Solid Earth, doi:10.1002/2014JB011547.

### 16.2 Base do projeto

9. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` (D-002, D-003, D-005).
10. Repositório da equipe, `docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md` (§7 tendência Mann-Kendall + Sen) e `bancos-de-dados-field-shift-brasil.md`.

*Consulta das fontes: 14 de novembro de 2026. Releases do GRACE mudam; confira a versão vigente no PO.DAAC.*
