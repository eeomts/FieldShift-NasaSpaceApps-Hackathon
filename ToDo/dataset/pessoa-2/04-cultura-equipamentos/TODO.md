# 04 — Exigência de equipamento por cultura

**Dono:** Pessoa 2 · **Status:** em revisão (rascunho; justificativas em notas.md) · **Depende de:** Pessoa 1, tarefa 01 (ids corrigidos)

## Por quê
A pergunta 26b ("que máquinas você tem?") elimina as culturas que o produtor não consegue plantar ou colher.

## Entrada
- As 16 culturas de `data/catalogo/culturas.csv`.
- As categorias de `agroia/base/equipamentos.json`: `trator`, `plantadeira_graos`, `colhedora`, `pulverizador`, `preparo_solo`, `rocadeira`, `ensiladeira`, `irrigacao`, `tracao_animal`, `manual`.

## Saída: `data/catalogo/cultura_equipamentos.csv` (rascunho com as 16 culturas; justificativas em `notas.md`)

| `cultura_id` | `equipamento_id` | `etapa` |
|---|---|---|
| `milho` | `plantadeira_graos` | `plantio` |
| `milho` | `manual` | `plantio` |

- Etapa: `plantio` ou `colheita`.
- Mais de uma linha na mesma etapa = **qualquer uma** delas serve (ex.: milho dá para plantar com plantadeira ou à mão).
- Se dá para fazer à mão, inclua `manual`.
- **Culturas fora das 16:** o `agroia/base/culturas.json` tem 40 culturas. As 24 sem linha aqui (cevada, cana, café etc.) ainda não têm comportamento definido no filtro 26b (passam sem restrição ou saem das sugestões): **a definir pelo dono do motor**.

## Pronto quando
- [x] As 16 culturas com plantio e colheita (64 linhas, conferido por script).
- [x] Todo `equipamento_id` existe no `equipamentos.json` (falta uma categoria? peça ao Pedro por PR, não invente o id).
- [ ] Fonte anotada para os casos não óbvios (ex.: colheita de braquiária). **Pendente:** citar uma publicação (título e link) por caso em `notas.md` — revisão da Pessoa 1.
