# AgroIA: código

Primeira parte do app: **login** e **coleta de dados do produtor** (onboarding).
O que cada tela pergunta e por quê está em `docs/NasaSpaceApps-FieldShift/v1/application/ONBOARDING.md`.

```text
agroia/
├── api/                  # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── main.py       # cria a API e liga as rotas
│   │   ├── config.py     # lê o .env (banco, JWT, Gemini)
│   │   ├── models.py     # tabelas: usuario, fazenda, calendario_item
│   │   ├── security.py   # senha (argon2) e token (JWT)
│   │   ├── base.py       # base de culturas/equipamentos e casamento por sinônimos
│   │   ├── routers/      # auth, fazenda, onboarding
│   │   ├── onboarding/   # formato das respostas, perfil A–D, retrato do solo
│   │   └── llm/          # texto livre -> lista (Gemini, com a lista como reserva)
│   ├── migrations/       # Alembic (criação das tabelas)
│   └── tests/            # pytest (rodam num Postgres local, nunca na VPS)
├── base/                 # culturas.json e equipamentos.json (sinônimos PT/EN/ES)
└── web/                  # React + Vite + TypeScript + Tailwind + Leaflet
    └── src/
        ├── pages/        # Entrar (login/cadastro), Dashboard (provisório)
        ├── onboarding/   # as 10 telas do questionário + resumo
        ├── components/   # botões, cartões, ícones (estética do protótipo em /layout)
        └── api/          # cliente REST e sessão
```

## Rodar

Pré-requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
# API
cd agroia/api
cp .env.example .env        # preencha DB_PASSWORD, JWT_SECRET e (opcional) GEMINI_API_KEY
uv sync
uv run alembic upgrade head # cria/atualiza as tabelas no banco do .env
uv run uvicorn app.main:app --reload --port 8000

# Front (outro terminal)
cd agroia/web
npm install
npm run dev                 # http://localhost:5173
```

Documentação interativa da API: http://localhost:8000/docs

## Testes

Os testes precisam de um Postgres **local** (configurado em `api/.env.test`, porta 55433).
O `conftest.py` se recusa a rodar se o host não for local.

```bash
cd agroia/api && uv run pytest
```

## Rotas

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/register` | Cria conta → token |
| POST | `/auth/login` | Entra → token |
| GET / DELETE | `/me` | Usuário logado / apaga conta e dados |
| GET / PUT | `/fazenda` | Lê / salva o questionário (parcial ou `concluir: true`) |
| POST | `/onboarding/interpretar` | Texto livre → itens da base (perguntas 8, 26a, 26b) |
| GET | `/culturas`, `/equipamentos` | Listas reserva |

## Decisões tomadas nesta parte

- Uma fazenda por usuário, um ponto no mapa (`lat`/`lon`). PostGIS fica para quando houver consulta geográfica.
- Respostas completas em JSONB (`fazenda.respostas`); o que o resto do sistema consulta virou coluna.
- Token JWT no header `Authorization: Bearer`, guardado no `localStorage` do navegador.
- Ao Gemini vai só o texto da resposta, nunca nome, e-mail ou local.
- Faixas de área (pergunta 2): até 2 / 2–20 / 20–200 / 200–1.000 / mais de 1.000 ha.
- Pergunta 19 usa amostras de cor no lugar das fotos reais de solo (pendência do ONBOARDING.md).
