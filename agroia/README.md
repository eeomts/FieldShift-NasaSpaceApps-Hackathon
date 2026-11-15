# AgroAI: código

Este é o código do app: login, questionário do produtor, Dashboard e a aba AgroAI (chat), em português e inglês.
O que cada tela pergunta e por quê está em [`ONBOARDING.md`](../docs/NasaSpaceApps-FieldShift/v1/application/ONBOARDING.md).

## O que já funciona

- **Login:** criar conta, entrar, sair e apagar a conta com todos os dados. A sessão dura 7 dias.
- **Questionário (visual do protótipo v3):** uma pergunta por tela, 23 perguntas em 6 partes, seguindo `data/onboarding/perguntas.yaml`. Cobre:
  - local por busca, mapa ou GPS, com país, hemisfério e zona climática (Köppen) do ponto;
  - respostas Sim / Não / Não sei, e os sinais do solo numa grade;
  - calendário de 12 meses, com o texto livre separado em culturas;
  - fotos reais da cor e do jeito da terra;
  - perdas de safra com o ano de cada uma, mostradas conforme o clima (geada, salinidade);
  - área em hectares ou acres, e até 3 prioridades.
- **Português e inglês:** botão PT/EN em todas as telas. O idioma fica salvo na conta e o chat responde no idioma escolhido.
- **Salvamento por etapa:** o questionário salva a cada "Continuar", então dá para parar e voltar depois. Só conclui com o ponto marcado no mapa.
- **Texto livre com IA (culturas, culturas que não planta e máquinas):** o Gemini separa o que o produtor escreveu em itens da base, e o produtor confirma um por um.
  - Sem chave do Gemini, ou se ele falhar, uma reserva sem IA casa os nomes, os meses, as estações e os consórcios.
- **Resumo final:** perfil do produtor (A, B ou C) e papel (produtor ou técnico), calendário, retrato do solo e próximos passos.
- **Dashboard:** o que vem do questionário é real, e a comparação de rotações ("Suas estratégias") é calculada com dados da NASA. Previsão, umidade e NDVI ainda são **exemplo**, e a tela avisa.
- **Aba AgroAI (`/agroia`):** chat com a lista de conversas. "Perguntar à AgroAI" no Dashboard abre o chat e já envia a pergunta.

## Como rodar

**Pré-requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+ e Docker. No Arch: `sudo pacman -S nodejs npm uv docker`.

Há dois jeitos. Para desenvolver, use o **A**: tudo roda no seu computador, não mexe nos dados da equipe e não gasta nada.

### A. Tudo no seu computador (recomendado)

Usa um PostgreSQL local (container `agroia-dev`, porta 55432) e o arquivo `api/.env.dev`, que **vence o `.env`**: o banco é o local e o Gemini fica desligado (sem custo). O chat, então, responde "AgroAI indisponível". O resto do app funciona inteiro.

**Só na primeira vez**, suba o banco:

```bash
docker run -d --name agroia-dev -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17
```

Depois de reiniciar o computador, basta `docker start agroia-dev`.

**Terminal 1: API** (os comandos funcionam no bash, no zsh e no fish)

