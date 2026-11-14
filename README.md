# Field Shift · AgroIA

Projeto da equipe para o **NASA Space Apps Challenge 2026**, desafio **[Field Shift: Adapting Farms with NASA Data](docs/NasaSpaceApps-FieldShift/v1/desafio-oficial-nasa-field-shift.md)**.

## O problema

Clima mudando, chuva irregular, falta de água e solo se desgastando tornam difícil escolher **o que plantar e quando**. O desafio pede uma ferramenta de apoio à decisão que use dados de satélite da NASA, o solo local, as características das culturas e as prioridades do produtor. Ela deve **comparar pelo menos 3 estratégias de rotação de culturas, incluindo a atual**, e explicar para cada uma o porquê, a evidência, os benefícios, as lacunas e os riscos.

## A solução: AgroIA

Um site, pensado primeiro para o celular, em que o produtor:

1. **Responde um questionário curto** sobre a fazenda: local, o que planta e quando, o que sabe do solo e suas prioridades.
2. **Acompanha um Dashboard** com clima, umidade do solo, saúde da lavoura, alertas e a comparação de estratégias de rotação, tudo a partir de dados da NASA.
3. **Conversa com a AgroIA**, um assistente que conhece a fazenda dele e explica os dados em linguagem simples, citando a fonte.

> A ferramenta **apoia, não decide**. A palavra final é do produtor e do técnico local.

## Status

| Parte | O que é | Situação |
|---|---|---|
| 1 | Login e cadastro | ✅ Pronta |
| 2 | Questionário do produtor (onboarding) | ✅ Pronta |
| 3 | Coleta dos dados da NASA e Dashboard | ⏳ A fazer (hoje a tela é provisória) |
| 4 | Comparação de 3 estratégias de rotação | ⏳ A fazer |
| 5 | Chat AgroIA (RAG) | ⏳ A fazer |

O banco de produção é um PostgreSQL 17 numa VPS da equipe, com as tabelas das partes 1 e 2 já criadas.

## Rodar o app

