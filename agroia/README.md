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
│   ├── app/                  # em camadas: routers -> services -> repositories -> models
│   │   ├── main.py           # cria a API, liga as rotas e trata os erros de negócio
│   │   ├── core/             # config.py (.env), db.py (PostgreSQL), security.py (senha e JWT), erros.py
│   │   ├── models/           # tabelas: usuario.py, fazenda.py (fazenda, calendario_item), conhecimento.py (documento, trecho), agente.py (conversa, mensagem, busca_log), clima.py (clima_celula, clima_mensal), relevo.py (relevo_ponto)
│   │   ├── schemas/          # entrada e saída das rotas: auth.py, fazenda.py, onboarding.py (respostas), chat.py
│   │   ├── repositories/     # acesso ao banco: usuario, fazenda, conhecimento (busca híbrida), clima, conversa
│   │   ├── services/         # regras de negócio
│   │   │   ├── auth_service.py      # cadastro, login, apagar conta
│   │   │   ├── catalogo.py          # culturas/equipamentos (agroia/base) e casamento por sinônimo
│   │   │   ├── interpretacao.py     # texto livre -> lista (Gemini, com a lista como reserva)
│   │   │   ├── onboarding/          # perfil.py (perfil A–C, papel, retrato do solo), fazenda_service.py
│   │   │   ├── rag/                 # base de conhecimento: chunker, embeddings (Gemini), fontes, ingestao
│   │   │   ├── conversa_service.py  # conversas do usuário (criar, listar, abrir, apagar)
│   │   │   ├── agente/              # o chat: agente_service.py (laço do Gemini), ferramentas.py, prompt.py, modelo.py, busca_conhecimento_service.py
│   │   │   ├── clima/               # célula da grade, ET0 (FAO-56), limites, agregação mensal, graus_dia.py, clima_service.py
│   │   │   ├── motor/               # base do motor de rotação: catalogo.py (CSV do BR e dos EUA), local.py (país e município/condado), relevo_service.py
│   │   │   └── integracao/          # nasa_power.py (NASA POWER), srtm.py (declividade, OpenTopoData)
│   │   ├── cli/              # comandos: rag.py (ingerir, buscar), clima.py (baixar, mostrar, demo)
│   │   └── routers/          # rotas (só HTTP): auth, fazenda, onboarding, chat
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
  pgvector/pgvector:pg17   # Postgres com a extensão vector (base de conhecimento do RAG)

