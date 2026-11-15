# Field Shift · AgroAI

Projeto da equipe para o **NASA Space Apps Challenge 2026**, desafio **[Field Shift: Adapting Farms with NASA Data](docs/NasaSpaceApps-FieldShift/v1/desafio-oficial-nasa-field-shift.md)**.

## O problema

Clima mudando, chuva irregular, falta de água e solo se desgastando tornam difícil escolher **o que plantar e quando**. O desafio pede uma ferramenta de apoio à decisão que use dados de satélite da NASA, o solo local, as características das culturas e as prioridades do produtor. Ela deve **comparar pelo menos 3 estratégias de rotação de culturas, incluindo a atual**, e explicar para cada uma o porquê, a evidência, os benefícios, as lacunas e os riscos.

## A solução: AgroAI

Um site em português e inglês, pensado primeiro para o celular, para pequenos e médios produtores do Brasil e dos EUA. Nele o produtor:

1. **Responde um questionário curto** sobre a fazenda: local, o que planta e quando, o que sabe do solo e suas prioridades.
2. **Acompanha um painel (dashboard)** com o retrato do solo, o clima do local (NASA POWER), o relevo (SRTM), a previsão do tempo e a comparação da rotação atual com duas alternativas.
3. **Conversa com a AgroAI**, um assistente que conhece a fazenda dele e explica os dados em linguagem simples, citando a fonte.

> A ferramenta **apoia, não decide**. A palavra final é do produtor e do técnico local. Todo número tem fonte, e a IA nunca calcula nem inventa número.

## Status

| Parte | O que é | Situação |
|---|---|---|
| 1 | Login e cadastro | Pronta |
| 2 | Questionário do produtor (onboarding), em PT e EN | Pronta |
| 3 | Dados da NASA: clima (NASA POWER), solo (SoilGrids), relevo (SRTM). Umidade do solo (SMAP) e NDVI ficaram fora desta versão | Pronta (solo em revisão) |
| 4 | Comparação de 3 estratégias de rotação (motor) | Pronta a v1; v2 em andamento |
| 5 | Chat AgroAI com base de conhecimento (RAG) | Pronta |
| — | Versão de apresentação (`agroai/web-demo`) | Pronta |

O andamento detalhado, com PRs e pendências, fica em [`ANDAMENTO.md`](docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md).

## As duas interfaces

| | `agroai/web` (completa) | `agroai/web-demo` (apresentação) |
|---|---|---|
| Para quê | Uso real e desenvolvimento | Demonstração para a NASA |
| Entrada | E-mail e senha | Só o nome |
| Questionário | Em branco | Já preenchido (fazenda de exemplo em Iowa), com o botão **Skip All** |
| Endereço local | http://localhost:5173 | http://localhost:5174 |
| Deploy na VPS | Sim (`.deploy/`) | Não, roda local |

As duas usam a mesma API e o mesmo banco. Detalhes da versão de apresentação em [`agroai/web-demo/README.md`](agroai/web-demo/README.md).

## Rodar o app

Precisa de Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+ e Docker. O jeito abaixo roda tudo no seu computador, com um banco local e sem gastar o Gemini. O passo a passo completo (inclusive contra a VPS), os testes e a solução de problemas estão em **[`agroai/README.md`](agroai/README.md)**.

```bash
# 0. Banco local (só na primeira vez; depois, `docker start agroai-dev`)
docker run -d --name agroai-dev -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17

# 1. API (terminal 1)
cd agroai/api
uv sync
env $(grep -v '^#' .env.dev) uv run alembic upgrade head
env $(grep -v '^#' .env.dev) uv run uvicorn app.main:app --reload --port 8000

# 2. Site (terminal 2): escolha uma das versões
cd agroai/web        # completa, abre em http://localhost:5173
cd agroai/web-demo   # apresentação, abre em http://localhost:5174
npm install
npm run dev
```

Para subir com Docker (local ou na VPS), veja [`.deploy/README.md`](.deploy/README.md).

## Estrutura do repositório

```text
.
├── agroai/                         # o código do app
│   ├── api/                        # back-end: FastAPI + PostgreSQL
│   ├── web/                        # front-end completo: React + Vite + TypeScript
│   ├── web-demo/                   # versão de apresentação (entrada só com o nome, Skip All)
│   └── base/                       # culturas e equipamentos do questionário (fonte única)
├── data/                           # dados preparados pela equipe (catálogo, demo, RAG, Brasil, EUA)
├── docs/NasaSpaceApps-FieldShift/v1/
│   ├── desafio-oficial-nasa-field-shift.md   # texto oficial do desafio
│   ├── context/                    # o problema e as decisões
│   │   ├── DECISOES.md             # decisões da equipe (D-xxx) e perguntas em aberto (Q-xx)
│   │   ├── CONTEXTO-DESAFIO.md     # requisitos, conceitos e indicadores
│   │   └── BANCO_DE_DADOS_NASA.md  # datasets e ferramentas
│   ├── application/                # o produto
│   │   ├── ANDAMENTO.md            # o que está feito, pendente e bloqueado
│   │   ├── site-contexto.md        # especificação do AgroAI (telas, chat, API, dados)
│   │   ├── ONBOARDING.md           # questionário do primeiro acesso
│   │   ├── DOR-DO-AGRICULTOR-E-CASO-DE-USO.md   # dores do produtor + caso da Dona Marta
│   │   ├── architecture/           # coleta, integração de dados, motor, dashboard/chat, banco
│   │   ├── dados/                  # guia de preparação dos dados
│   │   └── prompts/                # casos de teste do chat
│   ├── tools/                      # uma nota por fonte de dados + comparativos
│   └── others/                     # análise de ferramentas existentes
├── layout/                         # protótipo navegável (HTML e PDF): referência visual das telas
├── ToDo/                           # tarefas de dados com dono, uma pasta por tarefa
└── .deploy/                        # Docker, Caddy e scripts para subir na VPS
```

