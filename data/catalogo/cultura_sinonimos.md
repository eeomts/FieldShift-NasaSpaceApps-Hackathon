# Sinônimos e nomes regionais das culturas (proposta)

> Tarefa P3-02 (`ToDo/dataset/pessoa-3/02-sinonimos-culturas/`). Dono: Pessoa 3. Revisado em 15/11/2026 com o mapa de nomes do ZARC (`data/brasil/zarc/mapa_culturas_zarc.csv`) e a base de culturas nova (`data/catalogo/culturas.csv`).
>
> A fonte única dos nomes das culturas é o campo `nomes` de cada cultura em **`agroia/base/culturas.json`**, que é arquivo do app e só muda por PR, avisando o Pedro. Este documento lista o que já existe lá e **os nomes novos propostos** para as 17 culturas do motor.
>
> **Idiomas:** só português e inglês (decisão da Pessoa 3, 15/11/2026). A coluna "Já no app" também mostra só PT e EN; os nomes em espanhol que já existem no `culturas.json` não foram mexidos.

## Como aplicar
1. Para cada linha com nomes em **Novos propostos**, acrescentar o nome na lista do idioma certo em `nomes` (`pt` ou `en`) no `agroia/base/culturas.json`.
2. Criar o id `arroz_irrigado` no `culturas.json` (família gramínea, grupo grãos, não perene), com os nomes da tabela. O Yury marcou isso como bloqueio antes de carregar a linha no banco.
3. Rodar os testes da API (`agroia/api/tests/test_interpretar.py`).

## Resumo
- **44 nomes novos** para as 17 culturas: 33 regionais ou em outro idioma, 6 nomes do ZARC e 5 erros comuns de escrita.
- **Conferido por script** com a mesma normalização do app (`agroia/api/app/services/catalogo.py`: ignora acento, maiúscula e hífen): nenhum nome proposto já existe no app, e nenhum nome fica repetido em duas culturas.
- Saíram 4 nomes da versão anterior que só mudavam o hífen ("feijão-carioca", "feijão-preto", "feijão-macassar", "aveia-preta"): o app já os reconhece.
- ⚠️ Repetido que já existe no app (não é desta proposta): "batata" está em `batata` e em `batata_doce`.

## Nomes por cultura

