> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# Field Shift — Referência de APIs para RAG

> Projeto: Field Shift (NASA Space Apps Challenge 2026) · Atualizado em 2026-11-14
> Gerado por `gerar_referencia.py` a partir de uma lista única de endpoints. Formato pensado para RAG:
> cada bloco `### [id]` é autocontido e começa com um comentário `chunk_id` com metadados.

## Como usar este arquivo no RAG

1. **Divida por bloco**: cada seção `### [id]` é um chunk (corte no comentário `<!-- chunk_id ... -->`).
2. **Indexe os metadados** do comentário (`chunk_id`, `api`, `grupo`, `verificacao`) como filtros.
3. **Alternativa estruturada**: use `apis-field-shift.jsonl` (um registro JSON por endpoint, mesmos campos).
4. **Instrução sugerida para a IA**: "Responda apenas com base nos chunks recuperados. Copie URLs e parâmetros exatamente.
   Se o chunk marcar ⚠️, avise que o valor precisa ser confirmado. Nunca invente códigos, IDs ou nomes de colunas."
5. **⚠️** = valor a confirmar na primeira execução real (nenhuma chamada foi feita ao vivo no ambiente de pesquisa).

## Regras gerais (valem para todas as APIs)

| Regra | Detalhe |
|---|---|
| Chaves e senhas só no back-end | ANTHROPIC_API_KEY, Earthdata, tokens CKAN em variáveis de ambiente |
| Cache | Clima, NDVI, PAM e catálogos mudam pouco: baixar antes da demo |
| Valores ausentes | POWER: -999 · SIDRA: "..", "...", "X" · CKAN: records vazio. Nunca tratar como zero |
| Escala | Sempre exibir fonte e escala ao lado do número |
| Ordem no aplicativo | 1) POWER (clima) → 2) AppEEARS + crop-cycle (campo) → 3) SIDRA/PAM (mercado local) → 4) Harvest API (mercado nacional) → 5) Claude + MCP (chat) |

## Índice de endpoints

| id | API | Nome | Método | Verificação |
|---|---|---|---|---|
| `power.daily_point` | NASA POWER | Série diária por ponto | GET | doc |
| `power.climatology_point` | NASA POWER | Climatologia por ponto | GET | doc |
| `power.monthly_point` | NASA POWER | Mensal e anual por ponto | GET | doc |
| `power.daily_regional` | NASA POWER | Série diária regional | GET | doc |
| `power.manager_parameters` | NASA POWER | Catálogo de parâmetros (Manager) | GET | doc |
| `harvest.package_search` | NASA Harvest Portal (CKAN) | Buscar datasets | GET | doc |
| `harvest.package_show` | NASA Harvest Portal (CKAN) | Mostrar um dataset | GET | doc |
| `harvest.resource_show` | NASA Harvest Portal (CKAN) | Mostrar um arquivo | GET | doc |
| `harvest.organization_list` | NASA Harvest Portal (CKAN) | Listar organizações | GET | doc |
| `harvest.organization_show` | NASA Harvest Portal (CKAN) | Mostrar organização | GET | doc |
| `harvest.group_list` | NASA Harvest Portal (CKAN) | Listar grupos temáticos | GET | doc |
| `harvest.group_show` | NASA Harvest Portal (CKAN) | Mostrar grupo | GET | doc |
| `harvest.tag_list` | NASA Harvest Portal (CKAN) | Listar tags | GET | doc |
| `harvest.datastore_search` | NASA Harvest Portal (CKAN) | Consultar tabela (DataStore) | POST (ou GET) | doc |
| `harvest.resource_download` | NASA Harvest Portal (CKAN) | Baixar arquivo de um recurso | GET | doc |
| `harvest_mcp.list_tools` | NASA Harvest Portal MCP | Conectar e listar ferramentas (MCP Python SDK v2) | MCP (Streamable HTTP) | testado-local |
| `harvest_mcp.call_tool` | NASA Harvest Portal MCP | Chamar uma ferramenta MCP direto | MCP (Streamable HTTP) | testado-local |
| `claude.mcp_connector` | Claude API (MCP connector) | Chat com Claude usando o MCP do Harvest | POST | doc |
| `ibge.sidra_values` | IBGE SIDRA | Valores de uma tabela (PAM 5457) | GET | doc |
| `ibge.agregados_metadados` | IBGE Agregados v3 | Metadados de uma tabela | GET | doc |
| `ibge.localidades_municipios` | IBGE Localidades v1 | Municípios de uma UF | GET | doc |
| `appeears.login` | NASA AppEEARS | Login (token) | POST | doc |
| `appeears.product_layers` | NASA AppEEARS | Camadas de um produto | GET | doc |
| `appeears.task_point` | NASA AppEEARS | Criar tarefa por ponto | POST | doc |
| `appeears.task_status` | NASA AppEEARS | Status da tarefa | GET | doc |
| `appeears.bundle` | NASA AppEEARS | Arquivos prontos e download | GET | doc |
| `earthdata.cmr_granules` | NASA Earthdata CMR | Buscar arquivos (granules) | GET | doc |
| `lib.crop_cycle_detection` | NASA Harvest crop-cycle-detection (biblioteca Python) | Detectar safras e solo descoberto no NDVI | Função Python local | testado-local |

## Fluxo de dados entre as APIs

```
Talhão (lat, lon) + município
   ├─► power.daily_point / climatology / monthly ─► indicadores de clima, anos secos ─┐
   ├─► appeears.login → task_point → task_status → bundle ─► NDVI ─► lib.crop_cycle ─┤─► filtro + diagnóstico
   ├─► earthdata.cmr_granules ─► GPM IMERG / SRTM (opcional) ─────────────────────────┘
   ├─► ibge.localidades → ibge.agregados_metadados → ibge.sidra_values ─► mercado local + quebra em anos secos
   ├─► harvest.package_search → package_show → datastore_search ─► mercado nacional
   └─► claude.mcp_connector (+ harvest_mcp) ─► chat do agricultor (clima vai pronto no pacote)
```

---

## NASA POWER

<!-- chunk_id: power.daily_point | api: NASA POWER | grupo: Clima | verificacao: doc | atualizado: 2026-11-14 -->
### [power.daily_point] NASA POWER — Série diária por ponto