## Por onde começar

| Você quer… | Leia |
|---|---|
| Entender o desafio | [Texto oficial](docs/NasaSpaceApps-FieldShift/v1/desafio-oficial-nasa-field-shift.md) e [`CONTEXTO-DESAFIO.md`](docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md) |
| Saber o que já foi decidido | [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md) |
| Saber em que pé está | [`ANDAMENTO.md`](docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md) |
| Saber o que vamos construir | [`site-contexto.md`](docs/NasaSpaceApps-FieldShift/v1/application/site-contexto.md) e [`architecture/README.md`](docs/NasaSpaceApps-FieldShift/v1/application/architecture/README.md) |
| Mexer no código | [`agroai/README.md`](agroai/README.md) |
| Apresentar a demo | [`agroai/web-demo/README.md`](agroai/web-demo/README.md) |
| Subir na VPS | [`.deploy/README.md`](.deploy/README.md) |
| Ajudar com os dados | [`data/README.md`](data/README.md) e [`ToDo/README.md`](ToDo/README.md) |
| Saber como acessar uma fonte | a nota da fonte em [`tools/`](docs/NasaSpaceApps-FieldShift/v1/tools/) |

## Dados usados nesta versão

| Para quê | Fonte |
|---|---|
| Clima (chuva, temperatura, geada, calor; ET0 calculada pelo AgroAI) | NASA POWER |
| Relevo (declividade) | SRTM |
| Solo | SoilGrids |
| Previsão do tempo | Open-Meteo |

**Ficaram fora desta versão:** a umidade do solo (SMAP L4), o NDVI (MODIS, VIIRS e HLS) e a chuva de satélite (GPM IMERG) (ver D-009 em [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md)). Os dados do IBGE PAM, do ZARC e do USDA NASS estão preparados em `data/`, mas o motor ainda não os lê. As demais fontes da D-009 (ERA5, GLDAS, FAO GAEZ, NASA Harvest, MapBiomas, INMET/CEMADEN) são plano: o app não as usa.

A previsão do tempo dos próximos dias vem da **Open-Meteo**, porque a NASA não publica previsão. Ela já está no app, mas ainda não foi registrada no `DECISOES.md` (ver "Pontos em aberto").

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | React, Vite, TypeScript, Tailwind CSS, Leaflet (mapa) |
| Back-end | Python, FastAPI, SQLAlchemy, Alembic |
| Banco | PostgreSQL 17 com pgvector (VPS da equipe; local no Docker) |
| Login | Senha com hash argon2 + token JWT |
| IA (D-011) | Gemini: lê o texto livre do questionário e responde no chat, com embeddings para o RAG |
| Deploy | Docker Compose + Caddy (`.deploy/`) |

O visual segue o protótipo **Premium Playful** que está na pasta `layout/`: fundo creme, verde-folha, amarelo-sol, botões com "degrau" 3D, títulos em Bricolage Grotesque e texto em DM Sans.

## Pontos em aberto

Decisões que a equipe ainda precisa tomar ou registrar:

- **Previsão do tempo:** registrar a Open-Meteo no `DECISOES.md` (única fonte fora da D-009).
- **Numeração:** existem duas D-010 no `DECISOES.md`. Uma precisa ser renumerada.
- **Tabelas antigas no banco:** a VPS tem `propriedades` e `questionario_respostas`, que não são usadas pelo código. É preciso decidir se elas saem.
- **Produção:** a VPS precisa da extensão pgvector para as migrations a partir da `0003`.
- **Demo:** confirmar as regiões e os pontos de exemplo (Q-01 a Q-03) e o usuário da demo (Q-02).

A lista completa está em [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md), seção 3, e as pendências do dia a dia em [`ANDAMENTO.md`](docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md).

## Como contribuir

- Trabalhe numa branch (`feat/...`, `fix/...`, `docs/...`, `data/...`) e abra um PR para a `main`.
- **Nunca suba o `.env`** nem senhas. Use o `.env.example` como modelo.
- Rode os testes da API antes de abrir o PR (veja "Testes" em [`agroai/README.md`](agroai/README.md)).
- Decisões novas entram no `DECISOES.md` com número, status e motivo. Uma decisão que mudou não é apagada: ela é marcada como **Substituída**.
- Itens marcados com **[verificar]** precisam ser confirmados na fonte oficial antes de virar código ou entrar no pitch.
