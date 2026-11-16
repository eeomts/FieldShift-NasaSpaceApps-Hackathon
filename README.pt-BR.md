# Field Shift · AgroAI

Projeto da equipe para o **NASA Space Apps Challenge 2026**, desafio **[Field Shift: Adapting Farms with NASA Data](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=details)**.

## O problema

Clima mudando, chuva irregular, falta de água e solo se desgastando tornam difícil escolher **o que plantar e quando**. O desafio pede uma ferramenta de apoio à decisão que use dados de satélite da NASA, o solo local, as características das culturas e as prioridades do produtor. Ela deve **comparar pelo menos 3 estratégias de rotação de culturas, incluindo a atual**, e explicar para cada uma o porquê, a evidência, os benefícios, as lacunas e os riscos.

## A solução: AgroAI

Um site em português e inglês, pensado primeiro para o celular, para pequenos e médios produtores do Brasil e dos EUA. Nele o produtor:

1. **Responde um questionário curto** sobre a fazenda: local, o que planta e quando, o que sabe do solo e suas prioridades.
2. **Acompanha um painel (dashboard)** com o retrato do solo, o clima do local (NASA POWER), a umidade do solo (SMAP), o verde da lavoura (NDVI do MODIS), a chuva recente (GPM IMERG), o relevo (SRTM), a previsão do tempo e a comparação da rotação atual com duas alternativas.
3. **Conversa com a AgroAI**, um assistente que conhece a fazenda dele e explica os dados em linguagem simples, citando a fonte.

> A ferramenta **apoia, não decide**. A palavra final é do produtor e do técnico local. Todo número tem fonte, e a IA nunca calcula nem inventa número.

## Status

| Parte | O que é | Situação |
|---|---|---|
| 1 | Login e cadastro | Pronta |
| 2 | Questionário do produtor (onboarding), em PT e EN | Pronta |
| 3 | Dados: clima (NASA POWER), relevo (SRTM), solo (SoilGrids); no painel, umidade do solo (SMAP), NDVI (MODIS) e chuva recente (GPM IMERG), com token do Earthdata | Pronta (solo em revisão) |
| 4 | Comparação de 3 estratégias de rotação (motor) | Pronta a v1; v2 em andamento |
| 5 | Chat AgroAI com base de conhecimento (RAG) | Pronta |
| — | Versão de apresentação (`agroai/web-demo`) | Pronta |

O que funciona, o que é parcial e o que vem depois está em [`docs/05-limitations-roadmap.md`](docs/05-limitations-roadmap.md).

## As duas interfaces

| | `agroai/web` (completa) | `agroai/web-demo` (apresentação) |
|---|---|---|
| Para quê | Uso real e desenvolvimento | Demonstração para a NASA |
| Entrada | E-mail e senha | Só o nome |
| Questionário | Em branco | Já preenchido (fazenda de exemplo em Iowa), com o botão **Skip All** |
| Endereço local | http://localhost:5173 | http://localhost:5174 |
| Deploy na VPS (`.deploy/`) | https://agroai.mateusmoreira.dev | https://demo-agroai.mateusmoreira.dev |

As duas usam a mesma API e o mesmo banco, também no deploy (o mesmo Caddy serve os dois domínios). Detalhes da versão de apresentação em [`agroai/web-demo/README.md`](agroai/web-demo/README.md).

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
├── docs/                           # documentação da submissão (01 a 08, em inglês) e o texto do formulário
└── .deploy/                        # Docker, Caddy e scripts para subir na VPS
```

## Por onde começar

| Você quer… | Leia |
|---|---|
| Entender o desafio e a solução | [Texto oficial](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=details) e [`docs/01-overview.md`](docs/01-overview.md) |
| Saber como funciona | [`docs/02-how-it-works.md`](docs/02-how-it-works.md) e [`docs/04-methodology.md`](docs/04-methodology.md) |
| Saber em que pé está | [`docs/05-limitations-roadmap.md`](docs/05-limitations-roadmap.md) |
| Mexer no código | [`agroai/README.md`](agroai/README.md) |
| Apresentar a demo | [`agroai/web-demo/README.md`](agroai/web-demo/README.md) |
| Subir na VPS | [`.deploy/README.md`](.deploy/README.md) |
| Ajudar com os dados | [`data/README.md`](data/README.md) |
| Saber de onde vem cada dado | [`docs/03-nasa-data.md`](docs/03-nasa-data.md), [`docs/06-references.md`](docs/06-references.md) e [`data/FONTES.md`](data/FONTES.md) |

## Dados usados nesta versão

| Para quê | Fonte |
|---|---|
| Clima (chuva, temperatura, geada, calor; ET0 calculada pelo AgroAI) | NASA POWER |
| Relevo (declividade) | SRTM |
| Solo | SoilGrids |
| Previsão do tempo | Open-Meteo |
| Umidade do solo hoje x anos anteriores (só no painel) | SMAP L4 (SPL4SMGP) |
| Verde da lavoura nos últimos 12 meses (só no painel) | MODIS MOD13Q1 (NDVI) |
| Chuva dos últimos 30 dias (só no painel) | GPM IMERG; sem o token do Earthdata, NASA POWER |

SMAP, MODIS e GPM IMERG são lidos ao vivo do NASA Earthdata e precisam do token no servidor. Eles aparecem **só no painel**: o motor de rotação e o chat ainda não usam esses números. As janelas de semeadura dos EUA (USDA NASS, Handbook 628) estão transcritas no catálogo de culturas. Os dados do IBGE PAM, das tábuas do ZARC e do NASS Quick Stats são gerados pelos scripts de `data/scripts/`, mas o motor ainda não os lê. ERA5, GLDAS, FAO GAEZ, NASA Harvest, VIIRS, HLS, MapBiomas e INMET/CEMADEN não são usados.

A previsão do tempo dos próximos dias vem da **Open-Meteo**, porque a NASA não publica previsão.

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | React, Vite, TypeScript, Tailwind CSS, Leaflet (mapa) |
| Back-end | Python, FastAPI, SQLAlchemy, Alembic |
| Banco | PostgreSQL 17 com pgvector (VPS da equipe; local no Docker) |
| Login | Senha com hash argon2 + token JWT |
| IA (D-011) | Gemini: lê o texto livre do questionário e responde no chat, com embeddings para o RAG |
| Deploy | Docker Compose + Caddy (`.deploy/`) |

O visual segue o estilo **Premium Playful**: fundo creme, verde-folha, amarelo-sol, botões com "degrau" 3D, títulos em Bricolage Grotesque e texto em DM Sans.

## Como contribuir

- Trabalhe numa branch (`feat/...`, `fix/...`, `docs/...`, `data/...`) e abra um PR para a `main`.
- **Nunca suba o `.env`** nem senhas. Use o `.env.example` como modelo.
- Rode os testes da API antes de abrir o PR (veja "Testes" em [`agroai/README.md`](agroai/README.md)).
- Itens marcados com **[verificar]** precisam ser confirmados na fonte oficial antes de virar código ou entrar no pitch.
