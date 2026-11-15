---
name: onde-paramos
description: Retoma ou registra o andamento do AgroAI. No inicio, cruza git (branches, commits, mudancas nao commitadas), PRs abertos, perguntas abertas do DECISOES.md e tarefas de data/ e diz o que esta feito, pendente e bloqueado e qual o proximo passo. No fim, grava o progresso em docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md. Use em "onde paramos", "o que falta", "retomar", ao comecar a sessao e ao pausar uma tarefa.
---

# onde-paramos

O estado do trabalho fica no repositório, não só na memória do Claude. O time é de várias pessoas: sempre confira o que os outros subiram.

## Fontes
- `docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md`: o registro desta skill (pode não existir ainda).
- `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md`: decisões (D-xxx) e perguntas abertas (Q-xx).
- `data/README.md` e `data/FONTES.md`: tarefas de preparação de dados e o que já foi baixado.
- `README.md` da raiz: seção de decisões pendentes.
- Git e GitHub.

## Modo retomar (início)
1. `git fetch -q --all --prune`, depois:
   - `git status --short` e `git branch --show-current`: trabalho não commitado e branch atual;
   - `git log --oneline -15 origin/main`: o que entrou na `main` (de quem?);
   - `git log --oneline origin/main..HEAD`: commits locais que ainda não estão na `main`;
   - `gh pr list --state open`: PRs abertos (de quem, há quanto tempo).
2. Ler o `ANDAMENTO.md` (se existir) e as perguntas abertas do `DECISOES.md`.
3. Conferir com a realidade: o que o git mostra vence o que está escrito. Memória do projeto só como complemento.
4. Responder curto:
```
Branch: <atual> | main: <último merge>

Feito desde a última vez: <PRs/commits, 1 linha cada>
Em andamento: <item> - <estado>
Bloqueado: <item> - esperando <quem/o quê>
PRs abertos: #<n> <título> (<autor>)
Não commitado: <arquivos>
Pendente de produção: <migration a rodar na VPS, chave no .env>
Próximo passo: <uma ação concreta>
```

## Modo registrar (fim de tarefa ou pausa)
Criar ou atualizar `docs/NasaSpaceApps-FieldShift/v1/application/ANDAMENTO.md`:
```markdown
# Andamento - AgroAI

Atualizado: <DD-MM-AA>

| Frente | Status | PR / branch | Observação |
|---|---|---|---|
| Perfil e laudo | em revisão | #17 | falta migration 0002 na VPS |

## Decisões desta etapa
- <data>: <decisão com o usuário e o motivo> (se for decisão de time, registrar também no DECISOES.md)

## Bloqueios
- <item>: esperando <quem> (<desde quando>)

## Onde paramos
<1 a 3 linhas: o que estava sendo feito e o próximo passo exato, com arquivo:função>
```
- Status: `pendente`, `em andamento`, `em revisão`, `feito`, `bloqueado`, `descartado`.
- Decisões: só o que não dá para tirar do código.
- Migration ou configuração de produção pendente vai em "Pendente de produção".
