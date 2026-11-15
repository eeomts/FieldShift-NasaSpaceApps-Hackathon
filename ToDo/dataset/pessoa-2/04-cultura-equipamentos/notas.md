# Notas da tarefa 04: o que cada cultura exige de equipamento

> Rascunho de 14/11/2026, **a revisar por alguém de agronomia** (Pessoa 1). Os casos abaixo são os não óbvios que o `TODO.md` pede para justificar.
>
> **O CSV (`data/catalogo/cultura_equipamentos.csv`) é a fonte de verdade.** Estas notas só explicam as escolhas; se o CSV mudar, ele é que vale.

## Regras usadas

- Várias linhas na mesma etapa = **qualquer uma** serve. Por isso, cada etapa lista todas as formas comuns de fazer, para o filtro da pergunta 26b não eliminar uma cultura que o produtor consegue fazer de outro jeito.
- `trator` **não aparece sozinho**: plantadeira, colhedora e roçadeira já pressupõem o trator. Listar `trator` como alternativa diria que só o trator basta, o que não é verdade.
- Só os ids de `agroia/base/equipamentos.json`. Nenhum id foi inventado.

## Culturas de cobertura e forrageiras: o que é "colheita"

O CSV só tem as etapas `plantio` e `colheita`. Para as culturas que não são colhidas como grão, a `colheita` foi tratada como o **manejo do fim do ciclo**, a operação que encerra a cultura e deixa a palhada:

| Cultura | "Colheita" considerada | Equipamentos |
|---|---|---|
| Crotalária, guandu | Roçada ou corte para adubo verde | `rocadeira` ou `manual` (foice) |
| Nabo forrageiro | Roçada, rolagem ou dessecação | `rocadeira` (inclui rolo faca) ou `pulverizador` (inclui bomba costal) |
| Aveia-preta | Rolagem ou dessecação para palhada; ou colheita de grão para semente | `rocadeira`, `pulverizador` ou `colhedora` |
| Milheto | Grão, ou roçada como cobertura | `colhedora`, `rocadeira` ou `manual` |
| Braquiária (`pastagem`) | Pastejo direto, silagem ou roçada | `manual` (pastejo não exige máquina), `ensiladeira` ou `rocadeira` |

## Casos que merecem conferência

| Caso | Decisão no rascunho | Por quê |
|---|---|---|
| Mandioca, plantio e colheita | Só `manual` | A mecanização da mandioca usa **plantadeira de manivas** e **afofador/arrancador**, que não existem nas categorias. Sugestão para o Pedro (PR no `equipamentos.json`): criar uma categoria para essas máquinas, ou decidir que `plantadeira_graos`/`preparo_solo` as representam |
| Feijão e feijão-caupi, colheita | `colhedora` ou `manual` | Há colheita mecanizada direta, mas na agricultura familiar o arranquio ou a catação de vagens é manual |
| Algodão, colheita | `colhedora` ou `manual` | A colhedora de algodão é uma máquina própria, mas cai na categoria geral `colhedora`. A colheita manual ainda existe em áreas pequenas |
| Arroz, plantio e colheita | Inclui `manual` | Arroz de sequeiro da agricultura familiar (plantio com matraca e corte manual). O arroz irrigado por transplante não foi considerado |
| `tracao_animal` no plantio | Feijão, feijão-caupi, milho e sorgo: incluído. Algodão: não incluído (decisão do time, 14/11/2026) | Plantadeira de tração animal é comum no Semiárido. Sem ela no milho, o produtor de Irecê (milho + feijão consorciados) que só tem tração animal perderia o milho no filtro |
| Girassol, soja e trigo sem `manual` | Não incluído | Não há colheita manual viável fora de hortas experimentais |
| `irrigacao` e `preparo_solo` | Não usados | Nenhuma cultura da base **exige** irrigação (o projeto trata de sequeiro) nem preparo convencional (plantio direto é o padrão) |

## Fontes para conferir

As escolhas acima seguem a prática agrícola brasileira, mas não foram tiradas de uma fonte única. Para a revisão, as referências mais diretas são:

- Embrapa: sistemas de produção de cada cultura (seção "colheita") e publicações sobre plantas de cobertura (manejo com rolo faca, roçada e dessecação).
- Embrapa Mandioca e Fruticultura: mecanização da mandioca.
- Embrapa Meio-Norte: feijão-caupi na agricultura familiar.
