# MapBiomas no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o MapBiomas, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o MapBiomas aos outros datasets.

## O que é o MapBiomas

O MapBiomas é uma rede de universidades, ONGs e empresas de tecnologia que produz **mapas anuais de cobertura e uso da terra** do Brasil inteiro, em **30 m**, a partir de imagens Landsat. Cada pixel recebe uma classe por ano: floresta, savana, pastagem, soja, cana, arroz, café, área urbana e outras.

A **Coleção 11**, lançada em agosto de 2026, cobre **1985 a 2025**. São mais de 40 anos de história de cada pedaço do país.

A rede tem outros produtos úteis para o projeto:

- **Agricultura de segunda safra (beta):** primeira versão lançada em dezembro de 2025. Tenta separar a safrinha, que os mapas anuais não mostram.
- **MapBiomas Fogo:** cicatrizes de queimada anuais e mensais desde 1985, também a partir do Landsat, com frequência de fogo e ano da última queimada. A Coleção 5 vai até 2025.

## Por que usar

**1. É o substituto brasileiro do CDL.** Nos EUA, o desafio usa o Cropland Data Layer para saber o que foi plantado em cada lugar. Aqui, o MapBiomas cumpre esse papel (D-003).

**2. Mostra a história do talhão.** Dá para saber se a área era floresta, pasto ou lavoura em cada ano. Uma lavoura aberta sobre pasto degradado há 10 anos tem solo diferente de uma lavoura com 30 anos de plantio direto.

**3. Mostra o entorno.** Pastagem, reserva de vegetação nativa e rios perto do talhão mudam o risco de fogo, de pragas e de erosão.

**4. Cobre todos os biomas com o mesmo método.** Isso ajuda a regra da D-008: os indicadores precisam funcionar no país inteiro e ser separados por bioma.

**5. O Fogo completa o FIRMS.** O FIRMS mostra pontos de calor. O MapBiomas Fogo mostra a **área** que de fato queimou.

## Como entra no projeto

### Harmonização

- **Acesso:** plataforma web do MapBiomas (consulta e download por município ou polígono), mapas anuais em GeoTIFF para download, assets públicos no Google Earth Engine e planilhas de estatísticas de área por classe e município.
- **Processamento:** no panorama nacional, calcular a área de cada classe por célula da grade comum. Nos pontos escolhidos, extrair a sequência de classes de cada ano dentro do talhão e num raio de 5 km. Para o Fogo, somar os anos com queimada e guardar o último ano.

| Camada | O que é | Uso |
| --- | --- | --- |
| Cobertura e uso anual (uma banda por ano) | Classe do pixel naquele ano | Histórico do talhão e do entorno |
| Transições | Mudança de classe entre dois anos | Quando a área virou lavoura |
| Agricultura de segunda safra (beta) | Pixel com cultivo depois da safra de verão | Conferir se a safrinha é feita |
| Fogo anual e mensal | Cicatriz de queimada no ano ou no mês | Área queimada e calendário de fogo |
| Fogo: frequência e última queimada | Quantas vezes e quando queimou | Recorrência de fogo |

> Confirmar nas páginas oficiais os caminhos dos assets da Coleção 11 no Earth Engine, os códigos de cada classe na legenda da coleção (ex.: soja, pastagem, mosaico de usos), a acurácia por bioma e classe, a cobertura do mapa de segunda safra e a coleção mais recente do MapBiomas Fogo.

### Indicadores calculados

- **Idade da lavoura:** anos seguidos como lavoura temporária no talhão.
- **Uso anterior:** classe antes da lavoura (pasto, savana, floresta).
- **Frequência de safrinha:** anos com segunda safra detectada.
- **Paisagem do entorno:** fração de pastagem, vegetação nativa e lavoura num raio de 5 km.
- **Histórico de fogo:** anos com queimada no talhão e no entorno, e anos desde a última.

### Nível de confiança

A acurácia muda por bioma e por classe. Soja é bem mapeada; outras lavouras temporárias e mosaicos de uso têm mais erro. O MapBiomas vem do **Landsat**, como o HLS, então os dois **não contam como confirmações independentes**. O Sentinel-1 (radar), o IBGE PAM e o que o produtor informa são fontes independentes. Quando concordam, a confiança sobe.

## Onde o produtor vê isso

**Etapa 3, conferência da rotação.** A ferramenta mostra uma linha do tempo do talhão desde 1985: "pastagem até 2014, soja desde 2015". O produtor confirma ou corrige.

**Etapa 2, contexto do entorno.** Um resumo da paisagem: quanto há de pasto, mata e lavoura perto da propriedade.

**Cartão da estratégia.** O uso anterior e o fogo entram em "Por que foi sugerida" e em "Riscos para revisão local".

**Glossário.** Explica que o mapa é feito por satélite, que cada pixel tem 30 m e que pode haver erro de classe.

## Caso hipotético: MapBiomas junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Raimundo planta grãos perto de Paragominas, no leste do Pará, na borda da Amazônia. A chuva se concentra de dezembro a maio.

