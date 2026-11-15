# Notas da tarefa 04: o que cada cultura exige de equipamento

> Rascunho de 14/11/2026, ampliado em 15/11/2026 com `arroz_irrigado` e as culturas dos EUA (`alfafa`, `amendoim`, `canola`, `centeio`, `cevada`, `ervilhaca`, `trevo`) e com uma fonte publicada para cada caso não óbvio. **Ainda a revisar por alguém de agronomia** (Pessoa 1).
>
> **O CSV (`data/catalogo/cultura_equipamentos.csv`) é a fonte de verdade.** Estas notas só explicam as escolhas; se o CSV mudar, ele é que vale.

## Regras usadas

- Várias linhas na mesma etapa = **qualquer uma** serve. Por isso, cada etapa lista todas as formas comuns de fazer, para o filtro da pergunta 26b não eliminar uma cultura que o produtor consegue fazer de outro jeito.
- O CSV **não expressa "precisa de A e de B"**. Quando a operação exige duas máquinas em sequência (amendoim: arrancador-invertedor e depois recolhedora; feno: segadora, ancinho e enfardadora), a linha usa a categoria que representa o conjunto mecanizado.
- `trator` **não aparece sozinho**: plantadeira, colhedora e roçadeira já pressupõem o trator. Listar `trator` como alternativa diria que só o trator basta, o que não é verdade.
- Só os ids de `agroai/base/equipamentos.json`. Nenhum id foi inventado.
- O CSV não tem coluna de país: a mesma `cultura_id` vale para o Brasil e para os EUA (ex.: `aveia`, `milho`).
- O filtro (`agroai/api/app/services/motor/filtro.py`, `_equipamento`) só lê as etapas `plantio` e `colheita`. Por isso as coberturas usam `colheita` para o manejo do fim do ciclo (não há etapa `manejo`).

## Culturas de cobertura e forrageiras: o que é "colheita"

Para as culturas que não são colhidas como grão, a `colheita` é o **manejo do fim do ciclo**, a operação que encerra a cultura e deixa a palhada:

| Cultura | "Colheita" considerada | Equipamentos |
|---|---|---|
| Crotalária, guandu | Roçada ou corte para adubo verde | `rocadeira` ou `manual` (foice) |
| Nabo forrageiro | Roçada, rolagem ou dessecação | `rocadeira` (inclui rolo-faca) ou `pulverizador` (inclui bomba costal) |
| Aveia-preta | Rolagem ou dessecação para palhada; ou colheita de grão para semente | `rocadeira`, `pulverizador` ou `colhedora` |
| Milheto | Grão, ou roçada como cobertura | `colhedora`, `rocadeira` ou `manual` |
| Braquiária (`pastagem`) | Pastejo direto, silagem ou roçada | `manual` (pastejo não exige máquina), `ensiladeira` ou `rocadeira` |
| Centeio, ervilhaca peluda, trevo-encarnado (EUA) | Rolagem (roller-crimper), roçada (flail mower) ou dessecação | `rocadeira` ou `pulverizador` |
| Alfafa (EUA, feno) | Corte de feno ou pré-secado/silagem | `rocadeira` (segadora) ou `ensiladeira` |

## Culturas acrescentadas em 15/11/2026

| Cultura | Plantio | Colheita | Por quê |
|---|---|---|---|
| `arroz_irrigado` (RS/SC) | `plantadeira_graos`, `manual` | `colhedora`, `manual` | Plantio direto, cultivo mínimo e convencional semeiam em linha; no pré-germinado (98% de SC) a semente vai a lanço na lâmina d'água, à mão, com implemento no trator ou por avião. Colhedora com pneu arrozeiro ou esteira; a colheita manual (cutelo) existe em lavouras pequenas |
| `cevada` (ND/MN) | `plantadeira_graos` | `colhedora` | Óbvio, igual ao trigo: semeadora de cereais e colhedora. Sem `manual` (mesmo critério do trigo) |
| `canola` (ND/MN) | `plantadeira_graos` | `colhedora` | Colhe-se com a colhedora, direto ou depois do enleiramento (swather). Como o corte direto basta, a falta de enleiradora não elimina a cultura |
| `amendoim` (GA) | `plantadeira_graos`, `manual` | `colhedora`, `manual` | Mecanizado: arrancador-invertedor e depois recolhedora (combine de amendoim); `colhedora` representa o conjunto. Manual: no Nordeste o amendoim é cultivado em 0,3 a 5 ha só com mão de obra, do plantio à colheita (arranquio manual) |
| `alfafa` (NE/CA) | `plantadeira_graos` | `rocadeira`, `ensiladeira` | Semeadura em linha (drill) ou semeadora tipo Brillion. Colheita de feno: segadora/segadora-condicionadora, ancinho e enfardadora; ou picada para silagem/pré-secado. Sem `manual` |
| `centeio` (IA/IL) | `plantadeira_graos`, `manual` | `rocadeira`, `pulverizador` | Semeadura em linha ou a lanço; em área pequena, semeadora manual. Manejo por rolo (roller-crimper), roçada ou dessecação |
| `ervilhaca` (IA/IL/NE) | `plantadeira_graos`, `manual` | `rocadeira`, `pulverizador` | Mesmo critério do centeio. Roller-crimper funciona quando há vagens pequenas; leguminosas pedem herbicida (2,4-D/dicamba) |
| `trevo` (GA, trevo-encarnado) | `plantadeira_graos`, `manual` | `rocadeira`, `pulverizador` | Mesmo critério. No catálogo dos EUA o manejo é dessecação; o rolo mata pior o trevo, mas a roçada (flail) chega a 93% em 3 semanas |

