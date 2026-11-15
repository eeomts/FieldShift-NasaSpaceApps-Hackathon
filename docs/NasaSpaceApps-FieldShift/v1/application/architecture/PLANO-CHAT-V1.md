# Plano do chat v1

> 15/11/2026. Decisão de base: **D-011** (Gemini pelo `google-genai`, embeddings `gemini-embedding-001` em 768 dimensões, sem framework de agentes, RAG no próprio Postgres). Estrutura: `agroia/api` em camadas (PR #22).

## O que o chat v1 faz
1 agente com 4 ferramentas, que só respondem com dado do nosso banco ou da base de conhecimento:

| Ferramenta | De onde vem |
|---|---|
| `ver_ficha` | Fazenda do usuário: respostas, perfil, papel, retrato do solo, calendário |
| `info_cultura` | `agroia/base/culturas.json` + parâmetros de `data/catalogo/culturas.csv` |
| `buscar_conhecimento` | RAG (textos de `data/rag/`) |
| `consultar_clima` | NASA POWER agregado por mês, com cache por célula |

Regras do agente: não inventar número (todo número vem de ferramenta, com fonte e período), não prescrever (dose, defensivo), entender linguagem informal, responder no idioma do produtor, dizer quando falta dado.

## PR A — Base do RAG (sem o chat)
- **Migration `0003`:** `CREATE EXTENSION IF NOT EXISTS vector`; tabelas `documento`, `trecho` (`embedding vector(768)`, `tsv` gerado em português, índices HNSW e GIN) e `busca_log`.
- **Código** (portar do `git stash` "prototipo backend/", adaptado ao Gemini e às camadas):
  - `app/models/conhecimento.py` (documento, trecho) e `app/models/agente.py` (busca_log)
  - `app/services/rag/chunker.py` (divide o markdown por seção `#`–`###`, máx. ~1800 caracteres, sobreposição de 1 parágrafo)
  - `app/services/rag/embeddings.py` (Gemini: `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY`, 768d, **normalizar o vetor**)
  - `app/services/rag/ingestao.py` (só reprocessa documento cujo hash mudou) + lista de fontes (começa com o glossário atual)
  - `app/repositories/conhecimento_repository.py` (busca híbrida: vetor + full-text, RRF k=60, filtro por tipo)
  - `app/services/agente/busca_conhecimento_service.py` (descarta trecho fraco e grava `busca_log`)
  - `python -m app.cli.rag ingerir` / `python -m app.cli.rag buscar "..."`
- **Testes:** divisor de trechos; busca híbrida com embedder falso (sem gastar API).

Recuperar o protótipo: `git stash show --include-untracked --name-only stash@{0}` e `git checkout 'stash@{0}^3' -- backend/app/rag` (e os outros caminhos).

## PR B — Clima (NASA POWER)
- Tabelas `ponto_dado` (fonte + chave da célula + centro) e `serie_clima_mensal` (ponto, ano, mês, variável, valor).
- `app/services/integracao/nasa_power.py`: série diária → agregado mensal (chuva, temperaturas, ET0) + contagens (dias de geada, dias de calor, maior sequência sem chuva, dias de chuva forte). `-999` vira ausente.
- Cache por célula (~0,5°): fazendas vizinhas reaproveitam a mesma consulta.
- Testes com a resposta da API simulada.

## PR C — O agente
- Tabelas `conversa` e `mensagem` (conteúdo completo em JSONB, inclusive chamadas de ferramenta: o Gemini exige que voltem exatamente como vieram).
- `app/services/agente/`: prompt com as regras, as 4 ferramentas e o laço com `generate_content`, **chamada automática desligada** (`AutomaticFunctionCallingConfig(disable=True)`), limite de rodadas.
- **Rotas** (contrato fechado em 14/11/2026 para o front do Pedro: várias conversas, resposta de uma vez, fontes estruturadas). Todas exigem `Authorization: Bearer`.
  ```
  GET    /chat/conversas                     -> 200 ConversaResumo[]  (mais recente primeiro)
  POST   /chat/conversas                     -> 201 ConversaResumo     (conversa vazia)
  GET    /chat/conversas/{id}                -> 200 Conversa           (com as mensagens visíveis)
  POST   /chat/conversas/{id}/mensagens      -> 200 Mensagem           (a resposta do assistente)
         {"mensagem": "..."}                    1 a 2000 caracteres
  DELETE /chat/conversas/{id}                -> 204
  ```
  ```ts
  type TipoFonte = "clima" | "conhecimento" | "cultura" | "fazenda";
  interface Fonte { tipo: TipoFonte; titulo: string; detalhe: string | null }
  interface Mensagem {
    id: number; papel: "produtor" | "assistente"; texto: string;
    fontes: Fonte[]; ferramentas_usadas: string[]; criada_em: string;  // ISO 8601 UTC
  }
  interface ConversaResumo { id: number; titulo: string | null; criada_em: string; atualizada_em: string }
  interface Conversa extends ConversaResumo { mensagens: Mensagem[] }
  ```
  - `titulo`: os primeiros ~60 caracteres da primeira pergunta (null até a primeira mensagem).
  - Fontes e ferramentas vêm das ferramentas executadas pelo nosso código, nunca do texto do modelo.
  - Erros (`{"detail": "..."}`): 401 sem token; 404 "Conversa não encontrada." (inexistente ou de outro usuário); 422 mensagem vazia ou longa demais; 503 "O assistente está fora do ar agora. Tente de novo em alguns minutos." (sem chave ou Gemini falhou).
- **Testes:** modelo falso com chamadas de ferramenta roteirizadas; 5 casos do Sr. José (`application/prompts/examples/tests/TESTES_CHAT_SR_JOSE.md`) contra o Gemini real, só quando houver chave.

## Ajustes antes de começar
1. **Banco de teste sem `vector`:** o container `agroia-teste` usa `postgres:17`. Trocar por imagem com pgvector (ex.: `pgvector/pgvector:pg17`) e atualizar a instrução do `agroia/README.md`.
2. **`data/catalogo/culturas.csv` dentro da imagem da API:** o build da API (`.deploy/compose.yml`) só enxerga `agroia/`. Incluir o `data/catalogo/` no build.
3. **Banco de produção** (em aberto): Postgres atual da VPS (instalar `vector`, exige admin) ou o do compose (já tem; mover os dados com `.deploy/backup` + `.deploy/restaurar`).

## Perguntas em aberto para retomar
- Começar pelo PR A?
- A D-011 (já escrita no `context/DECISOES.md`, sem commit) vai no primeiro commit do PR A ou direto na `main`?