cd agroia/api
set -a; . ./.env.test; set +a; uv run alembic upgrade head   # cria as tabelas no banco de teste
uv run pytest
```

Os testes cobrem:
- **Login:** cadastro, e-mail repetido, senha errada, token inválido e apagar a conta.
- **Questionário:** salvamento parcial, conclusão, validações, regras do perfil, meses descobertos.
- **IA:** a IA não pode inventar culturas e, se cair, o app usa a lista reserva.
- **Chat:** rotas das conversas, 404 para conversa de outro usuário, e o agente com modelo falso (ferramentas, fontes, histórico, limite de rodadas, 503 sem gravar nada).

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
| GET | `/chat/conversas` | Lista as conversas do usuário (mais recente primeiro) |
| POST | `/chat/conversas` | Cria uma conversa vazia (201) |
| GET | `/chat/conversas/{id}` | Abre a conversa com as mensagens visíveis |
| POST | `/chat/conversas/{id}/mensagens` | Envia `{"mensagem": "..."}` (1 a 2000 caracteres) e devolve a resposta do assistente |
| DELETE | `/chat/conversas/{id}` | Apaga a conversa (204) |
| GET | `/saude` | Mostra se a API está no ar |

Todas as rotas, menos login, cadastro, listas e `/saude`, exigem o header `Authorization: Bearer <token>`.

## Banco de dados

| Tabela | Guarda |
|---|---|
| `usuario` | Nome, e-mail, hash da senha, idioma |
| `fazenda` | Uma por usuário. Todas as respostas em JSONB (`respostas`), mais as colunas que o resto do sistema consulta: local, `pais` (`BR`/`US`) e `codigo_local` (município IBGE de 7 dígitos ou condado FIPS de 5, calculados ao salvar o local; `NULL` fora das malhas), perfil, irrigação, animais, terreno, prioridades, culturas excluídas, equipamentos, retrato do solo |
| `calendario_item` | Cada cultura que o produtor confirmou, com os meses de plantio e colheita |
| `documento` | Cada texto da base de conhecimento (glossário, metodologia, culturas, satélites), com fonte, caminho de origem e hash do conteúdo |
| `trecho` | Pedaços de um documento com embedding (`vector(768)`) e busca textual em português |
| `conversa` | Uma conversa do chat: dono (`usuario_id`), título (início da primeira pergunta) e datas. Apaga junto com a conta |
| `mensagem` | Cada turno do Gemini (`papel` `user`/`model`), com o `Content` completo em JSONB (inclui as chamadas de ferramenta, que voltam no histórico), `visivel` (só a pergunta e a resposta final), texto, fontes, ferramentas usadas e tokens |
| `busca_log` | Cada busca na base de conhecimento: conversa, palavras do produtor, consulta, trechos devolvidos e descartados |
| `clima_celula` | Uma célula da grade do NASA POWER (0,5° × 0,625°, ~50 km): centro, elevação, período baixado, limite de chuva forte (P95 de 1991–2020) e fonte. Fazendas vizinhas dividem a mesma linha |
| `clima_mensal` | Por célula, ano e mês: chuva, ET0, temperaturas (média, média das máximas e mínimas, extremos), dias de geada (Tmin < 2 °C), de calor (Tmax > 35 °C) e de chuva forte, maior sequência seca (< 1 mm) e dias válidos. Sem dado fica `NULL`, nunca 0. `gd_por_tb`: graus-dia do mês para cada temperatura-base inteira de 0 a 20 °C (JSONB, sem teto); `{}` = mês sem temperatura completa, `NULL` = célula baixada antes da coluna (é baixada de novo) |
| `relevo_ponto` | Cache da declividade do SRTM por ponto (lat/lon com 4 casas): `declividade_pct`, classe da Embrapa e fonte |

## Base de conhecimento (RAG)

Os textos listados em `api/app/services/rag/fontes.py` (os de `data/rag/`) viram trechos com embedding do Gemini (`gemini-embedding-001`, 768 dimensões). Precisa de `GEMINI_API_KEY` no `.env` e do banco com a extensão `vector`.

```bash
cd agroia/api
uv run python -m app.cli.rag ingerir                 # grava só o que mudou (compara o hash); pula arquivo que ainda não existe
uv run python -m app.cli.rag ingerir --forcar        # regrava tudo
uv run python -m app.cli.rag buscar "veranico no milho" --tipo glossario   # testa uma busca
```

Documento que sai da lista de fontes é removido do banco na próxima ingestão. Os testes usam um embedder falso: não gastam a API.

## Chat (agente)

Um agente com 4 ferramentas, executadas pelo nosso código (o Gemini só pede a chamada): `ver_ficha`, `info_cultura`, `buscar_conhecimento` e `consultar_clima`. Os números vêm das ferramentas, e cada resposta devolve as `fontes` e as `ferramentas_usadas` delas, nunca do texto do modelo. Regras (não prescreve, não faz previsão, não inventa número) em `app/services/agente/prompt.py`.

- Precisa de `GEMINI_API_KEY` (e `GEMINI_MODEL`) no `.env` e das tabelas da base de conhecimento e do clima. Sem a chave, `POST .../mensagens` responde 503.
- Até 5 rodadas de ferramenta por pergunta. Se o assistente falhar ou estourar o limite, a resposta é 503 e **nada** daquela pergunta fica gravado.
- Ao Gemini vai só o texto da conversa e um resumo da fazenda: nunca nome, e-mail ou coordenada exata (a ficha vai com o local arredondado a 0,1°).
- Os testes usam um modelo falso roteirizado, um NASA POWER falso e um embedder falso: não gastam API nem rede.

## Clima (NASA POWER)

O clima de um ponto vem da API pública do NASA POWER (não precisa de chave). A API chama a célula pelo centro e baixa a série diária de 1991-01-01 até 31/12 do último ano completo, uma vez por célula; depois só relê o banco. A ET0 é calculada aqui (FAO-56 Penman-Monteith). Os critérios de geada, calor, chuva forte e sequência seca estão em `data/rag/metodologia-indicadores.md`.

```bash
cd agroia/api
uv run alembic upgrade head                                  # cria clima_celula e clima_mensal
uv run python -m app.cli.clima baixar --lat -11.31 --lon -41.81   # baixa e guarda a célula do ponto
uv run python -m app.cli.clima mostrar --lat -11.31 --lon -41.81  # climatologia mensal 1991–2020, com fonte e período
uv run python -m app.cli.clima demo                          # baixa e mostra os 3 pontos de data/demo/pontos_demo.csv
```

Os testes do clima usam respostas simuladas: não acessam a rede.

## Base do motor de rotação

- **Catálogo:** `app/services/motor/catalogo.py` lê `data/catalogo/culturas.csv` (Brasil) e, se existir, `data/catalogo/eua/culturas.csv`; sem o arquivo dos EUA o catálogo do país vem vazio, com aviso. `cultura_equipamentos.csv` dá os equipamentos de plantio e colheita de cada cultura.
- **País e local:** `app/services/motor/local.py` acha o município (`data/brasil/municipios/municipios.geojson`) ou o condado (`data/eua/condados/condados.geojson`) do ponto com `shapely` (dependência nova, índice STRtree). Fora das duas malhas: sem país.
- **Graus-dia:** `app/services/clima/graus_dia.py`, GD = soma de max(0, Tmed − Tb), sem teto, com Tmed = (Tmax + Tmin) / 2, a mesma conta de `data/catalogo/scripts/gd_nasa_power.py`. Gravado por mês para Tb de 0 a 20 °C; Tb fracionária é interpolada entre as inteiras vizinhas.
- **Declividade:** SRTM 30 m pelo OpenTopoData (sem chave, 1 chamada por segundo), grade 3×3 de ~30 m e método de Horn; classes da Embrapa. Se falhar, vale a resposta da pergunta 7, com a fonte marcada.
- Fazendas que já existiam ganham `pais` e `codigo_local` na migration `0006` (ou no próximo salvar, se as malhas não estiverem no disco).

Para mudar uma tabela, altere o model em `app/models/` e gere uma migração:

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
