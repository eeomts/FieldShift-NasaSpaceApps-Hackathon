# Harvest Portal API: guia de uso

## Como fazer requisições, autenticar, ler respostas e usar cada ação

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Estrutura baseada no *API Guide* oficial do CKAN, adaptada ao Harvest Portal
> Documentos relacionados: `NASA_HARVEST_PORTAL_API.md` (análise e parâmetros), `fluxo-aplicativo-power-harvest-mcp.md`, `ARQUITETURA-COMPLETA.md`

---

## Sumário

1. [Introdução](#1-introdução)
2. [Fazendo uma requisição](#2-fazendo-uma-requisição)
3. [Exemplo: primeira consulta, passo a passo](#3-exemplo-primeira-consulta-passo-a-passo)
4. [Versões da API](#4-versões-da-api)
5. [Autenticação e tokens de API](#5-autenticação-e-tokens-de-api)
6. [Funções acessíveis por GET](#6-funções-acessíveis-por-get)
7. [Suporte a JSONP](#7-suporte-a-jsonp)
8. [Exemplos de uso](#8-exemplos-de-uso)
9. [Referência das ações](#9-referência-das-ações)
10. [Baixando arquivos](#10-baixando-arquivos)
11. [O que o Harvest Portal não expõe](#11-o-que-o-harvest-portal-não-expõe)
12. [Receitas para o Field Shift](#12-receitas-para-o-field-shift)
13. [Caso de uso: nota de mercado para o agricultor](#13-caso-de-uso-nota-de-mercado-para-o-agricultor)
14. [Checklist de integração](#14-checklist-de-integração)
15. [Referências](#15-referências)

---

## Nível de verificação

- A estrutura e as regras gerais (envelope de resposta, GET/POST, versões, tokens, JSONP) vêm do **API Guide oficial do CKAN**, a plataforma em que o Harvest Portal roda.
- A lista de endpoints, a autenticação e os exemplos específicos vêm das páginas **`/api-docs`** e **`/api-examples`** do Harvest Portal e da captura de tela da página Swagger enviada pela equipe.
- **A especificação `openapi/harvest-portal-api.json` não pôde ser lida diretamente** e **nenhuma requisição foi executada ao vivo** (o acesso automatizado foi bloqueado). Os comportamentos do CKAN que o Harvest pode ter desligado ou alterado estão marcados com ⚠️. Confirme na Swagger (*Try it out*) antes de depender deles.

---

## 1. Introdução

O Harvest Portal é o repositório de dados do **NASA Harvest**, o programa de agricultura e segurança alimentar da NASA. Ele roda sobre o **CKAN**, um software livre de catálogo de dados usado por governos e organizações no mundo todo.

A **API de ações** (*Action API*) do CKAN é uma API no estilo RPC: cada endereço chama uma "ação" (uma função) do portal, como "buscar datasets" ou "mostrar um dataset". Tudo o que a interface web faz para leitura pode ser feito pela API.

### 1.1 O que o Harvest Portal publica da API

A página `/api-docs` documenta um **subconjunto curado** da API do CKAN: **somente operações públicas de leitura**. Criação, edição e exclusão de datasets e ações de conta ou administração **ficaram de fora de propósito**.

| Grupo | Ações documentadas |
|---|---|
| **Datasets** | `package_search`, `package_show` |
| **Resources** | `resource_show` |
| **Organizations** | `organization_list`, `organization_show` |
| **Groups** | `group_list`, `group_show` |
| **Tags** | `tag_list` |
| **DataStore** | `datastore_search` |

### 1.2 Vocabulário

| Termo do CKAN | Significado no portal |
|---|---|
| **package** | Um **dataset** (metadados + arquivos). Na API, "dataset" e "package" são a mesma coisa |
| **resource** | Um **arquivo ou link** dentro do dataset (CSV, GeoTIFF, SHP...) |
| **organization** | Quem publicou o dataset (NASA Harvest, FAO, OECD...) |
| **group** | Coleção temática (ex.: Supply Chain) |
| **tag** | Palavra-chave livre |
| **DataStore** | Banco interno onde planilhas viram tabelas consultáveis por filtro. Tem API própria (`datastore_search`) |

### 1.3 Dados de identificação

| Item | Valor |
|---|---|
| Base da API | `https://data.harvestportal.org/api/3/action/` |
| Documentação interativa | `https://data.harvestportal.org/api-docs` |
| Exemplos oficiais | `https://data.harvestportal.org/api-examples` |
| Especificação OpenAPI | `https://data.harvestportal.org/openapi/harvest-portal-api.json` |
| Servidor MCP (para assistentes de IA) | `https://mcp.harvestportal.org/mcp` |
| Autenticação para dados públicos | Nenhuma |

---

## 2. Fazendo uma requisição

### 2.1 O endereço

Toda requisição segue o mesmo formato:

```
https://data.harvestportal.org/api/3/action/<nome_da_ação>
```

Exemplos:

```
https://data.harvestportal.org/api/3/action/group_list
https://data.harvestportal.org/api/3/action/package_search?q=maize&rows=5
```

### 2.2 Dois jeitos de chamar: GET e POST

| Método | Como os parâmetros vão | Quando usar |
|---|---|---|
| **GET** | Na URL, depois do `?` (`?q=maize&rows=5`) | Ações de leitura. É o que a Swagger do Harvest documenta. Funciona no navegador |
| **POST** | Num **corpo JSON**, com o cabeçalho `Content-Type: application/json` | Quando há parâmetros complexos (dicionários, listas), como o `filters` do `datastore_search`. É o que a página de exemplos do Harvest usa para a DataStore |

**GET:**
```bash
curl "https://data.harvestportal.org/api/3/action/package_search?q=maize&rows=5"
```

**POST:**
```bash
curl -X POST "https://data.harvestportal.org/api/3/action/package_search" \
  -H "Content-Type: application/json" \
  -d '{"q": "maize", "rows": 5}'
```

Os dois devolvem o mesmo resultado.

### 2.3 O envelope da resposta

**Toda** resposta é um objeto JSON com três chaves:

```json
{
  "help": "https://data.harvestportal.org/api/3/action/help_show?name=package_search",
  "success": true,
  "result": { ... }
}
```

| Chave | Significado |
|---|---|
| `help` | Link para a documentação da ação chamada |
| `success` | `true` se deu certo, `false` se falhou. **Sempre verifique esta chave** |
| `result` | O resultado (só aparece quando `success` é `true`) |
| `error` | Aparece **no lugar** de `result` quando `success` é `false` |

### 2.4 Erros

Quando algo dá errado, a resposta traz `error` com duas informações:

```json
{
  "help": "...",
  "success": false,
  "error": {
    "__type": "Not Found Error",
    "message": "Not found"
  }
}
```

| `__type` comum | Causa típica | O que fazer |
|---|---|---|
| `Not Found Error` | `id` de dataset, recurso, organização ou grupo inexistente | Conferir o `id` ou o `name` |
| `Validation Error` | Parâmetro obrigatório ausente ou com formato errado; coluna inexistente no `filters` | Ler `error`: ele indica o campo com problema |
| `Authorization Error` | Tentativa de ver dado privado sem token | Usar token ou escolher dado público |

### 2.5 Códigos HTTP

O CKAN **tenta devolver `200 OK` mesmo quando a ação falha**. Por isso, o código HTTP não é confiável para saber se deu certo: **confie na chave `success`**.

Problemas graves de formato ainda podem devolver `409`, `400` ou `500`, nessa ordem crescente de gravidade.

**Regra prática para o código:**

```python
r = requests.get(url, params=params, timeout=60)
data = r.json()              # tenta ler o JSON mesmo com 4xx
if not data.get("success"):
    raise RuntimeError(data.get("error"))
resultado = data["result"]
```

---

## 3. Exemplo: primeira consulta, passo a passo

**Objetivo:** descobrir que datasets de produção agrícola existem e ler as primeiras linhas de um deles.

### Passo 1 — Quantos datasets existem e de quem são

```
GET https://data.harvestportal.org/api/3/action/package_search?rows=0&facet.field=["organization"]&facet.limit=20
```

- `rows=0`: não traz nenhum dataset, só a contagem e as facetas.
- `facet.field=["organization"]`: conta quantos datasets cada organização publicou.

### Passo 2 — Buscar datasets pelo tema

```
GET https://data.harvestportal.org/api/3/action/package_search?q=crop production&rows=10
```

Guarde o campo `name` do dataset que interessa (ex.: `oecd-crop-production`, fictício).

### Passo 3 — Ver os arquivos do dataset

```
GET https://data.harvestportal.org/api/3/action/package_show?id=oecd-crop-production
```

Na resposta, olhe `result.resources[]`. Guarde o `id` do recurso e veja se `datastore_active` é `true`.

### Passo 4 — Descobrir as colunas da tabela

```
GET https://data.harvestportal.org/api/3/action/datastore_search?resource_id=<id>&limit=0
```

Com `limit=0`, a resposta traz só `fields` (as colunas e seus tipos), sem linhas.

### Passo 5 — Puxar os dados filtrados

```bash
curl -X POST "https://data.harvestportal.org/api/3/action/datastore_search" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "<id>", "filters": {"<coluna>": "<valor>"}, "limit": 20}'
```

### Passo 6 — Se a tabela não estiver na DataStore

Baixe o arquivo pelo campo `url` do recurso (seção [10](#10-baixando-arquivos)).

---

## 4. Versões da API

| Forma | Exemplo | Comportamento |
|---|---|---|
| **Com versão** (recomendada) | `/api/3/action/package_search` | Sempre usa a versão 3 |
| Sem versão | `/api/action/package_search` | Usa a versão mais recente disponível no site |

A **versão 3** é a única versão da API de ações. Mesmo assim, o guia do CKAN recomenda **sempre incluir o `3`** no endereço, para o comportamento do cliente ficar estável. Todos os exemplos deste documento usam `/api/3/action/`.

---

## 5. Autenticação e tokens de API

### 5.1 Precisa de login?

| Situação | Precisa de token? |
|---|---|
| Ler datasets públicos (o caso do Field Shift) | **Não** |
| Ler datasets privados de uma organização da qual você é membro | **Sim** |

Sem credenciais, a API devolve **apenas datasets públicos**.

### 5.2 Como criar um token

1. Faça login no portal.
2. Abra o seu perfil.
3. Vá em **Manage → API Tokens**.
4. Crie o token e copie o valor (ele aparece só uma vez).

É possível ter vários tokens e revogar cada um separadamente.

### 5.3 Como enviar o token

No cabeçalho **`Authorization`** de cada requisição:

```bash
curl -H "Authorization: <SEU_TOKEN>" \
  "https://data.harvestportal.org/api/3/action/package_search?rows=5"
```

Em Python:

```python
headers = {"Authorization": TOKEN}
r = requests.get(f"{BASE}/package_search", params={"rows": 5}, headers=headers)
```

Com o cliente `ckanapi`:

```python
from ckanapi import RemoteCKAN
portal = RemoteCKAN("https://data.harvestportal.org", apikey=TOKEN, user_agent="fieldshift")
```

**No servidor MCP**, o token vai no cabeçalho `X-CKAN-API-Token` (ou em `Authorization`, se o cliente de IA só oferecer esse campo).

### 5.4 Cuidados

- O token dá acesso **como se fosse você**. Trate como senha.
- **Nunca** coloque o token no código do front-end, no repositório ou em prints.
- Guarde em variável de ambiente (`HARVEST_TOKEN`) e leia no back-end.
- Para o Field Shift, que usa só dados públicos, **não crie token**.

---

## 6. Funções acessíveis por GET

Todas as ações de leitura do CKAN aceitam GET. No Harvest Portal, são estas:

| Ação | Exemplo de GET |
|---|---|
| `package_search` | `.../package_search?q=yield&rows=10` |
| `package_show` | `.../package_show?id=<name ou id>` |
| `resource_show` | `.../resource_show?id=<id do recurso>` |
| `organization_list` | `.../organization_list?all_fields=true` |
| `organization_show` | `.../organization_show?id=<name>&include_datasets=true` |
| `group_list` | `.../group_list?all_fields=true` |
| `group_show` | `.../group_show?id=<name>&include_datasets=true` |
| `tag_list` | `.../tag_list?query=crop` |
| `datastore_search` | `.../datastore_search?resource_id=<id>&limit=10` |

### 6.1 Regras da URL

- Parâmetros depois do `?`, separados por `&`: `?q=yield&rows=10`.
- Espaços viram `%20` (ou `+`): `q=crop%20production`.
- **Listas**: repita o parâmetro (`terms=a&terms=b`) ou envie em JSON (`facet.field=["tags","organization"]`).
- **Dicionários** (como `filters` do `datastore_search`): envie como JSON codificado na URL, ou prefira **POST**.

### 6.2 Lendo no navegador

Cole qualquer URL GET acima na barra de endereços. O Firefox já formata o JSON. No Chrome, uma extensão de visualização de JSON ajuda.

---

## 7. Suporte a JSONP

O CKAN aceita o parâmetro `callback` em requisições **GET**, que envolve a resposta numa função JavaScript:

```
GET https://data.harvestportal.org/api/3/action/package_show?id=<name>&callback=minhaFuncao
```

Resposta:
```
minhaFuncao({"help": "...", "success": true, "result": {...}});
```

Isso servia para páginas web antigas lerem a API de outro domínio.

⚠️ **Não documentado na Swagger do Harvest.** Pode estar desligado. Para aplicações novas, **chame a API pelo back-end** do Field Shift (sem JSONP e sem problemas de CORS) e entregue o resultado ao front-end.

---

## 8. Exemplos de uso

### 8.1 Python com `requests`

```python
import requests

BASE = "https://data.harvestportal.org/api/3/action"

def ckan(action, method="GET", **params):
    url = f"{BASE}/{action}"
    if method == "GET":
        r = requests.get(url, params=params, timeout=60)
    else:
        r = requests.post(url, json=params, timeout=60)
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"{action}: {data.get('error')}")
    return data["result"]

# Buscar datasets
res = ckan("package_search", q="maize", rows=5)
print(res["count"], "datasets encontrados")
for d in res["results"]:
    print("-", d["name"], "|", d["title"])

# Ver arquivos do primeiro
ds = ckan("package_show", id=res["results"][0]["name"])
for r in ds["resources"]:
    print(r["format"], r.get("datastore_active"), r["url"])
```

### 8.2 Python com `ckanapi` (cliente oficial do CKAN)

```bash
pip install ckanapi
```

```python
from ckanapi import RemoteCKAN

portal = RemoteCKAN("https://data.harvestportal.org", user_agent="fieldshift")

res = portal.action.package_search(q="maize", rows=5)
ds  = portal.action.package_show(id=res["results"][0]["name"])
tab = portal.action.datastore_search(resource_id="<id>", limit=10)
```

O `ckanapi` monta as URLs, verifica `success` e levanta exceções Python (`NotFound`, `ValidationError`) quando a ação falha.

### 8.3 JavaScript (`fetch`)

```javascript
const BASE = "https://data.harvestportal.org/api/3/action";

async function ckan(action, params = {}) {
  const url = `${BASE}/${action}?` + new URLSearchParams(params);
  const res = await fetch(url);
  const data = await res.json();
  if (!data.success) throw new Error(JSON.stringify(data.error));
  return data.result;
}

const res = await ckan("package_search", { q: "maize", rows: 5 });
console.log(res.count, res.results.map(d => d.name));
```

DataStore com POST:

```javascript
const res = await fetch(`${BASE}/datastore_search`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ resource_id: "<id>", filters: { "<coluna>": "<valor>" }, limit: 50 })
});
const data = await res.json();
```

### 8.4 Linha de comando (`curl` e `ckanapi`)

```bash
# curl
curl "https://data.harvestportal.org/api/3/action/tag_list"

# ckanapi CLI
ckanapi -r https://data.harvestportal.org action tag_list
ckanapi -r https://data.harvestportal.org action package_search q=maize rows=5
```

### 8.5 Tags

**Listar todas as tags:**
```
GET .../tag_list
```

**As 10 tags mais usadas (com contagem):**
```
GET .../package_search?facet.field=["tags"]&facet.limit=10&rows=0
```

**Todos os datasets com uma tag:**
```
GET .../package_search?fq=tags:cropland
```

### 8.6 Facetas: explorar o catálogo sem baixar nada

```
GET .../package_search?rows=0&facet.field=["organization","groups","tags","res_format","license_id"]&facet.limit=-1
```

A resposta traz, em `result.search_facets`, quantos datasets existem por organização, grupo, tag, formato e licença. É o jeito mais leve de entender o portal.

### 8.7 Filtros com `fq`

| Objetivo | Parâmetro |
|---|---|
| Só de uma organização | `fq=organization:<name>` |
| Só com uma tag | `fq=tags:<tag>` |
| Só com arquivo CSV | `fq=res_format:CSV` |
| Só de um grupo | `fq=groups:<name>` |
| Combinar | `fq=organization:<name> AND res_format:CSV` |

### 8.8 DataStore: consultar tabelas

```bash
# 1) Colunas
curl "https://data.harvestportal.org/api/3/action/datastore_search?resource_id=<id>&limit=0"

# 2) Filtro exato + colunas escolhidas + ordenação
curl -X POST "https://data.harvestportal.org/api/3/action/datastore_search" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "<id>",
       "filters": {"<coluna_país>": "BRA"},
       "fields": ["<coluna_ano>", "<coluna_valor>"],
       "sort": "<coluna_ano> desc",
       "limit": 100}'

# 3) Busca de texto livre
curl "https://data.harvestportal.org/api/3/action/datastore_search?resource_id=<id>&q=sorghum"
```

**Paginação:** use `limit` e `offset`, ou siga o link `result._links.next` da resposta.

### 8.9 Arquivos Parquet

A página de exemplos do Harvest mostra a leitura direta de arquivos Parquet pelo link de download. Em Python:

```python
import pandas as pd
df = pd.read_parquet("https://data.harvestportal.org/dataset/<DATASET>/resource/<RESOURCE>/download/<ARQUIVO>.parquet")
```

No navegador, a página usa a biblioteca JavaScript `hyparquet`.

---

## 9. Referência das ações

> Parâmetros conforme o CKAN. ⚠️ = padrão do CKAN que pode não estar exposto na especificação curada do Harvest.

### 9.1 `package_search` — buscar datasets

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `q` | texto | `*:*` | Busca livre (sintaxe Solr) |
| `fq` | texto | — | Filtro por campo |
| `fq_list` ⚠️ | lista | — | Filtros extras |
| `sort` | texto | `score desc, metadata_modified desc` | Ordenação |
| `rows` | inteiro | 10 | Quantos datasets (máx. 1000) |
| `start` | inteiro | 0 | Posição inicial (paginação) |
| `facet` | booleano | `true` | Liga as facetas |
| `facet.field` | lista | — | Campos para contar |
| `facet.limit` | inteiro | 50 | Valores por faceta (`-1` = todos) |
| `facet.mincount` | inteiro | — | Contagem mínima |
| `include_private` ⚠️ | booleano | `false` | Inclui privados (com token) |

**Retorna:** `count`, `results` (lista de datasets), `facets`, `search_facets`.

### 9.2 `package_show` — mostrar um dataset

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | texto | **Sim** | UUID ou `name` do dataset |
| `use_default_schema` ⚠️ | booleano | Não | Usa o esquema padrão do CKAN |

**Retorna:** o dataset completo, com `resources`, `organization`, `tags`, `groups`, `license_id`, `notes`, datas.

### 9.3 `resource_show` — mostrar um arquivo

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | texto | **Sim** | UUID do recurso |

**Retorna:** `id`, `name`, `format`, `url`, `datastore_active`, `size`, `mimetype`, `last_modified`, `package_id`.

### 9.4 `organization_list` / `group_list` — listar

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `all_fields` | booleano | `false` | `true` devolve objetos completos com `package_count` |
| `sort` ⚠️ | texto | `title asc` | `name`, `package_count` ou `title` |
| `limit` ⚠️ | inteiro | 1000 (25 com `all_fields`) | Itens por página |
| `offset` ⚠️ | inteiro | 0 | Paginação |
| `include_dataset_count` ⚠️ | booleano | `true` | Contagem de datasets |

**Retorna:** lista de nomes, ou de objetos se `all_fields=true`.

### 9.5 `organization_show` / `group_show` — mostrar um

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | texto | **Sim** | UUID ou `name` |
| `include_datasets` | booleano | Não | Inclui a lista de datasets (padrão `false`) |
| `include_dataset_count` ⚠️ | booleano | Não | Inclui a contagem (padrão `true`) |

### 9.6 `tag_list` — listar tags

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `query` | texto | — | Só tags que contêm o texto |
| `vocabulary_id` ⚠️ | texto | — | Restringe a um vocabulário |
| `all_fields` ⚠️ | booleano | `false` | Objetos completos |

### 9.7 `datastore_search` — consultar uma tabela

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `resource_id` | texto | **obrigatório** | Recurso com `datastore_active=true` |
| `filters` | dicionário | — | Igualdade exata por coluna |
| `q` | texto ou dicionário | — | Busca de texto livre |
| `limit` | inteiro | 100 (máx. 32 000) | Linhas por chamada |
| `offset` | inteiro | 0 | Paginação |
| `fields` | lista | todas | Colunas a devolver |
| `sort` | texto | — | Ex.: `ano desc` |
| `distinct` | booleano | `false` | Só linhas distintas |
| `include_total` | booleano | `true` | Inclui o total |
| `records_format` | texto | `objects` | `objects`, `lists`, `csv`, `tsv` |

**Retorna:** `fields`, `records`, `total`, `limit`, `offset`, `_links`.

---

## 10. Baixando arquivos

O guia do CKAN cobre o **envio** de arquivos (`resource_create`, `resource_patch` com `multipart/form-data`). **No Harvest Portal, o envio não está disponível pela API pública.** O que existe é o **download**.

### 10.1 Pelo link do recurso

```
GET https://data.harvestportal.org/dataset/<DATASET_ID>/resource/<RESOURCE_ID>/download/<ARQUIVO>
```

Não monte essa URL à mão: use o campo `url` de `package_show` → `resources[]`.

```python
import requests
ds = ckan("package_show", id="<dataset>")
for r in ds["resources"]:
    arquivo = requests.get(r["url"], timeout=120)
    open(r["name"], "wb").write(arquivo.content)
```

### 10.2 Exportar uma tabela inteira da DataStore ⚠️

```
https://data.harvestportal.org/datastore/dump/<RESOURCE_ID>              (CSV)
https://data.harvestportal.org/datastore/dump/<RESOURCE_ID>?format=json
https://data.harvestportal.org/datastore/dump/<RESOURCE_ID>?bom=true     (CSV para Excel)
```

Recurso padrão do CKAN, não documentado na Swagger do Harvest. Teste antes.

---

## 11. O que o Harvest Portal não expõe

Comparação com o guia completo do CKAN:

| Grupo do CKAN | Exemplos | No Harvest Portal |
|---|---|---|
| **get** (leitura) | `package_show`, `package_search`, `group_list`... | ✅ Subconjunto de 8 ações + `datastore_search` |
| **create** | `package_create`, `resource_create` | ❌ Não documentado |
| **update** | `package_update`, `resource_update` | ❌ Não documentado |
| **patch** | `package_patch`, `resource_patch` | ❌ Não documentado |
| **delete** | `package_delete`, `dataset_purge` | ❌ Não documentado |
| **file** | `file_create`, `file_show` | ❌ Não documentado |
| **activity** | `package_activity_list` | ❌ Não documentado |
| Outras de leitura do CKAN (`package_list`, `tag_show`, `resource_search`...) | — | ⚠️ Podem responder, mas não estão na Swagger. Não dependa delas |

**Para o Field Shift isso não é problema:** o aplicativo só precisa **ler** dados de mercado.

---

## 12. Receitas para o Field Shift

### 12.1 Mapear o catálogo uma vez (preparo)

```python
cat = ckan("package_search", rows=0,
           **{"facet.field": '["organization","tags","res_format","license_id"]',
              "facet.limit": -1})
for campo, faceta in cat["search_facets"].items():
    print(campo, [(i["name"], i["count"]) for i in faceta["items"]][:10])
```

### 12.2 Achar tabelas de produção na DataStore

```python
achados = ckan("package_search", q="crop production", rows=50)
for d in achados["results"]:
    for r in d["resources"]:
        if r.get("datastore_active"):
            print(d["name"], "|", r["id"], "|", r["format"])
```

### 12.3 Ler as colunas e montar a ficha das culturas

```python
cols = ckan("datastore_search", resource_id="<id>", limit=0)["fields"]
print([c["id"] for c in cols])
```

Com os nomes reais das colunas e os códigos das culturas, preencha o campo `codigo_mercado` da ficha de cada cultura (ver `NASA_POWER_X_HARVEST_PORTAL.md`).

### 12.4 Nota de mercado de uma cultura

```python
def serie_mercado(resource_id, col_pais, pais, col_cultura, codigo, col_ano, col_valor):
    res = ckan("datastore_search", method="POST",
               resource_id=resource_id,
               filters={col_pais: pais, col_cultura: codigo},
               fields=[col_ano, col_valor],
               sort=f"{col_ano} desc", limit=15)
    return [(r[col_ano], r[col_valor]) for r in res["records"]]
```

### 12.5 Cache para a demo

```python
import json, pathlib
CACHE = pathlib.Path("cache_harvest"); CACHE.mkdir(exist_ok=True)

def com_cache(chave, func, *a, **kw):
    arq = CACHE / f"{chave}.json"
    if arq.exists():
        return json.loads(arq.read_text())
    dado = func(*a, **kw)
    arq.write_text(json.dumps(dado))
    return dado
```

---

## 13. Caso de uso: nota de mercado para o agricultor

> ⚠️ **Tudo nesta seção é fictício**: o agricultor, os nomes de datasets e organizações, os IDs, as colunas, os códigos e os números. Só as ações e os parâmetros seguem a API real.

### 13.1 Ficha do caso de uso

| Item | Descrição |
|---|---|
| **Nome** | UC-01 · Avaliar o mercado das culturas aprovadas no filtro climático |
| **Ator principal** | Agricultor |
| **Ator de sistema** | Back-end do Field Shift (quem chama a API) |
| **Sistema externo** | Harvest Portal API (`/api/3/action/`) |
| **Objetivo** | Mostrar se as culturas que aguentam o clima do talhão têm produção e comércio relevantes no país |
| **Gatilho** | O agricultor toca em **"Ver recomendação"** e o filtro climático (NASA POWER) termina |
| **Pré-condições** | 1) O agricultor fez login e cadastrou o talhão e a rotação atual. 2) O filtro climático aprovou pelo menos uma cultura. 3) A ficha de cada cultura tem o `codigo_mercado`. 4) A equipe já identificou o `resource_id` da tabela de produção (preparo, seção [12](#12-receitas-para-o-field-shift)) |
| **Pós-condição de sucesso** | Cada cultura aprovada tem uma nota de mercado (0 a 5) ou o selo "mercado não verificado", e a tela de ranking mostra a fonte |
| **Pós-condição de falha** | O ranking aparece só com o clima, com o aviso "mercado não verificado" |

### 13.2 A situação

O agricultor planta soja no verão e milho safrinha depois. Nos últimos anos, a chuva tem acabado cedo e o milho rende menos. Ele quer saber se vale trocar o milho por outra cultura.

O filtro climático, com o NASA POWER, já aprovou **sorgo**, **milho** e **milheto**, e descartou feijão (geada) e trigo (pouca chuva). Agora o aplicativo precisa da **nota de mercado** dessas três culturas.

### 13.3 Fluxo principal

| # | Quem | O que acontece | Chamada à API |
|---|---|---|---|
| 1 | Agricultor | Toca em **"Ver recomendação"** | — |
| 2 | Back-end | Recebe do filtro climático a lista: sorgo, milho, milheto | — |
| 3 | Back-end | Lê na ficha de cada cultura o código de mercado: `SORGHUM`, `MAIZE`, `MILLET` | — |
| 4 | Back-end | Verifica se já existe resultado em cache para essas culturas e esse país | — |
| 5 | Back-end | Sem cache: consulta a tabela de produção para o **sorgo** | `POST datastore_search` |
| 6 | Harvest Portal | Devolve `success: true` e as linhas de produção dos últimos anos | — |
| 7 | Back-end | Repete o passo 5 para **milho** e **milheto** | `POST datastore_search` (×2) |
| 8 | Back-end | Calcula tamanho, tendência de 10 anos e estabilidade de cada cultura e gera a nota de mercado | — |
| 9 | Back-end | Guarda o resultado em cache | — |
| 10 | Back-end | Combina com a nota de clima, usando os pesos do agricultor, e ordena | — |
| 11 | Agricultor | Vê o ranking com as duas notas, a fonte e o aviso para confirmar na cooperativa | — |

### 13.4 Chamadas reais do fluxo

**Passo 5 — produção de sorgo no país:**

```bash
curl -X POST "https://data.harvestportal.org/api/3/action/datastore_search" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "a1b2-c3d4",
       "filters": {"LOCATION": "BRA", "SUBJECT": "SORGHUM"},
       "fields": ["TIME", "Value"],
       "sort": "TIME desc",
       "limit": 15}'
```

**Passo 6 — resposta:**

```json
{
  "help": "https://data.harvestportal.org/api/3/action/help_show?name=datastore_search",
  "success": true,
  "result": {
    "resource_id": "a1b2-c3d4",
    "fields": [ {"id": "TIME", "type": "int"}, {"id": "Value", "type": "numeric"} ],
    "records": [
      {"TIME": 2024, "Value": 4100},
      {"TIME": 2023, "Value": 3900},
      {"TIME": 2015, "Value": 1500}
    ],
    "total": 10
  }
}
```

**Passo 8 — notas calculadas:**

| Cultura | Produção recente | Tendência em 10 anos | Nota de mercado |
|---|---|---|---|
| Milho | Muito grande | +30% | 4,5 |
| Sorgo | Pequena | Quase triplicou | 3,0 |
| Milheto | Muito pequena | Estável | 1,2 |

**Passo 10 — ranking com os pesos do agricultor (clima 4, mercado 3):**

| Posição | Cultura | Clima (NASA POWER) | Mercado (Harvest) | Nota final |
|---|---|---|---|---|
| 1º | Sorgo | 4,5 | 3,0 | 3,9 |
| 2º | Milho | 2,5 | 4,5 | 3,4 |
| 3º | Milheto | 4,8 | 1,2 | 3,3 |

**Passo 11 — o que o agricultor vê:**

> 📈 **Sorgo: melhor equilíbrio para você.** Aguenta melhor o fim de chuva em abril, e a produção dele no país quase triplicou em 10 anos.
> *Clima: NASA POWER, 1991–2025, grade de ~55 km. Mercado: OECD Crop Production via NASA Harvest Portal, dado nacional.*
> ⚠️ Confirme na sua cooperativa se há comprador de sorgo na sua região.

### 13.5 Fluxos alternativos

| Código | Situação | Onde ocorre | O que o sistema faz |
|---|---|---|---|
| **A1** | Resultado já está em cache | Passo 4 | Pula os passos 5 a 9 e vai direto ao passo 10 |
| **A2** | A cultura não tem linhas na tabela (`records` vazio) | Passo 6 | Marca a cultura como "mercado não verificado" e a ordena só pelo clima. **Nunca** usa nota zero |
| **A3** | A tabela não está na DataStore (`datastore_active=false`) | Preparo | A equipe baixa o arquivo pelo `url` do recurso e o back-end consulta a cópia local |
| **A4** | O agricultor muda os pesos em "Mudar prioridades" | Após o passo 11 | Recalcula só o passo 10, sem chamar a API |
| **A5** | O agricultor pergunta no chat sobre uma cultura fora da lista (ex.: gergelim) | Após o passo 11 | Segue o fluxo do assistente com MCP (ver `fluxo-aplicativo-power-harvest-mcp.md`) |

### 13.6 Fluxos de exceção

| Código | Situação | Sinal na resposta | O que o sistema faz |
|---|---|---|---|
| **E1** | `resource_id` mudou ou foi removido | `success: false`, `__type: "Not Found Error"` | Usa o cache antigo, se houver, e registra alerta para a equipe refazer o preparo |
| **E2** | Nome de coluna errado no `filters` | `success: false`, `__type: "Validation Error"` | Registra o erro; a cultura fica "mercado não verificado" |
| **E3** | Portal fora do ar ou lento | Timeout, HTTP 500 ou resposta não-JSON | Usa o cache; sem cache, mostra o ranking só pelo clima |
| **E4** | Dataset com licença restritiva | `license_id` não aberto (visto no preparo) | Não usa o dataset; procura outro |

### 13.7 Regras de negócio

| Código | Regra |
|---|---|
| **RN-01** | O mercado só é consultado para culturas **aprovadas** no filtro climático |
| **RN-02** | A nota de mercado é **nacional** e deve vir sempre acompanhada do aviso de confirmar na região |
| **RN-03** | Ausência de dado vira "mercado não verificado", nunca nota zero |
| **RN-04** | Toda nota exibida mostra a organização de origem do dado e o portal |
| **RN-05** | Chamadas à API são feitas só pelo **back-end**, nunca pelo navegador do agricultor |
| **RN-06** | A decisão final é do agricultor, com o técnico e a cooperativa |

### 13.8 Critérios de aceite (para testar o caso de uso)

| # | Dado que... | Quando... | Então... |
|---|---|---|---|
| 1 | Sorgo, milho e milheto foram aprovados | O agricultor toca em "Ver recomendação" | A tela mostra as três culturas com nota de clima, nota de mercado e fonte |
| 2 | A tabela não tem linhas de milheto | O back-end consulta o milheto | O milheto aparece com "mercado não verificado" e não com nota 0 |
| 3 | O resultado está em cache | O agricultor abre a recomendação de novo | Nenhuma chamada nova à API é feita |
| 4 | O Harvest Portal está fora do ar e não há cache | O agricultor toca em "Ver recomendação" | O ranking aparece só pelo clima, com aviso |
| 5 | O agricultor muda o peso do mercado de 3 para 5 | Ele salva as prioridades | O ranking muda sem nova chamada à API |

### 13.9 Código do caso de uso (esboço)

```python
import requests

BASE = "https://data.harvestportal.org/api/3/action"
TABELA = {"resource_id": "a1b2-c3d4", "pais": "LOCATION", "cultura": "SUBJECT",
          "ano": "TIME", "valor": "Value"}          # ⚠️ fictício: preencher no preparo
cache = {}

def serie_mercado(codigo, pais="BRA"):
    chave = (codigo, pais)
    if chave in cache:                                          # A1
        return cache[chave]
    corpo = {"resource_id": TABELA["resource_id"],
             "filters": {TABELA["pais"]: pais, TABELA["cultura"]: codigo},
             "fields": [TABELA["ano"], TABELA["valor"]],
             "sort": f'{TABELA["ano"]} desc', "limit": 15}
    try:
        data = requests.post(f"{BASE}/datastore_search", json=corpo, timeout=30).json()
    except Exception:
        return None                                             # E3
    if not data.get("success"):
        return None                                             # E1, E2
    registros = data["result"]["records"]
    serie = [(r[TABELA["ano"]], r[TABELA["valor"]]) for r in registros] or None   # A2
    cache[chave] = serie
    return serie

def nota_final(clima, mercado, peso_clima, peso_mercado):
    if mercado is None:                                         # RN-03
        return clima, "mercado não verificado"
    return (peso_clima * clima + peso_mercado * mercado) / (peso_clima + peso_mercado), None
```

---

## 14. Checklist de integração

| # | Item | Feito? |
|---|---|---|
| 1 | Todas as chamadas usam `/api/3/action/` (com versão) | ☐ |
| 2 | O código verifica `success` antes de ler `result` | ☐ |
| 3 | `datastore_search` com `filters` vai por **POST** com JSON | ☐ |
| 4 | Colunas descobertas com `limit=0` antes de filtrar | ☐ |
| 5 | Nenhum token no front-end ou no repositório | ☐ |
| 6 | Chamadas à API feitas pelo **back-end** (evita CORS) | ☐ |
| 7 | Resultados guardados em cache para a demo | ☐ |
| 8 | `license_id` conferido em cada dataset usado | ☐ |
| 9 | Organização de origem citada na tela ("OECD via NASA Harvest Portal") | ☐ |
| 10 | Tela mostra "mercado não verificado" quando não há dado | ☐ |

---

## 15. Referências

**Harvest Portal**
- Documentação da API (Swagger): https://data.harvestportal.org/api-docs
- Exemplos de uso (cURL, JavaScript, Python, Parquet): https://data.harvestportal.org/api-examples
- Especificação OpenAPI: https://data.harvestportal.org/openapi/harvest-portal-api.json
- Servidor MCP: https://data.harvestportal.org/mcp-docs

**CKAN**
- API Guide (estrutura seguida neste documento): https://docs.ckan.org/en/latest/api/index.html
- DataStore (parâmetros do `datastore_search` e exportação): https://docs.ckan.org/en/2.12/maintaining/datastore.html
- Cliente Python `ckanapi`: https://github.com/ckan/ckanapi

**Documentos do projeto**
- `NASA_HARVEST_PORTAL_API.md`: análise detalhada, conteúdo do portal e caso hipotético
- `NASA_POWER_X_HARVEST_PORTAL.md`: como o mercado se combina com o clima
- `fluxo-aplicativo-power-harvest-mcp.md`: quando usar API e quando usar MCP
- `ARQUITETURA-COMPLETA.md`: o sistema inteiro, passo a passo