- **Método:** GET
- **URL:** `https://power.larc.nasa.gov/api/temporal/daily/point`
- **Autenticação:** Nenhuma
- **Para que serve:** Série diária de clima (temperatura, chuva, umidade, radiação, vento, pressão) para uma coordenada, desde 1981.
- **Uso no Field Shift:** Filtro climático: fim das chuvas, veranicos, geada, calor, ET₀ (FAO-56), balanço hídrico; anos secos para cruzar com a PAM.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `parameters` | sim | Lista separada por vírgula, máx. 20 | `T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS` |
| `community` | sim | AG / RE / SB | `AG` |
| `latitude` | sim | -90 a 90 (sul negativo) | `-18.7` |
| `longitude` | sim | -180 a 180 (oeste negativo) | `-47.5` |
| `start` | sim | YYYYMMDD, >= 19810101 | `19910101` |
| `end` | sim | YYYYMMDD, não futuro | `20251231` |
| `format` | não | JSON / CSV / ASCII / NETCDF / ICASA | `JSON` |
| `time-standard` | não | LST / UTC | `LST` |
| `site-elevation` | não | metros (corrige pressão) | `950` |
| `user` | não | nome da aplicação | `fieldshift` |

**Chamada (curl)**

```bash
curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MIN,PRECTOTCORR&community=AG&latitude=-18.7&longitude=-47.5&start=20240101&end=20240131&format=JSON&time-standard=LST&user=fieldshift"
```

**Chamada (Python)**

```python
import requests, pandas as pd
r = requests.get("https://power.larc.nasa.gov/api/temporal/daily/point", params={
    "parameters": "T2M,T2M_MIN,PRECTOTCORR", "community": "AG",
    "latitude": -18.7, "longitude": -47.5, "start": "20240101", "end": "20240131",
    "format": "JSON", "time-standard": "LST", "user": "fieldshift"}, timeout=120)
r.raise_for_status()
d = r.json()
df = pd.DataFrame(d["properties"]["parameter"])
df.index = pd.to_datetime(df.index, format="%Y%m%d")
df = df.replace([-999, -999.0, -99], pd.NA)   # valor de preenchimento = ausente
```

**Resposta:** GeoJSON Feature: geometry.coordinates=[lon, lat, altitude da célula]; properties.parameter={PARAM: {"YYYYMMDD": valor}}; parameters={PARAM: {units, longname}}; header.fill_value=-999; messages=[]

**Erros:** 400/422 parâmetro inválido (corpo lista as violações); 429 excesso de requisições; 500/502/504 servidor. Valor -999 = ausente.

**Observações:** Resolução ~0,5°×0,625° (~55 km): pontos próximos devolvem os mesmos dados. Últimos 2–3 meses são provisórios. Uma requisição por célula, com cache.

**Fonte:** https://power.larc.nasa.gov/docs/services/api/temporal/daily/

---
<!-- chunk_id: power.climatology_point | api: NASA POWER | grupo: Clima | verificacao: doc | atualizado: 2026-11-14 -->
### [power.climatology_point] NASA POWER — Climatologia por ponto

- **Método:** GET
- **URL:** `https://power.larc.nasa.gov/api/temporal/climatology/point`
- **Autenticação:** Nenhuma
- **Para que serve:** Média de longo prazo de cada mês ('janeiro típico') para uma coordenada.
- **Uso no Field Shift:** Calendário agrícola típico: estação chuvosa, meses de déficit, janela de geada.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `parameters` | sim | Lista | `T2M,T2M_MAX,T2M_MIN,PRECTOTCORR` |
| `community` | sim | AG | `AG` |
| `latitude` | sim | decimal | `-18.7` |
| `longitude` | sim | decimal | `-47.5` |
| `start` | não | ano (climatologia personalizada) | `1991` |
| `end` | não | ano | `2020` |
| `format` | não | JSON/CSV | `JSON` |

**Chamada (curl)**

```bash
curl "https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR&community=AG&latitude=-18.7&longitude=-47.5&format=JSON&user=fieldshift"
```

**Chamada (Python)**

```python
r = requests.get("https://power.larc.nasa.gov/api/temporal/climatology/point", params={
    "parameters": "T2M,PRECTOTCORR", "community": "AG", "latitude": -18.7, "longitude": -47.5,
    "format": "JSON", "user": "fieldshift"}, timeout=60)
clima = r.json()["properties"]["parameter"]   # {"PRECTOTCORR": {"JAN": ..., ..., "ANN": ...}}
```

**Resposta:** properties.parameter={PARAM: {JAN..DEC, ANN}}

**Erros:** Iguais ao daily/point.

**Observações:** Sem start/end usa o período padrão.

**Fonte:** https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

---
<!-- chunk_id: power.monthly_point | api: NASA POWER | grupo: Clima | verificacao: doc | atualizado: 2026-11-14 -->
### [power.monthly_point] NASA POWER — Mensal e anual por ponto

- **Método:** GET
- **URL:** `https://power.larc.nasa.gov/api/temporal/monthly/point`
- **Autenticação:** Nenhuma
- **Para que serve:** Média de cada mês e do ano, para cada ano do período.
- **Uso no Field Shift:** Comparar anos (ano seco × chuvoso); identificar anos secos para cruzar com o rendimento da PAM.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `parameters` | sim | Lista | `PRECTOTCORR,T2M_MIN` |
| `community` | sim | AG | `AG` |
| `latitude` | sim | decimal | `-18.7` |
| `longitude` | sim | decimal | `-47.5` |
| `start` | sim | ano YYYY | `1991` |
| `end` | sim | ano YYYY | `2025` |
| `format` | não | JSON/CSV | `JSON` |

**Chamada (curl)**

```bash
curl "https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=PRECTOTCORR&community=AG&latitude=-18.7&longitude=-47.5&start=1991&end=2025&format=JSON&user=fieldshift"
```

**Chamada (Python)**

```python
r = requests.get("https://power.larc.nasa.gov/api/temporal/monthly/point", params={
    "parameters": "PRECTOTCORR", "community": "AG", "latitude": -18.7, "longitude": -47.5,
    "start": 1991, "end": 2025, "format": "JSON", "user": "fieldshift"}, timeout=120)
mensal = r.json()["properties"]["parameter"]["PRECTOTCORR"]   # {"199101": ..., "199113": anual}
```

**Resposta:** properties.parameter={PARAM: {YYYYMM: valor}}; mês 13 = valor anual ⚠️