Nenhuma cobertura dos EUA tem `colhedora` (diferente da aveia-preta, cuja semente é colhida no Brasil): o catálogo dos EUA trata centeio, ervilhaca e trevo só como cobertura. Nenhuma tem `manual` na colheita (mesmo critério de aveia e nabo): o manejo manual de dezenas de hectares não é prática citada.

### Categorias que faltam em `equipamentos.json` (sugestão para o Pedro, por PR)

- **Enfardadora (baler) e ancinho (rake)**: feno de alfafa. Hoje `rocadeira` (nome_en "Mower") representa a linha de feno; é a mais próxima, mas quem só tem segadora não consegue enfardar.
- **Arrancador-invertedor de amendoim (digger-shaker-inverter)**: hoje coberto por `colhedora`.
- **Enleiradora (swather/windrower)**: canola; não faz falta porque o corte direto com `colhedora` serve.
- **Preparo em lâmina d'água (enxada rotativa/grade na formação da lama)** do arroz pré-germinado: existe em `preparo_solo`, mas o CSV não tem etapa de preparo. Fica fora, como nas outras culturas.
- **Plantadeira de manivas e afofador/arrancador de mandioca** (já anotado abaixo).

## Casos que merecem conferência (culturas do Brasil)

| Caso | Decisão no rascunho | Por quê |
|---|---|---|
| Mandioca, plantio e colheita | Só `manual` | A mecanização da mandioca usa **plantadeira de manivas** e **afofador/arrancador**, que não existem nas categorias. Sugestão para o Pedro (PR no `equipamentos.json`): criar uma categoria para essas máquinas, ou decidir que `plantadeira_graos`/`preparo_solo` as representam |
| Feijão e feijão-caupi, colheita | `colhedora` ou `manual` | Há colheita mecanizada direta, mas na agricultura familiar o arranquio ou a catação de vagens é manual |
| Algodão, colheita | `colhedora` ou `manual` | A colhedora de algodão é uma máquina própria, mas cai na categoria geral `colhedora`. A colheita manual ainda existe em áreas pequenas |
| Arroz (terras altas), plantio e colheita | Inclui `manual` | Arroz de sequeiro da agricultura familiar (plantio com matraca e corte manual). O arroz irrigado agora tem linha própria (`arroz_irrigado`) |
| `tracao_animal` no plantio | Feijão, feijão-caupi, milho e sorgo: incluído. Algodão: não incluído (decisão do time, 14/11/2026) | Plantadeira de tração animal é comum no Semiárido. Sem ela no milho, o produtor de Irecê (milho + feijão consorciados) que só tem tração animal perderia o milho no filtro |
| Girassol, soja e trigo sem `manual` | Não incluído | Não há colheita manual viável fora de hortas experimentais |
| `irrigacao` e `preparo_solo` | Não usados | Nenhuma cultura **exige** irrigação como máquina de plantio ou colheita (o arroz irrigado sem irrigação é eliminado por outra regra do filtro, `arroz_sem_irrigacao`) nem preparo convencional (plantio direto é o padrão) |

## Fontes por caso

Todas foram abertas e lidas (texto do PDF ou da página) em 15/11/2026. A citação curta é o trecho que sustenta a decisão.

### Culturas acrescentadas

