# MODIS Land Cover (MCD12Q1) no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o MODIS Land Cover, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o MODIS Land Cover aos outros datasets.

## O que é o MODIS Land Cover

O **MCD12Q1** é um mapa anual de **cobertura do solo** do mundo inteiro, feito pela NASA a partir dos sensores MODIS dos satélites Terra e Aqua. Cada pixel de **500 m** recebe uma classe: floresta, arbustos, savana, campo, área úmida, agricultura, mosaico de agricultura com vegetação natural, área urbana, água e outras.

O produto traz vários esquemas de classes; o mais usado é o **IGBP** (camada `LC_Type1`). A série anual começa em 2001.

## Por que usar

**1. Máscara para os indicadores do país.** Na etapa 1, a ferramenta calcula indicadores para o Brasil todo. Sem separar o que é lavoura, o NDVI regional mistura floresta, cerrado, caatinga, pasto e cultivo, e o calendário de solo descoberto perde o sentido. O MCD12Q1 diz quais pixels olhar.

**2. Padrão global e consistente.** Mesma metodologia em todos os biomas e em todos os anos. Bom para comparar Cerrado, Pampa, Caatinga e Mata Atlântica sem mudar de fonte.

**3. Mudança ao longo do tempo.** Mostra onde floresta, cerrado ou pasto viraram lavoura desde 2001, contexto importante na fronteira agrícola.

Uma ressalva honesta: para o Brasil, o **MapBiomas** é mais detalhado (30 m e culturas específicas). O MCD12Q1 entra como camada simples para a escala nacional e como fonte independente para conferir o MapBiomas.

## Como entra no projeto

### Harmonização

- **Produto:** MCD12Q1, versão 6.1, 500 m, anual.
- **Acesso:** LP DAAC, pelo Earthdata Search, `earthaccess` ou AppEEARS.
- **Processamento:** recortar o Brasil (cerca de 25 tiles MODIS), reprojetar da projeção sinusoidal e calcular, para cada célula da grade comum, a **fração de área agrícola**. Separar também por bioma, usando o mapa de biomas do IBGE.

| Classe (IGBP, `LC_Type1`) | O que é | Onde aparece no Brasil | Uso |
| --- | --- | --- | --- |
| 2: Evergreen Broadleaf Forests | Floresta densa sempre verde | Amazônia e Mata Atlântica | Excluída; base para ver expansão |
| 6 e 7: Shrublands | Vegetação arbustiva | Caatinga | Excluídas da máscara agrícola |
| 8 e 9: Savanas | Áreas abertas com árvores | Cerrado | Excluídas da máscara agrícola |
| 10: Grasslands | Campos e muitas pastagens | Pampa e pastagens em geral | Separadas para comparação |
| 11: Permanent Wetlands | Áreas úmidas | Pantanal | Excluídas |
| 12: Croplands | Agricultura dominante | Cerrado, Sul, Sudeste | Pixels de lavoura |
| 14: Cropland/Natural Vegetation Mosaics | Mistura de lavoura e vegetação | Mata Atlântica, Caatinga, pequenas propriedades | Pixels mistos, usados com cuidado |

> Confirmar nas páginas oficiais a versão atual, o último ano disponível e a definição de cada classe.

### Indicadores calculados

- **Fração agrícola por célula:** proporção de pixels de lavoura.
- **Calendário de solo descoberto por bioma:** NDVI do MODIS calculado **só sobre pixels agrícolas**.
- **Expansão agrícola:** mudança da fração agrícola entre 2001 e o ano mais recente.

### Nível de confiança

Comparar a máscara com o MapBiomas. Onde os dois concordam que é lavoura, confiança alta. Onde o MODIS diz "mosaico" ou discorda do MapBiomas, confiança baixa, e o indicador regional leva aviso. Na Caatinga e na Mata Atlântica, onde as lavouras são pequenas e fragmentadas, a confiança tende a ser menor.

## Onde o produtor vê isso

O MCD12Q1 aparece pouco para o produtor; ele trabalha "por trás" da etapa 1.

**Etapa 1, panorama do país.** O mapa do Brasil mostra onde há agricultura e permite comparar biomas e regiões.

**"Regiões parecidas com a sua".** Ao escolher um ponto, a ferramenta mostra o calendário típico das lavouras do bioma e da região, calculado só sobre áreas agrícolas.

**Contexto de mudança.** Uma camada opcional mostra onde a agricultura cresceu desde 2001.