**Erros:** Iguais ao daily/point.

**Observações:** start/end são anos.

**Fonte:** https://power.larc.nasa.gov/docs/services/api/temporal/monthly/

---
<!-- chunk_id: power.daily_regional | api: NASA POWER | grupo: Clima | verificacao: doc | atualizado: 2026-11-14 -->
### [power.daily_regional] NASA POWER — Série diária regional

- **Método:** GET
- **URL:** `https://power.larc.nasa.gov/api/temporal/daily/regional`
- **Autenticação:** Nenhuma
- **Para que serve:** Série diária de UM parâmetro para todas as células dentro de um retângulo.
- **Uso no Field Shift:** Mapas regionais de chuva ou temperatura (opcional).
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `parameters` | sim | Apenas 1 | `PRECTOTCORR` |
| `community` | sim | AG | `AG` |
| `latitude-min` | sim | sul | `-19.5` |
| `latitude-max` | sim | norte | `-17.5` |
| `longitude-min` | sim | oeste | `-48.5` |
| `longitude-max` | sim | leste | `-46.5` |
| `start` | sim | YYYYMMDD | `20240101` |
| `end` | sim | YYYYMMDD | `20240131` |
| `format` | não | JSON/CSV | `CSV` |

**Chamada (curl)**

```bash
curl "https://power.larc.nasa.gov/api/temporal/daily/regional?latitude-min=-19.5&latitude-max=-17.5&longitude-min=-48.5&longitude-max=-46.5&parameters=PRECTOTCORR&community=AG&start=20240101&end=20240131&format=CSV"
```

**Chamada (Python)**

```python
r = requests.get("https://power.larc.nasa.gov/api/temporal/daily/regional", params={
    "latitude-min": -19.5, "latitude-max": -17.5, "longitude-min": -48.5, "longitude-max": -46.5,
    "parameters": "PRECTOTCORR", "community": "AG", "start": "20240101", "end": "20240131",
    "format": "CSV"}, timeout=300)
```

**Resposta:** Arquivo no formato pedido com uma série por célula.

**Erros:** Erro se pedir mais de 1 parâmetro.

**Observações:** Área máxima ~4,5°×4,5° ⚠️. Mais lento que point. Não aceita site-elevation.

**Fonte:** https://power.larc.nasa.gov/docs/services/api/temporal/daily/

---
<!-- chunk_id: power.manager_parameters | api: NASA POWER | grupo: Clima | verificacao: doc | atualizado: 2026-11-14 -->
### [power.manager_parameters] NASA POWER — Catálogo de parâmetros (Manager)

- **Método:** GET
- **URL:** `https://power.larc.nasa.gov/api/system/manager/parameters`
- **Autenticação:** Nenhuma
- **Para que serve:** Lista os parâmetros disponíveis por comunidade e nível temporal, com nomes longos e unidades.
- **Uso no Field Shift:** Confirmar nomes curtos e unidades antes de chamar daily/point.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `community` | sim | ag / re / sb | `ag` |
| `temporal` | sim | hourly / daily / monthly / climatology | `daily` |

**Chamada (curl)**

```bash
curl "https://power.larc.nasa.gov/api/system/manager/parameters?community=ag&temporal=daily"
```

**Chamada (Python)**

```python
params = requests.get("https://power.larc.nasa.gov/api/system/manager/parameters",
                      params={"community": "ag", "temporal": "daily"}).json()
```

**Resposta:** JSON com os parâmetros e metadados.

**Erros:** —

**Observações:** Responde só em JSON.

**Fonte:** https://power.larc.nasa.gov/docs/services/api/system/manager/

---
## NASA Harvest Portal (CKAN)

<!-- chunk_id: harvest.package_search | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.package_search] NASA Harvest Portal (CKAN) — Buscar datasets

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/package_search`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Busca datasets no catálogo; devolve contagem, resultados e facetas.
- **Uso no Field Shift:** Achar tabelas de produção/mercado; explorar o catálogo com rows=0 e facetas.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `q` | não | texto (Solr) | `crop production` |
| `fq` | não | filtro por campo | `organization:oecd` |
| `rows` | não | int, padrão 10, máx. 1000 | `20` |
| `start` | não | int (paginação) | `0` |
| `sort` | não | texto | `metadata_modified desc` |
| `facet.field` | não | lista JSON | `["organization","tags","res_format"]` |
| `facet.limit` | não | int, -1 = todos | `-1` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/package_search?q=crop%20production&rows=10"
```

**Chamada (Python)**

```python
r = requests.get("https://data.harvestportal.org/api/3/action/package_search",
                 params={"q": "crop production", "rows": 10}, timeout=60).json()
assert r["success"]
for d in r["result"]["results"]:
    print(d["name"], d["title"], d["organization"]["name"])
```

**Resposta:** result: {count, results: [dataset], facets, search_facets}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Use o campo name do dataset nas próximas chamadas.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.package_show | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.package_show] NASA Harvest Portal (CKAN) — Mostrar um dataset

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/package_show`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Metadados completos de um dataset, incluindo a lista de arquivos (resources).
- **Uso no Field Shift:** Obter resource id, formato, url de download e datastore_active.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `id` | sim | UUID ou name do dataset | `oecd-crop-production` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/package_show?id=oecd-crop-production"
```

**Chamada (Python)**

```python
ds = requests.get("https://data.harvestportal.org/api/3/action/package_show",
                  params={"id": "oecd-crop-production"}).json()["result"]
for res in ds["resources"]:
    print(res["id"], res["format"], res.get("datastore_active"), res["url"])
```

**Resposta:** result: {name, title, notes, organization, tags, license_id, resources: [{id, format, url, datastore_active}]}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Confira license_id antes de usar.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.resource_show | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.resource_show] NASA Harvest Portal (CKAN) — Mostrar um arquivo

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/resource_show`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Metadados de um recurso (arquivo).
- **Uso no Field Shift:** Saber se a tabela está na DataStore (datastore_active).
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `id` | sim | UUID do recurso | `<resource_id>` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/resource_show?id=<resource_id>"
```

**Chamada (Python)**

```python
res = requests.get("https://data.harvestportal.org/api/3/action/resource_show",
                   params={"id": RESOURCE_ID}).json()["result"]
```

