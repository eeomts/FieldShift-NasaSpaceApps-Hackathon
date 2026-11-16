# Sinônimos e nomes regionais das culturas (proposta)

> Revisado em 15/11/2026 com o mapa de nomes do ZARC (`data/brasil/zarc/mapa_culturas_zarc.csv`), a base de culturas do Brasil (`data/catalogo/culturas.csv`) e o catálogo dos EUA (`data/catalogo/eua/culturas.csv`).
>
> A fonte única dos nomes das culturas é o campo `nomes` de cada cultura em **`agroai/base/culturas.json`**, que é arquivo do app e só muda por PR, avisando o Pedro. Este documento lista o que já existe lá e **o que a proposta muda**.
>
> **Idiomas:** o app tem só **português e inglês** (decisão da Pessoa 3, 15/11/2026). Hoje o `culturas.json` ainda tem uma lista `"es"` (espanhol) em cada uma das 41 culturas: a proposta é **tirar todas**. As tabelas abaixo mostram só PT e EN.

## Como aplicar (no PR do app)
1. **Tirar o espanhol:** apagar a chave `"es"` do `nomes` das 41 culturas do `agroai/base/culturas.json`.
2. **Nomes novos:** para cada linha com nomes em **Novos propostos**, acrescentar o nome na lista do idioma certo (`pt` ou `en`).
3. **Código que ainda fala de espanhol** (fica para quem fizer o PR, não é desta tarefa):
   - `agroai/api/tests/test_arroz_irrigado.py` espera os idiomas `{"pt", "en", "es"}`: passa a esperar `{"pt", "en"}`.
   - A API ainda aceita `idioma="es"` em `GET /culturas` (`app/routers/onboarding.py`) e no cadastro (`app/schemas/auth.py`). O front já só usa PT e EN (`agroai/web/src/i18n.tsx`).
4. Rodar os testes da API (`agroai/api/tests/test_interpretar.py` e o resto).

## Resumo
- **48 nomes novos**: 41 para as 17 culturas do motor do Brasil (regionais, nomes do ZARC, nomes usados nos EUA e erros comuns de escrita) e 7 para culturas que só estão no catálogo dos EUA.
- **Conferido por script** com a mesma normalização do app (`agroai/api/app/services/catalogo.py`: ignora acento, maiúscula e hífen), já sem o espanhol: nenhum nome proposto já existe no app, e nenhum nome fica repetido em duas culturas.
- Sem o espanhol, o app deixa de reconhecer nomes como "maíz", "yuca" ou "frijol". Isso é esperado: o app só atende PT e EN.
- **Resolvido (15/11):** "batata" sozinha é ambígua: o app pede para o produtor escolher entre batata inglesa e batata-doce (campo `ambiguo` no `culturas.json`).
- **Arroz aplicado (15/11):** os nomes de terras altas do `arroz` entraram no app. "arroz" e "rice" sozinhos são ambíguos: o app pede para o produtor escolher entre terras altas e irrigado, sem decidir pelo país.

## Culturas do motor (Brasil)

| id | Cultura | Nome no ZARC | Já no app (`culturas.json`) | Novos propostos |
|---|---|---|---|---|
| `soja` | Soja | Soja | PT: soja · EN: soybean, soy, soya | — |
| `milho` | Milho | Milho 1ª Safra · Milho 2ª Safra | PT: milho, milho safrinha, milho verde · EN: corn, maize | milho 1ª safra (PT, ZARC), milho de verão (PT), milho 2ª safra (PT, ZARC), milho segunda safra (PT), milharal (PT), mio (PT, erro comum) |
| `feijao` | Feijão | Feijão · Feijão 2ª Safra | PT: feijão, feijao, feijão carioca, feijão preto · EN: bean, beans, common bean, dry bean | feijão-comum (PT), feijão das águas (PT), feijão da seca (PT), feijão 2ª safra (PT, ZARC), fejão (PT, erro comum), dry edible bean (EN, EUA) |
| `trigo` | Trigo | Trigo | PT: trigo · EN: wheat | winter wheat (EN, EUA), hard red winter wheat (EN, EUA) |
| `arroz` | Arroz de terras altas | Arroz (sequeiro) | PT: arroz de terras altas, arroz, arroz de sequeiro, arroz de morro · EN: upland rice, rice | — |
| `arroz_irrigado` | Arroz irrigado | Arroz (irrigado) | PT: arroz irrigado, arroz de várzea, arroz inundado, arroz alagado, arroz de banhado · EN: irrigated rice, paddy rice, lowland rice, flooded rice | — |
| `algodao` | Algodão | Algodão Herbáceo | PT: algodão, algodao · EN: cotton | algodoeiro (PT), algodão herbáceo (PT, ZARC), upland cotton (EN, EUA) |
| `mandioca` | Mandioca | Mandioca (aipim, macaxeira) — tábua de perenes | PT: mandioca, macaxeira, aipim, maniva · EN: cassava, manioc | macaxera (PT), macacheira (PT, erro comum), madioca (PT, erro comum) |
| `sorgo` | Sorgo | Sorgo Granífero · Sorgo Granífero 2ª Safra | PT: sorgo · EN: sorghum | sorgo granífero (PT, ZARC), sorgo de grão (PT), sorgo 2ª safra (PT, ZARC), milo (EN, EUA), grain sorghum (EN, EUA) |
| `milheto` | Milheto | Milheto — tábua sem safra | PT: milheto · EN: pearl millet, millet | milheto pérola (PT) |
| `feijao_caupi` | Feijão-caupi | Feijão Caupi | PT: feijão-caupi, feijão caupi, feijão-de-corda, feijão de corda, feijão macassar, caupi · EN: cowpea, black-eyed pea | feijão-fradinho (PT), feijão-verde (PT) |
| `girassol` | Girassol | Girassol | PT: girassol · EN: sunflower | oilseed sunflower (EN, EUA) |
| `crotalaria` | Crotalária | — (não está no ZARC) | PT: crotalária, crotalaria · EN: sunn hemp, crotalaria | crotalária juncea (PT) |
| `nabo_forrageiro` | Nabo forrageiro | — (não está no ZARC) | PT: nabo forrageiro, nabo · EN: forage radish, oilseed radish, tillage radish | — |
| `aveia` | Aveia-preta | — (fora de propósito: o "Aveia" do ZARC é a de grão) | PT: aveia, aveia preta, aveia branca · EN: oat, oats, black oat | — |
| `guandu` | Guandu | — (não está no ZARC) | PT: guandu, feijão-guandu, andu · EN: pigeon pea | guando (PT) |
| `pastagem` | Braquiária (Brasil) · Festuca alta (EUA) | — (não está no ZARC) | PT: pasto, pastagem, capim, braquiária, braquiaria, capim pras vacas · EN: pasture, grass, grazing, brachiaria | capim-braquiária (PT), braquiarão (PT), marandu (PT), brizantha (PT), braquiara (PT, erro comum), palisade grass (EN), festuca (PT), festuca alta (PT), tall fescue (EN, EUA), fescue (EN, EUA) |

