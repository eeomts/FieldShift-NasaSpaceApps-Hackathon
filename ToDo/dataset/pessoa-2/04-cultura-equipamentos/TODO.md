# 04 — Exigência de equipamento por cultura

**Dono:** Pessoa 2 · **Status:** em revisão (24 culturas; fontes por caso em notas.md) · **Depende de:** Pessoa 1, tarefa 01 (ids corrigidos)

## Por quê
A pergunta 26b ("que máquinas você tem?") elimina as culturas que o produtor não consegue plantar ou colher.

## Entrada
- As 16 culturas de `data/catalogo/culturas.csv`, mais `arroz_irrigado` (Brasil) e as culturas dos EUA que não existem no Brasil: `alfafa`, `amendoim`, `canola`, `centeio`, `cevada`, `ervilhaca`, `trevo` (`data/catalogo/eua/evidencias/`).
- As categorias de `agroai/base/equipamentos.json`: `trator`, `plantadeira_graos`, `colhedora`, `pulverizador`, `preparo_solo`, `rocadeira`, `ensiladeira`, `irrigacao`, `tracao_animal`, `manual`.

## Saída: `data/catalogo/cultura_equipamentos.csv` (24 culturas, 91 linhas; justificativas e fontes em `notas.md`)

| `cultura_id` | `equipamento_id` | `etapa` |
|---|---|---|
| `milho` | `plantadeira_graos` | `plantio` |
| `milho` | `manual` | `plantio` |

- Etapa: `plantio` ou `colheita` (o filtro só lê essas duas; nas coberturas, `colheita` = manejo do fim do ciclo).
- Sem coluna de país: a mesma `cultura_id` vale para o Brasil e para os EUA.
- Mais de uma linha na mesma etapa = **qualquer uma** delas serve (ex.: milho dá para plantar com plantadeira ou à mão).
- Se dá para fazer à mão, inclua `manual`.
- **Culturas sem linha:** o `agroai/base/culturas.json` tem 41 culturas; 24 têm linha aqui. As 17 restantes (batata, batata-doce, cana, café, cacau, banana, citros, frutíferas, hortaliças, abóbora, capineira, feijão-de-porco, mucuna, grão-de-bico, lentilha, gergelim, quinoa) hoje **passam sem restrição** no filtro 26b e geram a lacuna "Sem lista de máquinas para ..." (`filtro.py`, `_equipamento`). Se alguma entrar no catálogo do motor, precisa de linha aqui.

## Pronto quando
- [x] As 16 culturas com plantio e colheita (64 linhas, conferido por script).
- [x] `arroz_irrigado` e as 7 culturas dos EUA (alfafa, amendoim, canola, centeio, cevada, ervilhaca, trevo): +27 linhas, 91 no total (conferido por script: ids válidos, plantio e colheita em todas, sem linha repetida).
- [x] Todo `equipamento_id` existe no `equipamentos.json` (falta uma categoria? peça ao Pedro por PR, não invente o id).
- [x] Fonte anotada para os casos não óbvios: título, link e trecho lido de cada publicação em `notas.md` ("Fontes por caso").
- [ ] Ainda sem fonte: sorgo com tração animal, milheto com colhedora, braquiária com roçadeira, foice em publicação da Embrapa (ver "Ainda sem fonte publicada" em `notas.md`).
- [ ] Categorias que faltam no `equipamentos.json` (enfardadora/ancinho, arrancador-invertedor de amendoim, plantadeira de manivas e afofador de mandioca): decidir com o Pedro, por PR.
- [ ] Revisão de agronomia (Pessoa 1).