**Resposta:** result: {id, name, format, url, datastore_active, size, mimetype, last_modified, package_id}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** —

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.organization_list | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.organization_list] NASA Harvest Portal (CKAN) — Listar organizações

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/organization_list`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Lista as organizações que publicam dados.
- **Uso no Field Shift:** Descobrir o name da organização (ex.: oecd, fao) para usar em fq.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `all_fields` | não | true/false | `true` |
| `sort` | não | name/package_count/title | `package_count desc` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/organization_list?all_fields=true"
```

**Chamada (Python)**

```python
orgs = requests.get("https://data.harvestportal.org/api/3/action/organization_list",
                    params={"all_fields": "true"}).json()["result"]
```

**Resposta:** result: [name] ou [{name, title, package_count}] com all_fields

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Limite 25 objetos com all_fields ⚠️.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.organization_show | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.organization_show] NASA Harvest Portal (CKAN) — Mostrar organização

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/organization_show`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Detalhes de uma organização e, opcionalmente, seus datasets.
- **Uso no Field Shift:** Listar os datasets de FAO, OECD, NASA Harvest.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `id` | sim | name ou UUID | `nasa-harvest` |
| `include_datasets` | não | true/false | `true` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/organization_show?id=nasa-harvest&include_datasets=true"
```

**Chamada (Python)**

```python
org = requests.get("https://data.harvestportal.org/api/3/action/organization_show",
                   params={"id": "nasa-harvest", "include_datasets": "true"}).json()["result"]
```

**Resposta:** result: {name, title, package_count, packages: [...]}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Confirme o name com organization_list.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.group_list | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.group_list] NASA Harvest Portal (CKAN) — Listar grupos temáticos

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/group_list`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Lista os grupos temáticos.
- **Uso no Field Shift:** Explorar temas (ex.: Supply Chain).
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `all_fields` | não | true/false | `true` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/group_list?all_fields=true"
```

**Chamada (Python)**

```python
grupos = requests.get("https://data.harvestportal.org/api/3/action/group_list",
                      params={"all_fields": "true"}).json()["result"]
```

**Resposta:** result: [name] ou [{name, title, package_count}]

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** —

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.group_show | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.group_show] NASA Harvest Portal (CKAN) — Mostrar grupo

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/group_show`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Detalhes de um grupo e seus datasets.
- **Uso no Field Shift:** Listar datasets de um tema.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `id` | sim | name ou UUID | `supply-chain` |
| `include_datasets` | não | true/false | `true` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/group_show?id=supply-chain&include_datasets=true"
```

**Chamada (Python)**

```python
g = requests.get("https://data.harvestportal.org/api/3/action/group_show",
                 params={"id": "supply-chain", "include_datasets": "true"}).json()["result"]
```

**Resposta:** result: {name, title, packages: [...]}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Confirme o name com group_list ⚠️.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.tag_list | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.tag_list] NASA Harvest Portal (CKAN) — Listar tags

- **Método:** GET
- **URL:** `https://data.harvestportal.org/api/3/action/tag_list`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Lista as palavras-chave.
- **Uso no Field Shift:** Descobrir termos de busca (cropland, yield...).
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `query` | não | texto contido na tag | `crop` |

**Chamada (curl)**

```bash
curl "https://data.harvestportal.org/api/3/action/tag_list?query=crop"
```

**Chamada (Python)**

```python
tags = requests.get("https://data.harvestportal.org/api/3/action/tag_list",
                    params={"query": "crop"}).json()["result"]
```

**Resposta:** result: [tag]

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Para contagem por tag use package_search com facet.field=["tags"].

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.datastore_search | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.datastore_search] NASA Harvest Portal (CKAN) — Consultar tabela (DataStore)

- **Método:** POST (ou GET)
- **URL:** `https://data.harvestportal.org/api/3/action/datastore_search`
- **Autenticação:** Nenhuma para dados públicos; token no cabeçalho Authorization para privados
- **Para que serve:** Consulta linhas de um recurso carregado na DataStore, com filtros exatos, busca livre, colunas e ordenação.
- **Uso no Field Shift:** Série de produção por país e cultura para a nota de mercado nacional.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `resource_id` | sim | UUID do recurso com datastore_active=true | `<resource_id>` |
| `filters` | não | dicionário de igualdade exata | `{"LOCATION": "BRA", "SUBJECT": "SORGHUM"}` |
| `q` | não | busca livre | `sorghum` |
| `fields` | não | lista de colunas | `["TIME","Value"]` |
| `sort` | não | texto | `TIME desc` |
| `limit` | não | int, padrão 100, máx. 32000 | `15` |
| `offset` | não | int | `0` |
| `records_format` | não | objects/lists/csv/tsv | `objects` |

**Chamada (curl)**

```bash
curl -X POST "https://data.harvestportal.org/api/3/action/datastore_search" -H "Content-Type: application/json" -d '{"resource_id": "<resource_id>", "filters": {"LOCATION": "BRA", "SUBJECT": "SORGHUM"}, "sort": "TIME desc", "limit": 15}' 
```

**Chamada (Python)**

```python
r = requests.post("https://data.harvestportal.org/api/3/action/datastore_search", json={
    "resource_id": RESOURCE_ID, "filters": {"LOCATION": "BRA", "SUBJECT": "SORGHUM"},
    "fields": ["TIME", "Value"], "sort": "TIME desc", "limit": 15}, timeout=60).json()
if r["success"]:
    linhas = r["result"]["records"]
# Descobrir colunas antes: {"resource_id": RESOURCE_ID, "limit": 0} -> result.fields
```

**Resposta:** result: {fields: [{id, type}], records: [...], total, limit, offset, _links: {next}}

**Erros:** Envelope {"success": false, "error": {"__type": "Not Found Error" | "Validation Error" | "Authorization Error", "message": ...}}. O HTTP pode ser 200 mesmo com erro: verifique "success".

**Observações:** Chame primeiro com limit=0 para ver as colunas. Nomes de colunas e códigos do exemplo são fictícios.

**Fonte:** https://data.harvestportal.org/api-docs ; https://docs.ckan.org/en/latest/api/index.html

---
<!-- chunk_id: harvest.resource_download | api: NASA Harvest Portal (CKAN) | grupo: Mercado | verificacao: doc | atualizado: 2026-11-14 -->
### [harvest.resource_download] NASA Harvest Portal (CKAN) — Baixar arquivo de um recurso