## Caso hipotético: MODIS Land Cover junto com os outros dados

> Caso inventado, com números ilustrativos.

### A situação

A equipe prepara a etapa 1 da ferramenta: o panorama do Brasil por bioma. Depois, a Sra. Ana, que planta soja e trigo perto de Cascavel, no Paraná, abre a ferramenta e escolhe sua propriedade.

### O que cada dataset diz sobre o país

| Dataset | O que encontra (hipotético) |
| --- | --- |
| MODIS NDVI (sem máscara) | Calendários regionais quase planos no Cerrado e na Amazônia: a vegetação natural esconde o sinal das lavouras. |
| **MCD12Q1** | Agricultura concentrada no Cerrado, no Sul e em partes do Sudeste. Na Caatinga e na Mata Atlântica, a maior parte das lavouras aparece como mosaico. Na borda sul da Amazônia, a fração agrícola cresceu de 5% para 20% desde 2001. |
| MODIS NDVI (com máscara) | **Cerrado:** dois picos (soja e safrinha) e solo descoberto de julho a setembro. **Sul:** soja no verão e trigo ou aveia no inverno, com pouco solo descoberto. **Caatinga:** um pico curto nas águas e solo descoberto quase o resto do ano. |
| MapBiomas | Concorda com o MCD12Q1 em cerca de 85% da área agrícola do Cerrado e do Sul, mas bem menos na Caatinga e na Mata Atlântica, onde separa melhor as lavouras pequenas. |
| IBGE PAM | Confirma as culturas principais por município: soja e milho no Cerrado, soja e trigo no Sul, feijão e milho no Semiárido. |
| FIRMS | Focos de fogo concentrados nas áreas de savana e na borda da Amazônia, de julho a outubro. |

### Onde os dados se completam

**Sem máscara, o sinal some.** No Cerrado e na Amazônia, a vegetação natural fica verde boa parte do ano e esconde a entressafra das lavouras. Com a máscara do MCD12Q1, a janela de solo descoberto aparece.

**Cada bioma tem um calendário.** Com a máscara, o painel mostra o contraste que a ferramenta quer provar: solo descoberto longo no Cerrado e na Caatinga, quase nenhum no Sul, onde o inverno tem culturas de cobertura ou trigo.

**O MapBiomas refina onde o MODIS falha.** Na Caatinga e na Mata Atlântica, o MODIS vê "mosaico"; o MapBiomas separa as lavouras pequenas. Nesses biomas o indicador regional leva confiança **baixa** e a ferramenta usa o MapBiomas como fonte principal.

### O que muda para a Sra. Ana

O MCD12Q1 não gera a recomendação do talhão, mas define o **ponto de partida regional** com que a fazenda é comparada:

> **Panorama da sua região:** as lavouras do oeste do Paraná costumam ficar cobertas quase o ano todo, com soja no verão e trigo, aveia ou milho safrinha no inverno. A janela mais curta de solo descoberto aparece entre a colheita do trigo e o plantio da soja.
>
> **De onde vem:** áreas agrícolas (MODIS Land Cover, conferido com MapBiomas, confiança alta); calendário de vegetação (MODIS NDVI, confiança alta); culturas da região (IBGE PAM).
>
> **O que isso significa para você:** se seu talhão segue o padrão da região, o desafio não é cobrir o solo, mas diversificar a rotação e lidar com o risco de geada no inverno. A comparação com seu talhão vem na etapa 4.

Na etapa 4, as estratégias da Sra. Ana são geradas com HLS, MERRA-2, GLDAS e os demais dados do talhão, como nos outros casos.

## Conclusão

O MODIS Land Cover é uma peça de bastidor: ele garante que os indicadores do país falem de lavoura, e não de uma mistura de floresta, cerrado, caatinga e pasto. Sem ele, o panorama nacional esconde justamente as diferenças entre biomas que a ferramenta quer mostrar.

## Limitações

- **500 m:** pixels mistos são comuns onde as lavouras são pequenas, como na Mata Atlântica e na Caatinga.
- **Não separa culturas:** "agricultura" inclui soja, milho, cana e outras; para isso, usar o MapBiomas e o IBGE PAM.
- **Pastagem e campo confundidos:** a classe de campo mistura pasto plantado e vegetação nativa, no Cerrado e no Pampa.
- **Atraso:** o ano mais recente pode demorar a ser publicado.
- **Tratamento:** usar como máscara e como fonte independente para conferir o MapBiomas; marcar pixels mistos com confiança baixa.