- **Arroz irrigado, plantio** — Santos, A.B. dos. *Sistemas de Plantio*. Cap. 13 de Santos, Stone & Vieira (ed.), *A Cultura do Arroz no Brasil*, 2ª ed., Embrapa Arroz e Feijão, 2006. https://ainfo.cnptia.embrapa.br/digital/bitstream/doc/193280/1/lv-cultura-arroz-Brasil-2ed.cap13.pdf — "plantio direto e cultivo mínimo [...] vêm sendo usada em cerca de 47% da área cultivada com arroz irrigado no Rio Grande do Sul. O sistema pré-germinado é adotado em 98%, em Santa Catarina"; "A semeadura das sementes pré-germinadas é feita a lanço sobre a lâmina de água, manualmente, por meio de implementos acoplados ao trator ou por avião, dependendo da dimensão da lavoura."
- **Arroz irrigado, colheita** — Silva, J.G. da; Fonseca, J.R. *Colheita*. Cap. 18 do mesmo livro, 2006. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/193301/1/lv-cultura-arroz-Brasil-2ed.cap18.pdf — "As máquinas especiais para colheita em terrenos de baixa sustentação, como os de lavouras irrigadas, são equipadas com pneus arrozeiros ou com pneus duplados [...] ou com esteiras"; "A colheita manual do arroz requer em torno de dez dias de trabalho de um homem para cortar 1 ha, sendo mais difundida em pequenas lavouras."
- **Amendoim, colheita mecanizada** — Sumner, P.E. *Peanut Digger and Combine Efficiency*. UGA Extension Bulletin 1087, revisão de 31/07/2012. https://fieldreport.caes.uga.edu/publications/B1087/peanut-digger-and-combine-efficiency/ — "The modern peanut digger-inverter [...] lifts peanuts from the soil, separates pods from the soil"; "All peanuts produced commercially in Georgia are harvested directly from the windrow with a combine."
- **Amendoim, plantio e colheita manuais** — Suassuna, T.M.F.; Coutinho, W.M.; Sofiatti, V.; Suassuna, N.D.; Gondim, T.M.S. *Manual de Boas Práticas Agrícolas para a Produção do Amendoim no Nordeste do Brasil*. Embrapa Algodão, Documentos 207, 2008. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/278148/1/DOC207.pdf — "o tamanho das lavouras varia entre 0,3 hectares (uma tarefa) e cinco hectares. O cultivo emprega mão-de-obra, familiar ou contratada, para realizar todas atividades, desde o plantio até a colheita"; Fig. 1: "Plantas invertidas para cura do amendoim após colheita manual".
- **Alfafa, plantio** — Michel, J. *Establishing a New Stand of Alfalfa*. Iowa State Univ. Extension, ICM News, 14/04/2023. https://crops.extension.iastate.edu/cropnews/2023/04/establishing-new-stand-alfalfa — "Drilling spring forages is the preferred seeding method."; "Broadcast seeding may require a 10 to 15% higher seeding rate".
- **Alfafa, colheita** — Undersander, D. *Hay Harvesting Equipment and Harvest Strategies for Quality*. Proceedings, 2013 Western Alfalfa & Forage Symposium, UC Davis. https://alfalfasymposium.ucdavis.edu/+symposium/proceedings/2013/13WAS-27_Undersander_HarvestStrategies.pdf — "mow alfalfa with either disc or sickle mower, condition with properly adjusted roller conditioner [...] rake/merge into windrow [...] and bale when adequately dry"; "3 t/a (720 gallons) of water per acre before it can be chopped for silage".
- **Canola, colheita** — NDSU Extension. *Canola Straight Cut or Swath*. Crop & Pest Report, 28/07/2022. https://www.ndsu.edu/agriculture/ag-hub/ag-topics/crop-production/crops/canola/canola-straight-cut-or-swath — "Producers traditionally have swathed rather than straight combined canola."; pod shatter resistant hybrids "has made straight cutting the new trend for canola harvest"; "both swathing and straight combining have their places".
- **Centeio, ervilhaca, trevo: manejo por rolo ou roçada** — USDA-ARS National Soil Dynamics Laboratory (equipe de T. Kornecki, autor dos rolos das figuras). *Cover Crop Management for No-till Vegetables: Cantaloupe*, Conservation Systems Fact Sheet No. 12, fev. 2016. https://www.ars.usda.gov/ARSUserFiles/60100500/FactSheets/FS12.pdf — "Termination methods for cereal rye, crimson clover, and hairy vetch cover crops were 1) rolling/crimping [...] and 2) flail mowing"; Tab. 1: na 3ª semana, 96-99% (centeio), 89-92% (ervilhaca) e 87-93% (trevo).
- **Centeio, ervilhaca: rolo e herbicida** — Curran, W.; Ryan, M. (Penn State); Mirsky, S. (USDA-ARS). *Cover Crop Rollers for Northeastern Grain Production*. Penn State Extension, atualizado em 05/05/2026. https://extension.psu.edu/cover-crop-rollers-for-northeastern-grain-production — "cereal rye was consistently controlled at Zadoks growth stage 61"; "consistent hairy vetch control was achieved when small pods were visible"; "the roller, in combination with a half-rate herbicide, was as effective as the herbicide alone at the full rate".
- **Trevo: rolo pior que no centeio** — O'Brien, D. *Rolling Out Cover Crops for Higher Yields and Improved Soil Quality*. USDA-ARS, AgResearch Magazine 61(2), fev. 2013. https://agresearchmag.ars.usda.gov/2013/feb/crops — "The clover was difficult to kill with the crimper, but the device terminated the rye effectively."; "Conventional growers can use herbicides to kill their cover crops".
- **Centeio, ervilhaca, trevo: plantio manual** — Schonbeck, M.; Morse, R. *Using Manually-Operated Seeders for Precision Cover Crop Plantings on the Small Farm*. Virginia Association for Biological Farming, Information Sheet 4-06, 12/2006 (cópia na SARE). https://sare.org/wp-content/uploads/Cover-crop-seeders-for-small-farms.pdf — "Manually operated vegetable seeders can sow cover crops uniformly and precisely in small areas"; "good stands when planted with the #22 plate [...]: oats, rye, barley, wheat, black oats, vetches"; "Crimson clover [...] give good stands with the #5 plate".
- **Cevada**: sem fonte própria (caso óbvio, igual ao trigo).