- **Método:** GET
- **URL:** `https://data.harvestportal.org/dataset/{DATASET_ID}/resource/{RESOURCE_ID}/download/{FILENAME}`
- **Autenticação:** Nenhuma para dados públicos
- **Para que serve:** Download direto do arquivo (CSV, XLSX, SHP, GeoTIFF, Parquet...).
- **Uso no Field Shift:** Baixar tabelas de mercado inteiras antes da demo (cache).
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `DATASET_ID` | sim | no caminho | `oecd-crop-production` |
| `RESOURCE_ID` | sim | no caminho | `<resource_id>` |
| `FILENAME` | sim | no caminho | `crop_production.csv` |

**Chamada (curl)**

```bash
curl -L -o arquivo.csv "<url do recurso vinda de package_show>"
```

**Chamada (Python)**

```python
url = ds["resources"][0]["url"]          # nunca monte à mão
open("arquivo.csv", "wb").write(requests.get(url, timeout=120).content)
# Parquet: pandas.read_parquet(url)
```

**Resposta:** O próprio arquivo.

**Erros:** 404 se o recurso não existir.

**Observações:** Use o campo url de package_show.

**Fonte:** https://data.harvestportal.org/api-examples

---
## NASA Harvest Portal MCP

<!-- chunk_id: harvest_mcp.list_tools | api: NASA Harvest Portal MCP | grupo: Mercado (IA) | verificacao: testado-local | atualizado: 2026-11-14 -->
### [harvest_mcp.list_tools] NASA Harvest Portal MCP — Conectar e listar ferramentas (MCP Python SDK v2)

- **Método:** MCP (Streamable HTTP)
- **URL:** `https://mcp.harvestportal.org/mcp`
- **Autenticação:** Nenhuma (público); token opcional no cabeçalho X-CKAN-API-Token
- **Para que serve:** Conectar ao servidor MCP do Harvest Portal e listar as ferramentas disponíveis (nomes, descrições, esquemas).
- **Uso no Field Shift:** Passo 0 obrigatório: a documentação não lista as ferramentas.
- **Verificação:** testado-local

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `url` | sim | endpoint MCP | `https://mcp.harvestportal.org/mcp` |

**Chamada (curl)**

```bash
(sem curl simples: use o SDK MCP)
```

**Chamada (Python)**

```python
import asyncio, json
from mcp import Client          # pip install "mcp>=2"

async def main():
    async with Client("https://mcp.harvestportal.org/mcp") as client:
        tools = (await client.list_tools()).tools
        for t in tools:
            print(t.name, "|", t.description)
            print(json.dumps(t.input_schema, ensure_ascii=False))
asyncio.run(main())
```

**Resposta:** ListToolsResult.tools: [Tool(name, description, input_schema, ...)]

**Erros:** Erro de conexão se o servidor estiver fora do ar.

**Observações:** No SDK v2 o esquema é tool.input_schema (v1: inputSchema). Testado contra servidor falso local.

**Fonte:** https://data.harvestportal.org/mcp-docs ; https://py.sdk.modelcontextprotocol.io/client/

---
<!-- chunk_id: harvest_mcp.call_tool | api: NASA Harvest Portal MCP | grupo: Mercado (IA) | verificacao: testado-local | atualizado: 2026-11-14 -->
### [harvest_mcp.call_tool] NASA Harvest Portal MCP — Chamar uma ferramenta MCP direto

- **Método:** MCP (Streamable HTTP)
- **URL:** `https://mcp.harvestportal.org/mcp`
- **Autenticação:** Nenhuma
- **Para que serve:** Executar uma ferramenta do servidor MCP sem IA e ler o resultado.
- **Uso no Field Shift:** Testar ferramentas e descobrir IDs/colunas no preparo.
- **Verificação:** testado-local

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `name` | sim | nome da ferramenta (do list_tools) | `<nome_real>` |
| `arguments` | sim | dict conforme input_schema | `{"query": "crop production"}` |

**Chamada (curl)**

```bash
(use o SDK MCP)
```

**Chamada (Python)**

```python
from mcp import Client
from mcp.types import TextContent

async def chamar(nome, args):
    async with Client("https://mcp.harvestportal.org/mcp") as client:
        res = await client.call_tool(nome, args)
        if res.is_error:
            raise RuntimeError(res.content)
        texto = [b.text for b in res.content if isinstance(b, TextContent)]
        return texto, res.structured_content
```

**Resposta:** CallToolResult: content (para o modelo), structured_content (para o código), is_error

**Erros:** is_error=True quando a ferramenta falha.

**Observações:** Nomes de ferramentas reais ainda desconhecidos ⚠️.

**Fonte:** https://py.sdk.modelcontextprotocol.io/client/

---
## Claude API (MCP connector)

<!-- chunk_id: claude.mcp_connector | api: Claude API (MCP connector) | grupo: Mercado (IA) | verificacao: doc | atualizado: 2026-11-14 -->
### [claude.mcp_connector] Claude API (MCP connector) — Chat com Claude usando o MCP do Harvest

- **Método:** POST
- **URL:** `https://api.anthropic.com/v1/messages (client.beta.messages.create)`
- **Autenticação:** ANTHROPIC_API_KEY (só no back-end)
- **Para que serve:** A API do Claude conecta sozinha no servidor MCP remoto e usa as ferramentas para responder.
- **Uso no Field Shift:** Chat do agricultor: pergunta livre sobre qualquer cultura; o clima vai pronto do aplicativo.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `mcp_servers` | sim | [{type:'url', url:'https://...', name, authorization_token?}] | `harvest-portal` |
| `tools` | sim | [{type:'mcp_toolset', mcp_server_name}] | `harvest-portal` |
| `betas` | sim | lista de betas | `mcp-client-2025-11-20` |
| `system` | não | regras do assistente | `—` |
| `messages` | sim | pergunta + dados do aplicativo | `—` |

**Chamada (curl)**

```bash
curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "anthropic-beta: mcp-client-2025-11-20" -H "content-type: application/json" -d '{"model": "claude-sonnet-5-5", "max_tokens": 1000, "messages": [{"role": "user", "content": "Tem mercado de sorgo no Brasil?"}], "mcp_servers": [{"type": "url", "url": "https://mcp.harvestportal.org/mcp", "name": "harvest-portal"}], "tools": [{"type": "mcp_toolset", "mcp_server_name": "harvest-portal"}]}' 
```