- **Rotação atual:** soja (dezembro a abril), milho safrinha (abril a agosto) em alguns anos, pousio até dezembro.
- **Irrigação:** não tem.
- **Prioridades:** solo e renda altas; água média.
- **Mercado:** soja, milho e venda de pasto para gado de vizinhos.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **MapBiomas (cobertura)** | O talhão era pastagem de 1996 a 2014 e é soja desde 2015. No raio de 5 km: 45% pastagem, 30% floresta, 25% lavoura. |
| **MapBiomas (segunda safra)** | Safrinha detectada em 4 dos últimos 7 anos. |
| **MapBiomas Fogo** | O talhão queimou 3 vezes quando era pasto e nenhuma depois de 2015. A pastagem vizinha queimou em 7 anos desde 2005, sempre entre setembro e novembro. |
| HLS + Sentinel-1 | Confirmam dois ciclos nos anos de safrinha e solo descoberto de setembro a novembro. |
| FIRMS | Focos no entorno nos mesmos meses das cicatrizes. |
| GPM IMERG | A chuva cai muito a partir de junho. |
| GLDAS / SMAP L4 | Zona das raízes seca a partir de julho. |
| SRTM | Relevo plano a suave, 2–4% de declividade. |
| IBGE PAM | Produtividade municipal da soja estável nos últimos 8 anos. |

### Onde os dados se completam

**A safrinha não é sempre feita.** O produtor disse que faz milho "quase todo ano". O MapBiomas viu safrinha em 4 de 7 anos. O Sentinel-1, que é independente do Landsat, confirma. Nos outros anos, o solo ficou descoberto de maio a dezembro.

**O solo tem passado de pasto.** Vinte anos de pastagem, com queimadas, costumam deixar o solo compactado e com pouca matéria orgânica. O MapBiomas não mede o solo, mas o histórico justifica dar mais peso a raízes que reestruturam o solo.

**O fogo vem de fora.** O MapBiomas Fogo mostra que o talhão parou de queimar quando virou lavoura, mas a pastagem vizinha queima quase todo ano. O FIRMS confirma o calendário. Palhada seca na divisa vira risco.

### Regras ativadas

- **Lavoura aberta sobre pasto antigo** aumenta o peso das culturas de raiz profunda.
- **Solo descoberto longo na seca** aumenta o peso das culturas de cobertura.
- **Fogo recorrente no entorno** adiciona um risco às estratégias com palhada seca.
- **Mercado de pasto local** aumenta o valor da forragem.

### Comparação das estratégias

| Critério | A: atual (soja → milho em alguns anos → pousio) | B: soja → milho + braquiária, com pastejo na seca | C: soja → milheto de cobertura |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●○○○○ | ●●●●● | ●●●●○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●○○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●○○○○ | ●●●●● | ●●○○○ |
| Renda | ●●●○○ | ●●●●○ | ●●○○○ |

Com os pesos do Sr. Raimundo (solo e renda altos, água média), a **estratégia B** fica em primeiro: ela tem a melhor nota em solo e em renda. A C protege o solo quase tanto, mas rende menos.

### Cartão da estratégia B

> **Resumo:** uma opção é manter soja e milho e semear braquiária junto com o milho. Depois da colheita, a braquiária cobre o solo e pode ser pastejada na seca.
>
> **Por que foi sugerida:** seu talhão foi pasto por quase 20 anos antes da soja, a safrinha ficou de fora em 3 dos últimos 7 anos e, nesses anos, o solo ficou descoberto até dezembro.
>
> **Evidências:** histórico de uso (MapBiomas, confiança alta); frequência de safrinha (MapBiomas e Sentinel-1, confiança alta); solo seco a partir de julho (GLDAS e SMAP L4, confiança alta); fogo no entorno (MapBiomas Fogo e FIRMS, confiança alta).
>
> **Benefícios:** raízes da braquiária ajudam a recuperar a estrutura do solo, a palhada protege na seca e o pasto gera renda com os vizinhos.
>
> **Lacunas:** não sabemos a matéria orgânica nem a compactação do solo. Uma análise de solo ajudaria.
>
> **Riscos para revisão local:** palhada seca na divisa com a pastagem que queima; manter aceiros e combinar com os vizinhos. Ajustar a lotação para não degradar a cobertura. Confirmar com o agrônomo a época de semeadura da braquiária e a dessecação antes da soja.

## Conclusão

O MapBiomas dá à ferramenta a **memória** do lugar. Os dados de clima dizem como o ano costuma ser; o MapBiomas diz o que foi feito ali e o que existe em volta. Junto com o MapBiomas Fogo, ele mostra se o risco de queimada vem do talhão ou do vizinho. Em outra região, como uma lavoura antiga do Sul, o mesmo histórico levaria a outra leitura do solo.

## Limitações

- **Anual:** um pixel recebe uma classe por ano; a safrinha só aparece no mapa de segunda safra, ainda em versão beta.
- **Classes agrupadas:** várias culturas caem em "outras lavouras temporárias".
- **30 m:** talhões pequenos ou estreitos ficam com bordas misturadas.
- **Erro de classe:** a acurácia varia por bioma e por classe.
- **Não mede o solo:** o histórico sugere a condição, mas não substitui análise.
- **Mesma origem do HLS:** os dois vêm do Landsat e não se confirmam entre si.
- **Uso legal:** a ferramenta mostra o histórico, mas não faz verificação ambiental nem legal da propriedade.
- **Tratamento:** mostrar a linha do tempo para o produtor corrigir, cruzar com Sentinel-1 e IBGE PAM, e indicar a acurácia da classe.
