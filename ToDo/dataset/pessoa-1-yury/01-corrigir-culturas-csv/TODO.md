# 01 — Corrigir o `culturas.csv` duplicado

**Dono:** Pessoa 1 (Yury) · **Status:** feito (corrigido em 14/11/2026 no commit `fix(data): remove duplicated half of culturas.csv`) · **Prioridade:** —

> Só confira: o arquivo agora tem os **seus** dados, com `aveia` e `pastagem` no lugar de `aveia_preta` e `braquiaria`, e as evidências renomeadas. Se algo não bater com o que você pesquisou, avise.

## Por quê
Na resolução de um conflito de merge, o `data/catalogo/culturas.csv` ficou com **dois cabeçalhos e as 16 culturas duas vezes**:
- linhas 1–17: um modelo quase vazio (só id e nome científico), com os ids do app (`aveia`, `pastagem`);
- linhas 18–34: os **seus dados completos**, no formato antigo, com os ids antigos (`aveia_preta`, `braquiaria`).

Qualquer script que ler o arquivo vai quebrar ou pegar a linha vazia.

## O que fazer
1. Apague as linhas 1 a 17 (o modelo vazio). Fica o seu cabeçalho (linha 18) e as suas 16 linhas.
2. Troque os dois ids para os do app (`agroai/base/culturas.json` é a fonte única dos ids):
   - `aveia_preta` → `aveia`
   - `braquiaria` → `pastagem`
3. Renomeie as evidências do mesmo jeito: `data/catalogo/evidencias/aveia_preta.json` → `aveia.json` e `braquiaria.json` → `pastagem.json` (e o `id` dentro de cada uma, se houver).
4. Mantenha todas as colunas que você preencheu (nome, família, tipos, perene...). Nada da sua pesquisa se perde.

## Pronto quando
- [ ] O arquivo tem **1 cabeçalho e 16 linhas**.
- [ ] Todo `id` existe em `agroai/base/culturas.json`.
- [ ] Os nomes das evidências batem com os ids.
- [ ] Confere com: `python -c "import csv; l=list(csv.DictReader(open('data/catalogo/culturas.csv', encoding='utf-8'))); print(len(l), sorted(r['id'] for r in l))"`

## Desbloqueia
02 (PAM), 03 (ZARC), a tarefa de equipamentos da Pessoa 2 e as fichas de cultura da Pessoa 3.
