# GLDAS no Field Shift Brasil

Complemento à *Documentação do Projeto*. Explica por que usar o GLDAS, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o GLDAS aos outros datasets.

## O que é o GLDAS

O GLDAS (Global Land Data Assimilation System) não é uma imagem de satélite. É um **modelo de superfície** que recebe observações de chuva, temperatura e radiação, várias delas de satélite, e calcula o que acontece com a água no solo: quanto fica armazenado em cada camada, quanto evapora e quanto escoa.

## Por que usar

O GLDAS cobre três lacunas que os outros datasets da lista deixam.

**1. Umidade na zona das raízes.** O SMAP mede só os primeiros ~5 cm do solo. O GLDAS (versão Noah) estima a umidade em camadas: 0–10, 10–40, 40–100 e 100–200 cm. Para uma cultura de raiz profunda, um milho safrinha ou uma braquiária, o que importa é o que está abaixo da superfície.

**2. Série longa e sem buracos.** O SMAP começa em 2015 e tem falhas de passagem. O GLDAS 2.1 tem dados mensais contínuos desde 2000, e o GLDAS 2.0 volta até 1948. Com isso dá para calcular o que é "normal" para cada mês em cada lugar e dizer se um ano está seco *em relação ao normal*. Essa é a anomalia de umidade listada no glossário da ferramenta.

**3. Balanço hídrico completo.** Na mesma base vêm evapotranspiração, escoamento superficial e temperatura do solo. Isso permite fechar a conta de chuva que entra menos água que sai, sem misturar fontes incompatíveis.

Ele também conversa com o GRACE: a versão GLDAS 2.2 assimila dados do GRACE, o que ajuda a ligar o contexto de água armazenada nas grandes bacias do país à umidade do solo mês a mês.

Em resumo: o SMAP diz como está a superfície agora; o GLDAS diz como costuma estar a água onde as raízes trabalham e quando ela costuma faltar. Para decidir rotação, que é uma decisão de vários anos, o segundo pesa mais.

## Como entra no projeto

### Harmonização

- **Produto:** mensal, 0,25° (cerca de 28 km).
- **Acesso:** GES DISC da NASA, com login no Earthdata, em NetCDF. Leitura em Python com `xarray`.
- **Processamento:** recortar o Brasil e reamostrar para a grade comum de análise. Na resolução de 0,25°, o país inteiro cabe em cerca de 14 mil células, um volume leve para processar.
- **Variáveis principais:**

| Variável | O que é | Uso |
| --- | --- | --- |
| `SoilMoi0_10cm` | Umidade de 0–10 cm | Comparação com o SMAP |
| `SoilMoi10_40cm` | Umidade de 10–40 cm | Recarga do solo e janela de plantio |
| `SoilMoi40_100cm` | Umidade de 40–100 cm | Água para culturas de raiz profunda |
| `RootMoist` | Umidade na zona das raízes | Indicador principal de déficit hídrico |
| `Evap` | Evapotranspiração | Demanda de água, comparação com ECOSTRESS |
| `Qs` | Escoamento superficial | Risco de erosão, junto com SRTM e GPM |

> Confirmar nas páginas oficiais os nomes exatos das variáveis, a resolução e a latência (o produto mais recente costuma sair com um a dois meses de atraso).

### Indicadores calculados por célula e mês

- **Climatologia:** umidade média de 2000 a 2025.
- **Anomalia:** quanto o mês atual ou um ano específico fica acima ou abaixo do normal.
- **Frequência de déficit:** por exemplo, "em quantos anos de cada 10 a zona das raízes ficou abaixo do percentil 20 em abril".
- **Calendário da água no solo:** mês típico em que o solo seca e mês em que volta a umedecer.

### Nível de confiança

O GLDAS entra na comparação entre fontes junto com SMAP e ERA5. Se os três concordam, a confiança sobe. Como a resolução é regional, o indicador sempre leva o aviso de que é um valor da região, não do talhão.

## Onde o produtor vê isso

O produtor nunca vê a palavra "GLDAS". Ele vê o resultado traduzido em três lugares da ferramenta.

**Etapa 2, calendário de vulnerabilidade.** Uma faixa mensal mostra "água no solo onde as raízes alcançam" em verde, amarelo ou vermelho, comparada com o normal da região. Exemplo: "Na sua região, a água no solo costuma acabar em meados de abril."

**Cartão de cada estratégia, em "Por que foi sugerida" e "Evidências".** O déficit nas raízes justifica culturas tolerantes à seca ou de raiz profunda; o escoamento superficial, somado à declividade do SRTM, reforça a sugestão de cobertura do solo.

**Janela de plantio.** O mês em que a umidade de 10–40 cm se recupera depois da seca ajuda a mostrar quando é seguro plantar, complementando a chuva do GPM. Chover não significa que o solo já tem água suficiente.

Em todos os casos, o cartão traz o aviso: *"estimativa regional de modelo (~28 km); confira com a umidade real da sua lavoura ou com o agrônomo."*

## Caso hipotético: GLDAS junto com os outros dados

> Caso inventado, com números ilustrativos, para mostrar como os dados se juntam do começo ao fim.

### O produtor

O Sr. João tem uma fazenda perto de Patos de Minas (MG), no Alto Paranaíba, região de Cerrado.

