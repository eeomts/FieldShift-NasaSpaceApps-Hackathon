# Sinônimos e nomes regionais das culturas (proposta)

> Tarefa P3-02 (`ToDo/dataset/pessoa-3/02-sinonimos-culturas/`). Dono: Pessoa 3.
>
> A fonte única dos nomes das culturas é o campo `nomes` de cada cultura em **`agroia/base/culturas.json`**, que é arquivo do app e só muda por PR, avisando o Pedro. Este documento lista o que já existe lá e **os nomes novos propostos** para as 16 culturas do motor (`data/catalogo/culturas.csv`).

## Como aplicar
1. Para cada linha com nomes na coluna **Novos propostos**, acrescentar o nome na lista do idioma certo em `nomes` (`pt`, `en` ou `es`) no `agroia/base/culturas.json`.
2. Conferir que nenhum nome fica repetido em duas culturas.
3. Rodar os testes da API (`agroia/api/tests/test_interpretar.py`).

## Resumo
- **20 nomes novos** para as 16 culturas.
- **4** deles (marcados com ¹) só mudam a escrita de um nome que o app já tem (hífen no lugar de espaço, como "feijão-carioca" × "feijão carioca"). Só valem a pena se o casamento de texto do app **não** ignorar hífen.
- Todas as 16 culturas já têm pelo menos 1 nome em PT, EN e ES no app.
- ⚠️ **Nome repetido que já existe no app** (não é desta proposta): "batata" aparece em `batata` e em `batata_doce`.

## Nomes por cultura

| id | Cultura | Já no app (`culturas.json`) | Novos propostos |
|---|---|---|---|
| `soja` | Soja | PT: soja · EN: soybean, soy, soya · ES: soja, soya | — |
| `milho` | Milho | PT: milho, milho safrinha, milho verde · EN: corn, maize · ES: maíz, maiz, choclo, elote | — |
| `feijao` | Feijão | PT: feijão, feijao, feijão carioca, feijão preto · EN: bean, beans, common bean, dry bean · ES: frijol, fréjol, poroto, judía | feijão-comum (PT), feijão-carioca (PT) ¹, feijão-preto (PT) ¹ |
| `trigo` | Trigo | PT: trigo · EN: wheat · ES: trigo | — |
| `arroz` | Arroz | PT: arroz · EN: rice · ES: arroz | — |
| `algodao` | Algodão | PT: algodão, algodao · EN: cotton · ES: algodón, algodon | algodoeiro (PT) |
| `mandioca` | Mandioca | PT: mandioca, macaxeira, aipim, maniva · EN: cassava, manioc · ES: yuca, mandioca | macaxera (PT) |
| `sorgo` | Sorgo | PT: sorgo · EN: sorghum · ES: sorgo | milo (EN) |
| `milheto` | Milheto | PT: milheto · EN: pearl millet, millet · ES: mijo perla, mijo | milheto-pérola (PT) |
| `feijao_caupi` | Feijão-caupi | PT: feijão-caupi, feijão caupi, feijão-de-corda, feijão de corda, feijão macassar, caupi · EN: cowpea, black-eyed pea · ES: caupí, frijol caupí, chícharo de vaca | feijão-macassar (PT) ¹, feijão-fradinho (PT), feijão-verde (PT) |
| `girassol` | Girassol | PT: girassol · EN: sunflower · ES: girasol | maravilla (ES) |
| `crotalaria` | Crotalária | PT: crotalária, crotalaria · EN: sunn hemp, crotalaria · ES: crotalaria | crotalária-juncea (PT) |
| `nabo_forrageiro` | Nabo forrageiro | PT: nabo forrageiro, nabo · EN: forage radish, oilseed radish, tillage radish · ES: nabo forrajero, rábano forrajero | — |
| `aveia` | Aveia-preta | PT: aveia, aveia preta, aveia branca · EN: oat, oats, black oat · ES: avena | aveia-preta (PT) ¹, avena negra (ES) |
| `guandu` | Guandu | PT: guandu, feijão-guandu, andu · EN: pigeon pea · ES: guandú, gandul | guando (PT) |
| `pastagem` | Braquiária | PT: pasto, pastagem, capim, braquiária, braquiaria, capim pras vacas · EN: pasture, grass, grazing, brachiaria · ES: pasto, pastura, potrero, braquiaria | capim-braquiária (PT), braquiarão (PT), marandu (PT), brizantha (PT), palisade grass (EN) |

¹ Só muda a escrita (hífen) de um nome que o app já tem.

## Observações sobre alguns nomes
- **macaxera:** forma popular de "macaxeira" no Nordeste.
- **feijão-verde:** no Nordeste, é o feijão-caupi colhido ainda verde.
- **marandu / braquiarão:** cultivar mais plantada de *Urochloa brizantha*; o produtor costuma chamar o pasto por esse nome.
- **milo (EN):** nome do sorgo granífero nos EUA.
- **maravilla (ES):** nome do girassol no Chile.
- **avena negra (ES):** nome da aveia-preta na Argentina e no Uruguai.
