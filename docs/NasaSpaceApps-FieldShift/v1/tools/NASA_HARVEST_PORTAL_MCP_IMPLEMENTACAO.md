# Harvest Portal MCP: como programar

## Código do back-end para descobrir as ferramentas, chamá-las e ligar o chat do agricultor

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Código: pasta `mcp-harvest-exemplo/`
> Documentos relacionados: `NASA_HARVEST_PORTAL_MCP.md` (conceito e caso de uso UC-02), `fluxo-aplicativo-power-harvest-mcp.md`

---

## Sumário

1. [Os dois jeitos de programar](#1-os-dois-jeitos-de-programar)
2. [Fontes usadas](#2-fontes-usadas)
3. [Instalação](#3-instalação)
4. [Passo 0: descobrir as ferramentas](#4-passo-0-descobrir-as-ferramentas)
5. [Passo 1: chamar uma ferramenta direto](#5-passo-1-chamar-uma-ferramenta-direto)
6. [Passo 2: chat com Claude + MCP connector](#6-passo-2-chat-com-claude--mcp-connector)
7. [Passo 3: endpoint do back-end](#7-passo-3-endpoint-do-back-end)
8. [Testes realizados](#8-testes-realizados)
9. [Restringir ferramentas](#9-restringir-ferramentas)
10. [Erros comuns](#10-erros-comuns)
11. [Checklist](#11-checklist)
12. [Referências](#12-referências)

---

## Nível de verificação

- O código segue a **documentação oficial do MCP Python SDK v2** e a **documentação oficial do MCP connector da API do Claude** (seção 2).
- Os passos 0 e 1 foram **executados e funcionaram contra um servidor MCP falso local** (`servidor_falso_para_teste.py`), com o SDK `mcp` 2.3.0.
- **Nenhum script foi executado contra o servidor real** `https://mcp.harvestportal.org/mcp`: o acesso de rede ao servidor foi bloqueado no ambiente de pesquisa.
- **O passo 2 não foi executado** (exige chave da API da Anthropic e acesso à internet). A sintaxe foi conferida e o SDK `anthropic` 2.8.0 instalado aceita os parâmetros `mcp_servers` e `betas`.
- Os **nomes das ferramentas** do servidor real ainda são desconhecidos. Os nomes `search_datasets` e `datastore_search` usados nos exemplos são do servidor falso. **Rode o passo 0 primeiro.**

---

## 1. Os dois jeitos de programar

| Jeito | Quem conecta no MCP | Quando usar | Scripts |
|---|---|---|---|
| **A. Cliente MCP próprio** (MCP Python SDK) | O seu código Python | Descobrir ferramentas, testar, chamar uma ferramenta sem IA | `00_descobrir_ferramentas.py`, `01_chamar_ferramenta_direto.py` |
| **B. MCP connector da API do Claude** | A própria API da Anthropic | Chat do agricultor: a IA decide quais ferramentas chamar | `02_chat_com_claude_mcp_connector.py`, `03_backend_fastapi.py` |

```
JEITO A (sem IA)                           JEITO B (com IA)
Seu código ──MCP──► Harvest Portal         Seu back-end ──► API do Claude ──MCP──► Harvest Portal
                                                              (a API faz o papel de cliente MCP)
```

**Recomendação:** use o **A** agora para descobrir as ferramentas; use o **B** no chat.

---

## 2. Fontes usadas

| O quê | Fonte | O que ela diz e foi usado no código |
|---|---|---|
| Servidor MCP do Harvest | https://data.harvestportal.org/mcp-docs | Endpoint `https://mcp.harvestportal.org/mcp`; acesso público com autenticação "None"; token opcional no cabeçalho `X-CKAN-API-Token` ou `Authorization`; capacidades: pesquisar datasets, ler metadados, consultar a DataStore |
| Cliente MCP em Python (v2) | https://py.sdk.modelcontextprotocol.io/client/ | `async with Client("http://.../mcp") as client:` conecta e negocia; `client.list_tools()`; `client.call_tool(nome, argumentos)` devolve `content` (para o modelo), `structured_content` (para o código) e `is_error` |
| Cliente MCP em Python (v1, referência) | https://py.sdk.modelcontextprotocol.io/v1/client/ | Padrão antigo com `ClientSession` + `streamable_http_client`; cabeçalhos e timeouts via `httpx.AsyncClient` passado em `http_client=` |
| MCP connector da API do Claude | https://platform.claude.com/docs/en/agents-and-tools/mcp-connector | `client.beta.messages.create(...)` com `mcp_servers=[{"type":"url","url":..., "name":...}]`, `tools=[{"type":"mcp_toolset","mcp_server_name":...}]` e `betas=["mcp-client-2025-11-20"]`; a URL precisa começar com `https://`; resposta com blocos `mcp_tool_use` e `mcp_tool_result`; só chamadas de ferramenta são suportadas |

---

## 3. Instalação

```bash
cd mcp-harvest-exemplo
pip install -r requirements.txt
```

`requirements.txt`:

```
mcp>=2.0          # MCP Python SDK (passos 0 e 1)
anthropic         # API do Claude com MCP connector (passo 2)
fastapi           # back-end (passo 3)
uvicorn
```

**Atenção à versão do SDK `mcp`:** na versão 2, o `FastMCP` virou `MCPServer` e surgiu a classe `Client`. Se a equipe tiver código da versão 1 (`ClientSession`, `streamablehttp_client`), ou fixe `mcp<2` ou siga o guia de migração da documentação do SDK.

Para o passo 2, defina a chave da API **no servidor**:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 4. Passo 0: descobrir as ferramentas

**Arquivo:** `00_descobrir_ferramentas.py`

**Por quê:** a página `mcp-docs` não lista as ferramentas. Sem os nomes e parâmetros reais, não dá para restringir ferramentas nem testar chamadas.

```python
import asyncio, json, sys
from mcp import Client

URL = sys.argv[1] if len(sys.argv) > 1 else "https://mcp.harvestportal.org/mcp"

async def main() -> None:
    async with Client(URL) as client:          # conecta e negocia o protocolo
        result = await client.list_tools()
        print(f"Ferramentas encontradas: {len(result.tools)}")
        for tool in result.tools:
            print("Nome:       ", tool.name)
            print("Descrição:  ", (tool.description or "")[:300])
            print("Parâmetros: ", json.dumps(tool.input_schema, indent=2, ensure_ascii=False))

asyncio.run(main())
```

**Rodar:**

```bash
python 00_descobrir_ferramentas.py
```

**Depois:** copie a saída para a seção 4 do `NASA_HARVEST_PORTAL_MCP.md` e ajuste os nomes nos passos 1 e 9.

**Detalhe do SDK v2:** o esquema de parâmetros está em `tool.input_schema` (no v1 era `tool.inputSchema`).

---

## 5. Passo 1: chamar uma ferramenta direto

**Arquivo:** `01_chamar_ferramenta_direto.py`

**Por quê:** ver o formato exato da resposta de uma ferramenta, sem IA no meio.

```python
import asyncio, json, sys
from mcp import Client
from mcp.types import TextContent

URL = sys.argv[1] if len(sys.argv) > 1 else "https://mcp.harvestportal.org/mcp"
NOME_DA_FERRAMENTA = "search_datasets"                 # ⚠️ confirmar no passo 0
ARGUMENTOS = {"query": "crop production", "rows": 5}   # ⚠️ confirmar no passo 0

async def main() -> None:
    async with Client(URL) as client:
        result = await client.call_tool(NOME_DA_FERRAMENTA, ARGUMENTOS)
        if result.is_error:
            print("A ferramenta devolveu erro:")
        for block in result.content:              # parte para o modelo
            if isinstance(block, TextContent):
                print(block.text)
        if result.structured_content is not None: # parte para o código
            print(json.dumps(result.structured_content, indent=2, ensure_ascii=False))

asyncio.run(main())
```

| Campo do resultado | Para quê |
|---|---|
| `content` | Texto pensado para a IA ler |
| `structured_content` | Dados estruturados para o seu código |
| `is_error` | Verifique **antes** de usar o resultado |

**Uso no projeto:** é este jeito que permite, no preparo, descobrir `resource_id`, colunas e códigos das culturas sem gastar com IA.

---

## 6. Passo 2: chat com Claude + MCP connector

**Arquivo:** `02_chat_com_claude_mcp_connector.py`

**Por quê:** é o jeito mais simples de ter o chat do agricultor. A API do Claude conecta no MCP do Harvest sozinha; o back-end não precisa manter cliente MCP.

### 6.1 Declaração do servidor e das ferramentas

```python
SERVIDOR_MCP = {
    "type": "url",
    "url": "https://mcp.harvestportal.org/mcp",
    "name": "harvest-portal",
    # Sem "authorization_token": o Field Shift usa só dados públicos.
}
```

```python
tools=[{"type": "mcp_toolset", "mcp_server_name": "harvest-portal"}]
```

O `name` do servidor e o `mcp_server_name` do toolset **precisam ser iguais**.

### 6.2 O pacote enviado à IA

O clima e o campo vêm **prontos do aplicativo**, porque o MCP do Harvest não acessa o NASA POWER:

```python
contexto = {
    "clima_talhao": {"fonte": "NASA POWER 1991–2025 (~55 km)",
                     "fim_chuvas": "meados de abril", ...},
    "campo": {"fonte": "MODIS NDVI (250 m)", "solo_descoberto": "agosto a outubro"},
    "culturas_cadastradas": ["soja (out–fev)", "milho safrinha (fev–jul)"],
    "pais": "Brasil",
}
```

### 6.3 A chamada

```python
client = anthropic.Anthropic()   # lê ANTHROPIC_API_KEY do ambiente
response = client.beta.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1500,
    system=REGRAS,                                   # 6 regras de segurança
    messages=[{"role": "user", "content": montar_pacote(pergunta)}],
    mcp_servers=[SERVIDOR_MCP],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "harvest-portal"}],
    betas=["mcp-client-2025-11-20"],
)
```

### 6.4 Lendo a resposta

```python
for bloco in response.content:
    if bloco.type == "text":            # texto para o agricultor
        resposta.append(bloco.text)
    elif bloco.type == "mcp_tool_use":  # o que a IA pediu ao Harvest (guardar em log)
        chamadas.append({"ferramenta": bloco.name, "argumentos": bloco.input})
    elif bloco.type == "mcp_tool_result" and bloco.is_error:
        chamadas.append({"erro": True})
```

O script também acrescenta o aviso "Confirme com seu técnico e com sua cooperativa." se a IA esquecer. É a regra de segurança aplicada pelo back-end.

### 6.5 Rodar

```bash
python 02_chat_com_claude_mcp_connector.py "E gergelim, vale a pena aqui?"
```

### 6.6 Limitações do MCP connector (segundo a documentação)

- Só **chamadas de ferramenta** são suportadas; recursos e prompts do MCP, não.
- O servidor precisa ser **público via HTTP** e a URL começar com `https://`. O do Harvest atende.
- O recurso está em **beta** (cabeçalho `mcp-client-2025-11-20`). Se a Anthropic mudar a versão, atualize o `betas`.

---

## 7. Passo 3: endpoint do back-end

**Arquivo:** `03_backend_fastapi.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import importlib

chat = importlib.import_module("02_chat_com_claude_mcp_connector")
app = FastAPI(title="Field Shift — chat")

class Pergunta(BaseModel):
    pergunta: str

@app.post("/chat")
def responder(p: Pergunta):
    try:
        return chat.perguntar(p.pergunta)
    except Exception:
        raise HTTPException(status_code=503, detail="O assistente está indisponível agora.")
```

**Rodar e testar:**

```bash
uvicorn 03_backend_fastapi:app --reload
curl -X POST localhost:8000/chat -H "Content-Type: application/json" \
     -d '{"pergunta": "E gergelim, vale a pena aqui?"}'
```

Se o `uvicorn` reclamar do nome começando com número, renomeie para `backend.py` e o módulo do passo 2 para `chat_mcp.py`.

**Regras do back-end:**
- A chave `ANTHROPIC_API_KEY` fica **só** no servidor.
- O front-end chama `/chat`; nunca chama a API do Claude nem o MCP direto.
- Se o chat falhar, responde `503` e o resto do aplicativo continua funcionando.

---

## 8. Testes realizados

| Teste | Ambiente | Resultado |
|---|---|---|
| Instalar `mcp` e `anthropic` | Python 3.13 | ✅ `mcp` 2.3.0, `anthropic` 2.8.0 |
| `py_compile` de todos os scripts | Local | ✅ Sem erro de sintaxe |
| Passo 0 contra o servidor falso (`http://127.0.0.1:8000/mcp`) | Local | ✅ Listou 2 ferramentas com nome, descrição e esquema de parâmetros |
| Passo 1 contra o servidor falso | Local | ✅ Chamou `search_datasets` e imprimiu o `structured_content` |
| SDK `anthropic` aceita `mcp_servers`, `betas` e tipos `BetaMCPToolset` | Local | ✅ |
| Passo 0 e 1 contra o **servidor real** | — | ❌ Não testado (rede bloqueada) |
| Passo 2 e 3 com a **API do Claude** | — | ❌ Não testado (sem chave e sem rede) |

**Para testar sem internet:**

```bash
python servidor_falso_para_teste.py                         # terminal 1
python 00_descobrir_ferramentas.py http://127.0.0.1:8000/mcp   # terminal 2
python 01_chamar_ferramenta_direto.py http://127.0.0.1:8000/mcp
```

O servidor falso usa nomes de ferramentas **inventados**. Ele serve só para provar que o código do cliente funciona.

---

## 9. Restringir ferramentas

Depois do passo 0, libere **só as ferramentas de leitura de que o chat precisa**. Segundo a documentação do MCP connector, isso é feito com `default_config` e `configs`:

```python
tools=[{
    "type": "mcp_toolset",
    "mcp_server_name": "harvest-portal",
    "default_config": {"enabled": False},          # desliga tudo
    "configs": {
        "<nome_da_ferramenta_de_busca>": {"enabled": True},       # ⚠️ nomes do passo 0
        "<nome_da_ferramenta_da_datastore>": {"enabled": True},
    },
}]
```

A ordem de precedência é: `configs`, depois `default_config`, depois o padrão do sistema. O formato antigo `allowed_tools` pertencia à versão beta descontinuada `mcp-client-2025-04-04`.

---

## 10. Erros comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `AttributeError: 'Tool' object has no attribute 'inputSchema'` | Código do SDK v1 rodando no v2 | Use `tool.input_schema` |
| `No module named 'mcp.server.fastmcp'` | SDK v2 renomeou `FastMCP` | `from mcp.server.mcpserver import MCPServer` ou `pip install "mcp<2"` |
| Erro de conexão no passo 0 | Rede, firewall ou servidor fora do ar | Testar a URL; tentar mais tarde |
| A API do Claude rejeita `mcp_servers` | Falta o `betas` ou a versão mudou | Conferir `betas=["mcp-client-2025-11-20"]` na documentação atual |
| `mcp_server_name` não encontrado | Nome diferente entre `mcp_servers` e `tools` | Usar exatamente o mesmo `name` |
| A IA não usa o Harvest | Pergunta não precisa de mercado, ou ferramentas desligadas | Conferir `configs`; testar com uma pergunta de mercado |
| Resposta sem fonte | A IA ignorou a regra | O back-end acrescenta o aviso; registrar para revisão |

---

## 11. Checklist

| # | Item | Feito? |
|---|---|---|
| 1 | Rodar o passo 0 contra o servidor real e registrar as ferramentas | ☐ |
| 2 | Atualizar `NOME_DA_FERRAMENTA` e `ARGUMENTOS` no passo 1 | ☐ |
| 3 | Restringir as ferramentas do chat (seção 9) | ☐ |
| 4 | `ANTHROPIC_API_KEY` só no servidor, fora do repositório | ☐ |
| 5 | Testar o passo 2 com 3 perguntas: cultura com dado, cultura sem dado, pergunta fora do escopo | ☐ |
| 6 | Conferir que toda resposta tem fonte e aviso | ☐ |
| 7 | Confirmar que o aplicativo funciona com o chat desligado | ☐ |
| 8 | Anotar as versões usadas (`mcp`, `anthropic`, beta do connector) | ☐ |

---

## 12. Referências

- Harvest Portal MCP: https://data.harvestportal.org/mcp-docs
- MCP Python SDK v2 — The Client: https://py.sdk.modelcontextprotocol.io/client/
- MCP Python SDK v1 — Client (referência para código antigo): https://py.sdk.modelcontextprotocol.io/v1/client/
- Claude Platform Docs — MCP connector: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
- Model Context Protocol (especificação): https://modelcontextprotocol.io

**Código deste documento:** pasta `mcp-harvest-exemplo/`
- `00_descobrir_ferramentas.py`
- `01_chamar_ferramenta_direto.py`
- `02_chat_com_claude_mcp_connector.py`
- `03_backend_fastapi.py`
- `servidor_falso_para_teste.py`
- `requirements.txt`
