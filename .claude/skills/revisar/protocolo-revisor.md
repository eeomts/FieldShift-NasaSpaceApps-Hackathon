# Protocolo dos revisores do /revisar

Vale para revisor-cetico, revisor-purista e revisor-negocio. Cada um tem a sua lente, mas todos seguem este formato para o coordenador conseguir cruzar as análises.

## O que você recebe do coordenador
- FASE: `RODADA 1` ou `GIRO <n>`.
- Alvo: comando git que mostra as mudanças (`git diff`, `git show <hash>`, `git diff <de>..<ate>`, `gh pr diff <n>`) e a lista de arquivos, incluindo os novos (leia com Read).
- REGRA DE NEGÓCIO: o que a mudança deveria fazer. É a referência de "certo" para todos.
- Arquivo da revisão: `reviews/<alvo> <DD_MM_YY>/NN-revisao.md` (no GIRO você lê os achados dos outros nele).

## O que você pode rodar
Você NÃO altera nada: nem arquivo, nem git, nem banco. Pode rodar:
- git de leitura: `git status`, `git diff`, `git log`, `git show`, `git blame`, `git ls-files`, `gh pr diff`, `gh pr view`.
- Testes da API, no banco de teste LOCAL (nunca na VPS):
  ```bash
  cd agroai/api && set -a && . ./.env.test && set +a && .venv/Scripts/python.exe -m pytest -q
  ```
  (ou `uv run pytest -q`). O teste apaga os dados do banco de teste: é esperado.
- Checagem de tipos do front: `cd agroai/web && npx tsc -p tsconfig.json --noEmit`.
- Leitura de qualquer arquivo com Read/Grep/Glob.

Se um comando não funcionar no ambiente, diga no relatório; não invente o resultado.

## Escopo
- Revise o que mudou. Leia a função/tela inteira ao redor, mas não reporte problema antigo em código não tocado (no máximo 3 linhas em "Fora do escopo").
- Ignore `node_modules/`, `.venv/`, `dist/`, `reviews/` e `backend/` (protótipo antigo).
- Você revisa TUDO; a sua lente define onde você cava mais fundo.

## Severidade
- CRÍTICO: quebra o app ou o build, perde ou corrompe dado, falha de segurança ou de privacidade, segredo exposto.
- ALTO: bug em caso comum, regra de negócio não atendida, número errado ou sem fonte na tela.
- MÉDIO: caso de borda, convenção do projeto violada, documentação desatualizada pelo diff.
- BAIXO: estilo, nome, legibilidade.

## Formato: RODADA 1
Prefixo do id: C (cético), P (purista), N (negócio). Numeração sua: C-01, C-02...

```
REVISOR: <cetico|purista|negocio>
Veredito: <pode juntar | juntar após corrigir X | não juntar> (1 linha)
Testes: pytest <n passaram / falhas> | tsc <ok / erros> | <não rodado: motivo>

Achados (do mais grave ao menos):
[C-01] [ALTO] caminho:linha | categoria | problema
  Evidência: <entrada/estado concreto -> resultado errado; ou trecho/regra violada>
  Sugestão: <até 3 linhas de código ou 1 frase>

Regra de negócio: <item a item: atendido | parcial | não atendido | não verificável>
Perguntas ao usuário: <o que só ele responde; ou "nenhuma">
Fora do escopo: <opcional, máx. 3 linhas>
```

## Formato: GIRO
Leia no arquivo da revisão os achados dos OUTROS dois revisores e responda a CADA um:

```
REVISOR: <...> | GIRO <n>
[P-03] CONCORDO | DISCORDO | COMPLEMENTO | SEVERIDADE -> <nova> : <motivo com evidência>
...
Retiro: <ids próprios que você retira, com motivo; ou "nenhum">
Novos: <achados novos que os outros te fizeram ver, no formato da rodada 1; ou "nenhum">
```
- DISCORDO sem evidência não vale. Se não tem como confirmar, diga "não verificável".
- No GIRO 2 responda só aos itens que o coordenador listar.

## Regras gerais
- Só reporte o que confirmou lendo o código ou rodando o teste. Nada de "considere" sem cenário concreto.
- Português do Brasil, sem emojis.
- Não reescreva arquivos inteiros na sugestão.
