---
name: revisar
description: "Revisao de codigo do AgroIA com tres revisores independentes (revisor-cetico, revisor-purista, revisor-negocio) coordenados pela sessao principal: rodada 1 em paralelo, giro em que cada um responde aos achados dos outros, resumo consolidado, depois (se o usuario quiser) proposta do agroia-arquiteto e implementacao pelo agroia-backend/agroia-frontend. Grava tudo em reviews/. Uso: /revisar [alvo] [regra de negocio]."
argument-hint: "[alvo: vazio = diff atual | #<pr> | <hash> | <de>..<ate>] [regra de negocio]"
disable-model-invocation: true
---

# /revisar

Quem executa esta skill é a sessão principal, no papel de COORDENADOR. Subagente não chama subagente nem pergunta ao usuário, por isso a coordenação, as perguntas e a escrita dos arquivos de `reviews/` ficam aqui. Os revisores só leem.

Custo: 3 revisores (Sonnet) × até 3 rodadas + arquiteto (Opus) + implementação. Não faça um 2º giro sem divergência que justifique.

## 0. Coleta (antes de chamar qualquer agente)

1. **Alvo** (do argumento):
   - vazio: mudanças não commitadas. `git status --short`, `git diff --stat`, `git ls-files --others --exclude-standard`. Comando dos revisores: `git diff` (+ arquivos novos por nome).
   - `#<pr>`: `gh pr diff <pr>` e `gh pr view <pr>`.
   - `<hash>` ou `<de>..<ate>`: `git show <hash>` / `git diff <de>..<ate>`.
   - Ignore `node_modules/`, `.venv/`, `dist/`, `reviews/`, `backend/`. Nada sobrou: diga isso e pare.
2. **Regra de negócio:** texto do argumento. Sem argumento: o que está claro na conversa, na descrição do PR ou nos documentos (`docs/NasaSpaceApps-FieldShift/v1/application/`); resuma em até 5 linhas e confirme com o usuário. Sem nenhuma fonte: pergunte. Nunca revise sem regra de negócio.
3. **Pasta da revisão** (fora do Git, `reviews/` está no `.gitignore`):
   ```
   reviews/<alvo> <DD_MM_YY>/      # alvo: "pr-17", "diff", "<hash curto>"
       01-revisao.md
       02-arquiteto.md
       03-implementacao.md
   ```
   Segunda revisão do mesmo alvo: continue a numeração (`04-revisao.md`...). Caminho sempre entre aspas no shell.
   Cabeçalho do `NN-revisao.md`:
   ```markdown
   # Revisão <alvo> - <DD-MM-YY>
   Alvo: <comando> | Arquivos: <lista>
   Regra de negócio: <texto>
   ## Rodada 1
   ```

## 1. Rodada 1 (paralelo, independentes)

Dispare os três na MESMA mensagem, em background: `revisor-cetico`, `revisor-purista`, `revisor-negocio`. Prompt igual para os três:
```
FASE: RODADA 1
Alvo: <comando> | Arquivos: <lista, marcando os novos>
REGRA DE NEGÓCIO: <texto>
Arquivo da revisão: <caminho do NN-revisao.md>
Leia .claude/skills/revisar/protocolo-revisor.md e devolva no formato da RODADA 1.
```
Não mande para um o que o outro achou. Espere os três (você é notificado). Grave cada resposta, integral, no `NN-revisao.md` (`### Cético`, `### Purista`, `### Negócio`).

Os três rodam os testes no MESMO banco de teste local. Se der conflito de execução simultânea, peça que só o cético rode o `pytest` e os outros leiam o resultado no arquivo.

## 2. Giro

- Continue cada revisor com `SendMessage` (carregue a ferramenta pelo ToolSearch se estiver adiada):
  ```
  FASE: GIRO 1
  Leia em <caminho do NN-revisao.md> a Rodada 1 dos outros dois revisores e responda a cada achado deles no formato do GIRO.
  ```
- Dispare os três juntos e espere. Grave em `## Giro 1`.
- **Giro 2** só se sobrar DISCORDO em achado CRÍTICO ou ALTO, mandando só esses ids. Máximo 2 giros.

## 3. Consolidação

Grave em `## Consolidado`:

| Status | Regra |
|---|---|
| CONSENSO | ninguém discordou (3 concordam, ou 2 concordam e 1 não verificável) |
| MAIORIA | 2 × 1: mostre o voto vencido e o motivo |
| DIVERGENTE | sem maioria: mostre os lados |
| RETIRADO | o próprio autor retirou no giro |

- Severidade final: a mais citada no giro; empate fica com a maior.
- Junte achados iguais de revisores diferentes (`C-02 = P-05`).
- Ordem: CRÍTICO, ALTO, MÉDIO, BAIXO.

Mostre na conversa: veredito de cada revisor, contagem por severidade, CRÍTICO/ALTO em uma linha cada, divergências, perguntas ao usuário e o caminho do arquivo.

## 4. Pergunta 1
AskUserQuestion: "Enviar as sugestões da revisão de <alvo> para o arquiteto?" Sim / Não. Não → passo 7.

## 5. Arquiteto
Chame `agroia-arquiteto` como subagente:
```
MODO REVISAO
Alvo: <comando> | Arquivos: <lista>
REGRA DE NEGÓCIO: <texto>
Revisão consolidada: <caminho do NN-revisao.md>
Respostas do usuário às perguntas dos revisores: <se houver>
```
Grave a resposta em `NN-arquiteto.md`. Mostre: pontos que procedem com o agente de cada um, os que não procedem, os pacotes e o que ficou FORA.

## 6. Pergunta 2
AskUserQuestion: "Chamar os agentes de implementação?" com a lista `id -> agente` no texto. Sim / Não.
- Sim: dispare os pacotes (`agroia-backend` e `agroia-frontend` em paralelo quando não dependem um do outro, com o mesmo contrato). Pontos `FORA` não são implementados. Ao terminar: confira o diff, rode `pytest` e `tsc`, grave `NN-implementacao.md` (ponto → feito/não feito, arquivos, observações).

## 7. Fechamento
```
/revisar <alvo> - <DD-MM-YY>
Revisores: cético <veredito> | purista <veredito> | negócio <veredito>
Achados: <x> CRÍTICO, <y> ALTO, <z> MÉDIO, <w> BAIXO (<k> divergentes)
Arquiteto: <não chamado | p procedem, q não procedem, r fora>
Implementação: <não chamada | feitos / pendentes>
Pendente com você: <perguntas, FORA, testes de tela, migration na VPS>
Arquivos: <caminhos em reviews/>
```
Se houve implementação, termine com a sugestão de commit (skill `commit-agroia`). Só commitar se o usuário pedir.
