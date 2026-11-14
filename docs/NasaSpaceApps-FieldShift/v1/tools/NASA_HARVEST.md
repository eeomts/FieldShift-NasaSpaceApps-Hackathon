# NASA Harvest no GitHub (`github.com/nasaharvest`): análise e documentação

## O que existe nos repositórios e o que o Field Shift pode reaproveitar

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Documentos relacionados: `NASA_HARVEST_PORTAL_API.md`, `NASA_HARVEST_PORTAL_MCP.md`, `ARQUITETURA-COMPLETA.md`, `MODIS_VIIRS.md`, `HLS.md`

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Catálogo dos repositórios](#2-catálogo-dos-repositórios)
3. [crop-cycle-detection (prioridade alta)](#3-crop-cycle-detection-prioridade-alta)
4. [crop-stage-detection](#4-crop-stage-detection)
5. [Presto e Galileo (modelos de base)](#5-presto-e-galileo-modelos-de-base)
6. [CropHarvest (dataset de treino)](#6-cropharvest-dataset-de-treino)
7. [crop-mask e OpenMapFlow (mapas de lavoura)](#7-crop-mask-e-openmapflow-mapas-de-lavoura)
8. [Infraestrutura: GLAM e Harvest Portal](#8-infraestrutura-glam-e-harvest-portal)
9. [Como cada repositório entra no Field Shift](#9-como-cada-repositório-entra-no-field-shift)
10. [Integração: MODIS NDVI + crop-cycle-detection](#10-integração-modis-ndvi--crop-cycle-detection)
11. [Caso de uso: descobrir a rotação real e o solo descoberto](#11-caso-de-uso-descobrir-a-rotação-real-e-o-solo-descoberto)
12. [Licenças](#12-licenças)
13. [Limitações](#13-limitações)
14. [Boas práticas](#14-boas-práticas)
15. [Referências](#15-referências)

---

## Nível de verificação

- A lista de repositórios vem das páginas públicas da organização no GitHub (30 dos 31 repositórios listados; a página que continha o último não carregou).
- Os repositórios **crop-cycle-detection**, **crop-stage-detection**, **glam-api**, **galileo**, **openmapflow** e **crop-mask** foram **clonados e seus READMEs lidos**.
- **crop-cycle-detection** e **crop-stage-detection** foram **instalados e executados** com os dados de exemplo dos próprios repositórios. As saídas da seção 3.6 e 4.5 são reais.
- **presto** e **cropharvest** foram lidos pela página do GitHub, sem execução.
- Datas de atualização e estrelas mudam com o tempo; os valores são de 14/11/2026.

---

## 1. Visão geral

A organização **`nasaharvest`** no GitHub reúne o código aberto do **NASA Harvest**, o programa de segurança alimentar e agricultura da NASA, liderado pela Universidade de Maryland.

| Item | Valor |
|---|---|
| Endereço | https://github.com/nasaharvest |
| Repositórios públicos | 31 |
| Linguagens principais | Python e Jupyter Notebook |
| Licenças mais comuns | MIT, Apache-2.0, CC BY-SA 4.0 (dados) |
| Mais populares | presto, cropharvest, galileo, crop-mask, openmapflow |
| Mais recentes e úteis para o Field Shift | crop-cycle-detection, crop-stage-detection |

**Relação com o Harvest Portal:**

| | Harvest Portal | GitHub nasaharvest |
|---|---|---|
| Entrega | **Dados** (datasets, tabelas) | **Código** (modelos, ferramentas, pipelines) |
| Uso no Field Shift | Nota de mercado | Analisar o NDVI do talhão (rotação real, solo descoberto, fase da lavoura) |
| Acesso | API e MCP | `git clone` / `pip install` |

---

## 2. Catálogo dos repositórios

### 2.1 Análise de NDVI por talhão

| Repositório | O que faz | Linguagem | Licença | Atualizado |
|---|---|---|---|---|
| **crop-cycle-detection** | Conta os ciclos de cultivo numa série de NDVI e extrai início, fim, pico e *green-up* de cada safra | Python | Apache-2.0 | ago/2026 |
| **crop-stage-detection** | Estima a fase atual da lavoura (A a E) a partir do NDVI | Python | Apache-2.0 | ago/2026 |

### 2.2 Modelos de base (IA pré-treinada para satélite)

| Repositório | O que faz | Licença |
|---|---|---|
| **presto** | Transformer leve pré-treinado para séries temporais de sensoriamento remoto | MIT |
| **galileo** | Família de modelos pré-treinados (sucessor do Presto) | MIT |
| **presto-embeddings** | Material relacionado ao Presto | — |
| **timl** | Meta-aprendizado informado pela tarefa | — |
| **crop-maml** | Previsão de tipo de cultura com rótulos escassos (meta-aprendizado) | — |

### 2.3 Dados de treino e mapas de lavoura

| Repositório | O que faz | Licença |
|---|---|---|
| **cropharvest** | Dataset aberto de rótulos agrícolas com benchmarks | CC BY-SA 4.0 |
| **crop-mask** | Fluxo completo para mapas de lavoura em alta resolução | Apache-2.0 |
| **openmapflow** | Criação rápida de mapas com aprendizado de máquina e satélite | Apache-2.0 |
| **kenya-crop-mask**, **togo-crop-mask** | Mapas de lavoura do Quênia e do Togo | — |
| **us-inseason-phenorm** | Tipo de cultura durante a safra no Corn Belt (EUA) | — |
| **croptype-mapping-gsn** | Classificação de cultura com normalização por fase | — |

### 2.4 Infraestrutura

| Repositório | O que faz |
|---|---|
| **glam-api** | Backend Django e API do GLAM (Global Agriculture Monitoring) |
| **glam-processing**, **glam_data_processing** (arquivado) | Processamento de dados do GLAM |
| **octvi** | Baixa, junta e compõe NDVI na escala do MODIS |
| **ckanext-harvestportal**, **ckan** | Extensão e fork do CKAN: o código do próprio Harvest Portal |
| **rise-eo** | Pipeline de imagens de satélite (dados de treino, modelos, saída STAC/COG; local ou Azure ML) |
| **mlhub** | Biblioteca para o mlhub.earth |

### 2.5 Ensino e outros

| Repositório | O que é |
|---|---|
| **crop-mapping-course** | Curso de mapeamento de culturas |
| **ml-for-remote-sensing** | Materiais do ICLR 2023 |
| **capacity-building** | Material de capacitação |
| **nasaharvest.github.io** | Site com informações dos projetos |
| **street2sat**, **helmets-kenya**, **dora**, **yield** | Projetos menores ou sem descrição |

---

## 3. crop-cycle-detection (prioridade alta)

### 3.1 O que é

Um modelo que **detecta os ciclos de cultivo** numa série de NDVI e extrai as datas importantes de cada safra. Funciona com **qualquer cultura**, sem calibração específica.

**Por que funciona:** a maioria das culturas anuais segue a mesma forma de curva de NDVI: solo nu → crescimento → pico → senescência → colheita. O modelo encontra essa forma sem saber qual cultura é.

A série pode ter **vários anos**; o modelo encontra **todas** as safras completas dentro dela.

### 3.2 Como funciona por dentro

1. Remove picos para baixo causados por nuvem (regressão local).
2. Converte para série diária e preenche lacunas com interpolação PCHIP.
3. Suaviza com filtro de Whittaker.
4. Encontra picos e vales do NDVI e define cada safra de vale a vale.
5. Estima *green-up*, início e fim aproximados e data do pico de cada safra.

### 3.3 Entrada

`crop_cycle_model(df)` recebe uma tabela (pandas) de **um talhão**:

| Coluna | Tipo | Descrição |
|---|---|---|
| `date` | data | Data da observação |
| `NDVI` | número (0 a 1) | Valor de NDVI |
| `poly_name` | texto (opcional) | Identificador do talhão |

Para vários talhões, chame a função uma vez por talhão.

### 3.4 Saída

Uma tupla `(report, ndvi_for_processing)`.

**`report`** — uma linha por safra detectada:

| Coluna | Descrição |
|---|---|
| `season_number` | Número da safra, em ordem |
| `approx_season_start` | Início aproximado |
| `approx_season_end` | Fim aproximado |
| `approx_season_length` | Duração em dias |
| `greenup_date` | Data do *green-up* (arranque do crescimento) |
| `ndvi_peak_date` | Data do pico de NDVI |
| `ndvi_peak_value` | Valor do pico |
| `trough_before_peak` | Vale antes do pico |
| `trough_after_peak` | Vale depois do pico |
| `troughs_days_distance` | Dias entre os dois vales |

**`ndvi_for_processing`** — a série diária suavizada (`date`, `NDVI`, `NDVI_interpolated`).

### 3.5 Parâmetros ajustáveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `ndvi_threshold_for_approx_season_start` | 0,35 | NDVI fixo de início, usado se o limiar adaptativo falhar |
| `ndvi_threshold_for_approx_season_end` | 0,40 | NDVI fixo de fim, usado se o limiar adaptativo falhar |
| `min_season_length` | 60 | Duração mínima de uma safra válida (dias) |
| `min_ndvi_for_peak` | None | Limiar fixo de pico; se None, é adaptativo |
| `ndvi_peak_percentile` | 90 | Percentil usado no limiar adaptativo de pico |
| `ndvi_peak_threshold_ceiling` | 0,7 | Teto do limiar adaptativo de pico |
| `season_start_pct_of_peak` | 0,35 | Início = fração do pico (tentado antes do limiar fixo) |
| `season_end_pct_of_peak` | 0,35 | Fim = fração do pico |
| `season_window_days` | 90 | Janela de busca quando falta um vale |
| `exclude_months` | None | Ignora safras cujo pico cai nesses meses (ex.: para filtrar plantas de cobertura) |

**Atenção para o Brasil:** `min_season_length=60` pode cortar ciclos curtos de safrinha ou de cobertura. `exclude_months` pode ser usado para separar a safra principal da safrinha.

### 3.6 Teste executado (dados de exemplo do repositório)

```bash
git clone https://github.com/nasaharvest/crop-cycle-detection.git
cd crop-cycle-detection
pip install -r requirements.txt     # numpy, pandas, scipy, statsmodels, matplotlib
```

```python
import sys, pandas as pd
sys.path.insert(0, ".")
from src.crop_cycle import crop_cycle_model

df = pd.read_csv("sample_data/example_ndvi.csv", parse_dates=["date"])
report, ndvi_processado = crop_cycle_model(df)
print(report)
```

Entrada: 152 observações de NDVI, de 14/08/2024 a 09/08/2026.

**Saída real:**

| Safra | Início aprox. | Fim aprox. | Duração | Green-up | Pico | NDVI pico | Vale antes | Vale depois |
|---|---|---|---|---|---|---|---|---|
| 1 | 27/05/2025 | 09/10/2025 | 135 dias | 09/06/2025 | 18/08/2025 | 0,84 | 12/05/2025 | 21/11/2025 |
| 2 | 06/05/2026 | (em andamento) | — | 19/05/2026 | 22/06/2026 | 0,83 | 12/04/2026 | — |

A segunda safra ainda não terminou no fim da série; por isso o fim aparece vazio.

### 3.7 Outras informações

| Item | Valor |
|---|---|
| Requisito | Python 3.9+ |
| Notebook | `examples/01_byod.ipynb` (também no Colab) |
| Versão hospedada | `agri-field-cycle.growerstech.com` |
| Autor | Ran Pelta (Agmatix / GrowersTech, NASA Harvest) |
| Licença | Apache-2.0 |

---

## 4. crop-stage-detection

### 4.1 O que é

Estima **em que fase a lavoura está agora**, a partir da série de NDVI. Também funciona com qualquer cultura.

### 4.2 As cinco fases

| Fase | Nome | NDVI | Tendência | Pico já confirmado? |
|---|---|---|---|---|
| **A** | Solo nu / plantio / emergência | Abaixo do limiar inferior | Qualquer | Não |
| **B** | Crescimento rápido | Entre os limiares | Subindo | Não |
| **C** | Pico / maturidade vegetativa | Acima do limiar superior | Qualquer | — |
| **D** | Senescência | Entre os limiares | Caindo | Sim |
| **E** | Pós-colheita / palhada / solo nu | Abaixo do limiar inferior | Qualquer | Sim |

A tendência é estimada com um filtro de Kalman. A série passa pelo mesmo pré-processamento do crop-cycle-detection (diária, PCHIP, Whittaker). Com menos de 30 dias de dados, devolve "Insufficient Data".

### 4.3 Duas formas de entrada

| Função | Entrada | Observação |
|---|---|---|
| `run_crop_stage_from_dataframe(df, ...)` | Tabela com `date` e `NDVI` (e `id_col` opcional para vários talhões) | Traga seus próprios dados |
| `run_crop_stage_from_gee(polygon, ...)` | Polígono do talhão | Busca NDVI do Sentinel-2 e do Landsat no **Google Earth Engine**; padrão: últimos 150 dias. Exige conta no GEE |

### 4.4 Saída

| Chave | Descrição |
|---|---|
| `Stage` | A, B, C, D, E ou "Insufficient Data" |
| `Stage_description` | Nome da fase |
| `Value` | NDVI da última observação |
| `Velocity` | Velocidade de mudança do NDVI (por dia) |
| `Last_date` | Data da última observação |
| `Peak_date` | Data do pico detectado |
| `Days_since_peak` | Dias desde o pico |
| `Upper_threshold`, `Lower_threshold` | Limiares usados |

### 4.5 Teste executado (mesma série de exemplo)

```python
from src.crop_stage import run_crop_stage_from_dataframe
print(run_crop_stage_from_dataframe(df))
```

**Saída real:**

| Campo | Valor |
|---|---|
| Fase | **D — Senescência** |
| NDVI na última data | 0,46 |
| Velocidade | −0,0095 por dia (caindo) |
| Última data | 09/08/2026 |
| Pico | 19/06/2026 |
| Dias desde o pico | 51 |
| Limiar superior / inferior | 0,79 / 0,35 |

Leitura: a lavoura passou do pico há 51 dias e está secando, perto da colheita.

---

## 5. Presto e Galileo (modelos de base)

### 5.1 Presto

| Item | Descrição |
|---|---|
| O que é | Transformer leve, pré-treinado, para séries temporais de sensoriamento remoto |
| Artigo | "Lightweight, Pre-trained Transformers for Remote Sensing Timeseries" (Tseng et al.) |
| Entradas | Sentinel-1, Sentinel-2, ERA5 (clima), SRTM (relevo); Dynamic World (cobertura do solo) opcional |
| Tempo | 1 a 24 passos (até 2 anos) |
| Usos | *Fine-tuning* com uma camada de saída, ou extração de *embeddings* |
| Integração | Pode ser publicado na Vertex AI e chamado pelo Google Earth Engine |
| Pesos | `Presto.load_pretrained()` |
| Licença | MIT |

### 5.2 Galileo

| Item | Descrição |
|---|---|
| O que é | Família de modelos pré-treinados de sensoriamento remoto (sucessor do Presto) |
| Entradas | Dados que variam no espaço e no tempo, só no espaço, só no tempo e estáticos |
| Tamanhos | Vários; o menor é o "nano" |
| Uso | `Encoder.load_from_folder(...)` ou `single_file_galileo.py` para levar a outro projeto |
| Licença | MIT |

**Para o Field Shift:** poderosos, mas exigem montar entradas multissensor e treinar uma camada final. **Pesados demais para 48 horas.** Bons para citar no pitch como caminho futuro (ex.: classificar o tipo de cultura em cada talhão).

---

## 6. CropHarvest (dataset de treino)

| Item | Valor |
|---|---|
| O que é | Dataset aberto de sensoriamento remoto para agricultura, com benchmarks |
| Origem | 21 datasets de uso do solo agrícola + produtos de satélite |
| Tamanho | 95.186 pontos |
| Com tipo de cultura | 33.205 (35%); o resto é só "lavoura / não lavoura" |
| Com satélite e clima | 70.213 (74%) |
| Entradas | Sentinel-2, Sentinel-1, SRTM, ERA5 |
| Instalação | `pip install cropharvest` (no Windows, instalar `fiona` e `rasterio` com conda antes) |
| Download | Zenodo |
| Licença | CC BY-SA 4.0 |

**Uso típico:**

```python
from sklearn.ensemble import RandomForestClassifier
from cropharvest.datasets import Task, CropHarvest
from cropharvest.countries import get_country_bbox

bbox = get_country_bbox("France")[1]
task = Task(bounding_box=bbox, normalize=True)
dataset = CropHarvest("data", task)
X, y = dataset.as_array(flatten_x=True)
model = RandomForestClassifier(random_state=0).fit(X, y)
```

**Para o Field Shift:** a página não lista países nem menciona o Brasil. Serve como referência de método, não como fonte para a demo.

---

## 7. crop-mask e OpenMapFlow (mapas de lavoura)

| Repositório | O que faz | Como usar |
|---|---|---|
| **crop-mask** | Fluxo completo para mapas de lavoura em alta resolução. Treina dois modelos: um classificador "lavoura / não lavoura" por pixel e um previsor que completa uma série de 12 meses a partir de uma série parcial | Notebooks no Colab: criar mapa, treinar modelo, adicionar rótulos |
| **openmapflow** | Ferramenta genérica para criar mapas com aprendizado de máquina e satélite. Exemplos: lavoura, construções, milho | Gera um projeto, adiciona dados, treina e publica |

**Para o Field Shift:** úteis se o projeto evoluir para mapear lavouras numa região inteira. Fora do escopo das 48 horas.

---

## 8. Infraestrutura: GLAM e Harvest Portal

| Repositório | Relação com o Field Shift |
|---|---|
| **glam-api** | Backend do GLAM, o sistema de monitoramento agrícola global da NASA/USDA. Referência de como a NASA serve séries de NDVI por região |
| **octvi** | Baixa e compõe NDVI na escala do MODIS. Pode inspirar o passo de coleta do NDVI |
| **ckanext-harvestportal** e **ckan** | O código do próprio Harvest Portal. Explica por que a API segue o padrão CKAN |

---

## 9. Como cada repositório entra no Field Shift

| Repositório | Passo da arquitetura | Uso | Prioridade |
|---|---|---|---|
| **crop-cycle-detection** | Passo 4 — diagnóstico | Detectar a **rotação real** do talhão e os **períodos de solo descoberto** a partir do MODIS NDVI | 🟢 Alta |
| **crop-stage-detection** | Passo 8 — tela | Mostrar "sua lavoura está em senescência, 51 dias depois do pico" | 🟡 Média |
| **presto / galileo** | Futuro | Classificar o tipo de cultura de cada talhão | ⚪ Pitch |
| **cropharvest** | Futuro | Dados de treino para classificação | ⚪ Pitch |
| **crop-mask / openmapflow** | Futuro | Mapa regional de lavouras | ⚪ Pitch |
| **glam-api / octvi** | Referência | Como processar NDVI do MODIS | ⚪ Consulta |

**Por que o crop-cycle-detection é o mais importante:** o desafio pede explicitamente para destacar **quando os campos ficam descobertos**. O modelo entrega isso pronto, com método publicado pela própria NASA Harvest. Em vez de inventar uma regra de NDVI, a equipe usa um modelo oficial e cita no pitch.

---

## 10. Integração: MODIS NDVI + crop-cycle-detection

### 10.1 Fluxo

```
Talhão (lat, lon)
      │
      ▼
MODIS MOD13Q1 NDVI (250 m, 16 dias), via AppEEARS ⚠️      ← preparo (Earthdata Login)
      │  CSV: data, NDVI (escala 0,0001 → converter para 0–1), qualidade
      ▼
Limpeza: descartar pixels de baixa qualidade; NDVI = valor × 0,0001
      │
      ▼
crop_cycle_model(df)                                       ← crop-cycle-detection
      │
      ├── report: safras com início, fim, pico
      └── série diária suavizada
      │
      ▼
Derivados para o Field Shift:
  • nº de safras por ano (1 = só verão; 2 = verão + safrinha)
  • meses de solo descoberto = intervalos fora das safras com NDVI baixo
  • comparação com a rotação que o agricultor cadastrou
```

⚠️ Confirme o nome do produto, a camada de NDVI, o fator de escala e a camada de qualidade em `MODIS_VIIRS.md` e no AppEEARS.

### 10.2 Código de integração (esboço)

```python
import pandas as pd
from src.crop_cycle import crop_cycle_model

def preparar_modis(csv_appeears):
    df = pd.read_csv(csv_appeears)
    # ⚠️ ajustar nomes de colunas conforme o CSV do AppEEARS
    df = df.rename(columns={"Date": "date", "MOD13Q1_061__250m_16_days_NDVI": "NDVI"})
    df["date"] = pd.to_datetime(df["date"])
    df["NDVI"] = df["NDVI"] * 0.0001          # escala do MOD13Q1 ⚠️
    df = df[(df["NDVI"] > -0.2) & (df["NDVI"] <= 1)]
    return df[["date", "NDVI"]]

def diagnostico_campo(df_ndvi):
    report, diario = crop_cycle_model(df_ndvi, min_season_length=60)
    diario = diario.set_index("date")
    # meses de solo descoberto: NDVI suavizado < 0,3 fora das safras
    diario["mes"] = diario.index.month
    descoberto = (diario["NDVI_interpolated"] < 0.3).groupby(diario["mes"]).mean()
    meses_descobertos = [m for m, frac in descoberto.items() if frac > 0.5]
    safras_por_ano = report.groupby(report["ndvi_peak_date"].dt.year).size().mean()
    return {"safras_por_ano": round(safras_por_ano, 1),
            "meses_solo_descoberto": meses_descobertos,
            "safras": report}
```

O limiar de 0,3 para "solo descoberto" é uma proposta e precisa ser validado.

---

## 11. Caso de uso: descobrir a rotação real e o solo descoberto

> ⚠️ Os números do agricultor são fictícios. A saída do modelo nas seções 3.6 e 4.5 é real, mas vem dos dados de exemplo do repositório, não de um talhão brasileiro.

### 11.1 Ficha

| Item | Descrição |
|---|---|
| **Nome** | UC-03 · Diagnosticar a rotação real e os períodos de solo descoberto do talhão |
| **Ator principal** | Agricultor |
| **Ator de sistema** | Back-end do Field Shift |
| **Componentes** | MODIS NDVI (dado), crop-cycle-detection (modelo), crop-stage-detection (opcional) |
| **Objetivo** | Mostrar ao agricultor quantas safras o talhão realmente tem por ano, quando o solo fica descoberto e em que fase a lavoura está |
| **Gatilho** | O agricultor toca em **"Analisar meu campo"** |
| **Pré-condições** | 1) Talhão cadastrado. 2) Série de MODIS NDVI do talhão baixada no preparo (2001 em diante). 3) crop-cycle-detection instalado no back-end |
| **Pós-condição de sucesso** | A tela "Raio-x do campo" mostra as safras detectadas, os meses de solo descoberto e a comparação com a rotação cadastrada |
| **Pós-condição de falha** | O raio-x mostra só os dados de clima, com o aviso "histórico de vegetação indisponível" |

### 11.2 Situação

O agricultor cadastrou: **soja (out–fev) → milho safrinha (fev–jul) → pousio (ago–out)**. Ele reclama de erosão nas primeiras chuvas. A ferramenta quer confirmar com dados de satélite.

### 11.3 Fluxo principal

| # | Quem | O que acontece |
|---|---|---|
| 1 | Agricultor | Toca em **"Analisar meu campo"** |
| 2 | Back-end | Carrega a série MODIS NDVI do talhão (cache) |
| 3 | Back-end | Converte a escala, remove pixels ruins e monta a tabela `date`, `NDVI` |
| 4 | Back-end | Chama `crop_cycle_model(df)` |
| 5 | crop-cycle-detection | Devolve as safras detectadas e a série diária suavizada |
| 6 | Back-end | Calcula safras por ano e meses de solo descoberto |
| 7 | Back-end | Compara com a rotação cadastrada |
| 8 | Back-end | (Opcional) chama `run_crop_stage_from_dataframe(df)` para a fase atual |
| 9 | Back-end | Cruza os meses de solo descoberto com as chuvas fortes (GPM/POWER) e a declividade (SRTM) |
| 10 | Agricultor | Vê os cartões do raio-x |

### 11.4 O que o agricultor vê (fictício)

> 🌱 **Seu talhão tem 2 safras por ano** na maioria dos anos (verão e safrinha), igual ao que você cadastrou.
> *De onde vem: MODIS NDVI 2001–2025 (250 m), analisado com o modelo crop-cycle-detection do NASA Harvest.*

> 🟫 **O solo fica descoberto de agosto a outubro** em 8 de cada 10 anos. As primeiras chuvas fortes de outubro caem sobre esse solo nu, na parte mais inclinada do talhão.
> *De onde vem: MODIS NDVI, GPM IMERG e SRTM.*

> 📍 **Agora:** sua lavoura está em **senescência**, cerca de 50 dias depois do pico.
> *De onde vem: MODIS NDVI, modelo crop-stage-detection do NASA Harvest.*

### 11.5 Como isso alimenta a recomendação

| Resultado do UC-03 | Efeito nos passos seguintes |
|---|---|
| Solo descoberto de agosto a outubro | Estratégias com planta de cobertura ou consórcio (ex.: braquiária) ganham nota em "proteção do solo" |
| 2 safras por ano confirmadas | A janela de safrinha é real; o filtro climático avalia culturas para ela |
| Safrinha com pico de NDVI mais baixo que o verão | Indício de estresse na safrinha; reforça o diagnóstico de déficit hídrico do NASA POWER |

### 11.6 Fluxos alternativos

| Código | Situação | O que acontece |
|---|---|---|
| **A1** | O modelo encontra 1 safra por ano, mas o agricultor cadastrou 2 | A tela mostra a diferença e pergunta se a safrinha é recente ou se o talhão marcado está certo |
| **A2** | Safra curta (< 60 dias) não detectada | Rodar de novo com `min_season_length` menor e indicar "safra curta" |
| **A3** | Talhão menor que um pixel MODIS (250 m) | Avisar que o NDVI mistura o entorno; sugerir Landsat (30 m) |

### 11.7 Fluxos de exceção

| Código | Situação | O que acontece |
|---|---|---|
| **E1** | Série de NDVI ausente ou com poucas observações válidas | Raio-x sem vegetação, com aviso |
| **E2** | `report` vazio (nenhuma safra detectada) | Mostrar "não foi possível identificar safras; o talhão pode ser pastagem ou vegetação nativa" |
| **E3** | `crop-stage-detection` devolve "Insufficient Data" | Omitir o cartão "Agora" |

### 11.8 Critérios de aceite

| # | Dado que... | Quando... | Então... |
|---|---|---|---|
| 1 | Existe série MODIS do talhão | O agricultor toca em "Analisar meu campo" | A tela mostra o número de safras por ano e a fonte "MODIS + crop-cycle-detection" |
| 2 | O NDVI fica abaixo do limiar de agosto a outubro | O diagnóstico roda | O cartão "solo descoberto" aparece com esses meses |
| 3 | O modelo detecta menos safras que o cadastro | O diagnóstico roda | A tela mostra a diferença e pede confirmação |
| 4 | Não há série de NDVI | O diagnóstico roda | O raio-x mostra só o clima, com aviso |
| 5 | A série de exemplo do repositório | `crop_cycle_model` roda | Devolve 2 safras, com picos em 18/08/2025 e 22/06/2026 (teste de regressão) |

---

## 12. Licenças

| Repositório | Licença | O que permite |
|---|---|---|
| crop-cycle-detection, crop-stage-detection, crop-mask, openmapflow | **Apache-2.0** | Usar, modificar e distribuir, inclusive comercialmente, mantendo o aviso de licença |
| presto, galileo, octvi, dora | **MIT** | Usar, modificar e distribuir com aviso de copyright |
| cropharvest (dados) | **CC BY-SA 4.0** | Usar com atribuição; derivados com a mesma licença |
| ckanext-harvestportal | **AGPL-3.0** | Se modificar e oferecer como serviço, precisa publicar o código |
| Vários outros | Não informada | **Não reutilize código sem licença** sem pedir autorização |

**Citação do crop-cycle-detection** (recomendada pelo autor): Pelta, R. (2026). *Crop Cycle Detection*. NASA Harvest / Agmatix. https://github.com/nasaharvest/crop-cycle-detection

---

## 13. Limitações

| Limitação | Consequência |
|---|---|
| **Nenhum README cita o Brasil** | Os modelos de NDVI dizem funcionar com qualquer cultura, mas não há validação publicada para soja/milho safrinha brasileiros. Testar antes |
| **Limiares padrão** | `min_season_length=60` e limiares de NDVI podem não servir para safrinhas curtas ou culturas de cobertura |
| **Dependência do NDVI** | Nuvem na estação chuvosa reduz observações válidas; o pré-processamento ajuda, mas não resolve tudo |
| **Resolução do MODIS** | 250 m mistura talhões pequenos com o entorno |
| **GEE no crop-stage-detection** | A função que busca dados sozinha exige conta no Google Earth Engine |
| **Modelos de base pesados** | Presto e Galileo exigem montagem de entradas multissensor e GPU para treinar |
| **Repositórios antigos** | Vários sem atualização desde 2020–2022 e sem licença |

---

## 14. Boas práticas

1. **Comece pelo crop-cycle-detection.** É o de maior retorno para o desafio e roda em segundos.
2. **Valide com um talhão conhecido** (onde a equipe sabe o que foi plantado) antes da demo.
3. **Ajuste os parâmetros** para o calendário brasileiro (`min_season_length`, `exclude_months`).
4. **Fixe a versão** do repositório (anote o commit usado) para a demo não mudar.
5. **Cite o modelo e a NASA Harvest** na tela e no pitch.
6. **Respeite as licenças**; não use código sem licença declarada.
7. **Guarde o resultado em cache**; o histórico de NDVI não muda.

---

## 15. Referências

**Organização**
- https://github.com/nasaharvest
- Lista de repositórios: https://github.com/orgs/nasaharvest/repositories

**Repositórios analisados**
- crop-cycle-detection: https://github.com/nasaharvest/crop-cycle-detection
- crop-stage-detection: https://github.com/nasaharvest/crop-stage-detection
- presto: https://github.com/nasaharvest/presto (artigo: https://arxiv.org/abs/2304.14065)
- galileo: https://github.com/nasaharvest/galileo (artigo: https://arxiv.org/abs/2502.09356)
- cropharvest: https://github.com/nasaharvest/cropharvest
- crop-mask: https://github.com/nasaharvest/crop-mask
- openmapflow: https://github.com/nasaharvest/openmapflow
- glam-api: https://github.com/nasaharvest/glam-api

**Documentos do projeto**
- `NASA_HARVEST_PORTAL_API.md`, `NASA_HARVEST_PORTAL_API_GUIA.md`, `NASA_HARVEST_PORTAL_MCP.md`
- `ARQUITETURA-COMPLETA.md`
- `MODIS_VIIRS.md`, `HLS.md`