```bash
cd agroia/api
uv sync                                                  # instala as dependências
env $(grep -v '^#' .env.dev) uv run alembic upgrade head # cria ou atualiza as tabelas no banco local
env $(grep -v '^#' .env.dev) uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2: site**

```bash
cd agroia/web
npm install
npm run dev                   # abra http://localhost:5173
```

Crie uma conta no site: ela fica só no seu banco local. A documentação interativa da API fica em http://localhost:8000/docs.

> Para testar o chat de verdade, troque `GEMINI_API_KEY=` no `.env.dev` pela sua chave. **Cada mensagem gasta a cota do Gemini.**

### B. Contra o banco da VPS

> ⚠️ Hoje não funciona: o banco da VPS está na migração `0001`, e a `0003` precisa da extensão `vector` (pgvector), que a VPS ainda não tem. Quem cuida da VPS precisa instalar o pgvector antes.

1. Na primeira vez, copie o modelo de configuração:

   ```bash
   cd agroia/api
   cp .env.example .env
   ```

2. Abra o `.env` e preencha:

| Variável | O que colocar |
|---|---|
| `DB_PASSWORD` | Senha do banco. Peça a quem cuida da VPS |
| `JWT_SECRET` | Gere com `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEMINI_API_KEY` | Opcional. Sem ela, o questionário usa a reserva sem IA e o chat responde 503 |

> ⚠️ Rode o `cp` **só uma vez**: ele sobrescreve o `.env` e apaga o que você preencheu.

3. Suba a API como no jeito A, só que sem o `env $(...)` na frente:

   ```bash
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload --port 8000
   ```

4. Suba o site igual ao jeito A.

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
- **v3:** idioma da conta, `q21_correcao` (e o formato antigo), novas perdas, zona Köppen com séries sintéticas, `/local/*` com cliente HTTP falso e a reserva sem IA (meses, estações, consórcio, motivo). Nenhum teste chama a internet nem o Gemini.
- **Motor de rotação:** catálogo, filtros, critérios, pontuação, relevo e a rota `/fazenda/estrategias`.
- **Chat:** rotas das conversas, 404 para conversa de outro usuário, e o agente com modelo falso (ferramentas, fontes, histórico, limite de rodadas, 503 sem gravar nada).

## Rotas da API

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/register` | Cria a conta e devolve o token |
| POST | `/auth/login` | Entra e devolve o token |
| GET | `/me` | Dados do usuário logado |
| PATCH | `/me` | Troca o idioma da conta: `{"idioma": "pt" \| "en"}` |
| DELETE | `/me` | Apaga a conta e todos os dados |
| GET | `/fazenda` | Questionário salvo, perfil, resumo, `status_processamento` (`pendente`, `processando`, `pronto`, `erro`) e o retrato do solo (`indicadores`, `figuras`, `sintese`, `soilgrids`) |
| PUT | `/fazenda` | Salva o questionário (parcial, ou com `concluir: true`). Com local novo, responde na hora com `status_processamento: "processando"` e busca o solo no SoilGrids em segundo plano (veja "Solo") |
| GET | `/fazenda/estrategias` | Compara a rotação atual com as 2 melhores alternativas, na hora (a 1ª vez numa região baixa o NASA POWER, 10–30 s). Erros: 404 sem fazenda, 422 sem local / sem culturas da região / sem calendário, 503 se o NASA POWER falhar |
| POST | `/onboarding/interpretar` | Texto livre → itens da base (perguntas 8, 26a e 26b). Aceita `hemisferio` (`N`/`S`) e `idioma` (`pt`/`en`) |
| GET | `/culturas`, `/equipamentos` | Listas reserva (`?idioma=pt\|en`) |
| GET | `/local/buscar?q=&idioma=` | Busca cidade ou região (OpenStreetMap / Nominatim), até 5 resultados. Falha → lista vazia |
| GET | `/local/info?lat=&lon=&idioma=` | Hemisfério, zona climática Köppen (climatologia do NASA POWER), lugar, país e se já houve geada no histórico. Cada campo vira `null` se o serviço falhar |
| GET | `/chat/conversas` | Lista as conversas do usuário (mais recente primeiro) |
| POST | `/chat/conversas` | Cria uma conversa vazia (201) |
| GET | `/chat/conversas/{id}` | Abre a conversa com as mensagens visíveis |
| POST | `/chat/conversas/{id}/mensagens` | Envia `{"mensagem": "...", "idioma": "pt" | "en"}` (1 a 2000 caracteres; sem `idioma`, vale o da conta) e devolve a resposta do assistente |
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
| `solo_ponto` | Cache do SoilGrids por ponto (lat/lon com 3 casas) e **propriedade** (`clay`, `sand`, `silt`, `soc`, `phh2o`, `bdod`, `cec`): média de 0–30 cm (`superficial`) e de 0–100 cm (`raizes`) já convertidas, a incerteza relativa de cada e a fonte. Cada propriedade é gravada assim que chega (a busca retoma de onde parou). Ponto sem dado no mapa (área urbana ou água) também é guardado, com `sem_dado = true` |

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

Um agente com 5 ferramentas, executadas pelo nosso código (o Gemini só pede a chamada): `ver_ficha`, `info_cultura`, `buscar_conhecimento`, `consultar_clima` e `comparar_estrategias` (roda o motor de rotação na fazenda do usuário e devolve as notas de 0 a 100, o por que e o onde piora; a fonte sai com `tipo: "analise"`). Os números vêm das ferramentas, e cada resposta devolve as `fontes` e as `ferramentas_usadas` delas, nunca do texto do modelo. Regras (não prescreve, não faz previsão, não inventa número) em `app/services/agente/prompt.py`.

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

## Solo (SoilGrids)

O solo por ponto vem da API REST do ISRIC (`/soilgrids/v2.0/properties/query`, sem chave): argila, areia, silte, carbono, pH, CTC e densidade, nas profundidades de 0 a 100 cm, com média e quantis 0,05, 0,50 e 0,95 (nitrogênio e pedregosidade ficaram de fora: nada os usa ainda). Os números chegam em "unidades mapeadas" e são convertidos (argila, areia, silte, carbono, pH e CTC ÷ 10; densidade ÷ 100); a textura é renormalizada se não somar 100 ± 2; as profundidades viram duas médias ponderadas pela espessura (0–30 e 0–100 cm); a incerteza relativa é (Q0,95 − Q0,05) ÷ Q0,50. Área urbana ou água vem tudo nulo: fica `sem_dado`. A API pública é **lenta** e tem limite de uso justo: nos testes de 15/11 o custo era por propriedade (uma propriedade levou de 20 a 90 s; três já estouravam os 180 s do gateway, com 504). Por isso o cliente pede **uma propriedade por vez** (7 pedidos, textura primeiro; mínimo de 15 s entre o início de um e o do próximo), com timeout de 170 s (o gateway devolve 504 aos 180 s) e uma nova tentativa em 429/5xx/timeout. Cada propriedade vai para o cache `solo_ponto` assim que chega; uma falha não derruba as outras (a busca desiste depois de 2 falhas) e a próxima busca pede só o que falta. O resultado pode ser **parcial**: o `soilgrids` sai com o que veio (o que falta é `null`) e a síntese usa o que existir (só o pH já dá a acidez). Um ponto novo leva alguns minutos; a fase 2 (COG do ISRIC lido direto) tira essa espera.

- **Segundo plano:** o `PUT /fazenda` com local novo (ou sem mapa no retrato) grava o retrato só com o que o produtor contou, marca `processando` e responde. Uma tarefa (`BackgroundTasks`, sessão de banco própria) busca o solo, refaz o retrato com a fusão e grava `pronto` se veio ao menos a textura (argila, areia e silte) ou se o ponto não tem dado; senão grava `erro` (o que veio fica no retrato e no cache). Sem local: `pendente`. Mesmo local já processado: não chama de novo. Busca em andamento (menos de 15 min) ou que falhou há menos de 10 min: não agenda outra. Fazenda `processando` há mais de 15 min (o servidor reiniciou no meio): o `GET /fazenda` devolve `erro` e a próxima gravação agenda de novo.
- **Derivados** (`services/solo/derivados.py`): classe textural pelos grupamentos da Embrapa (SiBCS 2018), matéria orgânica = carbono × 1,724, acidez pelas mesmas faixas do laudo (`perfil.py`) e erodibilidade K da USLE pelo método de Williams (modelo EPIC), em t·ha·h/(ha·MJ·mm).
- **Fusão** (`services/solo/fusao.py`, `MOTOR-DE-ANALISE.md`, cálculo 2): para textura, matéria orgânica e acidez, cada fonte vota com seu peso (laudo 0,9; teste de campo 0,7, ainda não existe no app; observação do produtor 0,5; SoilGrids 0,4; "não sei" não vota). Vence o valor com mais votos; o laudo decide sozinho. Confiança: alta com soma ≥ 0,9 e sem discordância, média com soma ≥ 0,5, baixa abaixo disso. Quando o mapa discorda do produtor, `divergencia` traz a frase "O mapa global sugere X, mas você observou Y. No seu campo vale o que você vê." Resultado em `retrato_solo.sintese`; os números do mapa em `retrato_solo.soilgrids`.
- **Motor:** o critério de erosão multiplica o fator de declive por um fator da classe de K (baixa 0,75, média 1, alta 1,25; limites e fatores são proposta em `parametros.py`). Sem K, o fator é neutro e entra uma lacuna. O K vem do retrato da fazenda: o motor não chama o SoilGrids.
- **Chat:** `ver_ficha` manda a `sintese` (valor, confiança, evidências e divergência), nunca a coordenada.

**Pré-carga para a demo abrir na hora** (respeita o intervalo mínimo e retoma de onde parou; rode de novo se algum ponto ficar `parcial` ou `falhou`):

```bash
cd agroia/api
uv run python -m app.cli.solo demo                           # pontos de data/demo/pontos_demo.csv e pontos_demo_eua.csv
uv run python -m app.cli.solo baixar --lat -17.64 --lon -51.08   # um ponto
```

Os testes usam um cliente falso e respostas simuladas no formato real da API: não acessam a rede.

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
| `Cannot connect to the Docker daemon` | O Docker está parado. Rode `sudo systemctl start docker` |
| `ModuleNotFoundError: No module named 'app'` | Os comandos da API precisam rodar de dentro de `agroia/api` |
| `type "vector" does not exist` no `alembic upgrade head` | O banco não tem a extensão pgvector (é o caso da VPS hoje). Use o jeito A, ou peça para instalar o pgvector na VPS |
| `Conflict. The container name "/agroia-dev" is already in use` | O banco local já existe. Rode `docker start agroia-dev` |
| Chat diz "A AgroAI está indisponível agora" | Sem `GEMINI_API_KEY` (normal no jeito A) ou o Gemini falhou |
| Erro de conexão com o banco | Seu IP precisa estar liberado no firewall e no `pg_hba.conf` da VPS. Fale com quem cuida dela |

## Decisões desta parte

- **Uma fazenda por usuário**, marcada por um ponto no mapa (`lat`/`lon`). O PostGIS fica para quando houver consulta geográfica.
- **Token JWT** no header `Authorization: Bearer`, guardado no `localStorage` do navegador.
- **Privacidade:** ao Gemini vai só o texto da resposta, nunca nome, e-mail ou local. O nome do lugar é digitado pelo produtor; nenhum serviço de endereço recebe a localização.
- **Faixas de área (pergunta 2):** até 2 / 2–20 / 20–200 / 200–1.000 / mais de 1.000 ha.
- **Pergunta 19:** amostras de cor no lugar das fotos reais de solo, até as fotos de `data/onboarding/fotos-solo/` ficarem prontas.
- **Idioma:** só português nas telas por enquanto. A base de culturas já tem nomes em PT, EN e ES.
- **CORS:** em desenvolvimento, a API aceita o site em qualquer porta do `localhost`. Em produção, liste o domínio em `CORS_ORIGINS`.
