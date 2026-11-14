# ESA WorldCover no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o ESA WorldCover, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o ESA WorldCover aos outros datasets.

## O que é o ESA WorldCover

O ESA WorldCover é um **mapa global de cobertura do solo em 10 m**, feito pela Agência Espacial Europeia (ESA) a partir de imagens do **Sentinel-1** (radar) e do **Sentinel-2** (óptico).

Existem **dois mapas**, e só dois:

- **2020** (versão v100), com acurácia global de cerca de 74%.
- **2021** (versão v200), com acurácia global de cerca de 77%.

Os dois usam **11 classes** e são abertos, com licença CC BY 4.0. Os mapas foram feitos com versões diferentes do algoritmo, então a diferença entre 2020 e 2021 mistura mudança real com mudança de método.

## Por que usar

**1. Detalhe de 10 m no entorno da lavoura.** O MODIS Land Cover tem 500 m. O WorldCover separa a mata ciliar estreita, o banhado ao lado da várzea e o capão de mato no meio do campo.

**2. Uma segunda opinião sobre o MapBiomas.** O MapBiomas é a referência de uso do solo no Brasil, com série anual. O WorldCover usa outros satélites (Sentinel, contra Landsat do MapBiomas) e outro método. Quando os dois concordam numa classe, a confiança sobe.

**3. Classes que importam para a regra.** Áreas úmidas herbáceas, mangues e água permanente indicam onde **não** expandir lavoura nem drenar. A ferramenta usa isso para marcar restrições, não para sugerir culturas.

## Como entra no projeto

### Harmonização

- **Acesso:** download em tiles de 3° × 3° (GeoTIFF) pelo site do WorldCover, pelo Zenodo ou pela cópia aberta na AWS; também está no Google Earth Engine.
- **Processamento:** recortar a fazenda e um entorno de alguns quilômetros, calcular a fração de cada classe por talhão e por célula da grade comum, e comparar com o MapBiomas do mesmo ano (2020 e 2021). No panorama nacional, só a fração das classes por célula entra na grade comum.

| Classe (código) | O que é | Uso |
| --- | --- | --- |
| Cobertura arbórea (10) | Florestas, matas, silvicultura | Mata ciliar, reserva, quebra-vento |
| Arbustiva (20) | Vegetação de arbustos | Cerrado aberto, Caatinga |
| Herbácea (30) | Campos e pastagens | Campo nativo, pasto |
| Cultivo (40) | Lavouras temporárias | Área agrícola |
| Construída (50) | Cidades, estradas, galpões | Excluir da análise |
| Solo exposto ou vegetação esparsa (60) | Pouca ou nenhuma vegetação | Areais, solo degradado |
| Água permanente (80) | Rios, lagos, represas | Restrição e fonte de água |
| Área úmida herbácea (90) | Banhados, várzeas alagáveis | Restrição a drenagem |
| Mangue (95) | Manguezais | Restrição (litoral) |

As classes neve e gelo (70) e musgo e líquen (100) existem no mapa, mas quase não aparecem no Brasil.

> Confirmar nas páginas oficiais se há mapa de anos depois de 2021, a acurácia das classes "cultivo", "herbácea" e "área úmida" na América do Sul (o relatório de validação traz valores por continente) e a definição exata de cada classe.

### Indicadores calculados

- **Composição do entorno:** fração de mata, campo, cultivo, água e área úmida num raio de 2 km.
- **Restrições:** área do talhão ou da faixa vizinha classificada como água, área úmida ou mangue.
- **Concordância com o MapBiomas:** percentual de pixels em que as duas fontes dizem a mesma coisa.

### Nível de confiança

A acurácia global de cerca de 75% significa que, em média, **um em cada quatro pixels pode estar errado**. Os erros se concentram em classes parecidas: campo nativo e pasto confundidos com lavoura, arroz alagado confundido com área úmida. Por isso o WorldCover nunca decide sozinho. Se ele e o MapBiomas concordam, a confiança é **alta**; se discordam, a ferramenta mostra as duas versões e pergunta ao produtor.

A mudança de 2020 para 2021 **não** é tratada como mudança de uso, porque parte dela vem do novo algoritmo.

## Onde o produtor vê isso

**Etapa 2, mapa do entorno.** Uma camada mostra mata, campo, água e áreas úmidas em volta dos talhões.

**Riscos para revisão local.** Quando uma estratégia envolve drenar ou ampliar a lavoura perto de uma área úmida, o cartão avisa.

**Glossário.** Explica que o mapa é de 2020 e 2021 e que um em cada quatro pixels pode estar errado.

## Caso hipotético: ESA WorldCover junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Sra. Helena tem 400 ha perto de Dom Pedrito, na Campanha Gaúcha, no Pampa. Planta arroz na várzea e cria gado de corte no campo nativo.

