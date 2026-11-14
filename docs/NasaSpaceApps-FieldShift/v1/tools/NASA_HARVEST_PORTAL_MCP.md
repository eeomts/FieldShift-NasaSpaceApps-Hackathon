# Harvest Portal MCP: análise e documentação

## Como assistentes de IA consultam o Harvest Portal e como isso entra no Field Shift

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Documentos relacionados: `NASA_HARVEST_PORTAL_API.md`, `NASA_HARVEST_PORTAL_API_GUIA.md`, `fluxo-aplicativo-power-harvest-mcp.md`, `ARQUITETURA-COMPLETA.md`

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [O que é MCP](#2-o-que-é-mcp)
3. [Dados do servidor](#3-dados-do-servidor)
4. [O que a IA consegue fazer](#4-o-que-a-ia-consegue-fazer)
5. [Autenticação](#5-autenticação)
6. [Como conectar](#6-como-conectar)
7. [MCP × API: quando usar cada um](#7-mcp--api-quando-usar-cada-um)
8. [Uso 1: a equipe explorando o portal](#8-uso-1-a-equipe-explorando-o-portal)
9. [Uso 2: o chat do agricultor](#9-uso-2-o-chat-do-agricultor)
10. [Caso de uso: pergunta livre no chat](#10-caso-de-uso-pergunta-livre-no-chat)
11. [Segurança e regras do assistente](#11-segurança-e-regras-do-assistente)
12. [Limitações](#12-limitações)
13. [Boas práticas](#13-boas-práticas)
14. [Referências](#14-referências)

---

## Nível de verificação

- As informações vêm da página oficial **`/mcp-docs`** do Harvest Portal e dos documentos de API do projeto.
- **A página não lista as ferramentas (tools) do servidor nem seus parâmetros.** Ela descreve apenas as capacidades: pesquisar datasets, ler metadados e consultar tabelas da DataStore. Os nomes de chamada usados neste documento descrevem o que a IA faz, não os nomes reais das tools.
- **Não foi possível conectar ao servidor** a partir do ambiente de pesquisa (acesso de rede bloqueado), então nenhuma chamada foi testada ao vivo.
- Itens marcados com ⚠️ precisam ser confirmados conectando o servidor num cliente de IA.
- Todos os exemplos de conversa e números são **fictícios**.

---

## 1. Visão geral

O **Harvest Portal MCP** é um servidor que conecta **assistentes de IA** (Claude, ChatGPT e outros) ao **Harvest Portal**, o repositório de dados do NASA Harvest. Com ele, a IA busca datasets, lê metadados e consulta tabelas do portal **sozinha**, a partir de uma pergunta em linguagem natural.

| Item | Valor |
|---|---|
| Endpoint | `https://mcp.harvestportal.org/mcp` |
| Tipo | Servidor MCP remoto (HTTP) |
| Acesso público | Sem autenticação |
| Acesso com conta | Token de API do portal |
| Dados alcançados | Os mesmos do Harvest Portal: datasets, metadados e DataStore |
| Por baixo | As mesmas ações da API CKAN (`package_search`, `package_show`, `datastore_search`...) ⚠️ |
| Documentação | `https://data.harvestportal.org/mcp-docs` |

**Em uma frase:** a API é o caminho para **o código** pedir dados; o MCP é o caminho para **a IA** pedir dados.

---

## 2. O que é MCP

**MCP** (*Model Context Protocol*) é um padrão aberto que liga modelos de IA a fontes de dados e ferramentas externas. Funciona como uma "tomada universal": qualquer assistente que fale MCP consegue usar qualquer servidor MCP.

### 2.1 Analogia

| | Quem faz o pedido | Como |
|---|---|---|
| **API** | O código do aplicativo | Pedido exato, com códigos e IDs: *"datastore_search, resource_id a1b2, filtro BRA + SORGHUM"* |
| **MCP** | A IA | A pessoa fala do seu jeito: *"tem mercado de sorgo no Brasil?"*. A IA descobre os códigos e faz as chamadas |

A "cozinha" é a mesma: o Harvest Portal. Muda **quem faz o pedido**.

### 2.2 As três peças

```
Pessoa  ──►  Cliente de IA  ──►  Servidor MCP do Harvest  ──►  Harvest Portal
(pergunta)   (Claude, ChatGPT,    (mcp.harvestportal.org)        (CKAN + DataStore)
              ou o back-end do
              Field Shift)
```

| Peça | Papel |
|---|---|
| **Cliente de IA** | Entende a pergunta, decide quais ferramentas chamar e escreve a resposta |
| **Servidor MCP** | Expõe as capacidades do portal como "ferramentas" que a IA pode chamar |
| **Harvest Portal** | Guarda os dados |

---

## 3. Dados do servidor

| Campo | Valor |
|---|---|
| URL | `https://mcp.harvestportal.org/mcp` |
| Transporte | HTTP remoto. A página não nomeia o tipo exato; diz que funciona com clientes que aceitam "servidores HTTP remotos" ⚠️ |
| Autenticação pública | **None** |
| Autenticação com conta | Cabeçalho `X-CKAN-API-Token` (ou `Authorization`) |
| Instruções por produto | Não há. A página orienta seguir a documentação de cada assistente, porque os passos de conexão mudam com frequência |

---

## 4. O que a IA consegue fazer

Segundo a `/mcp-docs`, o servidor permite que o assistente:

| Capacidade | Equivalente na API | Exemplo de pergunta |
|---|---|---|
| **Pesquisar datasets** | `package_search` | "Quais datasets falam de produção de milho?" |
| **Ler metadados** | `package_show`, `resource_show`, `organization_show` | "Quem publicou esse dataset, qual a licença e que arquivos ele tem?" |
| **Consultar tabelas da DataStore** | `datastore_search` | "Me dá a produção de sorgo no Brasil nos últimos 10 anos" |

⚠️ **Os nomes reais das ferramentas e seus parâmetros não estão publicados.** Ao conectar, o cliente de IA lista as ferramentas disponíveis. Registre a lista e atualize este documento.

### 4.1 O que acontece por trás de uma pergunta

Pergunta: *"Tem tabela com produção de sorgo no Brasil?"*

```
1. IA → MCP: pesquisar datasets ("crop production")     → acha "OECD Crop Production"
2. IA → MCP: ler metadados do dataset                     → acha o recurso CSV na DataStore
3. IA → MCP: consultar a tabela com limite 0              → descobre as colunas
4. IA → MCP: consultar a tabela filtrando Brasil + sorgo  → recebe os números
5. IA → pessoa: resposta em linguagem natural, com a fonte
```

A pessoa só fez **uma pergunta**. A IA fez **quatro chamadas**.

---

## 5. Autenticação

| Modo | Configuração | O que a IA vê |
|---|---|---|
| **Público** (recomendado para o Field Shift) | Autenticação **None** | Só datasets públicos |
| **Com conta** | Token criado em **Manage → API Tokens** no perfil do portal, enviado no cabeçalho `X-CKAN-API-Token` (ou `Authorization`, se o cliente só oferecer campo genérico de API key ou bearer token) | Tudo o que a sua conta vê, inclusive datasets privados das suas organizações |

**Cuidados com o token:**
- Com token, a IA enxerga **tudo** o que a conta enxerga.
- Nunca coloque o token num cliente de IA compartilhado nem no front-end.
- Para o Field Shift, **não use token**: os dados de mercado são públicos.

---

## 6. Como conectar

### 6.1 Num assistente (Claude, ChatGPT e outros)

1. Abra as configurações de **conectores** (ou *plugins*, *integrations*) do assistente.
2. Adicione um **servidor MCP remoto personalizado**.
3. URL: `https://mcp.harvestportal.org/mcp`.
4. Autenticação: **None**.
5. Salve e abra uma conversa nova.
6. Peça: *"Liste as ferramentas do Harvest Portal que você tem disponíveis."* Registre a resposta.

Os nomes dos menus mudam com frequência; siga a documentação do assistente.

### 6.2 No back-end do Field Shift ⚠️

Para o chat do agricultor, o back-end precisa de um **cliente MCP** ou de uma **API de IA que aceite servidores MCP remotos**. Esquema:

```
Front-end (chat) ──► Back-end Field Shift ──► API de IA (com o MCP do Harvest configurado)
                         │                          │
                         │ envia: pergunta,          │ chama as ferramentas do Harvest
                         │ resumo do clima,          ▼
                         │ regras de segurança   Harvest Portal
                         ◄──────────── resposta com fontes
```

O formato exato depende do provedor de IA escolhido. Consulte a documentação dele para "MCP connector" ou "remote MCP servers".

---

## 7. MCP × API: quando usar cada um

| Situação | Usar | Por quê |
|---|---|---|
| Tela de recomendação (sempre as mesmas consultas) | **API** | Rápida, barata, previsível, sem IA |
| Equipe descobrindo datasets, IDs, colunas e códigos | **MCP** num assistente | Pergunta em português e a IA faz a sequência de chamadas |
| Agricultor perguntando sobre uma cultura fora da lista | **MCP** no chat | A pergunta não foi programada |
| Clima do talhão | **API do NASA POWER** | O MCP do Harvest **não** acessa o POWER |
| Download de arquivos grandes (GeoTIFF, SHP) | **API** (link de download) | O MCP é para consulta e resposta, não para transferir arquivos |

| Critério | API | MCP |
|---|---|---|
| Quem decide as chamadas | O código | A IA |
| Pergunta | Fixa | Livre |
| Velocidade | Rápida | Mais lenta (várias chamadas + IA) |
| Custo | Grátis | Custo da IA |
| Previsibilidade | Sempre igual | Pode variar ou errar |
| Precisa de IA | Não | Sim |

---

## 8. Uso 1: a equipe explorando o portal

**Quando:** agora, no preparo do hackathon.

**Objetivo:** trocar os valores fictícios dos documentos (`resource_id`, colunas, códigos de cultura) pelos reais.

### 8.1 Prompts prontos

> **Prompt 1 — mapa do catálogo**
> "Use o Harvest Portal. Quantos datasets públicos existem? Agrupe por organização e por formato."

> **Prompt 2 — tabelas de produção**
> "No Harvest Portal, encontre datasets com produção agrícola por país que estejam carregados na DataStore. Para cada um, me dê: nome do dataset, organização, licença, resource_id e lista de colunas."

> **Prompt 3 — códigos das culturas**
> "Na tabela <resource_id>, quais valores a coluna de cultura usa para soja, milho, sorgo, milheto, feijão, trigo, girassol e gergelim? E qual valor representa o Brasil?"

> **Prompt 4 — teste de uma série**
> "Na tabela <resource_id>, traga a produção de sorgo no Brasil dos últimos 10 anos, com a unidade."

### 8.2 O que fazer com as respostas

| Resposta | Onde vai |
|---|---|
| `resource_id` e colunas | Configuração da tabela de mercado no back-end |
| Códigos das culturas | Campo `codigo_mercado` da ficha de cada cultura |
| Código do país | Configuração do país |
| Licença | Coluna "licença" do registro de fontes |

**Sempre confira** a resposta da IA com uma chamada direta à API (`datastore_search?limit=0`), porque a IA pode errar nomes.

---

## 9. Uso 2: o chat do agricultor

**Quando:** extra do protótipo, se der tempo; se não, próximo passo no pitch.

**Ideia:** o agricultor pergunta do jeito dele sobre qualquer cultura. A IA usa o clima que o aplicativo já calculou e busca o mercado no Harvest Portal pelo MCP.

### 9.1 O que a IA recebe e o que ela busca

| Informação | Origem | Como chega |
|---|---|---|
| Pergunta | Chat | O aplicativo envia |
| Resumo do clima e do campo | NASA POWER, MODIS, SRTM... (já calculados) | O aplicativo envia **pronto** |
| Culturas e prioridades do agricultor | Cadastro | O aplicativo envia |
| Regras de segurança | Equipe | O aplicativo envia |
| **Mercado da cultura perguntada** | **Harvest Portal** | **A IA busca pelo MCP** |

### 9.2 Três usos interessantes

| Uso | Exemplo de pergunta | Valor |
|---|---|---|
| **Cultura fora da lista** | "E gergelim? E girassol?" | O aplicativo deixa de ficar limitado às culturas cadastradas |
| **Explicar a recomendação** | "Por que o milho ficou em segundo se paga mais?" | Atende o pedido do desafio de explicar o porquê de cada sugestão |
| **Resumo para o técnico** | "Faz um resumo pra eu levar pro agrônomo" | Reforça que a decisão é do agricultor com o técnico |

---

## 10. Caso de uso: pergunta livre no chat

> ⚠️ Tudo nesta seção é fictício.

### 10.1 Ficha

| Item | Descrição |
|---|---|
| **Nome** | UC-02 · Consultar o mercado de uma cultura fora da lista pelo chat |
| **Ator principal** | Agricultor |
| **Atores de sistema** | Back-end do Field Shift, IA (LLM), servidor MCP do Harvest |
| **Objetivo** | Responder se uma cultura que o aplicativo não avaliou combina com o clima do talhão e tem mercado |
| **Gatilho** | O agricultor envia uma pergunta em **"Perguntar ao assistente"** |
| **Pré-condições** | 1) O UC-01 (recomendação) já rodou, então o resumo de clima e campo existe. 2) O back-end tem uma IA configurada com o MCP do Harvest |
| **Pós-condição de sucesso** | O agricultor recebe uma resposta em linguagem simples, com fontes, escala do dado e o aviso de confirmar com técnico e cooperativa |
| **Pós-condição de falha** | O chat informa que o assistente está indisponível; a tela de recomendação continua funcionando |

### 10.2 Situação

O aplicativo recomendou sorgo para a safrinha. O agricultor lembra que o cunhado está plantando **gergelim**, que não estava na lista. Ele abre o chat e pergunta.

### 10.3 Fluxo principal

| # | Quem | O que acontece |
|---|---|---|
| 1 | Agricultor | Digita: *"E gergelim, vale a pena aqui? Meu cunhado tá plantando."* |
| 2 | Back-end | Monta o pacote: pergunta + resumo do clima + culturas cadastradas + ranking atual + regras de segurança |
| 3 | Back-end | Envia o pacote à IA, com o MCP do Harvest habilitado |
| 4 | IA | Identifica que precisa do mercado do gergelim no país |
| 5 | IA → MCP | Pesquisa datasets de produção agrícola |
| 6 | IA → MCP | Lê os metadados e acha a tabela na DataStore |
| 7 | IA → MCP | Consulta as colunas e depois a produção de gergelim no Brasil |
| 8 | IA | Cruza o mercado com o resumo do clima recebido |
| 9 | IA | Escreve a resposta seguindo as regras de segurança |
| 10 | Back-end | Verifica se a resposta tem fonte e aviso; se faltar, acrescenta o aviso padrão |
| 11 | Agricultor | Lê a resposta no chat |

### 10.4 Pacote enviado à IA (passo 2)

```json
{
  "pergunta": "E gergelim, vale a pena aqui? Meu cunhado tá plantando.",
  "clima_talhao": {
    "fonte": "NASA POWER 1991–2025 (~55 km) e GPM IMERG (~10 km)",
    "fim_chuvas": "meados de abril",
    "veranico_safrinha": "6 em cada 10 anos",
    "geada_junho_julho": "3 em cada 10 anos"
  },
  "campo": {
    "fonte": "MODIS NDVI (250 m) e SRTM (30 m)",
    "solo_descoberto": "agosto a outubro",
    "declividade": "parte do talhão acima de 8%"
  },
  "culturas_cadastradas": ["soja (out–fev)", "milho safrinha (fev–jul)"],
  "ranking_atual": [{"cultura": "sorgo", "clima": 4.5, "mercado": 3.0}],
  "pais": "Brasil"
}
```

### 10.5 Resposta esperada (passo 11)

> 🤖 **Assistente:** O gergelim aguenta bem a seca, então combina com o fim de chuva em meados de abril na sua região. No Harvest Portal, a produção de gergelim no Brasil é pequena perto da de milho e soja, mas vem crescendo nos últimos anos.
>
> Um ponto de atenção: ele cobre pouco o solo, então não resolve o problema do campo descoberto de agosto a outubro nem a erosão na parte inclinada.
>
> Antes de decidir, pergunte na cooperativa se eles compram gergelim na sua região e qual cultivar o técnico recomenda.
>
> *Fontes: clima, NASA POWER e GPM IMERG; campo, MODIS e SRTM; mercado, OECD/FAO via NASA Harvest Portal (dado nacional).*
> *Isto é uma sugestão. A decisão é sua, junto com seu técnico.*

### 10.6 Fluxos alternativos

| Código | Situação | O que acontece |
|---|---|---|
| **A1** | Não há dado de mercado do gergelim no portal | A IA diz que não encontrou dado de mercado e responde só sobre o clima, sem estimar números |
| **A2** | A pergunta é sobre algo fora do escopo (ex.: dose de defensivo) | A IA recusa e encaminha ao técnico (regra 5) |
| **A3** | O agricultor pede o resumo para o técnico | A IA monta o texto com recomendação, evidências e perguntas |
| **A4** | A pergunta é sobre uma cultura já avaliada | A IA explica usando as notas recebidas, sem chamar o MCP |

### 10.7 Fluxos de exceção

| Código | Situação | O que acontece |
|---|---|---|
| **E1** | Servidor MCP fora do ar | A IA avisa que não conseguiu consultar o portal; o chat oferece responder só sobre o clima |
| **E2** | IA fora do ar ou demora > 30 s | O chat mostra "O assistente está indisponível agora" |
| **E3** | A resposta veio sem fonte | O back-end acrescenta o aviso padrão e registra o caso para revisão |
| **E4** | A IA citou um número que não veio nem do pacote nem do portal | Registrado como falha de qualidade; ajustar as regras do assistente |

### 10.8 Critérios de aceite

| # | Dado que... | Quando... | Então... |
|---|---|---|---|
| 1 | O UC-01 rodou | O agricultor pergunta sobre gergelim | A resposta cita clima e mercado, cada um com fonte |
| 2 | O portal não tem gergelim | O agricultor pergunta sobre gergelim | A resposta diz que não encontrou dado de mercado e não inventa números |
| 3 | O MCP está fora do ar | O agricultor pergunta algo | O chat avisa, e a tela de recomendação continua funcionando |
| 4 | Qualquer resposta | O assistente responde | Termina com o lembrete de confirmar com técnico e cooperativa |
| 5 | O agricultor pergunta sobre dose de defensivo | O assistente responde | Encaminha ao técnico, sem indicar produto ou dose |

---

## 11. Segurança e regras do assistente

Instruções fixas enviadas à IA em toda conversa:

1. Use **apenas** os dados recebidos do aplicativo e os encontrados no Harvest Portal. **Não invente números.**
2. Cite **sempre a fonte e a escala** de cada número.
3. Se não encontrar dado, **diga que não encontrou**. Não estime.
4. Termine com o lembrete de **confirmar com o técnico e a cooperativa**.
5. **Não recomende** defensivo, dose ou manejo químico. Encaminhe ao técnico.
6. Use **linguagem simples**.
7. **Não afirme certeza**: use "pode", "costuma", "nos últimos anos".

**Do lado do back-end:**
- Acesso **público** ao MCP (sem token).
- Tempo limite de 30 s por pergunta.
- Registro das perguntas e respostas (sem dados pessoais) para revisão de qualidade.
- O chat **nunca** substitui a tela de recomendação: se ele cair, o resto funciona.

---

## 12. Limitações

| Limitação | Consequência |
|---|---|
| **Só acessa o Harvest Portal** | Não traz clima, satélite ou solo. Esses dados vêm prontos do aplicativo |
| **Ferramentas não documentadas** | É preciso conectar para descobrir nomes e parâmetros ⚠️ |
| **Conteúdo do portal** | Forte em mercado e segurança alimentar; pouco dado de campo; quase nada explícito sobre o Brasil |
| **Dado nacional** | Mercado por país, não por região do agricultor |
| **A IA pode errar** | Nomes de colunas, códigos ou interpretação. Regras e conferência são obrigatórias |
| **Custo e latência** | Cada pergunta gasta com IA e leva alguns segundos |
| **Fora da lista do desafio** | O Harvest Portal é complemento, não dataset oficial do Field Shift |

---

## 13. Boas práticas

1. **Use o MCP para explorar e a API para produção.** Descobriu o que precisa com o MCP? Programe a consulta fixa pela API.
2. **Confira a IA com a API.** Toda informação estrutural (IDs, colunas, códigos) deve ser validada com `datastore_search?limit=0`.
3. **Entregue o clima pronto.** A IA explica; o código calcula.
4. **Acesso público.** Não use token no Field Shift.
5. **Mostre a fonte em toda resposta.**
6. **Chat como extra.** O aplicativo funciona sem ele.
7. **Registre a lista de ferramentas** assim que conectar e atualize este documento.

---

## 14. Referências

- Documentação do MCP do Harvest Portal: https://data.harvestportal.org/mcp-docs
- Endpoint do servidor: `https://mcp.harvestportal.org/mcp`
- API do Harvest Portal: https://data.harvestportal.org/api-docs
- Exemplos da API: https://data.harvestportal.org/api-examples
- Especificação do Model Context Protocol: https://modelcontextprotocol.io

**Documentos do projeto**
- `NASA_HARVEST_PORTAL_API.md` e `NASA_HARVEST_PORTAL_API_GUIA.md`: a API que o MCP usa por baixo
- `fluxo-aplicativo-power-harvest-mcp.md`: Fluxo A (API) e Fluxo B (MCP)
- `ARQUITETURA-COMPLETA.md`: o sistema inteiro
