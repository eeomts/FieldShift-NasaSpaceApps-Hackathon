# TOPODATA no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o TOPODATA, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o TOPODATA aos outros datasets.

## O que é o TOPODATA

O TOPODATA é um **banco de dados de relevo do Brasil** feito pelo INPE (Instituto Nacional de Pesquisas Espaciais), com método publicado por Valeriano em 2008. Ele parte do **SRTM** de cerca de 90 m e o refina para cerca de **30 m** (1 segundo de arco) por krigagem, uma interpolação estatística.

Além da altitude, o TOPODATA entrega **variáveis de relevo já calculadas** para todo o país:

- declividade;
- orientação da encosta;
- curvatura vertical (se a encosta é côncava, reta ou convexa de cima para baixo);
- curvatura horizontal (se a água converge ou diverge);
- formas do terreno, que combinam as duas curvaturas;
- relevo sombreado e linhas de drenagem.

## Por que usar

**1. Feito para o Brasil.** O processamento foi pensado para o território nacional e é usado em trabalhos de solos, erosão e planejamento no país. Está em folhas que seguem a articulação cartográfica brasileira.

**2. Curvaturas prontas.** O SRTM e o Copernicus DEM dão a altitude; as curvaturas exigem cálculo extra e cuidado com ruído. O TOPODATA já entrega essas camadas. A curvatura diz **para onde a água vai e onde ela se acumula**, algo que a declividade sozinha não mostra.

**3. Referência nacional para o produtor.** Técnicos de extensão e pesquisadores já conhecem o TOPODATA. Citar a fonte nacional ajuda a confiar no resultado.

## Como entra no projeto

### Harmonização

- **Acesso:** site do TOPODATA no INPE, com download por folha, em GeoTIFF.
- **Processamento:** baixar as folhas da região, recortar a fazenda e reprojetar para UTM (SIRGAS 2000). A declividade pode ser comparada com a calculada do SRTM no `SRTM.md`. As curvaturas e as formas do terreno são resumidas por talhão: fração da área em cada forma.
- **No panorama nacional:** só os resumos por célula da grade comum (declividade média, fração de áreas côncavas), pré-calculados.

| Variável | O que é | Uso |
| --- | --- | --- |
| Altitude | Elevação refinada para 30 m | Comparar com SRTM e Copernicus DEM |
| Declividade | Inclinação do terreno, em % ou graus | Risco de erosão |
| Orientação | Direção da encosta | Insolação e exposição ao vento |
| Curvatura vertical | Côncava, retilínea ou convexa | Onde a água acelera ou desacelera |
| Curvatura horizontal | Convergente, planar ou divergente | Onde a água se junta ou se espalha |
| Formas do terreno | Combinação das duas curvaturas | Zonas de acúmulo e de perda de água e solo |

> Confirmar nas páginas oficiais o endereço atual de download, o tamanho e a nomenclatura das folhas, as unidades de cada variável (declividade em % ou graus, curvatura em graus por metro) e os limiares usados para classificar as curvaturas.

### Indicadores calculados

- **Zonas de acúmulo:** fração do talhão em áreas côncavas e convergentes, onde a água e o solo carregado param.
- **Zonas de perda:** fração em áreas convexas e divergentes, onde a água escorre e leva solo.
- **Declividade por zona:** média e máximo em cada uma.

### Nível de confiança

O TOPODATA **deriva do SRTM**. Se os dois mostram a mesma declividade, isso **não** conta como duas confirmações: é o mesmo dado de 2000, processado de outro jeito. A confirmação independente do relevo vem do **Copernicus DEM**, que é de outra missão. As curvaturas são mais sensíveis a ruído que a declividade; por isso a ferramenta usa formas resumidas por zona, não pixel a pixel, e dá confiança **média** quando só o TOPODATA as mostra.

## Onde o produtor vê isso

**Etapa 2, mapa do relevo.** Além da declividade, uma camada mostra as zonas onde a água se junta e as zonas onde ela escorre.

**Cartão da estratégia.** Exemplo: "A parte de baixo do roçado é côncava e recebe a água da encosta; é onde a umidade dura mais."

**Glossário.** Explica côncavo, convexo, convergente e divergente com desenhos simples.

## Caso hipotético: TOPODATA junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Dona Francisca tem 8 ha perto de Serra Talhada, no sertão de Pernambuco, no Semiárido. Planta em sequeiro e cria cabras.

