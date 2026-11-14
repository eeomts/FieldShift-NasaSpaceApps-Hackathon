# SMAP — Análise e documentação

## Umidade do solo por satélite

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP (Field Shift Minas) · 14 de novembro de 2026*

> ⚠️ Todos os números do caso hipotético (seção 15) são fictícios. As aplicações descrevem possibilidades para o projeto, não funcionalidades já implementadas.

---

## Sumário

1. [Como ler este documento](#1-como-ler-este-documento)
2. [Visão geral](#2-visão-geral)
3. [De onde vêm os dados](#3-de-onde-vêm-os-dados)
4. [Produtos e versões](#4-produtos-e-versões)
5. [Formas de acesso](#5-formas-de-acesso)
6. [Parâmetros explicados (AppEEARS)](#6-parâmetros-explicados-appeears)
7. [Estrutura dos dados](#7-estrutura-dos-dados)
8. [Tratamento dos dados no Field Shift](#8-tratamento-dos-dados-no-field-shift)
9. [Como testar](#9-como-testar)
10. [Códigos de erro e problemas comuns](#10-códigos-de-erro-e-problemas-comuns)
11. [Limitações](#11-limitações)
12. [Boas práticas](#12-boas-práticas)
13. [Como e por que usar o SMAP no Field Shift](#13-como-e-por-que-usar-o-smap-no-field-shift)
14. [Parâmetros úteis e indicadores derivados](#14-parâmetros-úteis-e-indicadores-derivados)
15. [Caso hipotético: o Sr. José](#15-caso-hipotético-o-sr-josé)
16. [Fontes e rastreabilidade](#16-fontes-e-rastreabilidade)

---

## 1. Como ler este documento

**Estrutura.** Mesmo formato do `nasa-power-api-daily.md`. Autenticação, AppEEARS e orquestração entre APIs estão detalhados em `comunicacao-entre-apis.md`.

**Referências.** Números entre colchetes apontam para a seção 16.

**O que foi verificado.** Versões vigentes, grade, formatos e opções de acesso foram conferidos nas páginas do NSIDC; nomes de variáveis, unidades, preenchimento e flags, no guia do usuário do SMAP L3 em 14/11/2026. **Nenhum download executado ao vivo** (exige Earthdata Login).

**Mudança importante encontrada:** versões citadas em muitos tutoriais foram **aposentadas** (SPL3SMP v6 e SPL4SMGP v7) [3][4].

**O que vem do contexto e o que foi acrescentado.** A classificação do SMAP como obrigatório e o indicador "anomalia de umidade do solo" vêm do repositório [13][14]. O restante foi acrescentado aqui.

---

## 2. Visão geral

**SMAP** (*Soil Moisture Active Passive*) mede a umidade da camada superficial do solo e o estado de congelamento, com revisita global a cada 2–3 dias [7].

| Item | Valor | Fonte |
|---|---|---|
| Início dos dados | 31/03/2015 | [1] |
| Instrumento em operação | Radiômetro de micro-ondas banda L | [4][6] |
| Profundidade | ~5 cm superiores | [7] |
| Passagens | **6h** (descendente) e **18h** (ascendente), hora solar local no Equador | [2] |
| Grade | EASE-Grid 2.0 Global (EPSG:6933) | [1] |
| Formato | HDF5 | [1] |
| Login | NASA Earthdata Login | [1] |

---

## 3. De onde vêm os dados

| Etapa | O que acontece | Quem faz | Fonte |
|---|---|---|---|
| 1. Observação | O radiômetro banda L mede a **temperatura de brilho** da superfície; solo úmido emite menos micro-ondas | Satélite SMAP (NASA/JPL) | [6][7] |
| 2. Recuperação (L2) | Algoritmo converte temperatura de brilho em umidade volumétrica, corrigindo vegetação e temperatura | Equipe SMAP | [6] |
| 3. Grade diária (L3) | Passagens do dia compostas numa grade global; manhã e tarde em grupos separados | Equipe SMAP | [1][2] |
| 4. Versão Enhanced (L3_E) | Reamostragem para grade de 9 km | Equipe SMAP | [1] |
| 5. Assimilação (L4) | As temperaturas de brilho são assimiladas no modelo de superfície **GEOS-5**, gerando umidade superficial e da **zona radicular** a cada 3 h | NASA GMAO | [3][12] |
| 6. Distribuição | **NSIDC DAAC**, migrando para o Earthdata Cloud | NSIDC | [1][3] |
| 7. Acesso | AppEEARS, Data Access Tool, earthaccess, Harmony | Usuário | [1] |
| 8. Field Shift | Série do talhão, filtro de qualidade e anomalias (seção 8) | Equipe | — |

> **Resumo para o agricultor:** "Um satélite mede o quanto o solo emite de micro-ondas. Solo molhado emite menos. Isso vira uma estimativa de quanta água há nos primeiros centímetros, para quadrados de ~9 km."

---

## 4. Produtos e versões

| Produto | Descrição | Resolução | Frequência | Situação em 14/11/2026 | Fonte |
|---|---|---|---|---|---|
| **SPL3SMP_E** | L3 Enhanced, umidade superficial | **9 km** | Diária | **v6 é a mais recente** | [1] |
| SPL3SMP | L3 padrão | 36 km | Diária | v6 aposentada; NSIDC aponta versão mais nova | [4] |
| **SPL4SMGP** | L4, superfície e **zona radicular**, modelo + observação | 9 km | **3 horas** | v7 aposentada (dados até 03/07/2025); **v8 vigente** | [3] |

A v8 do L4 acrescenta um módulo de hidrologia de turfeiras e parâmetros revisados de transferência radiativa [3].

**Para o Field Shift:** SPL3SMP_E v6 (observação direta, anomalias) + SPL4SMGP v8 (zona radicular, estresse das culturas).

---

## 5. Formas de acesso

| Ferramenta | O que faz | Fonte |
|---|---|---|
| **AppEEARS** | Série por ponto (CSV) ou área (GeoTIFF/NetCDF), já reprojetada | [1][8] |
| **NSIDC Data Access Tool** | Filtra, baixa e gera script Python | [1] |
| **Earthdata Search** | Busca visual | [1] |
| **earthaccess** | Busca e download em Python | [1][10] |
| **Harmony** | Serviços de transformação (recorte, reformatação) | [1] |
| **HTTPS File System** | Diretório de arquivos | [1] |
| **Earthdata Cloud (S3, us-west-2)** | Acesso direto na AWS, com credenciais adicionais | [1] |

**Recomendado:** AppEEARS por ponto, que evita lidar com HDF5 e EASE-Grid.

---

## 6. Parâmetros explicados (AppEEARS)

Base: `https://appeears.earthdatacloud.nasa.gov/api/` [8].

### 6.1 Endpoints usados

| Método | Caminho | Autenticação | Função |
|---|---|---|---|
| POST | `/login` | Basic (usuário e senha Earthdata) | Gera token (validade ~48 h) |
| GET | `/product/{product_id}` | Nenhuma | Lista as camadas do produto |
| GET | `/quality/{product_id}` | Nenhuma | Lista as camadas de qualidade |
| POST | `/task` | Bearer | Envia o pedido |
| GET | `/task/{task_id}` | Bearer | Status (`pending`, `processing`, `done`, `error`) |
| GET | `/bundle/{task_id}` | Bearer | Lista os arquivos prontos |
| GET | `/bundle/{task_id}/{file_id}` | Bearer | Baixa um arquivo (link válido por 48 h) |

Lista completa em `comunicacao-entre-apis.md`.

### 6.2 Campos do pedido (`POST /task`)

| Campo | Obrigatório | Formato | Explicação |
|---|---|---|---|
| `task_type` | Sim | `"point"` ou `"area"` | Ponto (CSV) ou área (raster) |
| `task_name` | Sim | Texto | Nome do pedido, para encontrá-lo depois |
| `params.dates[].startDate` / `endDate` | Sim | **`MM-DD-AAAA`** | Período. Atenção ao formato americano |
| `params.dates[].recurring` | Não | `true`/`false` | Repetir o mesmo intervalo do ano em vários anos |
| `params.dates[].yearRange` | Não | `[ano_ini, ano_fim]` | Anos da recorrência |
| `params.layers[].product` | Sim | Ex.: `SPL3SMP_E.006` ⚠️ | Produto e versão (confirme em `GET /product`) |
| `params.layers[].layer` | Sim | Nome exato | Camada (de `GET /product/{id}`) |
| `params.coordinates[]` | Sim (ponto) | `latitude`, `longitude`, `id`, `category` | Pontos; `id` identifica o talhão |
| `params.geo` | Sim (área) | GeoJSON em EPSG:4326 | Polígono |
| `params.output.format.type` | Sim (área) | `geotiff` ou `netcdf4` | Formato de saída |
| `params.output.projection` | Sim (área) | Ex.: `native`, `geographic` | Projeção (lista em `GET /spatial/proj`) |

Fonte: [8].

---

## 7. Estrutura dos dados

### 7.1 SPL3SMP_E

Grupos HDF5 [2]:
- `Soil_Moisture_Retrieval_Data_AM` → passagem descendente (6h).
- `Soil_Moisture_Retrieval_Data_PM` → passagem ascendente (18h).

| Variável | Descrição | Unidade | Preenchimento | Faixa válida | Fonte |
|---|---|---|---|---|---|
| `soil_moisture` | Umidade volumétrica superficial | cm³/cm³ | **−9999,0** | 0,02 até a porosidade do solo | [2] |
| `soil_moisture_dca`, `_scah`, `_scav` | Mesma variável por algoritmos alternativos | cm³/cm³ | −9999,0 | — | [2] |
| `retrieval_qual_flag` | Qualidade (16 bits) | — | 65534 | 0–65536 | [2] |
| `surface_flag` | Condições da superfície (16 bits) | — | 65534 | 0–65536 | [2][5] |

**Como ler a qualidade [2]:** no `retrieval_qual_flag`, **bit 0 = 0** significa "qualidade recomendada". O guia indica que os valores **0 ou 8** correspondem a estimativas de alta qualidade.

⚠️ Os nomes vêm do guia do SPL3SMP (36 km); o SPL3SMP_E segue a mesma estrutura, mas confirme no guia da versão usada. No grupo PM as variáveis podem ter sufixo `_pm`.

**Leitura dos valores:** 0,10 = 10% do volume do solo é água (seco para latossolo argiloso); 0,35 = bem úmido.

### 7.2 SPL4SMGP

Umidade superficial (~0–5 cm) e da zona radicular (~0–100 cm) em m³/m³, a cada 3 horas [3][12]. ⚠️ Nomes usuais `sm_surface` e `sm_rootzone`; confirme no guia da v8.

### 7.3 Saída do AppEEARS por ponto

CSV com uma linha por data e colunas de identificação do ponto, data, valor de cada camada e qualidade decodificada; o pacote inclui o JSON do pedido, a lista das URLs de origem e um arquivo com a qualidade decodificada [9]. ⚠️ Os nomes exatos das colunas variam por produto: leia o cabeçalho antes de processar.

---

## 8. Tratamento dos dados no Field Shift

| Passo | O que é feito | Por quê |
|---|---|---|
| 1. Pedido | AppEEARS `point` com SPL3SMP_E (AM + qualidade) e SPL4SMGP (zona radicular), de 31/03/2015 até o fim do ano anterior | Evita HDF5 e reprojeção |
| 2. Ausentes | Remover −9999 e 65534 | Não confundir falta de dado com solo seco |
| 3. Qualidade | Manter só `retrieval_qual_flag` com bit 0 = 0 (ou valores 0 e 8) | Recomendação do guia [2] |
| 4. Passagem | Usar **AM**; PM só para preencher | Pela manhã, solo e vegetação estão mais próximos do equilíbrio térmico |
| 5. Agregação temporal | Média mensal e decendial | Série diária tem falhas entre passagens |
| 6. Climatologia | Média e desvio por mês (2015–2025) | Referência do "normal" |
| 7. Anomalia | z = (valor − média do mês) / desvio do mês | Indicador citado no desafio e no repositório [14] |
| 8. Zona radicular | Mesma rotina com o L4 | Estresse das culturas |
| 9. Comparação | Contra `GWETROOT` do NASA POWER | Duas estimativas de umidade alimentam a confiança |
| 10. Armazenamento | CSV/Parquet por talhão, com versão do produto | Reprodutibilidade |

```python
import pandas as pd
df = pd.read_csv("SPL3SMP-E-006-results.csv", parse_dates=["Date"])
sm  = [c for c in df.columns if c.endswith("soil_moisture") and "AM" in c][0]   # ⚠️ ajuste
qf  = [c for c in df.columns if "retrieval_qual_flag" in c and "AM" in c][0]

df = df[(df[sm] > 0) & (df[qf].isin([0, 8]))]          # passos 2 e 3
m = df.set_index("Date")[sm].resample("MS").mean()     # passo 5
clim = m.groupby(m.index.month).agg(["mean", "std"])   # passo 6
z = (m - m.index.month.map(clim["mean"])) / m.index.month.map(clim["std"])  # passo 7
```

---

## 9. Como testar

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | `GET /product` | Lista contém SPL3SMP_E e SPL4SMGP |
| 2 | `GET /product/SPL3SMP_E.006` | Camadas AM, PM e de qualidade |
| 3 | Pedido de 1 mês por ponto | Status `done`; CSV com dias válidos e dias sem passagem |
| 4 | Valores | Entre 0,02 e ~0,5; −9999 nos dias sem dado |
| 5 | Série de 1 ano | Alta em dez–mar, baixa em jun–set |
| 6 | Comparar com chuva (IMERG ou POWER) | Picos de umidade logo após chuvas |
| 7 | Superfície × zona radicular | Zona radicular varia mais devagar |
| 8 | Data anterior a 31/03/2015 | Sem dados |
| 9 | Ponto sobre represa | `surface_flag` indica água; qualidade não recomendada |
| 10 | Pedir SPL4SMGP v7 depois de 07/2025 | Sem dados (versão aposentada) |

---

## 10. Códigos de erro e problemas comuns

| Situação | Causa | Solução | Fonte |
|---|---|---|---|
| AppEEARS 401 no `/login` | Usuário ou senha do Earthdata errados | Conferir credenciais | [8] |
| AppEEARS 403 em outras rotas | Token expirado (~48 h) | Novo `POST /login` | [8] |
| AppEEARS 400 no `/task` | Campo inválido (data fora do formato `MM-DD-AAAA`, camada inexistente) | Ler a mensagem e corrigir | [8] |
| AppEEARS 429 | Requisições rápidas demais | Reduzir a frequência | [8] |
| Status `done` com `summary.empty: true` | Nenhum dado no período/local | Rever datas e produto | [8] |
| Download 401 direto do NSIDC | Earthdata Login ausente ou `.netrc` errado | Configurar `.netrc` e cookies | [11] |

---

## 11. Limitações

1. **9 km**: talhões vizinhos com manejos diferentes ficam na mesma célula.
2. **Só ~5 cm** no L3; a zona radicular do L4 é **modelo** [3].
3. **Histórico curto** (desde 2015) [1].
4. **Vegetação densa** atenua o sinal; qualidade cai em lavouras fechadas e matas [5][6].
5. **Falhas entre passagens** no L3.
6. **Irrigação** muda a umidade localmente.
7. **Versões mudam**: v6 (L3 padrão) e v7 (L4) aposentadas [3][4].

---

## 12. Boas práticas

1. **AppEEARS por ponto** e passagem **AM**.
2. **Filtre a qualidade** pelo bit 0 do `retrieval_qual_flag` [2].
3. Trabalhe com **anomalias**.
4. **L4** para estresse de culturas; **L3** para mostrar observação direta.
5. **Mostre a escala**: "média de uma área de ~9 × 9 km".
6. Registre **produto e versão** em cada série salva.

---

## 13. Como e por que usar o SMAP no Field Shift

> Contexto: SMAP está entre os **6 obrigatórios** (D-002) [13]; a anomalia de umidade é indicador do `CONTEXTO-DESAFIO.md` §7 [14].

| Motivo | Por que importa |
|---|---|
| **Mede o solo, não o ar** | Chuva diz quanto entrou; umidade diz quanto ficou disponível |
| **Alerta precoce** | O solo seca antes de o NDVI cair |
| **Zona radicular (L4)** | Indica se culturas de raiz profunda acessam água que as rasas não alcançam |
| **Termo do desafio** | "Soil moisture anomalies" aparece no enunciado |

| Etapa | Papel |
|---|---|
| Indicadores | Anomalia mensal; dias abaixo de limiar crítico |
| Diagnóstico | Meses de solo seco durante a safrinha |
| Pontuação | Reforça o critério **risco hídrico** |
| Incerteza | Comparação com `GWETROOT` do POWER |

**Não resolve:** diferença entre talhões (9 km), previsão, consumo de água da cultura (ECOSTRESS, POWER + FAO-56).

---

## 14. Parâmetros úteis e indicadores derivados

| Indicador | Cálculo | Uso |
|---|---|---|
| Anomalia de umidade superficial | z-score mensal do L3 | Mostrar seca observada |
| Anomalia da zona radicular | z-score mensal do L4 | Estresse das culturas |
| Dias secos críticos | Dias com umidade abaixo de um limiar por textura de solo ⚠️ | Risco na fase de enchimento |
| Velocidade de secagem | Queda média da umidade nos 10 dias após a última chuva | Retenção de água do solo |

---

## 15. Caso hipotético: o Sr. José

> ⚠️ **Fictício**. Continuação do caso do `nasa-power-api-daily.md` (seção 16).

**Dados usados:** SPL3SMP_E v6 (AM, qualidade recomendada) e SPL4SMGP v8 (zona radicular), 2015–2025, via AppEEARS, tratados conforme a seção 8.

| Indicador | Valor |
|---|---|
| Anos (de 10) com anomalia < −1 na zona radicular em maio | 4 |
| Anos de quebra da safrinha relatados pelo Sr. José | 2 dos últimos 5 |
| Esses 2 anos tiveram anomalia < −1 em abril–maio? | **Sim** |

> 💧 **Em abril e maio o solo seca rápido.** Em 4 dos últimos 10 anos, a umidade na zona das raízes ficou bem abaixo do normal justamente quando o milho enche os grãos. Os dois anos em que você perdeu produção estão entre eles.
> *De onde vem: satélite SMAP (NASA), 2015–2025, quadrados de ~9 km.*

**Efeito:** segunda evidência independente do risco hídrico (confiança do critério sobe de Média para **Alta**); favorece a estratégia C (sorgo). Na estratégia B, a raiz profunda da braquiária é citada como possível vantagem, marcada como **ponto a validar com o técnico**.

---

## 16. Fontes e rastreabilidade

### 16.1 Referências técnicas

1. NSIDC. SPL3SMP_E — página atual (v6): resolução, grade, cobertura, formato e opções de acesso. <https://nsidc.org/data/SPL3SMP_E>
2. NSIDC. Guia do usuário SMAP L3 Radiometer (SPL3SMP v7): grupos, variáveis, unidades, preenchimento, flags e horários de passagem. <https://nsidc.org/sites/default/files/spl3smp-v007-userguide_0.pdf>
3. NSIDC. SPL4SMGP v7 (aposentada; aponta a v8 e suas mudanças). <https://nsidc.org/data/spl4smgp/versions/7>
4. NSIDC. SPL3SMP v6 (aposentada). <https://nsidc.org/data/SPL3SMP/versions/6>
5. NSIDC. Como interpretar as flags de superfície e qualidade dos produtos L2 e L3. <https://nsidc.org/ru/node/32053>
6. NASA/JPL. ATBD do SMAP L2 passivo (rev. F). <https://smap.jpl.nasa.gov/system/internal_resources/details/original/484_L2_SM_P_ATBD_rev_F_final_Aug2020.pdf>
7. NASA/JPL. SMAP — descrição da missão. <https://smap.jpl.nasa.gov/mission/description/>
8. NASA LP DAAC. AppEEARS API: endpoints, autenticação, formato dos pedidos e limites. <https://appeears.earthdatacloud.nasa.gov/api/>
9. NASA Openscapes. Tutorial AppEEARS (conteúdo do pacote de saída). <https://nasa-openscapes.github.io/2022-Fall-ECOSTRESS-Cloud-Workshop/tutorials/AppEEARS.html>
10. earthaccess. Documentação. <https://earthaccess.readthedocs.io/en/latest/quick-start/>
11. Earthdata Login. Acesso a dados com curl e wget. <https://urs.earthdata.nasa.gov/documentation/for_users/data_access/curl_and_wget>
12. NASA Earthdata. SPL4SMGP v7 (descrição do produto L4). <https://www.earthdata.nasa.gov/data/catalog/nsidc-cprd-spl4smgp-007>

### 16.2 Base do projeto

13. Repositório da equipe, `docs/v1/.md/context/DECISOES.md` (D-002).
14. Repositório da equipe, `docs/v1/.md/context/CONTEXTO-DESAFIO.md` (§7 indicadores, §9.2 pipeline).

*Consulta das fontes: 14 de novembro de 2026. Versões e endereços devem ser conferidos novamente no momento da implementação.*