## Culturas que só estão no catálogo dos EUA (D-013)

Estas culturas já existem no app, mas não no motor do Brasil. Os nomes novos são os que o catálogo dos EUA usa (`data/catalogo/eua/culturas.csv`).

| id | Cultura nos EUA | Já no app (`culturas.json`) | Novos propostos |
|---|---|---|---|
| `alfafa` | Alfafa (alfalfa hay) | PT: alfafa · EN: alfalfa, lucerne | alfalfa hay (EN) |
| `amendoim` | Amendoim, tipo runner | PT: amendoim · EN: peanut, groundnut | runner peanut (EN) |
| `canola` | Canola de primavera | PT: canola, colza · EN: canola, rapeseed | spring canola (EN) |
| `centeio` | Centeio (cereal rye) | PT: centeio · EN: rye, cereal rye | — |
| `cevada` | Cevada de primavera | PT: cevada · EN: barley | spring barley (EN) |
| `ervilhaca` | Ervilhaca-peluda (hairy vetch) | PT: ervilhaca · EN: vetch, hairy vetch | ervilhaca-peluda (PT) |
| `trevo` | Trevo-encarnado (crimson clover) | PT: trevo · EN: clover | trevo-encarnado (PT), crimson clover (EN) |

## Não incluir (de propósito)

| Nome | Por quê |
|---|---|
| sorgo forrageiro | É outra cultura (o ZARC tem linha própria). A base é o sorgo granífero; se virar `sorgo`, o motor usa números de grão para um sorgo de pasto. |
| trigo duplo propósito | Linha própria no ZARC (forragem + grão), fora da base. |
| milho consorciado com braquiária | Linha própria no ZARC (integração lavoura-pecuária); o app já trata consórcio pelo `consorcio_com` do calendário. |
| hay (sozinho) | Feno pode ser de alfafa, de capim ou de trevo; casaria a cultura errada. |
| spring wheat | O trigo do catálogo dos EUA é o de inverno (hard red winter); o de primavera tem outro ciclo. |

## Observações
- **"arroz" sozinho:** fica no `arroz` (terras altas), porque o mesmo nome não pode estar em duas culturas. Quando o texto é só "arroz" ou "rice", o app pergunta ao produtor se é irrigado (de várzea) ou de terras altas, no cadastro e no chat.
- **Safras do ZARC:** "milho 1ª/2ª safra", "feijão 2ª safra" e "sorgo 2ª safra" continuam sendo a mesma cultura na base; a safra entra no calendário do produtor (meses), não no id.
- **`pastagem` nos dois países:** no Brasil é a braquiária; no catálogo dos EUA, a mesma linha é a festuca alta (tall fescue). Por isso os nomes da festuca entram no `pastagem`.
- **Erros comuns de escrita:** "mio", "fejão", "madioca", "macacheira" e "braquiara" aparecem no texto livre do produtor. Como o app compara palavras inteiras, eles não atrapalham outras palavras.
- **macaxera:** forma popular de "macaxeira" no Nordeste. **feijão-verde:** no Nordeste, é o feijão-caupi colhido ainda verde. **marandu / braquiarão:** cultivar mais plantada de *Urochloa brizantha*. **milo / grain sorghum:** sorgo de grão nos EUA. **arroz de banhado / arroz de morro:** nomes do Sul (banhado = várzea) e do Centro-Norte (morro = terras altas).
