# AgroIA: código

Este é o código do app. Por enquanto ele cobre a **parte 1 (login)** e a **parte 2 (questionário do produtor)**.
O que cada tela pergunta e por quê está em [`ONBOARDING.md`](../docs/NasaSpaceApps-FieldShift/v1/application/ONBOARDING.md).

## O que já funciona

- **Login:** criar conta, entrar, sair e apagar a conta com todos os dados. A sessão dura 7 dias.
- **Questionário:** os 6 blocos do `ONBOARDING.md` em 10 telas e um resumo. Cobre:
  - mapa com GPS;
  - respostas Sim / Não / Não sei;
  - calendário de 12 meses;
  - cor e jeito da terra;
  - perdas com o ano;
  - até 3 prioridades.
- **Salvamento por etapa:** o questionário salva a cada "Continuar", então dá para parar e voltar depois. Só conclui com o ponto marcado no mapa.
- **Texto livre com IA (perguntas 8, 26a e 26b):** o Gemini separa o que o produtor escreveu em itens da base, e o produtor confirma um por um.
  - Sem chave do Gemini, ou se ele falhar, o texto é casado pelos nomes conhecidos e o produtor completa pela lista.
- **Resumo final:** perfil do produtor (A, B ou C) e papel (produtor ou técnico), meses com a terra descoberta, retrato do solo e próximos passos sugeridos.

## Estrutura

```text
agroia/
├── api/                      # back-end (FastAPI)
│   ├── app/
│   │   ├── main.py           # cria a API e liga as rotas
│   │   ├── config.py         # lê o .env (banco, JWT, Gemini, CORS)
│   │   ├── db.py             # conexão com o PostgreSQL
│   │   ├── models.py         # tabelas: usuario, fazenda, calendario_item
│   │   ├── security.py       # senha (argon2) e token (JWT)
│   │   ├── base.py           # carrega culturas/equipamentos e casa nomes por sinônimo
│   │   ├── routers/          # rotas: auth, fazenda, onboarding
│   │   ├── onboarding/       # formato das respostas, perfil A–C, papel, retrato do solo
│   │   └── llm/              # texto livre -> lista (Gemini, com a lista como reserva)
│   ├── migrations/           # Alembic: cria e atualiza as tabelas
│   ├── tests/                # pytest (só rodam num Postgres local)
│   ├── .env.example          # modelo de configuração
│   └── .env.test             # configuração do banco local de teste (sem segredo real)
├── base/                     # culturas.json e equipamentos.json (sinônimos PT/EN/ES)
└── web/                      # front-end (React + Vite + TypeScript + Tailwind)
    └── src/
        ├── pages/            # Entrar (login e cadastro) e Dashboard (provisório)
        ├── onboarding/       # telas do questionário, mapa, calendário, seletor de meses
        ├── components/       # botões, cartões, ícones e ilustração (visual do protótipo)
        └── api/              # cliente da API, tipos e sessão de login
```

## Como rodar

**Pré-requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/) e Node 20+. No Arch: `sudo pacman -S nodejs npm uv`.

### 1. Configurar (só na primeira vez)

```bash
cd agroia/api
cp .env.example .env
```

Abra o `.env` e preencha:

| Variável | O que colocar |
|---|---|
| `DB_PASSWORD` | Senha do banco. Peça a quem cuida da VPS |
| `JWT_SECRET` | Gere com `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEMINI_API_KEY` | Opcional. Sem ela, o questionário usa a lista reserva |

> ⚠️ Rode o `cp` **só uma vez**: ele sobrescreve o `.env` e apaga o que você preencheu.

### 2. Subir a API (terminal 1)

```bash
cd agroia/api
uv sync                       # instala as dependências
uv run alembic upgrade head   # cria ou atualiza as tabelas no banco
uv run uvicorn app.main:app --reload --port 8000
```

A documentação interativa da API fica em http://localhost:8000/docs.

### 3. Subir o site (terminal 2)

```bash
cd agroia/web
npm install
npm run dev                   # http://localhost:5173
```

Se a API não estiver em `localhost:8000`, crie `web/.env` com `VITE_API_URL=<endereço da API>`.

