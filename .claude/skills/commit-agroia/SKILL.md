---
name: commit-agroia
description: 'Sugere commits e PR no padrao do repositorio (tipo(escopo): descricao, em ingles, UM COMMIT POR PROBLEMA), separa os arquivos de cada commit e deixa de fora o que nao e da tarefa. Use no fim de toda tarefa ou quando o usuario pedir mensagem de commit/PR. So commita, faz push ou merge quando o usuario pedir.'
---

# commit-agroia

## Regras do time
- **Um commit por problema.** Mudanças de assuntos diferentes nunca vão no mesmo commit, mesmo que tenham sido feitas juntas.
- Branch a partir da `main` atualizada: `feat/...`, `fix/...`, `docs/...`, `data/...`, `refactor/...`.
- Commitar, fazer push, abrir PR ou fazer merge **só quando o usuário pedir**. Merge na `main` com migration nova exige avisar que a migration precisa rodar na VPS.

## 1. O que mudou
- `git status --short` e `git diff --stat`.
- Agrupe os arquivos por problema. Cada grupo vira um commit.
- Fica FORA, avisando o motivo:
  - arquivo que não foi mexido nesta tarefa (trabalho de outra pessoa: pergunte);
  - `.env`, `node_modules/`, `.venv/`, `dist/`, `reviews/`, `data/brutos/*`;
  - `agroia/web/tsconfig.tsbuildinfo` alterado só pelo build.

## 2. Mensagem
Formato: `<tipo>(<escopo>): <descrição curta em inglês, imperativo>` + corpo explicando o problema e a solução.
- Tipos: `feat`, `fix`, `refactor`, `docs`, `data`, `test`, `chore`.
- Escopos usados: `perfil`, `onboarding`, `solo`, `api`, `web`, `chat`, `rag`, `integracao`, `motor`.
- Corpo: o problema (por que mudou), o que mudou, efeito em dados existentes e se há migration para a VPS.
- No PowerShell, mensagem com aspas quebra o comando: use o Bash com heredoc (`git commit -F - <<'EOF' ... EOF`).

## 3. PR
- Título curto; corpo com `## Summary` (um item por commit), `## Before merging` (migration na VPS, chave nova no `.env`) e `## Test plan` (pytest, tsc, build, migration testada).
- Antes de abrir: `git fetch` e conferir se a `main` andou; se andou, trazer a `main` para a branch e repetir os testes.

## 4. Entrega
```
Commit 1 - fix(perfil): ...
  arquivos: ...
Commit 2 - feat(onboarding): ...
  arquivos: ...
Fora: <arquivo> (<motivo>)
```