Precisa de Python 3.12+, [uv](https://docs.astral.sh/uv/) e Node 20+. O passo a passo completo, os testes e a solução de problemas comuns estão em **[`agroia/README.md`](agroia/README.md)**.

```bash
# 1. API (terminal 1)
cd agroia/api
cp .env.example .env              # só na primeira vez; peça a senha do banco a quem cuida da VPS
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# 2. Site (terminal 2)
cd agroia/web
npm install
npm run dev                       # abre em http://localhost:5173
```

## Estrutura do repositório

```text
.
├── agroia/                         # 💻 o código do app
│   ├── api/                        # back-end: FastAPI + PostgreSQL
│   ├── web/                        # front-end: React + Vite + TypeScript
│   └── base/                       # culturas e equipamentos usados pelo questionário
├── layout/                         # 🎨 protótipo navegável (HTML e PDF): referência visual das telas
├── data/                           # 📦 dados preparados pela equipe (catálogo, demo, RAG, fotos de solo)
│   └── README.md                   # divisão das tarefas de dados entre 3 pessoas
└── docs/NasaSpaceApps-FieldShift/v1/
    ├── desafio-oficial-nasa-field-shift.md   # texto oficial do desafio
    ├── context/                    # o problema e as decisões
    │   ├── DECISOES.md             # ⭐ decisões da equipe (D-xxx) e perguntas em aberto (Q-xx)
    │   ├── CONTEXTO-DESAFIO.md     # requisitos, conceitos e indicadores
    │   └── BANCO_DE_DADOS_NASA.md  # datasets e ferramentas
    ├── application/                # o produto
    │   ├── site-contexto.md        # especificação do AgroIA (telas, chat, API, dados)
    │   ├── ONBOARDING.md           # questionário do primeiro acesso (implementado na parte 2)
    │   ├── DOR-DO-AGRICULTOR-E-CASO-DE-USO.md   # dores do produtor + caso da Dona Marta
    │   ├── architecture/           # coleta, integração de dados, motor, dashboard/chat, banco
    │   ├── dados/                  # guia de preparação dos dados
    │   └── prompts/                # casos de teste do chat
    ├── tools/                      # uma nota por fonte de dados + comparativos
    ├── others/                     # análise de ferramentas existentes
    └── .md/ e .pdf/                # guias de estudo (explicado do zero, glossário)
```

## Por onde começar

| Você quer… | Leia |
|---|---|
| Entender o desafio do zero | [Desafio explicado do zero](docs/NasaSpaceApps-FieldShift/v1/.md/desafio-field-shift-nasa-space-apps-explicado-do-zero.md) |
| Saber o que já foi decidido | [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md) |
| Saber o que vamos construir | [`site-contexto.md`](docs/NasaSpaceApps-FieldShift/v1/application/site-contexto.md) e [`architecture/README.md`](docs/NasaSpaceApps-FieldShift/v1/application/architecture/README.md) |
| Mexer no código | [`agroia/README.md`](agroia/README.md) |
| Ajudar com os dados | [`data/README.md`](data/README.md) e o [guia de preparação](docs/NasaSpaceApps-FieldShift/v1/application/dados/GUIA-PREPARACAO-DADOS.md) |
| Saber como acessar uma fonte | a nota da fonte em [`tools/`](docs/NasaSpaceApps-FieldShift/v1/tools/) |

## Dados principais (D-009)

| Para quê | Fonte |
|---|---|
| Clima | NASA POWER, ERA5 |
| Chuva | GPM IMERG |
| Água no solo | SMAP L4, GLDAS |
| Vegetação (NDVI) | MODIS, HLS |
| Relevo | SRTM |
| Solo e aptidão | SoilGrids, FAO GAEZ v5 |
| Mercado | NASA Harvest Portal |
| Brasil (uso do solo, validação) | MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM |
| Acesso | Earthdata, earthaccess, AppEEARS |

A previsão do tempo dos próximos dias deve vir da **Open-Meteo**, porque a NASA não publica previsão. Isso ainda precisa ser aprovado (ver "Pontos em aberto").

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | React, Vite, TypeScript, Tailwind CSS, Leaflet (mapa) |
| Back-end | Python, FastAPI, SQLAlchemy, Alembic |
| Banco | PostgreSQL 17 (VPS da equipe) |
| Login | Senha com hash argon2 + token JWT |
| IA | Gemini (lê o texto livre do questionário; depois, o chat) |

O visual segue o protótipo **Premium Playful** que está na pasta `layout/`: fundo creme, verde-folha, amarelo-sol, botões com "degrau" 3D, títulos em Bricolage Grotesque e texto em DM Sans.

## Pontos em aberto

Decisões que a equipe ainda precisa tomar:

- **Escopo:** Brasil inteiro (D-008) ou mundo todo (`site-contexto.md`)? O código já aceita qualquer ponto do mapa.
- **IA:** o código usa Gemini, mas o `architecture/README.md` fala em Claude. Falta registrar a escolha no `DECISOES.md`.
- **Previsão do tempo:** aprovar a Open-Meteo (única fonte fora da D-009).
- **Catálogo de culturas duplicado:** o app usa `agroia/base/culturas.json` (40 culturas com sinônimos em PT/EN/ES). Em paralelo, `data/catalogo/` tem 16 culturas com parâmetros agronômicos. É preciso juntar os dois numa fonte só.
- **Tabelas antigas no banco:** a VPS tem `propriedades` e `questionario_respostas`, que não são usadas pelo código. É preciso decidir se elas saem.
- **Questionário:** as perguntas estão escritas direto nas telas. O `data/onboarding/perguntas.yaml` propõe tirá-las de um arquivo.
- **Demo:** quais regiões e fazendas de exemplo (Q-01 a Q-03)?
- **Pendências do questionário:** fotos reais de solo (pergunta 19), validar as faixas de área (pergunta 2) e a tabela cor × jeito da terra.

A lista completa está em [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md), seção 3.

## Como contribuir

- Trabalhe numa branch (`feat/...`, `fix/...`, `docs/...`, `data/...`) e abra um PR para a `main`.
- **Nunca suba o `.env`** nem senhas. Use o `.env.example` como modelo.
- Rode os testes da API antes de abrir o PR (`cd agroia/api && uv run pytest`).
- Decisões novas entram no `DECISOES.md` com número, status e motivo. Uma decisão que mudou não é apagada: ela é marcada como **Substituída**.
- Itens marcados com **[verificar]** precisam ser confirmados na fonte oficial antes de virar código ou entrar no pitch.