### Culturas que já estavam no arquivo

- **Mandioca, plantio e colheita manuais** — Ferreira Filho, J.R.; Silveira, H.F.; Macedo, J.J.G.; Lima, M.B.; Cardoso, C.E.L. *Cultivo, processamento e uso da mandioca: instruções práticas*. Embrapa Mandioca e Fruticultura, 2013. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/974126/1/CartilhaMandioca2013.pdf — "Nas pequenas lavouras, o plantio é feito em 'cova rasa' (buraco feito a enxada)"; "A colheita da mandioca é primordialmente manual e/ou com o auxilio de ferramentas, embora já existam implementos mecanizados."
- **Mandioca, máquinas que faltam** — Rocha, H.S. et al. *Miniestacas de mandioca – nova alternativa de material de plantio*. Embrapa Mandioca e Fruticultura, Comunicado Técnico 179, 2021. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1133022/1/ComunicadoTecnico179-Herminio-2021-AINFO.pdf — "plantio mecanizado, sistema largamente utilizado na cultura da mandioca na região Centro-Sul do Brasil". E Delalibera et al. *Desempenho técnico da colhedora de mandioca Maná-Inroda na colheita de mandioca para indústria*. IDR-Paraná, IT 07, 2025. https://www.idrparana.pr.gov.br/system/files/publico/pesquisa/publicacoes/it/007/IT-07-Colhedora-Mandioca.pdf — "utilizando um subsolador alado (afofador) montado no sistema de três pontos do trator [...] facilitando o arranquio das raízes. Na etapa subsequente, as operações passam a ser manuais".
- **Feijão, colheita** — Silva, J.G.; Aidar, H.; Beduschi, L.C.; Mardegan Filho, J.; Fonseca, J.R. *Mecanização da colheita do feijoeiro: uso de recolhedoras trilhadoras*. Embrapa Arroz e Feijão, Circular Técnica 37, 2000. https://www.infoteca.cnptia.embrapa.br/bitstream/doc/208468/1/circ37.pdf — "são três os sistemas empregados na colheita do feijoeiro: o manual, o semi-mecanizado e o mecanizado."
- **Feijão-caupi, plantio (manual e tração animal) e colheita** — Andrade, A.S. et al.; Ribeiro, V.Q. (ed.). *Cultivo do Feijão-caupi*. Embrapa Meio-Norte, Sistemas de Produção 2, 2002. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/66591/1/sistemaproducao2.PDF — "Plantio manual — É mais utilizado em pequenas propriedades, utilizando-se de enxada ou matraca."; "Plantio à tração animal — São utilizadas plantadeiras simples"; "O caupi tradicionalmente, é colhido manualmente, vagem por vagem"; "colheita e debulha através de colheitadeira".
- **Algodão, colheita manual** — Silva, O.R.R.F.; Sofiatti, V.; Cartaxo, W.V.; Barbosa, V.S.C.; Wanderley, M.J.R. *Algodão em Pluma* (Coleção Agroindústria Familiar). Embrapa Algodão / Embrapa Informação Tecnológica, 2009. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/659531/1/AGROINDFAMAlgodaoempluma1ed012009.pdf — "Na agricultura familiar, a colheita é sempre feita manualmente e por etapas."
- **Arroz de terras altas, matraca e colheita manual** — Utumi, M.M. (ed.). *Sistema de produção de arroz de terras altas*. Embrapa Rondônia, Sistemas de Produção 31, 2008. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/709721/1/sp31.pdf — Tab. 11 (baixa tecnologia): "Semeadura com 'matraca'" e colheita em "Corte", "Empilhamento" e "Trilhagem" (dias-homem). Ver também o cap. 18 citado acima (colheita manual "mais difundida em pequenas lavouras").
- **Tração animal no plantio (milho e feijão)** — Guimarães Sobrinho, J.B.; Finch, E.O.; Ramalho, M.A.P. *Cultivador a tração animal modificado para a realização da adubação nitrogenada em cobertura e para a semeadura do feijão da seca consorciado com milho*. Embrapa Milho e Sorgo (CNPMS), Circular Técnica 12, 1986. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/482837/1/circ121.pdf — "há uma predominância de pequenos agricultores, sem condições de adquirir implementos tratorizados. Sendo assim, o uso da tração animal nesta cultura desempenha um papel preponderante"; cita "plantadeiras tradicionais de uma linha, a tração animal". O caupi está coberto pela fonte da Embrapa Meio-Norte acima.
- **Braquiária (`pastagem`), uso e plantio** — Pereira, M.C.; Queiroz, H.P. *Principais cuidados na formação de pastagens*. Embrapa Gado de Corte, Comunicado Técnico 140, 2017. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1087115/1/Principaiscuidadosnaformacaodepastagens.pdf — uso para "pastejo, silagem, fenação, vedação ou combinação de usos"; "Regulagem da semeadora"; "No caso da semeadura a lanço, essas profundidades são alcançadas com uma grade niveladora fechada."
- **Coberturas (crotalária, guandu, nabo, milheto): rolo-faca, roçadeira ou dessecação** — Carvalho, A.M. et al. *Plantas de cobertura do solo recomendadas para a entressafra de milho em Sistema Plantio Direto no cerrado*. Embrapa Cerrados, Comunicado Técnico 181, 2018. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1097400/1/CT181.pdf — "O manejo dessas plantas de cobertura pode ser mecânico, por meio de rolo-faca, roçadeira ou triton; e químico, com aplicação de dessecantes/herbicidas."; "milheto e crotalária-juncea, podem ser deixadas até a maturação dos grãos". E Bevilaqua, G.P. et al. *Adubação verde na agricultura sustentável*, em Embrapa Clima Temperado, Documentos 527, 2022, p. 27. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1149635/1/CPACT-Doc-527-pag27.pdf — "rolo-faca, picador de palha, roçadeira ou mesmo a grade aradora, sendo que a preferência recai sobre o rolo faca".
- **Crotalária e guandu, corte com foice (`manual`)** — Moreira, V.R.R. *Adubação verde como fonte de nitrogênio*. Coordenação de Agroecologia/MAPA, ficha sem data (cópia em site de terceiros). https://www.fitoterapiabrasil.com.br/sites/default/files/documentos-oficiais/2-adubacao-verde-como-fonte-de-nitrogenio.pdf — "As plantas devem ser cortadas com foice, roçadeira costal, roçadeira tratorizada, rolofaca, grade leve [...]".
- **Aveia-preta: rolo-faca/roçadeira, dessecação ou colhedora** — Machado, L.A.Z.; Sousa, P.G.; Hernani, L.C. *Lavoura de Aveia* (folder). Embrapa Agropecuária Oeste, Dourados-MS, 1999. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/242258/1/AVEIA.pdf — "Para cobertura do solo pode proceder-se das seguintes formas: a) realizar o manejo cultural com rolo-faca ou com roçadeira na fase de grão leitoso; b) fazer dessecação com herbicidas [...]; e c) colher os grãos com colhedora equipada com distribuidor de palha."; "A semente da aveia pode ser outra fonte de renda".

### Ainda sem fonte publicada (pendente)

- `sorgo` com `tracao_animal` no plantio (a fonte da Embrapa Milho e Sorgo cita milho e feijão).
- `milheto` com `colhedora`: o CT181 só diz que o milheto "pode ser deixado até a maturação dos grãos", não fala da colhedora.
- `pastagem` com `rocadeira` (o CT 140 não fala de roçada) e `manual` como pastejo (decisão de modelagem: pastejo não exige máquina).
- Crotalária e guandu com `manual`: a fonte da foice é do MAPA, não da Embrapa, e a cópia lida está num site de terceiros.
- Girassol, soja e trigo sem `manual`: nenhuma fonte procurada a fundo (caso tratado como óbvio).
