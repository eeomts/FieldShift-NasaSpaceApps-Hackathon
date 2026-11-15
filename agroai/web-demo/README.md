# AgroAI · versão de apresentação (NASA Space Apps)

Cópia do `web/` feita para a demonstração. Ela tem duas diferenças:

| | `web/` (completo) | `web-demo/` (apresentação) |
|---|---|---|
| Entrada | E-mail e senha | **Só o nome** |
| Questionário | Em branco | **Já preenchido**, com o botão **Skip All** |
| Endereço local | http://localhost:5173 | http://localhost:5174 |

O resto é igual ao `web/`: dashboard, estratégias e chat. A API é a mesma e não precisa de nada novo.

A visão geral do projeto está no [README principal](../../README.md), e os detalhes da API e dos testes, no [`agroai/README.md`](../README.md).

## Como rodar

**Pré-requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+ e Docker.

São três passos, todos a partir da raiz do repositório (`nasa-space-app/`).

### 1. Banco local

Na primeira vez, crie o container:

```bash
docker run -d --name agroai-dev -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17
```

Nas outras vezes, por exemplo depois de reiniciar o computador, basta ligá-lo:

```bash
docker start agroai-dev
```

### 2. API (terminal 1)

```bash
cd agroai/api
uv sync
env $(grep -v '^#' .env.dev) uv run alembic upgrade head
env $(grep -v '^#' .env.dev) uv run uvicorn app.main:app --reload --port 8000
```

A documentação da API fica em http://localhost:8000/docs.

### 3. Site de apresentação (terminal 2)

```bash
cd agroai/web-demo
npm install
npm run dev
```

Abra **http://localhost:5174**, digite um nome e clique em **Skip All**. O painel abre com a fazenda de exemplo.

## O que muda nesta versão

**Entrada só com o nome.** O app cria a conta sozinho na API (`POST /auth/register`), com um e-mail `demo-<aleatório>@demo.agroai.app` e uma senha aleatória, e guarda o token no navegador.

**Questionário já respondido.** As 23 perguntas vêm marcadas com um produtor fictício do Corn Belt (Story County, Iowa), baseado no ponto `cornbelt_1` de `data/demo/pontos_demo_eua.csv`. Ele planta milho e soja de maio a outubro e deixa o solo descoberto no inverno. As respostas ficam em `src/onboarding/exemplo.ts`.

**Botão Skip All.** Fica no topo de cada pergunta (em português aparece como "Pular tudo"). Um clique salva tudo e abre o dashboard. Se a pessoa mudou alguma resposta antes, a resposta dela é mantida e o resto vem do exemplo. Quem quiser mostrar as perguntas pode ir clicando em "Continuar", e elas aparecem já marcadas.

## Para a apresentação

- **Chat com IA:** por padrão o `.env.dev` deixa o Gemini desligado, e o chat responde "AgroAI indisponível". Para ligar, coloque sua chave em `GEMINI_API_KEY=` no `agroai/api/.env.dev`. Cada mensagem gasta a cota do Gemini.
- **Dados de satélite:** a umidade do solo e o NDVI só aparecem com o `EARTHDATA_TOKEN` no `agroai/api/.env`. Sem ele, o dashboard mostra a chuva do NASA POWER e avisa o que falta.
- **Em outro endereço:** se o site rodar fora do `localhost`, inclua o endereço dele no `CORS_ORIGINS` da API.

## Se der problema

| Sintoma | O que fazer |
|---|---|
| A API não conecta ao banco | `docker start agroai-dev` |
| `Port 5174 is already in use` | Feche o outro processo que usa a porta (o Vite não troca de porta sozinho) |
| A tela fica em "Carregando…" ou dá erro de rede | Confira se a API está de pé em http://localhost:8000/docs |
| O chat responde "AgroAI indisponível" | Gemini desligado: veja "Chat com IA" acima |

## Observações

- Cada pessoa que entra vira uma conta nova no banco. "Sair" volta para a tela do nome, e a conta antiga continua salva.
- Esta pasta é uma cópia: o que mudar no `web/` não chega aqui sozinho. Se algo importante mudar lá antes da apresentação, copie para cá.