**Chamada (Python)**

```python
import anthropic
client = anthropic.Anthropic()
resp = client.beta.messages.create(
    model="claude-sonnet-5-5", max_tokens=1500, system=REGRAS,
    messages=[{"role": "user", "content": PACOTE_COM_CLIMA_E_PERGUNTA}],
    mcp_servers=[{"type": "url", "url": "https://mcp.harvestportal.org/mcp", "name": "harvest-portal"}],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "harvest-portal"}],
    betas=["mcp-client-2025-11-20"])
texto = "".join(b.text for b in resp.content if b.type == "text")
chamadas = [b for b in resp.content if b.type == "mcp_tool_use"]
```

**Resposta:** content com blocos text, mcp_tool_use {name, server_name, input} e mcp_tool_result {is_error, content}

**Erros:** Rejeição se faltar o beta ou se name ≠ mcp_server_name.

**Observações:** Só chamadas de ferramenta; servidor HTTP público (https). Restringir ferramentas com default_config/configs.

**Fonte:** https://platform.claude.com/docs/en/agents-and-tools/mcp-connector

---
## IBGE SIDRA

<!-- chunk_id: ibge.sidra_values | api: IBGE SIDRA | grupo: Mercado local (Brasil) | verificacao: doc | atualizado: 2026-11-14 -->
### [ibge.sidra_values] IBGE SIDRA — Valores de uma tabela (PAM 5457)

- **Método:** GET
- **URL:** `https://apisidra.ibge.gov.br/values/t/{tabela}/n{nivel}/{localidades}/v/{variaveis}/p/{periodos}/c{classificacao}/{categorias}`
- **Autenticação:** Nenhuma
- **Para que serve:** Baixar dados da PAM: área plantada (8331), área colhida (216), quantidade (214), rendimento (112), valor (215), por município/microrregião e ano.
- **Uso no Field Shift:** Nota de mercado LOCAL e quebra de rendimento nos anos secos do NASA POWER.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `t` | sim | tabela | `5457` |
| `n{nivel}` | sim | 1 Brasil, 3 UF, 6 município, 9 microrregião + códigos ou all | `n6/<código do município>` |
| `v` | sim | variáveis ou allxp | `8331,216,214,112,215` |
| `p` | sim | last / last%20N / first N / AAAA-AAAA / all | `last%2010` |
| `c782` | não ⚠️ | produtos (códigos) ou all | `<códigos de sorgo, milho, soja>` |
| `h` | não | n = sem cabeçalho | `n` |

**Chamada (curl)**

```bash
curl "https://apisidra.ibge.gov.br/values/t/5457/n6/<COD_MUNICIPIO>/v/8331,216,214,112,215/p/last%2010/c782/<COD_PRODUTOS>"
```

**Chamada (Python)**

```python
import requests, pandas as pd
url = ("https://apisidra.ibge.gov.br/values/t/5457/n6/" + COD_MUN +
       "/v/8331,216,214,112,215/p/last%2010/c782/" + ",".join(COD_PRODUTOS))
dados = requests.get(url, timeout=60).json()
cab, linhas = dados[0], dados[1:]                 # 1ª linha = cabeçalho
df = pd.DataFrame(linhas).rename(columns=cab)
df["Valor"] = pd.to_numeric(df["Valor"].replace({"-": "0"}), errors="coerce")  # "..", "X" = ausente
```

**Resposta:** Lista JSON; item 0 = cabeçalho {"V": "Valor", "D1C": "Município (Código)", "D2C": "Variável (Código)", "D3C": "Ano (Código)", "D4C": "Produto ... (Código)", ...}; demais = linhas com V como texto

**Erros:** Erro se exceder o limite de valores por consulta: dividir por produto ou período.

**Observações:** PAM: município, anual, 64 produtos, corte de 1 ha/1 t, valor nominal (corrigir pelo IPCA, tabela 1737). Classificação c782 e códigos de produto ⚠️: confirme com ibge.agregados_metadados.

**Fonte:** https://apisidra.ibge.gov.br/home/ajuda ; https://sidra.ibge.gov.br/tabela/5457 ; https://rdrr.io/cran/datazoom.amazonia/src/R/pam.R

---
## IBGE Agregados v3

<!-- chunk_id: ibge.agregados_metadados | api: IBGE Agregados v3 | grupo: Mercado local (Brasil) | verificacao: doc | atualizado: 2026-11-14 -->
### [ibge.agregados_metadados] IBGE Agregados v3 — Metadados de uma tabela

- **Método:** GET
- **URL:** `https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/metadados`
- **Autenticação:** Nenhuma
- **Para que serve:** Variáveis, classificações e categorias (códigos dos produtos), períodos e níveis territoriais de uma tabela.
- **Uso no Field Shift:** Descobrir os códigos de sorgo, milho, soja etc. na tabela 5457.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `tabela` | sim | no caminho | `5457` |

**Chamada (curl)**

```bash
curl "https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados"
```

**Chamada (Python)**

```python
meta = requests.get("https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados").json()
for c in meta["classificacoes"]:
    produtos = {cat["nome"]: cat["id"] for cat in c["categorias"]}
```

**Resposta:** {id, nome, periodicidade, nivelTerritorial, variaveis: [{id, nome, unidade}], classificacoes: [{id, nome, categorias: [{id, nome}]}]} ⚠️

**Erros:** —

**Observações:** Guarde em cache: muda raramente.

**Fonte:** https://servicodados.ibge.gov.br/api/docs/agregados?versao=3

---
## IBGE Localidades v1

<!-- chunk_id: ibge.localidades_municipios | api: IBGE Localidades v1 | grupo: Mercado local (Brasil) | verificacao: doc | atualizado: 2026-11-14 -->
### [ibge.localidades_municipios] IBGE Localidades v1 — Municípios de uma UF

- **Método:** GET
- **URL:** `https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF}/municipios`
- **Autenticação:** Nenhuma
- **Para que serve:** Código IBGE de 7 dígitos dos municípios (e microrregião de cada um).
- **Uso no Field Shift:** Traduzir o município do talhão no código usado pelo SIDRA.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `UF` | sim | sigla ou código | `MG` |

**Chamada (curl)**