- **Rotação atual:** milho com feijão em consórcio em toda a área (fevereiro a maio), pousio no resto do ano; um pequeno palmal perto da casa.
- **Irrigação:** não tem; usa cisterna para a casa.
- **Prioridades:** água e forragem altas; renda média.
- **Mercado:** feijão e milho para consumo e venda na feira; cabritos.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **TOPODATA** | A parte de baixo do roçado (cerca de 2,5 ha) é côncava e convergente: recebe a água da encosta. A parte de cima é convexa e divergente, com declividade de 8% a 12%. |
| SRTM | Mesma declividade (não conta como confirmação: o TOPODATA vem dele). |
| Copernicus DEM | Mesma divisão entre parte de cima e baixio, com declividade parecida. Esta sim é confirmação independente. |
| GPM IMERG | Chuva concentrada de fevereiro a abril, com veranicos de 15 dias ou mais em 6 de 10 anos. |
| SMAP L4 | Depois de uma chuva boa, a zona das raízes volta a ficar seca em cerca de 10 dias. |
| HLS | Na parte de baixo, o NDVI do milho fica alto por mais tempo; na parte de cima, cai logo no primeiro veranico. |
| MapBiomas | Mosaico de agricultura e Caatinga no entorno. |

### Onde os dados se completam

**O roçado tem duas partes diferentes.** O TOPODATA mostra que a água da encosta desce e se junta no baixio. O HLS confirma: ali o milho aguenta mais o veranico. A divisão aparece também no Copernicus DEM, que é de outra missão. Confiança **alta** para a divisão; **média** para os limites exatos das zonas.

**O veranico explica o resto.** O IMERG mostra veranicos em 6 de 10 anos, e o SMAP L4 mostra que o solo seca em cerca de 10 dias. Na parte de cima, que perde água, o milho sofre primeiro.

**O SRTM não confirma o TOPODATA.** Os dois concordam porque são o mesmo dado de origem. A ferramenta só conta o Copernicus DEM como segunda fonte.

### Regras ativadas

- **Zona de acúmulo de água confirmada** aumenta o peso de concentrar as culturas mais exigentes nela.
- **Encosta convexa com veranicos frequentes** aumenta o peso de culturas tolerantes à seca e de práticas que seguram a água.
- **Prioridade alta em forragem** aumenta o peso de palma, sorgo e leguminosas forrageiras.

### Comparação das estratégias

| Critério | A: atual (milho + feijão em toda a área) | B: milho + feijão no baixio; sorgo e palma em nível na parte de cima | C: milho + feijão no baixio; palma em nível com faixas de gliricídia na parte de cima |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●○○ | ●●●●○ |
| Solo | ●○○○○ | ●●●○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●●●○ |
| Erosão | ●○○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●●○○○ | ●●●●○ | ●●●●● |
| Renda | ●●●○○ | ●●●○○ | ●●○○○ |

A C rende um pouco menos no começo, porque a gliricídia demora a crescer. Com água e forragem altas, a **estratégia C** fica em primeiro: perde um ponto em renda para a B, mas ganha em água, forragem, solo e nitrogênio. A atual fica em último.

### Cartão da estratégia C

> **Resumo:** uma opção é concentrar o milho com feijão no baixio, onde a água se junta, e usar a parte de cima para palma plantada em nível, com faixas de gliricídia (uma leguminosa forrageira) entre as fileiras.
>
> **Por que foi sugerida:** a parte de baixo do seu roçado recebe a água da encosta e segura o milho por mais tempo; a parte de cima perde água e o milho sofre no primeiro veranico.
>
> **Evidências:** zonas de acúmulo e de perda de água (TOPODATA, confirmado pelo Copernicus DEM, confiança alta); milho mais verde no baixio (HLS, confiança alta); veranicos em 6 de 10 anos (GPM IMERG, confiança alta); solo seco em cerca de 10 dias (SMAP L4, confiança média).
>
> **Benefícios:** milho e feijão onde a água dura mais, forragem para as cabras na seca, nitrogênio e sombra da gliricídia, e menos solo levado da encosta.
>
> **Lacunas:** não sabemos se há mudas de gliricídia e raquetes de palma disponíveis nem quanto da colheita é vendida.
>
> **Riscos para revisão local:** marcar as curvas de nível no terreno com o técnico da extensão rural antes de plantar; confirmar no campo o limite do baixio, que o mapa de 30 m só aproxima; avaliar se vale fazer um barreiro no ponto onde a água se junta.

## Conclusão

O TOPODATA mostra o que a declividade sozinha esconde: onde a água se junta e onde ela foge. Num roçado do Semiárido, isso decide onde vale plantar a cultura mais exigente. O cuidado é não contar o SRTM como confirmação, porque o TOPODATA nasce dele. A confirmação independente vem do Copernicus DEM, e a resposta da lavoura vem do HLS.

## Limitações

- **Deriva do SRTM:** herda a data (2000), as copas das árvores e os erros do SRTM; não é fonte independente.
- **Resolução real menor que 30 m:** a origem é o SRTM de cerca de 90 m, refinado por interpolação.
- **Curvaturas sensíveis a ruído:** principalmente em áreas planas; usar zonas, não pixels.
- **30 m não capta microrrelevo:** curvas de nível, cordões e pequenas grotas ficam de fora.
- **Só Brasil:** não serve para comparar com outros países.
- **Tratamento:** resumir por zona, confirmar o relevo com o Copernicus DEM, conferir a resposta da lavoura no HLS e marcar os limites no campo.