- **Rotação atual:** soja (outubro a fevereiro), milho safrinha (fevereiro a junho), pousio até outubro.
- **Irrigação:** não tem.
- **Prioridades:** água e solo altas; renda média.
- **Mercado:** milho, sorgo e venda de palhada ou forragem para um vizinho pecuarista.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| GPM IMERG | A chuva termina, em média, no fim de março. Em dezembro e janeiro há de 2 a 3 eventos por ano acima de 50 mm/dia. |
| NASA POWER | Evapotranspiração de referência alta de abril a setembro. Risco regional de geada baixo. |
| **GLDAS** | A água na zona das raízes cai abaixo do percentil 20 em maio em 6 de cada 10 anos. A camada de 10–40 cm só se recupera em meados de novembro. |
| SMAP | Confirma que a superfície seca a partir de abril (série 2015–2025). |
| ERA5 | Também mostra a recarga tardia do solo em novembro. |
| ECOSTRESS | A evapotranspiração do milho safrinha despenca em maio, sinal de estresse hídrico. |
| Sentinel-2 / Landsat | O NDVI do talhão fica abaixo de 0,3 de julho a outubro: cerca de 4 meses de solo descoberto. |
| SRTM | Parte do talhão tem de 6 a 8% de declividade, e há uma baixada no canto sul. |
| FAO GAEZ | Aptidão boa para sorgo, braquiária e milheto; média para milho safrinha. |
| GRACE | Tendência regional de queda na água armazenada. Entra só como contexto. |

### Onde os dados se completam

**Por que a safrinha sofre.** O GPM mostra que a chuva acaba em março, mas isso sozinho não diz se o milho passa fome. O GLDAS mostra que a água *nas raízes* acaba em maio, justamente no enchimento de grãos. O ECOSTRESS confirma que a planta reduziu a transpiração. Três fontes independentes apontam o mesmo problema: confiança **alta**.

**O risco do solo descoberto.** O NDVI mostra quatro meses sem cobertura, o SRTM mostra declividade e o GPM mostra chuvas fortes no início da safra. Juntos, indicam que a primeira chuva pesada bate em solo nu e inclinado: risco alto de erosão.

**A armadilha do plantio cedo.** O GPM mostra chuvas começando em outubro, mas o GLDAS e o ERA5 dizem que o solo só tem água de verdade em novembro. A ferramenta avisa: "choveu não quer dizer que o solo já recarregou." Aqui entra um aviso de **validação local**, porque um modelo de 28 km não sabe se o talhão retém mais ou menos água que a média da região.

**Onde os dados não alcançam.** O POWER, em escala regional, diz que o risco de geada é baixo, mas o SRTM aponta uma baixada no talhão. A ferramenta marca a geada com confiança **baixa** naquele ponto e pede ao produtor que confirme se já viu geada ali.

### Regras ativadas

- **Déficit recorrente na safrinha** aumenta o peso das culturas tolerantes à seca.
- **Solo descoberto, declividade e chuva extrema** juntos aumentam o peso das culturas de cobertura.
- **Prioridade alta em solo** aumenta o peso das culturas de raiz profunda.

### Comparação das estratégias

| Critério | A: atual (soja → milho → pousio) | B: soja → milho + braquiária | C: soja → sorgo safrinha |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●●○ |
| Solo | ●○○○○ | ●●●●● | ●●●○○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●●○○ |
| Erosão | ●○○○○ | ●●●●● | ●●●○○ |
| Forragem | ●○○○○ | ●●●●○ | ●●●○○ |
| Renda | ●●●●○ | ●●●●○ | ●●●○○ |

Com os pesos do Sr. João (água e solo altos), a **estratégia B** fica em primeiro.

### Cartão da estratégia B

> **Resumo:** manter o milho, mas semear braquiária junto para cobrir o solo depois da colheita.
>
> **Por que foi sugerida:** na sua região, a água onde as raízes alcançam costuma acabar em maio, e seu talhão fica cerca de 4 meses descoberto antes das chuvas fortes de dezembro.
>
> **Evidências:** déficit de umidade nas raízes (GLDAS, SMAP e ERA5 concordam, confiança alta); solo descoberto de julho a outubro (Sentinel-2, confiança alta); declividade de 6–8% (SRTM, confiança alta).
>
> **Benefícios:** a palhada protege o solo na seca, as raízes da braquiária abrem caminho para a água infiltrar, e sobra forragem para o vizinho.
>
> **Lacunas:** não sabemos a textura do solo nem a matéria orgânica. Se houver análise de solo, informe aqui.
>
> **Riscos para revisão local:** a braquiária pode competir com o milho se semeada na hora errada. É preciso planejar a dessecação antes da soja e confirmar com o agrônomo a dose e a época de semeadura.

## Conclusão

O GLDAS não decide nada sozinho. Ele explica o *porquê* por trás do que o NDVI e a chuva mostram: os satélites veem a superfície, e o GLDAS estima o que acontece embaixo dela. O cruzamento com SMAP e ERA5 é o que transforma uma estimativa de modelo em evidência com nível de confiança.

Esse roteiro pode virar a demonstração da apresentação. Rodando o mesmo caso em outra região, como o Semiárido nordestino ou o Sul do país, os mesmos dados levariam a uma recomendação diferente, que é o diferencial descrito na documentação do projeto.

## Limitações

- **Resolução de ~28 km:** valor regional, não do talhão.
- **É modelo, não medição:** os parâmetros de solo são genéricos e podem não representar bem a variedade de solos do Brasil.
- **Latência:** os meses mais recentes podem demorar a sair.
- **Tratamento:** sempre cruzar com SMAP e ERA5, mostrar o nível de confiança e indicar validação local.
