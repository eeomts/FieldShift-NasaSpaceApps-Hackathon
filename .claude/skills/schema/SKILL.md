---
name: schema
description: Busca a estrutura REAL das tabelas do AgroAI (colunas, tipos, constraints, indices) no banco de teste local e confere com os models SQLAlchemy antes de escrever query, model, migration ou schema Pydantic que cite colunas. Use sempre que for usar uma tabela cujas colunas nao foram conferidas nesta sessao. Argumentos: tabelas (ex.: fazenda calendario_item).
---

# schema: estrutura real das tabelas

Objetivo: nunca escrever query, model, migration ou schema com coluna suposta.

## Passo a passo

1. **Tabelas:** as citadas pelo usuário ou as que o plano vai tocar.

2. **Banco de teste local** (porta 55433, credenciais em `agroai/api/.env.test`). Se o container não estiver de pé, suba como no README do `agroai` e aplique as migrations:
   ```bash
   docker start agroai-teste 2>/dev/null || docker run -d --name agroai-teste -p 55433:5432 \
     -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=agricultura postgres:17
   cd agroai/api && set -a && . ./.env.test && set +a && .venv/Scripts/alembic.exe upgrade head
   ```

3. **Estrutura**, uma tabela por `-c`:
   ```bash
   docker exec agroai-teste psql -U agricultura_app -d agricultura -c "\d+ fazenda" -c "\d calendario_item"
   ```
   Revisão das migrations aplicadas: `-c "SELECT version_num FROM alembic_version"`.

4. **Comparar com o model** (`agroai/api/app/models*`) e com a última migration em `agroai/api/migrations/versions/`. Divergência (coluna no model sem migration, ou o contrário) é achado.

## NUNCA
- Conectar no banco da VPS para conferir estrutura sem confirmação explícita do usuário. A VPS pode estar atrás das migrations do repositório (migration ainda não aplicada): se a tarefa depende disso, avise.
- Rodar `ALTER`/`INSERT` aqui. Mudança de estrutura é com a skill `nova-tabela`.

## O que registrar na resposta
- Colunas que a tarefa vai usar, com tipo, NULL/default.
- Chaves, índices e constraints (`ck_*`) relevantes.
- Colunas JSONB e o formato esperado do conteúdo (ver o schema Pydantic correspondente).
- Divergências entre banco, model e migration.
