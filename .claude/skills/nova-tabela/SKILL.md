---
name: nova-tabela
description: Cria tabela nova, coluna nova ou mudanca de estrutura no AgroIA seguindo as convencoes do projeto - model SQLAlchemy em agroia/api/app/models, migration Alembic com upgrade/downgrade completos e migracao de dados, teste em upgrade -> downgrade -> upgrade no banco de teste. Use ao planejar ou implementar qualquer mudanca de estrutura de banco.
---

# nova-tabela: model + migration

## 1. Conferir o que já existe
- Rode a skill `schema` nas tabelas que a nova vai referenciar e na que vai ganhar coluna.
- Veja se o dado cabe numa coluna JSONB existente da `fazenda` (o projeto guarda respostas e derivados do onboarding em JSONB) antes de criar tabela.
- Catálogo de culturas e equipamentos NÃO vira tabela: a fonte é `agroia/base/*.json`. Referência a cultura é `cultura_id` texto (`"milho"`), sem FK.

## 2. Desenhar com as convenções do `agroia`
- Nomes em português, `snake_case`, tabela no singular (`fazenda`, `calendario_item`).
- Chave primária: `UUID` (`default=uuid4`) para entidades do usuário; `Integer` autoincremento para linhas de série ou itens.
- FK para a fazenda: `fazenda_id UUID REFERENCES fazenda(id) ON DELETE CASCADE` com índice. Apagar a conta apaga tudo (`DELETE /me`).
- Datas: `criado_em` / `atualizado_em` (`DateTime(timezone=True)`, `server_default=func.now()`, `onupdate` no atualizado).
- Valores restritos: `CheckConstraint` com nome explícito (`ck_<tabela>_<campo>`).
- Ausente é `NULL`, nunca 0.
- Dados externos (NASA, SoilGrids): guardar agregado e pequeno (ver `docs/.../architecture/BANCO-DE-DADOS.md`), não o arquivo bruto.
- Apresente o desenho (colunas, tipos, constraints) no plano antes de gerar os arquivos.

## 3. Gerar a migration
```bash
cd agroia/api && set -a && . ./.env.test && set +a
.venv/Scripts/alembic.exe revision --autogenerate -m "<o que muda>"   # ou: uv run alembic ...
```
- Confira o arquivo gerado em `migrations/versions/`. Numeração do projeto: `0003_<descricao>.py`, `revision = '0003'`, `down_revision` = a anterior.
- Uma migration por mudança lógica.
- `downgrade` completo (desfaz tudo o que o `upgrade` fez).
- Mudou o formato de um dado existente? Migre os dados no mesmo arquivo (`op.execute(...)`) e diga no docstring o que acontece com as linhas antigas.
- Extensão do Postgres (`vector`, `postgis`): `CREATE EXTENSION IF NOT EXISTS ...` e avise que na VPS precisa de permissão de administrador.
- Nunca editar uma migration que já foi aplicada na VPS: crie outra.

## 4. Testar no banco de teste
```bash
.venv/Scripts/alembic.exe upgrade head
.venv/Scripts/alembic.exe downgrade -1
.venv/Scripts/alembic.exe upgrade head
.venv/Scripts/python.exe -m pytest -q
```

## 5. Avisar
No resumo e na descrição do PR: **"rodar `alembic upgrade head` na VPS antes de usar este código"**. Quem roda na VPS é quem tem acesso a ela, com confirmação do usuário.