| id | Cultura | Nome no ZARC | Já no app (`culturas.json`) | Novos propostos |
|---|---|---|---|---|
| `soja` | Soja | Soja | PT: soja · EN: soybean, soy, soya | — |
| `milho` | Milho | Milho 1ª Safra · Milho 2ª Safra | PT: milho, milho safrinha, milho verde · EN: corn, maize | milho 1ª safra (PT, ZARC), milho de verão (PT), milho 2ª safra (PT, ZARC), milho segunda safra (PT), milharal (PT), mio (PT, erro comum) |
| `feijao` | Feijão | Feijão · Feijão 2ª Safra | PT: feijão, feijao, feijão carioca, feijão preto · EN: bean, beans, common bean, dry bean | feijão-comum (PT), feijão das águas (PT), feijão da seca (PT), feijão 2ª safra (PT, ZARC), fejão (PT, erro comum) |
| `trigo` | Trigo | Trigo | PT: trigo · EN: wheat | — |
| `arroz` | Arroz de terras altas | Arroz | PT: arroz · EN: rice | arroz de sequeiro (PT), arroz de terras altas (PT), arroz de morro (PT), upland rice (EN) |
| `algodao` | Algodão | Algodão Herbáceo | PT: algodão, algodao · EN: cotton | algodoeiro (PT), algodão herbáceo (PT, ZARC) |
| `mandioca` | Mandioca | — (não está no ZARC) | PT: mandioca, macaxeira, aipim, maniva · EN: cassava, manioc | macaxera (PT), macacheira (PT, erro comum), madioca (PT, erro comum) |
| `sorgo` | Sorgo | Sorgo Granífero · Sorgo Granífero 2ª Safra | PT: sorgo · EN: sorghum | sorgo granífero (PT, ZARC), sorgo de grão (PT), sorgo 2ª safra (PT, ZARC), milo (EN), grain sorghum (EN) |
| `milheto` | Milheto | — (não está no ZARC) | PT: milheto · EN: pearl millet, millet | milheto pérola (PT) |
| `feijao_caupi` | Feijão-caupi | Feijão Caupi | PT: feijão-caupi, feijão caupi, feijão-de-corda, feijão de corda, feijão macassar, caupi · EN: cowpea, black-eyed pea | feijão-fradinho (PT), feijão-verde (PT) |
| `girassol` | Girassol | Girassol | PT: girassol · EN: sunflower | — |
| `crotalaria` | Crotalária | — (não está no ZARC) | PT: crotalária, crotalaria · EN: sunn hemp, crotalaria | crotalária juncea (PT) |
| `nabo_forrageiro` | Nabo forrageiro | — (não está no ZARC) | PT: nabo forrageiro, nabo · EN: forage radish, oilseed radish, tillage radish | — |
| `aveia` | Aveia-preta | Aveia | PT: aveia, aveia preta, aveia branca · EN: oat, oats, black oat | — |
| `guandu` | Guandu | — (não está no ZARC) | PT: guandu, feijão-guandu, andu · EN: pigeon pea | guando (PT) |
| `pastagem` | Braquiária | — (não está no ZARC) | PT: pasto, pastagem, capim, braquiária, braquiaria, capim pras vacas · EN: pasture, grass, grazing, brachiaria | capim-braquiária (PT), braquiarão (PT), marandu (PT), brizantha (PT), braquiara (PT, erro comum), palisade grass (EN) |
| `arroz_irrigado` | Arroz irrigado | (ver arroz) | **id ainda não existe no app** | arroz irrigado (PT), arroz de várzea (PT), arroz inundado (PT), arroz alagado (PT), arroz de banhado (PT), irrigated rice (EN), paddy rice (EN), lowland rice (EN) |

## Não incluir (de propósito)

| Nome | Por quê |
|---|---|
| sorgo forrageiro | É outra cultura (o ZARC tem linha própria). A base é o sorgo granífero; se virar `sorgo`, o motor usa números de grão para um sorgo de pasto. |
| trigo duplo propósito | Linha própria no ZARC (forragem + grão), fora da base. |
| milho consorciado com braquiária | Linha própria no ZARC (integração lavoura-pecuária); o app já trata consórcio pelo `consorcio_com` do calendário. |

## Observações
- **"arroz" sozinho:** fica no `arroz` (terras altas), porque o mesmo nome não pode estar em duas culturas. No Sul, quem escreve só "arroz" quase sempre planta arroz irrigado. Sugestão para o app: quando o texto for só "arroz" e o produtor tiver irrigação ou várzea, perguntar "É arroz irrigado (de várzea) ou de sequeiro?".
- **Safras do ZARC:** "milho 1ª/2ª safra", "feijão 2ª safra" e "sorgo 2ª safra" continuam sendo a mesma cultura na base; a safra entra no calendário do produtor (meses), não no id.
- **Erros comuns de escrita:** "mio", "fejão", "madioca", "macacheira" e "braquiara" aparecem no texto livre do produtor. Como o app compara palavras inteiras, eles não atrapalham outras palavras.
- **macaxera:** forma popular de "macaxeira" no Nordeste. **feijão-verde:** no Nordeste, é o feijão-caupi colhido ainda verde. **marandu / braquiarão:** cultivar mais plantada de *Urochloa brizantha*. **milo / grain sorghum:** sorgo de grão nos EUA. **arroz de banhado / arroz de morro:** nomes do Sul (banhado = várzea) e do Centro-Norte (morro = terras altas).
- **EUA (D-010):** quando o catálogo dos EUA do Yury (`data/catalogo/eua/`) tiver culturas novas, os nomes delas entram aqui.