```bash
curl "https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios"
```

**Chamada (Python)**

```python
muns = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios").json()
cod = next(m["id"] for m in muns if m["nome"] == "Monte Carmelo")
```

**Resposta:** [{id, nome, microrregiao: {id, nome, mesorregiao: {...}}, ...}] ⚠️

**Erros:** —

**Observações:** Para microrregião use o id de microrregiao com /n9/ no SIDRA.

**Fonte:** https://servicodados.ibge.gov.br/api/docs/localidades

---
## NASA AppEEARS

<!-- chunk_id: appeears.login | api: NASA AppEEARS | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [appeears.login] NASA AppEEARS — Login (token)

- **Método:** POST
- **URL:** `https://appeears.earthdatacloud.nasa.gov/api/login`
- **Autenticação:** Earthdata Login (usuário e senha, HTTP Basic)
- **Para que serve:** Obter o token Bearer usado em todas as outras chamadas do AppEEARS.
- **Uso no Field Shift:** Pré-requisito para baixar MODIS NDVI, SMAP, ECOSTRESS por ponto.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `auth` | sim | (usuário, senha) Earthdata | `—` |

**Chamada (curl)**

```bash
curl -X POST -u "USUARIO:SENHA" "https://appeears.earthdatacloud.nasa.gov/api/login"
```

**Chamada (Python)**

```python
API = "https://appeears.earthdatacloud.nasa.gov/api/"
tok = requests.post(API + "login", auth=(USUARIO, SENHA)).json()["token"]
HEAD = {"Authorization": f"Bearer {tok}"}
```

**Resposta:** {token_type: 'Bearer', token, expiration}

**Erros:** 401 credenciais inválidas.

**Observações:** Conta gratuita em urs.earthdata.nasa.gov. Não versionar senha.

**Fonte:** https://nasa-openscapes.github.io/earthdata-cloud-cookbook/external/appeears_csv_cloud_access.html

---
<!-- chunk_id: appeears.product_layers | api: NASA AppEEARS | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [appeears.product_layers] NASA AppEEARS — Camadas de um produto

- **Método:** GET
- **URL:** `https://appeears.earthdatacloud.nasa.gov/api/product/{ProductAndVersion}`
- **Autenticação:** Nenhuma ⚠️
- **Para que serve:** Listar as camadas (layers) de um produto, ex.: MOD13Q1.061.
- **Uso no Field Shift:** Descobrir o nome exato da camada de NDVI, umidade do solo ou temperatura.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `ProductAndVersion` | sim | no caminho | `MOD13Q1.061` |

**Chamada (curl)**

```bash
curl "https://appeears.earthdatacloud.nasa.gov/api/product/MOD13Q1.061"
```

**Chamada (Python)**

```python
camadas = requests.get(API + "product/MOD13Q1.061").json()
print(list(camadas))     # ex.: "_250m_16_days_NDVI" ⚠️
```

**Resposta:** {nome_da_camada: {Description, Units, ScaleFactor, FillValue, ...}}

**Erros:** —

**Observações:** Lista de produtos: GET /api/product.

**Fonte:** https://appeears.earthdatacloud.nasa.gov/api/

---
<!-- chunk_id: appeears.task_point | api: NASA AppEEARS | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [appeears.task_point] NASA AppEEARS — Criar tarefa por ponto

- **Método:** POST
- **URL:** `https://appeears.earthdatacloud.nasa.gov/api/task`
- **Autenticação:** Bearer token
- **Para que serve:** Pedir a série temporal de camadas de satélite para coordenadas e datas.
- **Uso no Field Shift:** Série MODIS NDVI do talhão (solo descoberto, rotação real com crop-cycle-detection); SMAP; ECOSTRESS.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `task_type` | sim | point / area | `point` |
| `task_name` | sim | texto | `fieldshift_ndvi` |
| `params.dates` | sim | [{startDate, endDate}] MM-DD-YYYY | `01-01-2001 a 12-31-2025` |
| `params.layers` | sim | [{product, layer}] | `MOD13Q1.061 / _250m_16_days_NDVI ⚠️` |
| `params.coordinates` | sim | [{latitude, longitude, id}] | `-18.7, -47.5, talhao3` |

**Chamada (curl)**

```bash
curl -X POST "https://appeears.earthdatacloud.nasa.gov/api/task" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"task_type":"point","task_name":"fieldshift_ndvi","params":{"dates":[{"startDate":"01-01-2001","endDate":"12-31-2025"}],"layers":[{"product":"MOD13Q1.061","layer":"_250m_16_days_NDVI"}],"coordinates":[{"latitude":-18.7,"longitude":-47.5,"id":"talhao3"}]}}' 
```

**Chamada (Python)**

```python
task = {"task_type": "point", "task_name": "fieldshift_ndvi",
        "params": {"dates": [{"startDate": "01-01-2001", "endDate": "12-31-2025"}],
                   "layers": [{"product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI"}],
                   "coordinates": [{"latitude": -18.7, "longitude": -47.5, "id": "talhao3"}]}}
task_id = requests.post(API + "task", json=task, headers=HEAD).json()["task_id"]
```

**Resposta:** {task_id, status}

**Erros:** 400 JSON inválido; 401 token.

**Observações:** Processamento assíncrono (minutos a horas). Faça no preparo, não na demo.

**Fonte:** https://nasa-openscapes.github.io/earthdata-cloud-cookbook/external/appeears_csv_cloud_access.html

---
<!-- chunk_id: appeears.task_status | api: NASA AppEEARS | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [appeears.task_status] NASA AppEEARS — Status da tarefa

- **Método:** GET
- **URL:** `https://appeears.earthdatacloud.nasa.gov/api/task/{task_id}`
- **Autenticação:** Bearer token
- **Para que serve:** Ver se a tarefa terminou.
- **Uso no Field Shift:** Esperar a série ficar pronta.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `task_id` | sim | no caminho | `<task_id>` |

**Chamada (curl)**

```bash
curl -H "Authorization: Bearer $TOKEN" "https://appeears.earthdatacloud.nasa.gov/api/task/<task_id>"
```

**Chamada (Python)**

```python
import time
while requests.get(API + f"task/{task_id}", headers=HEAD).json()["status"] != "done":
    time.sleep(30)
```

**Resposta:** {task_id, status: queued|pending|processing|done|error, ...} ⚠️

