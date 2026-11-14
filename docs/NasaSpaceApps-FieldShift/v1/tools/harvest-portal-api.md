# Harvest Portal API (NASA Harvest): análise e documentação

## Foco: endpoints de leitura (`GET /api/3/action/...`)

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [A página Swagger "Harvest Portal API"](#2-a-página-swagger-harvest-portal-api)
3. [Arquitetura da API](#3-arquitetura-da-api)
4. [Endpoint principal: `package_search`](#4-endpoint-principal-package_search)
5. [Parâmetros de cada endpoint](#5-parâmetros-de-cada-endpoint)
6. [Estrutura da resposta](#6-estrutura-da-resposta)
7. [Download direto de arquivos](#7-download-direto-de-arquivos)
8. [Fluxo de uso: do catálogo ao dado](#8-fluxo-de-uso-do-catálogo-ao-dado)
9. [O que existe hoje no portal](#9-o-que-existe-hoje-no-portal)
10. [Como testar a API](#10-como-testar-a-api)
11. [Códigos de erro](#11-códigos-de-erro)
12. [Limitações](#12-limitações)
13. [Boas práticas](#13-boas-práticas)
14. [Datasets potencialmente úteis para o Field Shift](#14-datasets-potencialmente-úteis-para-o-field-shift)
15. [Como e por que usar o Harvest Portal no Field Shift](#15-como-e-por-que-usar-o-harvest-portal-no-field-shift)
16. [Caso hipotético: a história do Seu Joãozinho](#16-caso-hipotético-a-história-do-seu-joãozinho)
17. [Referências](#17-referências)

---

## Nível de verificação

- As informações vêm das páginas oficiais do portal (`/api-docs`, `/api-examples`, listas de datasets, organizações e grupos), da captura de tela da página Swagger enviada pela equipe e da documentação oficial do **CKAN**, a plataforma em que o portal roda.
- **A especificação `openapi/harvest-portal-api.json` não pôde ser lida diretamente**: o acesso automatizado a esse arquivo foi bloqueado. A lista de endpoints vem da captura de tela. Os parâmetros de cada endpoint vêm da documentação do CKAN.
- **Nenhuma requisição foi executada ao vivo** neste documento, pelo mesmo motivo. A seção [10](#10-como-testar-a-api) mostra como testar em menos de um minuto.
- Itens marcados com ⚠️ são padrão do CKAN, mas a especificação "curada" do Harvest pode não expor todos. Confirme abrindo o endpoint na Swagger.
- **O Harvest Portal não está na lista oficial de recursos do desafio Field Shift.** Ele entra como referência de metodologia e fonte complementar, não como dataset obrigatório.

---

## 1. Visão geral

O **NASA Harvest** é o programa de segurança alimentar e agricultura da NASA, um consórcio liderado pela Universidade de Maryland. O **Harvest Portal** é o repositório de dados desse programa: reúne datasets dos parceiros do Harvest e dados públicos de outras instituições sobre produção agrícola, condição das lavouras, clima, mercado e segurança alimentar.

A **Harvest Portal API** é a interface de programação desse catálogo. Ela responde perguntas como "quais datasets existem sobre X?", "quem publicou?", "quais arquivos esse dataset tem?" e, para tabelas carregadas no banco do portal, "quais linhas atendem a este filtro?".

| Item | Valor |
|---|---|
| Plataforma | CKAN (software livre de catálogo de dados), Action API versão 3 |
| Versão da especificação | 3.0.0 (OpenAPI 3.0), segundo a página Swagger |
| Base URL | `https://data.harvestportal.org/api/3/action/` |
| Tipo de operação documentada | **Somente leitura** (busca e consulta) |
| Autenticação | **Nenhuma** para dados públicos. Token opcional para datasets privados |
| Conteúdo | 86 datasets, 16 organizações, 6 grupos temáticos (contagem lida em 14/11/2026) |
| Cobertura | Global, mas concentrada em mercado, comércio e segurança alimentar |
| Formatos mais comuns | CSV, XLSX, ZIP, SHP, GeoJSON, GeoTIFF, Parquet |
| Licenças | Variam por dataset. Muitos estão como "License not specified" |

**Diferença importante em relação ao NASA POWER:** o POWER entrega **o dado em si** (temperatura de um ponto, por exemplo). A Harvest Portal API entrega principalmente **o catálogo**: metadados e links. O dado de verdade vem do download do arquivo ou, em tabelas, da DataStore.

---

## 2. A página Swagger "Harvest Portal API"

A página de documentação da API é uma interface **Swagger UI**, a mesma ferramenta usada pelo NASA POWER. Ela lê a especificação OpenAPI (`/openapi/harvest-portal-api.json`) e mostra cada endpoint com seus parâmetros e um botão para testar.

O texto do topo da página diz, em resumo, que ela documenta um **subconjunto curado** da Action API do CKAN, apenas com operações públicas de leitura. Criação, edição e exclusão de datasets e ações de conta e administração foram deixadas de fora de propósito.

Os endpoints aparecem em seis grupos:

| Grupo | Endpoint | O que faz |
|---|---|---|
| **Datasets** | `GET /package_search` | Busca datasets |
| | `GET /package_show` | Mostra um dataset completo |
| **Resources** | `GET /resource_show` | Mostra um arquivo (recurso) de um dataset |
| **Organizations** | `GET /organization_list` | Lista as organizações que publicam dados |
| | `GET /organization_show` | Mostra uma organização |
| **Groups** | `GET /group_list` | Lista os grupos temáticos |
| | `GET /group_show` | Mostra um grupo |
| **Tags** | `GET /tag_list` | Lista as palavras-chave usadas nos datasets |
| **DataStore** | `GET /datastore_search` | Consulta linhas de uma tabela carregada no banco do portal |

### 2.1 Vocabulário do CKAN

Os nomes dos endpoints usam termos do CKAN. A tradução:

| Termo do CKAN | Significado | Exemplo |
|---|---|---|
| **package** | Um **dataset**: o conjunto de metadados mais um ou mais arquivos | "FAO / NASA Harvest Public Yield Datasets" |
| **resource** | Um **arquivo ou link** dentro do dataset | O `.shp` ou o `.csv` desse dataset |
| **organization** | Quem **publicou** o dataset. Cada dataset pertence a uma só | "NASA Harvest", "FAO", "World Bank" |
| **group** | Uma **coleção temática**. Um dataset pode estar em vários | "Supply Chain" |
| **tag** | **Palavra-chave** livre | `cropland`, `food security` |
| **DataStore** | Banco de dados interno onde planilhas viram **tabelas consultáveis** | Um CSV carregado que aceita filtros por coluna |

### 2.2 Qual endpoint usar no Field Shift

| Necessidade | Endpoint |
|---|---|
| Achar datasets por tema ("yield", "crop", "cropland") | `package_search` |
| Ver os arquivos de um dataset e seus links de download | `package_show` |
| Saber se um arquivo é consultável por filtro | `resource_show` (campo `datastore_active`) |
| Ver só o que a NASA Harvest publicou | `organization_show` ou `package_search` com `fq=organization:...` |
| Explorar temas disponíveis | `group_list`, `tag_list` |
| Puxar só algumas linhas de uma tabela grande | `datastore_search` |
| Baixar o arquivo inteiro (TIFF, SHP, ZIP, Parquet) | URL de download (seção [7](#7-download-direto-de-arquivos)) |

---

## 3. Arquitetura da API

- **Estilo RPC sobre HTTP**: cada endpoint é uma "ação" do CKAN, chamada em `/api/3/action/<nome_da_ação>`. O número `3` é a versão da Action API. A documentação do CKAN recomenda sempre incluí-lo.
- **GET ou POST**: as ações de leitura aceitam GET, com os parâmetros na URL (`?q=maize&rows=5`). Também aceitam POST com um corpo JSON. A página Swagger do Harvest documenta todas como GET. A página de exemplos do portal usa POST no `datastore_search`.
- **Listas na URL**: parâmetros do tipo lista podem ser enviados em formato JSON (`facet.field=["tags"]`) ou repetindo o parâmetro.
- **Resposta sempre em JSON**, dentro de um "envelope" padrão (seção [6](#6-estrutura-da-resposta)).
- **Sucesso não é só o código HTTP**: o CKAN tenta devolver `200` mesmo quando algo dá errado. **Sempre verifique o campo `success`** (seção [11](#11-códigos-de-erro)).

### 3.1 Autenticação

| Situação | O que fazer |
|---|---|
| Datasets públicos (o caso do Field Shift) | Nada. Chame a URL direto |
| Datasets privados de uma organização da qual você é membro | Crie um token em **Manage → API Tokens** no seu perfil e envie no cabeçalho `Authorization: <token>` |

O token dá acesso como se fosse você. **Nunca coloque o token no código do front-end nem no repositório.**

### 3.2 Especificação OpenAPI

```
https://data.harvestportal.org/openapi/harvest-portal-api.json
```

Esse arquivo pode ser importado no Postman, Insomnia ou em geradores de cliente (`openapi-generator`).

---

## 4. Endpoint principal: `package_search`

```
GET https://data.harvestportal.org/api/3/action/package_search
```

**O que faz:** busca datasets no catálogo. Devolve a contagem total, a lista de datasets encontrados (com metadados e arquivos) e, se pedido, as **facetas**, ou seja, contagens por organização, grupo, tag ou formato.

**Por que é o principal:** é a porta de entrada. Quase todo fluxo começa aqui para descobrir o `id` do dataset que interessa.

### Exemplo mínimo

```
https://data.harvestportal.org/api/3/action/package_search?q=maize&rows=5
```

### Exemplos para o Field Shift

Datasets sobre produtividade:
```
https://data.harvestportal.org/api/3/action/package_search?q=yield&rows=20
```

Só datasets publicados pela organização NASA Harvest (⚠️ confirme o nome curto da organização com `organization_list`):
```
https://data.harvestportal.org/api/3/action/package_search?fq=organization:nasa-harvest&rows=50
```

Quantos datasets existem por formato, sem trazer os datasets:
```
https://data.harvestportal.org/api/3/action/package_search?rows=0&facet.field=["res_format"]&facet.limit=-1
```

---

## 5. Parâmetros de cada endpoint

Na URL, cada parâmetro aparece como `nome=valor`, separados por `&`, depois do `?`. A ordem não importa.

```
.../package_search?q=yield&rows=20&start=0
```

### 5.1 `package_search`: buscar datasets

| Parâmetro | Obrigatório | Tipo | Padrão | Descrição |
|---|---|---|---|---|
| `q` | Não | Texto (sintaxe Solr) | Tudo (`*:*`) | Termo de busca livre |
| `fq` | Não | Texto (sintaxe Solr) | Nenhum | Filtro por campo (organização, tag, formato...) |
| `fq_list` | Não ⚠️ | Lista de textos | Nenhum | Vários filtros extras |
| `sort` | Não | Texto | `score desc, metadata_modified desc` | Ordenação |
| `rows` | Não | Inteiro | 10 | Quantos datasets devolver. Limite máximo: 1000 |
| `start` | Não | Inteiro | 0 | Posição inicial, para paginação |
| `facet` | Não | `true`/`false` | `true` | Liga ou desliga as facetas |
| `facet.field` | Não | Lista de campos | Vazia | Campos para contar (ex.: `["organization","tags","res_format"]`) |
| `facet.limit` | Não | Inteiro | 50 | Máximo de valores por faceta. `-1` = sem limite |
| `facet.mincount` | Não | Inteiro | Nenhum | Contagem mínima para a faceta aparecer |
| `include_private` | Não ⚠️ | `true`/`false` | `false` | Inclui datasets privados. Só funciona com token |
| `include_drafts` | Não ⚠️ | `true`/`false` | `false` | Inclui rascunhos. Só funciona com token |

#### `q`: o que procurar

**O que é:** o texto da busca. Procura no título, na descrição, nas tags e em outros campos indexados.

**Como escrever:**
- Uma palavra: `q=yield`
- Várias palavras (todas precisam aparecer): `q=crop+type`
- Frase exata: `q="crop type"` (na URL, `q=%22crop%20type%22`)
- Em um campo específico: `q=tags:cropland`

**Erro comum:** colocar acentos ou termos em português. O catálogo está em inglês: use `yield`, não `produtividade`.

#### `fq`: filtrar sem mudar a relevância

**O que é:** um filtro. Diferente do `q`, ele não influencia a ordem por relevância. Só **corta** o que não atende à condição.

**Filtros úteis:**

| Filtro | O que retorna |
|---|---|
| `fq=organization:nasa-harvest` | Só datasets dessa organização (use o nome curto, não o título) |
| `fq=tags:cropland` | Só datasets com essa tag |
| `fq=res_format:GeoTIFF` | Só datasets com algum arquivo GeoTIFF |
| `fq=groups:supply-chain` | Só datasets desse grupo (⚠️ confirme o nome curto com `group_list`) |
| `fq=license_id:cc-by` | Só datasets com licença CC BY |

Combine com `AND`: `fq=organization:nasa-harvest AND res_format:CSV`.

#### `sort`: ordem dos resultados

**Exemplos:**
- `sort=metadata_modified desc`: os atualizados mais recentemente primeiro
- `sort=title_string asc`: ordem alfabética pelo título
- `sort=score desc`: mais relevantes primeiro (padrão, quando há `q`)

#### `rows` e `start`: paginação

**O que são:** `rows` é o tamanho da página e `start` é onde ela começa.

- Página 1: `rows=20&start=0`
- Página 2: `rows=20&start=20`
- Página 3: `rows=20&start=40`

**Regras:**
- `rows` máximo de **1000** por chamada (padrão do CKAN; o site pode configurar outro valor).
- Com 86 datasets no portal, `rows=100` traz o catálogo inteiro em uma chamada.
- `rows=0` não traz datasets, só a contagem e as facetas. É o jeito mais leve de explorar o catálogo.

#### `facet.field`, `facet.limit`, `facet.mincount`: contagens

**O que são:** pedem ao portal que conte quantos datasets existem para cada valor de um campo.

**Exemplo:** `facet.field=["organization","tags"]&facet.limit=10&rows=0` devolve as 10 organizações e as 10 tags mais frequentes, sem nenhum dataset.

**Uso no projeto:** descobrir rapidamente se existe algo de "yield", "cropland" ou "crop type" antes de gastar tempo.

---

### 5.2 `package_show`: ver um dataset completo

| Parâmetro | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `id` | **Sim** | Texto | O `id` (UUID) ou o `name` (nome curto da URL) do dataset |
| `use_default_schema` | Não ⚠️ | `true`/`false` | Usa o esquema padrão do CKAN em vez de um personalizado. Padrão `false` |

#### `id`

**O que é:** o identificador do dataset. Aceita duas formas:
- **UUID**: `3f2a9c1e-5b7d-...` (vem do campo `id` do `package_search`)
- **Nome curto (slug)**: o final da URL da página do dataset. Exemplo: em `data.harvestportal.org/dataset/iowa-in-season-crop-type-map-2020`, o nome é `iowa-in-season-crop-type-map-2020`.

**Exemplo:**
```
https://data.harvestportal.org/api/3/action/package_show?id=iowa-in-season-crop-type-map-2020
```

**O que você recebe:** título, descrição, organização, tags, licença, datas e, principalmente, a lista `resources`, com o link (`url`) e o formato de cada arquivo.

---

### 5.3 `resource_show`: ver um arquivo

| Parâmetro | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `id` | **Sim** | Texto (UUID) | O `id` do recurso, vindo da lista `resources` do `package_show` |

**Campo mais importante da resposta:** `datastore_active`.
- `true`: o arquivo foi carregado na DataStore e aceita consulta por linhas com `datastore_search`.
- `false`: só dá para baixar o arquivo inteiro (seção [7](#7-download-direto-de-arquivos)).

Outros campos úteis: `format`, `url`, `size`, `mimetype`, `last_modified`, `package_id`.

---

### 5.4 `organization_list` e `group_list`: listar quem publica e os temas

Os dois endpoints têm os mesmos parâmetros.

| Parâmetro | Obrigatório | Tipo | Padrão | Descrição |
|---|---|---|---|---|
| `all_fields` | Não | `true`/`false` | `false` | `false` devolve só os nomes curtos. `true` devolve o objeto completo (título, descrição, contagem de datasets) |
| `sort` | Não ⚠️ | Texto | `title asc` | Ordenação. Campos aceitos: `name`, `package_count`, `title` |
| `limit` | Não ⚠️ | Inteiro | 1000 sem `all_fields`; 25 com `all_fields` | Máximo de itens por página |
| `offset` | Não ⚠️ | Inteiro | 0 | Posição inicial (só com `limit`) |
| `organizations` / `groups` | Não ⚠️ | Lista de nomes | Todos | Restringe a lista a esses nomes |
| `include_dataset_count` | Não ⚠️ | `true`/`false` | `true` | Com `all_fields`, inclui a contagem de datasets |
| `include_extras`, `include_tags`, `include_groups`, `include_users` | Não ⚠️ | `true`/`false` | `false` | Com `all_fields`, inclui informações extras |

**Exemplo:** todas as organizações com contagem de datasets:
```
https://data.harvestportal.org/api/3/action/organization_list?all_fields=true&sort=package_count%20desc
```

**Uso no projeto:** descobrir o **nome curto** de cada organização e grupo, que é o que vai nos filtros `fq`.

---

### 5.5 `organization_show` e `group_show`: ver uma organização ou um grupo

| Parâmetro | Obrigatório | Tipo | Padrão | Descrição |
|---|---|---|---|---|
| `id` | **Sim** | Texto | — | UUID ou nome curto da organização ou do grupo |
| `include_datasets` | Não | `true`/`false` | `false` | Inclui a lista de datasets (até 1000) |
| `include_dataset_count` | Não ⚠️ | `true`/`false` | `true` | Inclui a contagem |
| `include_extras`, `include_users`, `include_groups`, `include_tags`, `include_followers` | Não ⚠️ | `true`/`false` | Variam | Detalhes extras, pouco úteis para o projeto |

**Exemplo:**
```
https://data.harvestportal.org/api/3/action/organization_show?id=nasa-harvest&include_datasets=true
```
⚠️ Confirme o nome curto com `organization_list`.

---

### 5.6 `tag_list`: listar palavras-chave

| Parâmetro | Obrigatório | Tipo | Padrão | Descrição |
|---|---|---|---|---|
| `query` | Não | Texto | Nenhum | Devolve só tags que contêm esse texto |
| `vocabulary_id` | Não ⚠️ | Texto | Nenhum | Restringe a um vocabulário controlado de tags |
| `all_fields` | Não ⚠️ | `true`/`false` | `false` | `true` devolve objetos completos em vez de só os nomes |

**Exemplo:**
```
https://data.harvestportal.org/api/3/action/tag_list?query=crop
```

**Dica:** para saber **quantos** datasets usam cada tag, use `package_search?rows=0&facet.field=["tags"]`. O `tag_list` só lista os nomes.

---

### 5.7 `datastore_search`: consultar linhas de uma tabela

```
GET  https://data.harvestportal.org/api/3/action/datastore_search?resource_id=...
POST https://data.harvestportal.org/api/3/action/datastore_search   (corpo JSON)
```

Só funciona para recursos com `datastore_active = true`.

| Parâmetro | Obrigatório | Tipo | Padrão | Descrição |
|---|---|---|---|---|
| `resource_id` | **Sim** | Texto | — | `id` do recurso (arquivo) a consultar |
| `filters` | Não | Dicionário JSON | Nenhum | Filtro de **igualdade exata** por coluna. Ex.: `{"country":"Brazil"}` |
| `q` | Não | Texto ou dicionário | Nenhum | Busca de texto livre em todas as colunas, ou em colunas específicas |
| `limit` | Não | Inteiro | **100** | Linhas por chamada. Máximo **32 000** |
| `offset` | Não | Inteiro | 0 | Quantas linhas pular (paginação) |
| `fields` | Não | Lista ou texto com vírgulas | Todas | Colunas a devolver |
| `sort` | Não | Texto | Nenhum | Ex.: `year desc, country asc` |
| `distinct` | Não | `true`/`false` | `false` | Só linhas distintas |
| `include_total` | Não | `true`/`false` | `true` | Inclui o total de linhas que atendem ao filtro |
| `records_format` | Não | `objects`, `lists`, `csv`, `tsv` | `objects` | Formato das linhas na resposta |
| `plain`, `language` | Não | — | `true`, `english` | Ajustes da busca de texto livre |
| `include_next_page` | Não ⚠️ | `true`/`false` | `false` | Devolve o filtro da próxima página. Só funciona ordenando por `_id` |

#### `filters` × `q`

| | `filters` | `q` |
|---|---|---|
| Tipo de busca | Igualdade exata | Texto livre, com ranking |
| Exemplo | `{"crop":"Soybeans"}` | `"soy"` |
| Use quando | Você sabe o valor exato da coluna | Você está explorando |

#### Primeiro passo recomendado: descobrir as colunas

Chame com `limit=0`. A resposta traz só a lista `fields` (nome e tipo de cada coluna), sem nenhuma linha:
```
https://data.harvestportal.org/api/3/action/datastore_search?resource_id=RESOURCE_ID&limit=0
```

Assim você sabe os nomes exatos antes de montar o `filters` e evita erro 400 por coluna inexistente.

#### Exemplo POST (o formato usado na página de exemplos do portal)

```bash
curl -X POST "https://data.harvestportal.org/api/3/action/datastore_search" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "RESOURCE_ID", "filters": {"country": "Brazil"}, "limit": 50}'
```

---

### Resumo: o que é obrigatório

| Endpoint | Parâmetro obrigatório | Parâmetros mais usados no Field Shift |
|---|---|---|
| `package_search` | Nenhum | `q`, `fq`, `rows`, `facet.field` |
| `package_show` | `id` | — |
| `resource_show` | `id` | — |
| `organization_list` | Nenhum | `all_fields=true` |
| `organization_show` | `id` | `include_datasets=true` |
| `group_list` | Nenhum | `all_fields=true` |
| `group_show` | `id` | `include_datasets=true` |
| `tag_list` | Nenhum | `query` |
| `datastore_search` | `resource_id` | `filters`, `fields`, `limit` |

---

## 6. Estrutura da resposta

Toda resposta da API vem num "envelope" JSON com três campos:

```json
{
  "help": "https://data.harvestportal.org/api/3/action/help_show?name=package_search",
  "success": true,
  "result": { ... }
}
```

| Campo | Significado |
|---|---|
| `success` | `true` ou `false`. **É aqui que você confirma se deu certo** |
| `result` | O conteúdo pedido (só aparece em caso de sucesso) |
| `help` | Link para a documentação da ação |
| `error` | Só em caso de falha, no lugar de `result`. Tem `__type` (tipo do erro) e `message` |

### 6.1 Resposta do `package_search`

```json
{
  "success": true,
  "result": {
    "count": 86,
    "results": [
      {
        "id": "uuid-do-dataset",
        "name": "iowa-in-season-crop-type-map-2020",
        "title": "Iowa In-Season Crop Type Map (2020)",
        "notes": "Descrição do dataset...",
        "organization": { "name": "nasa-harvest", "title": "NASA Harvest" },
        "tags": [ { "name": "cropland" } ],
        "license_id": "cc-by",
        "metadata_modified": "2024-01-01T00:00:00",
        "num_resources": 1,
        "resources": [
          {
            "id": "uuid-do-recurso",
            "name": "crop_type_map.tif",
            "format": "GeoTIFF",
            "url": "https://data.harvestportal.org/dataset/.../download/crop_type_map.tif",
            "datastore_active": false
          }
        ]
      }
    ],
    "facets": { },
    "search_facets": { }
  }
}
```

> Os valores acima são ilustrativos. Os campos exatos podem variar com a versão do CKAN e com extensões instaladas no portal.

**Pontos importantes:**
- `count` é o total encontrado, não o número de itens devolvidos nesta página.
- `name` é o nome curto, usado em URLs e no `package_show`.
- `organization.name` é o valor que vai no filtro `fq=organization:...`.
- `resources[].url` é o link de download de cada arquivo.
- `license_id` diz se você pode reutilizar o dado. Vários datasets do portal **não informam licença**.

### 6.2 Resposta do `datastore_search`

```json
{
  "success": true,
  "result": {
    "resource_id": "uuid-do-recurso",
    "fields": [
      { "id": "_id", "type": "int" },
      { "id": "country", "type": "text" },
      { "id": "year", "type": "int" },
      { "id": "yield", "type": "numeric" }
    ],
    "records": [
      { "_id": 1, "country": "Brazil", "year": 2020, "yield": 3.4 }
    ],
    "total": 1,
    "total_was_estimated": false,
    "limit": 100,
    "offset": 0,
    "_links": { "start": "...", "next": "..." }
  }
}
```

> Colunas e valores ilustrativos.

- `fields` lista as colunas e seus tipos. O CKAN cria sempre a coluna `_id`.
- `records` são as linhas.
- `total` é o número de linhas que atendem ao filtro, independentemente do `limit`.
- `_links.next` é a URL da próxima página.

### 6.3 Lendo em Python

```python
import requests, pandas as pd

BASE = "https://data.harvestportal.org/api/3/action"

def ckan(action, **params):
    r = requests.get(f"{BASE}/{action}", params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(data.get("error"))
    return data["result"]

# 1. Buscar datasets
res = ckan("package_search", q="yield", rows=20)
print(res["count"], "datasets")
for d in res["results"]:
    print(d["name"], "|", d["organization"]["title"] if d.get("organization") else "-")

# 2. Ver os arquivos de um dataset
ds = ckan("package_show", id=res["results"][0]["name"])
for r in ds["resources"]:
    print(r["format"], r["datastore_active"], r["url"])

# 3. Consultar uma tabela (se datastore_active for True)
# tab = ckan("datastore_search", resource_id="RESOURCE_ID", limit=1000)
# df = pd.DataFrame(tab["records"])
```

Também é possível usar o cliente oficial do CKAN em Python, o `ckanapi`:

```python
from ckanapi import RemoteCKAN
portal = RemoteCKAN("https://data.harvestportal.org", user_agent="fieldshift")
res = portal.action.package_search(q="yield", rows=20)
```

---

## 7. Download direto de arquivos

A maior parte dos dados úteis (mapas GeoTIFF, shapefiles, ZIPs, Parquet) **não está na DataStore**. Eles são baixados pelo link do recurso:

```
GET https://data.harvestportal.org/dataset/DATASET_ID/resource/RESOURCE_ID/download/FILENAME
```

| Parte | De onde vem |
|---|---|
| `DATASET_ID` | `id` ou `name` do dataset |
| `RESOURCE_ID` | `id` do recurso |
| `FILENAME` | Nome do arquivo |

**Na prática, não monte essa URL à mão:** use o campo `url` que vem em `resources[]` no `package_show`.

**Arquivos Parquet:** a página de exemplos do portal mostra a leitura direta de Parquet no navegador com a biblioteca JavaScript `hyparquet`. Em Python, use `pandas.read_parquet(url)`.

### 7.1 Exportar uma tabela da DataStore inteira ⚠️

Para recursos com `datastore_active = true`, o CKAN oferece uma URL de exportação completa:

```
https://data.harvestportal.org/datastore/dump/RESOURCE_ID              (CSV)
https://data.harvestportal.org/datastore/dump/RESOURCE_ID?format=json
https://data.harvestportal.org/datastore/dump/RESOURCE_ID?format=tsv
https://data.harvestportal.org/datastore/dump/RESOURCE_ID?bom=true     (CSV que abre certo no Excel)
```

⚠️ Recurso padrão do CKAN, não documentado na Swagger do Harvest. Teste antes de depender dele.

---

## 8. Fluxo de uso: do catálogo ao dado

```
package_search  ──►  package_show  ──►  resource_show  ──┬──►  datastore_search   (tabela, por filtro)
 (achar o dataset)    (ver arquivos)    (datastore_active?)  │
                                                             └──►  download direto   (arquivo inteiro)
```

| Passo | Pergunta | Endpoint | O que guardar |
|---|---|---|---|
| 1 | Existe algo sobre o tema? | `package_search?q=...` | `name` do dataset |
| 2 | Quais arquivos ele tem? | `package_show?id=...` | `resources[].id`, `format`, `url` |
| 3 | Dá para consultar por linhas? | `resource_show?id=...` | `datastore_active` |
| 4a | Sim: quais colunas? | `datastore_search?limit=0` | `fields` |
| 4b | Sim: puxar as linhas | `datastore_search` com `filters` | `records` |
| 4c | Não: baixar | URL em `resources[].url` | O arquivo |

---

## 9. O que existe hoje no portal

> Contagens lidas nas páginas do portal em 14/11/2026. Elas mudam com o tempo; use `package_search?rows=0&facet.field=[...]` para a contagem atual.

### 9.1 Números gerais

| Item | Quantidade |
|---|---|
| Datasets | 86 |
| Organizações | 16 |
| Grupos temáticos | 6 |

### 9.2 Organizações com mais datasets

| Organização | Datasets |
|---|---|
| External Sources | 25 |
| NASA Harvest | 13 |
| Food and Agriculture Organization of the UN (FAO) | 11 |
| OECD | 9 |
| International Monetary Fund | 7 |
| World Bank | 6 |
| FEWS NET | 4 |
| Harvest Ukraine Work | 4 |
| World Food Programme | 3 |
| IFPRI | 2 |
| Crop Monitor | 1 |
| NASA Harvest Yield Intercomparison | 1 |

Quatro organizações aparecem com **zero datasets públicos**: ADAPT, LAI4EO Consortium, Logistics Cluster e **NASA Harvest Crop Type Maps** (descrita como armazenamento privado de mapas de tipo de cultura).

### 9.3 Grupos temáticos

| Grupo | Datasets | Observação |
|---|---|---|
| Supply Chain | 47 | Cadeia de suprimentos, preços, comércio |
| NASA Harvest Encyclopedia | 1 | |
| NASA Harvest Crop Production Statistics | **0** | Produção agrícola para treinar e validar modelos de produtividade |
| Pest & Disease Data | **0** | |
| OECD_IGC_Ports | 0 | |
| Yield Group 1 | 0 | "Grupo temporário para teste" |

### 9.4 Formatos e tags mais frequentes

| Formato | Datasets | | Tag | Datasets |
|---|---|---|---|---|
| CSV | 42 | | supply | 22 |
| XLSX | 10 | | agriculture | 21 |
| ZIP | 8 | | demand | 15 |
| SHP | 6 | | market price | 12 |
| GeoJSON | 4 | | covid | 8 |
| tif | 2 | | food security | 7 |
| | | | cropland | 5 |

### 9.5 Leitura crítica

- **O catálogo é forte em mercado, comércio e segurança alimentar** (FAO, OECD, IMF, World Bank, WFP) e **fraco em dados de campo**. Os grupos de produção agrícola e de pragas estão vazios.
- **Há poucos dados geoespaciais**: só 6 datasets com SHP, 4 com GeoJSON e 2 com TIFF.
- **Não foi encontrado nenhum dataset que cite o Brasil ou a América do Sul** nas listas lidas. Datasets globais (FAOSTAT, WFP, GIEWS) podem incluir o Brasil sem dizer isso no título.
- **40 datasets estão sem licença informada.** Antes de usar no projeto, confira o `license_id`.

---

## 10. Como testar a API

### 10.1 Pelo navegador (mais simples)

Cole na barra de endereços:
```
https://data.harvestportal.org/api/3/action/package_search?q=maize&rows=5
```
O navegador mostra o JSON. No Firefox, a visualização já vem formatada.

### 10.2 Pela página Swagger (interface oficial)

1. Abra `https://data.harvestportal.org/api-docs`.
2. Clique em um endpoint, por exemplo `GET /package_search`.
3. Clique em **Try it out**.
4. Preencha os parâmetros (ex.: `q = yield`, `rows = 5`).
5. Clique em **Execute**.
6. A página mostra:
   - **Request URL**: a URL pronta, para copiar para o seu código.
   - **Curl**: o comando equivalente no terminal.
   - **Server response**: código HTTP e corpo da resposta.

### 10.3 Pelo terminal (curl)

```bash
curl -s "https://data.harvestportal.org/api/3/action/package_search?q=yield&rows=5"
curl -s "https://data.harvestportal.org/api/3/action/organization_list?all_fields=true"
```

### 10.4 Roteiro de testes sugerido

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | `package_search?rows=0` | `success: true` e `count` com o total do catálogo |
| 2 | `package_search?q=yield&rows=5` | Até 5 datasets |
| 3 | `package_search?q=xyzxyz` | `success: true` e `count: 0` |
| 4 | `package_show` sem `id` | `success: false`, erro de validação |
| 5 | `package_show?id=nao-existe` | `success: false`, erro "Not Found" |
| 6 | `organization_list?all_fields=true` | Lista com `name`, `title` e `package_count` |
| 7 | `package_search?fq=organization:<nome>` | Só datasets dessa organização |
| 8 | `package_search?rows=0&facet.field=["res_format"]` | Contagem de formatos em `search_facets` |
| 9 | `resource_show` em um recurso CSV | Campo `datastore_active` presente |
| 10 | `datastore_search` com `limit=0` | Lista `fields`, nenhuma linha |
| 11 | `datastore_search` em recurso com `datastore_active=false` | `success: false` |
| 12 | `package_search?rows=2000` | Devolve no máximo 1000 (ou erro, conforme a configuração) |

### 10.5 Teste automatizado em Python

```python
import requests

BASE = "https://data.harvestportal.org/api/3/action"

def test(nome, action, **params):
    r = requests.get(f"{BASE}/{action}", params=params, timeout=60)
    try:
        ok = r.json().get("success")
    except ValueError:
        ok = "não-JSON"
    print(f"{nome:<35} HTTP {r.status_code}  success={ok}")

test("catálogo (só contagem)", "package_search", rows=0)
test("busca yield", "package_search", q="yield", rows=5)
test("show sem id", "package_show")
test("show inexistente", "package_show", id="nao-existe-123")
test("organizações", "organization_list", all_fields="true")
test("tags com crop", "tag_list", query="crop")
```

---

## 11. Códigos de erro

O CKAN tenta responder **`200 OK` mesmo quando a ação falha**. Por isso, o primeiro teste no código deve ser o campo `success`, não o código HTTP.

Exemplo de falha:
```json
{
  "help": "...",
  "success": false,
  "error": { "__type": "Not Found Error", "message": "Not found" }
}
```

| Situação | HTTP comum | `error.__type` | Ação |
|---|---|---|---|
| Sucesso | 200 | — | — |
| Parâmetro obrigatório ausente ou inválido | 400 ou 409 | `Validation Error` | Leia `error`: ele lista o campo com problema |
| Dataset, recurso ou organização não existe | 404 | `Not Found Error` | Confira o `id` ou o `name` |
| Dataset privado sem token | 403 | `Authorization Error` | Use token ou escolha outro dataset |
| Coluna inexistente no `filters` do `datastore_search` | 400 / 409 | `Validation Error` | Chame antes com `limit=0` para ver as colunas |
| Erro no servidor | 500 | — | Tente mais tarde |
| Excesso de requisições | 429 ⚠️ | — | Espere e tente de novo com intervalo crescente |

⚠️ A documentação do Harvest não publica limite de taxa. O 429 é uma resposta genérica de servidores web; trate por precaução.

---

## 12. Limitações

### 12.1 Limites técnicos

| Limite | Valor |
|---|---|
| `package_search` | Máximo de **1000** datasets por chamada (padrão do CKAN) |
| `datastore_search` | Padrão de **100** linhas; máximo de **32 000** por chamada |
| `organization_list` / `group_list` | 1000 nomes, ou 25 objetos completos com `all_fields=true` |
| Operações documentadas | Só leitura |
| Datasets privados | Exigem token |
| Taxa de requisições | Não publicada |
| Especificação | Subconjunto "curado": parâmetros avançados do CKAN podem não estar documentados ⚠️ |

### 12.2 Limitações de conteúdo (importantes para o projeto)

1. **Não é uma fonte de observação de satélite.** O portal cataloga produtos derivados (mapas de cultura, estatísticas, preços), não entrega NDVI, umidade do solo ou temperatura como o POWER, o SMAP ou o MODIS.
2. **Pouco dado de campo e quase nada do Brasil.** Os grupos de produção agrícola e de pragas estão vazios, e nenhum dataset listado cita o Brasil.
3. **Pouco dado geoespacial.** A maioria é CSV ou XLSX de estatística por país.
4. **Datasets antigos ou fora do tema.** Há vários datasets de COVID-19 e índices econômicos que não servem para rotação de culturas.
5. **Licenças incompletas.** Quase metade dos datasets não informa licença.
6. **Os mapas de tipo de cultura são privados.** A organização "NASA Harvest Crop Type Maps" aparece com zero datasets públicos.
7. **Não está na lista oficial do desafio.** Usar como fonte principal pode contar menos na avaliação do que os datasets listados pela NASA no desafio.

### 12.3 Limitações operacionais

- A especificação `harvest-portal-api.json` e algumas páginas bloqueiam leitura automatizada por robôs. O uso normal da API por código não foi afetado nos exemplos oficiais.
- A busca pela **interface web** (`/dataset/?q=...`) pode devolver resultados diferentes da busca pela API. Confie na API.

---

## 13. Boas práticas

1. **Verifique sempre `success`** antes de ler `result`.
2. **Use `rows=0` com facetas** para explorar o catálogo sem baixar nada.
3. **Use o `name` do dataset**, não o título, para chamar `package_show`. O `name` é estável e aparece na URL.
4. **Antes de filtrar a DataStore, chame `limit=0`** para ver os nomes das colunas.
5. **Pagine** com `rows`/`start` (catálogo) ou `limit`/`offset` (DataStore). Em tabelas grandes, prefira paginação por `_id`.
6. **Faça cache local.** O catálogo muda pouco; baixe uma vez e reutilize.
7. **Não exponha token.** Para o Field Shift, nem é preciso usar um.
8. **Confira a licença** (`license_id`) de cada dataset antes de usar ou redistribuir.
9. **Cite a fonte original** do dataset (a organização que publicou), não só o portal.
10. **Envie um `User-Agent` identificando a aplicação** (ex.: `fieldshift`), como na boa prática do POWER.

---

## 14. Datasets potencialmente úteis para o Field Shift

> Os títulos abaixo aparecem nas listas do portal. **Confirme cobertura, formato e licença com `package_show`** antes de usar.

| Dataset | O que parece oferecer | Uso possível no projeto |
|---|---|---|
| **FAO / NASA Harvest Public Yield Datasets** (SHP, DOC) | Dados públicos de produtividade em parceria FAO/Harvest | Contexto de produtividade histórica; validar se as culturas candidatas são produtivas na região |
| **GEOCIF_v2** (CSV) | Resultados do modelo de previsão de produtividade GEOCIF | Referência de metodologia (como a NASA Harvest prevê safra com satélite e clima) |
| **Crop Monitor** | Relatórios de condição das lavouras (GEOGLAM) | Citar no pitch; contexto de risco por região |
| **[PROCESSED] Crop/Non-Crop Labels** (CSV) | Rótulos de "é lavoura / não é lavoura" | Exemplo de dado de treino para separar área agrícola de não agrícola |
| **Iowa In-Season Crop Type Map (2020)** (GeoTIFF) | Mapa de culturas feito com HLS (Landsat + Sentinel-2) e aprendizado de máquina | Referência de metodologia para mapear rotação com Landsat/Sentinel-2. Só cobre Iowa (EUA) |
| **OECD Crop Production** (CSV) | Produção agrícola por país | Contexto de mercado por cultura |
| **WFP VAM Economic Explorer** (CSV) | Preços mensais de alimentos em mercados do mundo | Critério "mercado" da rotação, quando houver dado do país |
| **FAO AQUASTAT** (CSV) | Mais de 180 variáveis sobre recursos hídricos e uso de água | Contexto de disponibilidade de água por país |
| **FAOSTAT Detailed Trade Matrix** (ZIP/CSV) | Comércio agrícola entre países | Viabilidade de mercado de culturas candidatas |

**O que buscar primeiro (consultas prontas):**
```
.../package_search?q=yield&rows=50
.../package_search?q=cropland&rows=50
.../package_search?q="crop type"&rows=50
.../package_search?rows=0&facet.field=["organization","tags","res_format"]&facet.limit=-1
```

---

## 15. Como e por que usar o Harvest Portal no Field Shift

> Esta seção parte do contexto atual do projeto: escopo **global**, foco nos datasets da lista oficial do desafio, ferramenta que **apoia e não decide** e **explicável antes de preciso**.

### 15.1 Por que considerar o Harvest Portal

| Motivo | Por que importa para o projeto |
|---|---|
| **É o repositório do programa oficial da NASA para agricultura** | Dá credibilidade no pitch: "seguimos a mesma linha do NASA Harvest" |
| **API aberta, sem login e em JSON** | Mesma facilidade do NASA POWER: uma URL devolve o resultado |
| **Padrão CKAN** | O mesmo código serve para outros portais CKAN (portais de dados abertos de governos, HDX da ONU). Bibliotecas prontas: `ckanapi` (Python), `ckanr` (R) |
| **Contexto de mercado e segurança alimentar** | Ajuda no critério "mercado" e "renda" das estratégias, que os dados de satélite não cobrem |
| **Referência de método** | GEOCIF, mapas de cultura com HLS e rótulos crop/non-crop mostram como a NASA combina satélite, clima e estatística |

### 15.2 Por que **não** usar como fonte principal

| Motivo | Consequência |
|---|---|
| Não está na lista oficial de recursos do desafio | Os avaliadores esperam ver os datasets indicados (SMAP, GPM, MODIS, Landsat, POWER, ECOSTRESS...) |
| Pouco dado geoespacial e de campo | Não substitui NDVI, umidade do solo, chuva ou temperatura |
| Quase nada explícito sobre o Brasil | Não resolve a falta de dados locais fora dos EUA |
| Licenças incompletas | Risco de usar algo que não pode ser redistribuído |

### 15.3 Onde ele entra no pipeline do produto

| Etapa | Papel do Harvest Portal | Endpoint |
|---|---|---|
| 1. Ingestão | Opcional: baixar tabelas de contexto (preços, produção por país) | `package_show`, download, `datastore_search` |
| 2. Harmonização | Agregar dados por país ao nível da análise | — |
| 3. Indicadores | — (os indicadores climáticos vêm do POWER, GPM, SMAP, MODIS) | — |
| 4. Diagnóstico | — | — |
| 5. Candidatas | Verificar se a cultura candidata tem produção e comércio relevantes no país | `datastore_search` em FAOSTAT/OECD |
| 6. Filtro de viabilidade | Apoiar o filtro "há mercado?" | Idem |
| 7. Pontuação (MCDA) | Alimentar o critério "mercado / renda", quando houver dado do país | Idem |
| 9. Explicação | Citar a fonte do contexto de mercado ("FAOSTAT via Harvest Portal") | — |
| Pitch | Mostrar alinhamento com o programa oficial da NASA | — |

### 15.4 Onde ele aparece para o agricultor

| Tela | O que o Harvest Portal mostra |
|---|---|
| **Comparar estratégias** | Linha "mercado", quando houver dado do país: "a soja tem forte comércio no país" |
| **Detalhe da estratégia** | Bloco "evidência de mercado", com a fonte original |
| **Selo de confiança** | "Dado de mercado nacional, não regional; confirme com a cooperativa" |

### 15.5 O que o Harvest Portal **não** resolve

| Pergunta | Por que não responde | Fonte certa |
|---|---|---|
| Quando o campo fica descoberto? | Não tem série de vegetação | **MODIS NDVI**, Landsat, Sentinel-2 |
| Qual é o clima do talhão? | Não tem dado climático por ponto | **NASA POWER**, GPM IMERG, ERA5 |
| O solo está seco? | Não tem umidade do solo | **SMAP** |
| Qual é o solo do talhão? | Não tem dado de solo | **FAO GAEZ** |
| O talhão é inclinado? | Não tem relevo | **SRTM** |
| Há mercado na região do agricultor? | Os dados são por país | Agricultor, cooperativa, órgãos locais |

### 15.6 Recomendações de implementação

1. **Não colocar o Harvest Portal no caminho crítico da demo.** Se usar, baixe e guarde as tabelas antes da apresentação.
2. **Usar só para o critério de mercado e para o pitch.**
3. **Chamar `package_search` com `rows=0` e facetas** na fase de exploração, para decidir em minutos se vale a pena.
4. **Registrar a licença e a organização de origem** de qualquer dataset usado.
5. **Exibir sempre a escala do dado** (nacional) ao lado do número.

---

## 16. Caso hipotético: a história do Seu Joãozinho

> ⚠️ **Tudo nesta seção é fictício**: o produtor, a fazenda, os nomes curtos de datasets e organizações, os IDs, as colunas e **todos os números**. Só os endpoints e os parâmetros seguem a API real. Base de todas as URLs: `https://data.harvestportal.org/api/3/action/`.

### 16.1 A situação

O **Seu Joãozinho** planta soja no verão e milho safrinha logo depois. Nos últimos anos, o milho tem sofrido com a chuva que acaba cedo. O vizinho dele comentou: *"Eu troquei o milho pelo sorgo, aguenta mais a seca."*

Seu Joãozinho ficou com uma dúvida: **"Tá, mas tem pra quem vender sorgo? Ou vou plantar e ficar com o grão parado no barracão?"**

Ele abre a ferramenta do Field Shift e clica em **"Ver mercado das culturas"**. Enquanto isso, a ferramenta conversa com o Harvest Portal.

### 16.2 Passo 1 — "O que tem nessa biblioteca?"

A ferramenta primeiro dá uma olhada geral no catálogo, sem baixar nada:

```
GET package_search?rows=0&facet.field=["organization"]
```

O portal responde: *"Tenho 86 datasets. 11 são da FAO e 9 são da OECD."* A ferramenta conclui que FAO e OECD são as organizações que publicam dados de produção agrícola.

### 16.3 Passo 2 — "Tem algo sobre produção de culturas?"

```
GET package_search?q=crop production&fq=organization:oecd
```

O portal responde: *"Tenho o **OECD Crop Production**, com licença CC BY."* A licença é aberta, então a ferramenta pode usar o dado.

### 16.4 Passo 3 — "Que arquivo tem dentro?"

```
GET package_show?id=oecd-crop-production
```

O portal responde: *"Tem um CSV, e ele está carregado no banco (`datastore_active: true`)."* Isso significa que a ferramenta não precisa baixar a planilha inteira. Ela pode pedir só as linhas de que precisa.

### 16.5 Passo 4 — "Quais são as colunas?"

```
GET datastore_search?resource_id=a1b2-c3d4&limit=0
```

O portal responde: *"As colunas são País, Cultura, Ano e Valor."* Agora a ferramenta sabe exatamente como montar o filtro.

### 16.6 Passo 5 — "Me mostra só o sorgo do Brasil"

```json
POST datastore_search
{ "resource_id": "a1b2-c3d4",
  "filters": { "LOCATION": "BRA", "SUBJECT": "SORGHUM" },
  "sort": "TIME desc", "limit": 10 }
```

O portal devolve 10 linhas, uma por ano. A ferramenta repete a consulta para o **milho** e para a **soja**.

### 16.7 Passo 6 — A ferramenta compara

| Cultura | Produção nos últimos 10 anos (fictício) | Leitura |
|---|---|---|
| Soja | Subiu 45% | Mercado forte e consolidado |
| Milho | Subiu 30% | Mercado forte |
| Sorgo | Quase triplicou | Crescendo rápido, mas ainda é pequeno |

### 16.8 Passo 7 — O que o Seu Joãozinho vê na tela

> 📈 **Sorgo: mercado em crescimento**
> A produção de sorgo no Brasil quase triplicou em 10 anos. Ainda é bem menor que a de milho, mas o interesse está aumentando.
>
> *Fonte: OECD Crop Production, via NASA Harvest Portal. Este número é do país inteiro.*
>
> ⚠️ **Antes de decidir:** pergunte na sua cooperativa ou cerealista se eles compram sorgo **na sua região**.

### 16.9 Como termina

Seu Joãozinho liga para a cooperativa. O comprador diz: *"Sorgo a gente pega, sim, mas paga um pouco menos que o milho."*

Agora ele tem duas informações. **A ferramenta** mostrou que o mercado de sorgo no país está crescendo. **A cooperativa** confirmou que existe comprador perto dele. Seu Joãozinho decide testar o sorgo em **um talhão** na próxima safrinha, sem trocar a fazenda toda de uma vez.

**A decisão foi dele.** A ferramenta só ajudou a fazer a pergunta certa.

### 16.10 O que a API fez e o que não fez

| A API do Harvest Portal… | Fez? |
|---|---|
| Encontrou o dataset certo no catálogo | ✅ |
| Conferiu a licença | ✅ |
| Trouxe só as linhas necessárias, sem baixar a planilha inteira | ✅ |
| Comparou a produção das culturas no país | ✅ |
| Disse se há comprador **na região** do Seu Joãozinho | ❌ Isso veio da cooperativa |
| Disse se o sorgo aguenta o clima da fazenda | ❌ Isso vem do NASA POWER, do GPM e do SMAP |

---

## 17. Referências

**Harvest Portal**
- Página inicial do catálogo: https://data.harvestportal.org/
- Sobre o portal: https://data.harvestportal.org/about
- Documentação da API (Swagger): https://data.harvestportal.org/api-docs
- Exemplos de uso da API (cURL, JavaScript, Python): https://data.harvestportal.org/api-examples
- Especificação OpenAPI: https://data.harvestportal.org/openapi/harvest-portal-api.json
- Lista de datasets: https://data.harvestportal.org/dataset/
- Organizações: https://data.harvestportal.org/organization/
- Grupos temáticos: https://data.harvestportal.org/group/

**NASA Harvest**
- Site do programa: https://www.nasaharvest.org
- Perguntas frequentes (relação com a NASA, GEOGLAM): https://www.nasaharvest.org/faqs

**CKAN (plataforma do portal)**
- Guia da API do CKAN: https://docs.ckan.org/en/latest/api/index.html
- DataStore (parâmetros do `datastore_search` e exportação): https://docs.ckan.org/en/2.12/maintaining/datastore.html
- Envelope de resposta, GET/POST e autenticação: https://github.com/ckan/ckan/blob/release-v2.5.4/doc/api/index.rst
- Parâmetros do `package_search`: https://ckanaction.dathere.com/docs/package_search
- Parâmetros do `organization_list`: https://ckanaction.dathere.com/docs/organization_list
- Cliente R `ckanr` (`organization_show`, `ds_search`): https://docs.ropensci.org/ckanr/

**Documento relacionado do projeto**
- `nasa-power-api-daily.md` (mesmo padrão de documentação, para o NASA POWER)