## Testes

Os testes usam um PostgreSQL **local**, configurado em `api/.env.test` (porta 55433). O `conftest.py` se recusa a rodar se o banco não for local, para nunca apagar dados da VPS.

Para subir esse banco uma vez com Docker:

```bash
docker run -d --name agroia-teste -p 55433:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=agricultura \
  postgres:17

cd agroia/api
set -a; . ./.env.test; set +a; uv run alembic upgrade head   # cria as tabelas no banco de teste
uv run pytest
```

Os testes cobrem:
- **Login:** cadastro, e-mail repetido, senha errada, token inválido e apagar a conta.
- **Questionário:** salvamento parcial, conclusão, validações, regras do perfil, meses descobertos.
- **IA:** a IA não pode inventar culturas e, se cair, o app usa a lista reserva.

## Rotas da API

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/register` | Cria a conta e devolve o token |
| POST | `/auth/login` | Entra e devolve o token |
| GET | `/me` | Dados do usuário logado |
| DELETE | `/me` | Apaga a conta e todos os dados |
| GET | `/fazenda` | Questionário salvo, perfil e resumo |
| PUT | `/fazenda` | Salva o questionário (parcial, ou com `concluir: true`) |
| POST | `/onboarding/interpretar` | Texto livre → itens da base (perguntas 8, 26a e 26b) |
| GET | `/culturas`, `/equipamentos` | Listas reserva |
| GET | `/saude` | Mostra se a API está no ar |

Todas as rotas, menos login, cadastro, listas e `/saude`, exigem o header `Authorization: Bearer <token>`.

## Banco de dados

| Tabela | Guarda |
|---|---|
| `usuario` | Nome, e-mail, hash da senha, idioma |
| `fazenda` | Uma por usuário. Todas as respostas em JSONB (`respostas`), mais as colunas que o resto do sistema consulta: local, perfil, irrigação, animais, terreno, prioridades, culturas excluídas, equipamentos, retrato do solo |
| `calendario_item` | Cada cultura que o produtor confirmou, com os meses de plantio e colheita |

Para mudar uma tabela, altere `app/models.py` e gere uma migração:

```bash
uv run alembic revision --autogenerate -m "o que mudou"
```

Confira o arquivo gerado em `migrations/versions/` antes de rodar `alembic upgrade head`.

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `jwt_secret` ou `db_password` "should have at least…" | O `.env` está vazio ou foi sobrescrito pelo `cp`. Preencha de novo (passo 1) |
| `Address already in use` ao subir a API | Já tem algo na porta 8000. Feche o outro processo ou use `--port 8001` (e ajuste `VITE_API_URL`) |
| Site diz "Sem conexão com o servidor" | A API não está rodando, ou está noutro endereço. Confira com `curl localhost:8000/saude` |
| `ModuleNotFoundError: No module named 'app'` | Os comandos da API precisam rodar de dentro de `agroia/api` |
| Erro de conexão com o banco | Seu IP precisa estar liberado no firewall e no `pg_hba.conf` da VPS. Fale com quem cuida dela |

## Decisões desta parte

- **Uma fazenda por usuário**, marcada por um ponto no mapa (`lat`/`lon`). O PostGIS fica para quando houver consulta geográfica.
- **Token JWT** no header `Authorization: Bearer`, guardado no `localStorage` do navegador.
- **Privacidade:** ao Gemini vai só o texto da resposta, nunca nome, e-mail ou local. O nome do lugar é digitado pelo produtor; nenhum serviço de endereço recebe a localização.
- **Faixas de área (pergunta 2):** até 2 / 2–20 / 20–200 / 200–1.000 / mais de 1.000 ha.
- **Pergunta 19:** amostras de cor no lugar das fotos reais de solo, até as fotos de `data/onboarding/fotos-solo/` ficarem prontas.
- **Idioma:** só português nas telas por enquanto. A base de culturas já tem nomes em PT, EN e ES.
- **CORS:** em desenvolvimento, a API aceita o site em qualquer porta do `localhost`. Em produção, liste o domínio em `CORS_ORIGINS`.