**Erros:** —

**Observações:** Não consulte mais que 1 vez a cada 30 s.

**Fonte:** https://appeears.earthdatacloud.nasa.gov/api/

---
<!-- chunk_id: appeears.bundle | api: NASA AppEEARS | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [appeears.bundle] NASA AppEEARS — Arquivos prontos e download

- **Método:** GET
- **URL:** `https://appeears.earthdatacloud.nasa.gov/api/bundle/{task_id} e /bundle/{task_id}/{file_id}`
- **Autenticação:** Bearer token
- **Para que serve:** Listar e baixar os arquivos gerados (CSV da série por ponto).
- **Uso no Field Shift:** Obter o CSV de NDVI para o crop-cycle-detection.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `task_id` | sim | no caminho | `<task_id>` |
| `file_id` | sim | no caminho (do bundle) | `<file_id>` |

**Chamada (curl)**

```bash
curl -L -H "Authorization: Bearer $TOKEN" -o ndvi.csv "https://appeears.earthdatacloud.nasa.gov/api/bundle/<task_id>/<file_id>"
```

**Chamada (Python)**

```python
bundle = requests.get(API + f"bundle/{task_id}", headers=HEAD).json()
for f in bundle["files"]:
    if f["file_name"].endswith(".csv"):
        r = requests.get(API + f"bundle/{task_id}/{f['file_id']}", headers=HEAD, allow_redirects=True)
        open(f["file_name"], "wb").write(r.content)
```

**Resposta:** bundle: {files: [{file_id, file_name, file_type, file_size, sha256}], task_id, bundle_type}

**Erros:** —

**Observações:** NDVI do MOD13Q1 tem fator de escala 0,0001 ⚠️ (confira em product_layers).

**Fonte:** https://nasa-openscapes.github.io/earthdata-cloud-cookbook/external/appeears_csv_cloud_access.html

---
## NASA Earthdata CMR

<!-- chunk_id: earthdata.cmr_granules | api: NASA Earthdata CMR | grupo: Satélite | verificacao: doc | atualizado: 2026-11-14 -->
### [earthdata.cmr_granules] NASA Earthdata CMR — Buscar arquivos (granules)

- **Método:** GET
- **URL:** `https://cmr.earthdata.nasa.gov/search/granules.json`
- **Autenticação:** Nenhuma para buscar; Earthdata Login para baixar
- **Para que serve:** Encontrar arquivos de um dataset por nome curto, período e área (GPM IMERG, SRTM, GRACE, SMAP...).
- **Uso no Field Shift:** Achar os arquivos de chuva GPM IMERG diária (GPM_3IMERGDF) ou SRTM do talhão para baixar no preparo.
- **Verificação:** doc

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `short_name` | sim* | nome curto da coleção | `GPM_3IMERGDF` |
| `version` | não | versão | `07 ⚠️` |
| `temporal` | não | início,fim ISO 8601 | `2024-01-01T00:00:00Z,2024-01-31T23:59:59Z` |
| `bounding_box` | não | oeste,sul,leste,norte | `-48.5,-19.5,-46.5,-17.5` |
| `point` | não | lon,lat | `-47.5,-18.7` |
| `page_size` | não | int (até 2000) | `50` |

**Chamada (curl)**

```bash
curl "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=GPM_3IMERGDF&temporal=2024-01-01T00:00:00Z,2024-01-31T23:59:59Z&bounding_box=-48.5,-19.5,-46.5,-17.5&page_size=50"
```

**Chamada (Python)**

```python
r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json", params={
    "short_name": "GPM_3IMERGDF", "temporal": "2024-01-01T00:00:00Z,2024-01-31T23:59:59Z",
    "bounding_box": "-48.5,-19.5,-46.5,-17.5", "page_size": 50}).json()
links = [l["href"] for g in r["feed"]["entry"] for l in g["links"] if l["href"].endswith((".nc4", ".tif", ".hdf", ".h5"))]
# Download: pip install earthaccess -> earthaccess.login(); earthaccess.download(...)
```

**Resposta:** feed.entry: [{id, title, time_start, links: [{href}]}]

**Erros:** Sem short_name/concept_id, bounding_box não funciona.

**Observações:** Para baixar use Earthdata Login (earthaccess facilita). *Exige um identificador de coleção.

**Fonte:** https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

---
## NASA Harvest crop-cycle-detection (biblioteca Python)

<!-- chunk_id: lib.crop_cycle_detection | api: NASA Harvest crop-cycle-detection (biblioteca Python) | grupo: Satélite (análise) | verificacao: testado-local | atualizado: 2026-11-14 -->
### [lib.crop_cycle_detection] NASA Harvest crop-cycle-detection (biblioteca Python) — Detectar safras e solo descoberto no NDVI

- **Método:** Função Python local
- **URL:** `https://github.com/nasaharvest/crop-cycle-detection`
- **Autenticação:** Nenhuma (Apache-2.0)
- **Para que serve:** A partir de uma série de NDVI, detectar cada safra: início, fim, green-up, pico.
- **Uso no Field Shift:** Rotação real do talhão e meses de solo descoberto (pedido explícito do desafio).
- **Verificação:** testado-local

**Parâmetros**

| Parâmetro | Obrigatório | Tipo / valores | Exemplo |
|---|---|---|---|
| `df` | sim | DataFrame com date e NDVI (0–1) | `série MODIS do AppEEARS` |
| `min_season_length` | não | dias, padrão 60 | `60` |
| `exclude_months` | não | meses a ignorar | `None` |

**Chamada (curl)**

```bash
git clone https://github.com/nasaharvest/crop-cycle-detection.git && pip install -r requirements.txt
```

**Chamada (Python)**

```python
import sys; sys.path.insert(0, "crop-cycle-detection")
from src.crop_cycle import crop_cycle_model
report, diario = crop_cycle_model(df_ndvi)   # df_ndvi: colunas date, NDVI
print(report[["season_number", "approx_season_start", "approx_season_end", "ndvi_peak_date"]])
```

**Resposta:** report: season_number, approx_season_start/end/length, greenup_date, ndvi_peak_date/value, troughs; diario: série suavizada

**Erros:** report vazio se não houver safra.

**Observações:** Testado com os dados de exemplo do repositório (2 safras).

**Fonte:** https://github.com/nasaharvest/crop-cycle-detection

---