- **Rotação atual:** arroz irrigado (outubro a março), seguido de dois anos de pousio com pastejo de gado na resteva e no campo.
- **Irrigação:** arroz por inundação, com água de um açude próprio.
- **Prioridades:** renda e forragem altas; água média.
- **Mercado:** arroz para a cooperativa, bezerros e novilhos; há compradores de soja na região.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **ESA WorldCover** | Em 2021, 60 ha na borda sul da várzea são "área úmida herbácea", ligados a um banhado maior. Uma faixa de "cobertura arbórea" de 30 m segue o arroio. Parte dos talhões de arroz aparece como "área úmida" em 2020 e como "cultivo" em 2021. |
| MapBiomas | Mostra o arroz nos talhões de várzea em quase todos os anos e classifica a borda sul como campo alagado e área pantanosa desde 1985. |
| HLS | Lâmina d'água nos talhões de outubro a dezembro; cobertura rala na resteva de abril a julho. |
| GPM IMERG | Primaveras chuvosas em anos de El Niño; verões com estiagem em anos de La Niña. |
| NASA POWER | Geadas de junho a agosto na maioria dos anos. |
| SRTM | Várzea quase plana, com declividade abaixo de 1%. |

### Onde os dados se completam

**O banhado é real.** O WorldCover e o MapBiomas, feitos com satélites e métodos diferentes, concordam que a borda sul é área úmida há décadas. Confiança **alta**. Uma estratégia que drena a várzea inteira para soja avançaria sobre ele.

**O arroz alagado confunde o mapa.** Em 2020, o WorldCover chamou parte do arroz de "área úmida"; em 2021, de "cultivo". Não houve mudança de uso, e sim um erro esperado da classe. O MapBiomas e o HLS mostram que ali sempre houve arroz.

**O pasto da entressafra é fraco.** O HLS mostra a resteva com pouca cobertura no outono e no inverno, quando o campo nativo também para de crescer por causa do frio.

### Regras ativadas

- **Área úmida confirmada por duas fontes ao lado da lavoura** adiciona restrição de drenagem às estratégias com soja na várzea.
- **Prioridade alta em forragem e pasto fraco no inverno** aumentam o peso de pastagens de inverno.
- **Arroz contínuo com água limitada em anos de La Niña** aumenta o peso de culturas de sequeiro na rotação.

### Comparação das estratégias

| Critério | A: atual (arroz → 2 anos de pousio pastejado) | B: arroz → soja em toda a várzea, com drenos | C: arroz → azevém com cornichão pastejado → soja só na parte já drenada |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●●○○○ | ●●●○○ | ●●●●○ |
| Nitrogênio | ●○○○○ | ●●●○○ | ●●●●○ |
| Erosão | ●●●○○ | ●●●○○ | ●●●●○ |
| Forragem | ●●○○○ | ●○○○○ | ●●●●● |
| Renda | ●●●○○ | ●●●●● | ●●●●○ |

A B tem a maior renda, mas tira forragem e avança sobre o banhado. Com renda e forragem altas, a **estratégia C** fica em primeiro: perde um ponto em renda e ganha quatro em forragem. A B fica em segundo e a atual em último.

### Cartão da estratégia C

> **Resumo:** uma opção é, depois do arroz, semear azevém com cornichão para pastejo no inverno e incluir soja só nos talhões que já têm drenagem, mantendo a faixa do banhado fora da lavoura.
>
> **Por que foi sugerida:** o pasto da resteva fica fraco no inverno, e a borda sul da várzea é área úmida há décadas.
>
> **Evidências:** banhado na borda sul (ESA WorldCover e MapBiomas, confiança alta); resteva com pouca cobertura no outono e inverno (HLS, confiança alta); geadas de junho a agosto (POWER, confiança alta); várzea plana (SRTM, confiança alta).
>
> **Benefícios:** pasto de inverno para o gado, nitrogênio do cornichão para a cultura seguinte e menos água de irrigação nos anos com soja.
>
> **Lacunas:** não sabemos quais talhões já têm drenos nem como o cornichão se estabelece no seu solo.
>
> **Riscos para revisão local:** conferir com o órgão ambiental do estado as regras para áreas úmidas antes de qualquer drenagem; avaliar com o agrônomo a drenagem dos talhões de soja e o controle do arroz-vermelho.

## Conclusão

O ESA WorldCover não diz o que plantar. Ele mostra, em 10 m, o que existe em volta da lavoura, e serve de segunda opinião para o MapBiomas. No caso, a concordância das duas fontes sobre o banhado tirou da frente uma estratégia que parecia boa só pela renda. O mesmo caso mostra o limite do mapa: arroz alagado e área úmida se confundem, e por isso o WorldCover nunca é usado sozinho.

## Limitações

- **Só 2020 e 2021:** não serve para ver rotação nem mudança ao longo dos anos.
- **Algoritmos diferentes:** a diferença entre os dois mapas não é mudança real de uso.
- **Acurácia de cerca de 75%:** um em cada quatro pixels pode estar errado.
- **Classes amplas:** "cultivo" não diz qual cultura; campo nativo e pasto ficam na mesma classe.
- **Confusões típicas:** arroz alagado com área úmida; campo com lavoura no Pampa.
- **Tratamento:** usar como contexto e restrição, sempre cruzado com o MapBiomas e o HLS, sem tratar a diferença 2020–2021 como mudança.
