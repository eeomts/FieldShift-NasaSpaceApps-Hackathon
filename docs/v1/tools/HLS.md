# HLS no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o HLS, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o HLS aos outros datasets.

## O que é o HLS

O HLS (Harmonized Landsat Sentinel-2) junta as imagens do Landsat 8/9 e do Sentinel-2 num **único produto em 30 m**, já corrigido para que os dois satélites "falem a mesma língua": mesma grade, mesma correção atmosférica e ajuste das bandas para que o NDVI de um seja comparável ao do outro.

São duas coleções: **HLSL30** (vinda do Landsat) e **HLSS30** (vinda do Sentinel-2). Somadas, dão uma imagem nova do mesmo lugar a cada **2 a 3 dias**.

## Por que usar

**1. Resolve parte da harmonização.** A documentação do projeto prevê juntar dados de resoluções diferentes. Com o HLS, Landsat e Sentinel-2 já chegam harmonizados.

**2. Mais imagens sem nuvem.** Em boa parte do Brasil a estação chuvosa é muito nublada, e na Amazônia e no Mato Grosso isso é ainda mais forte. Com revisita de 2 a 3 dias, as chances de pegar uma imagem limpa sobem bastante.

**3. Calendário real do talhão.** Com NDVI frequente em 30 m, dá para ver quando cada cultura nasceu, quando foi colhida e quanto tempo o solo ficou descoberto, talhão por talhão.

## Como entra no projeto

### Escala: o HLS não entra no Brasil inteiro

O país inteiro em 30 m são centenas de tiles e milhares de imagens por ano, volume inviável para o hackathon. Por isso o HLS entra **só nos pontos ou polígonos escolhidos**: as regiões de demonstração e o talhão que o produtor informa. Para o panorama nacional, o NDVI vem do MODIS (250 m).

### Harmonização

- **Produtos:** HLSL30 e HLSS30 (versão 2.0), em tiles do sistema MGRS, desde 2013 (Landsat) e 2015 (Sentinel-2).
- **Acesso:** LP DAAC, pelo AppEEARS (recomendado, por extrair só a área de interesse), `earthaccess` ou Earthdata Search. Os arquivos são Cloud Optimized GeoTIFF, então dá para ler só o recorte necessário.
- **Processamento:** aplicar a máscara de nuvem (`Fmask`), calcular NDVI e EVI, suavizar a série (por exemplo, com mediana móvel) e resumir por talhão e por mês.

| Banda / camada | O que é | Uso |
| --- | --- | --- |
| Vermelho e infravermelho próximo | Reflectância de superfície | NDVI e EVI |
| Infravermelho de ondas curtas | Reflectância de superfície | Índice de queimada (NBR) e umidade da vegetação |
| `Fmask` | Máscara de nuvem, sombra e água | Descartar pixels ruins |

> Confirmar nas páginas oficiais a versão atual, os nomes das bandas em cada coleção, os limites de área do AppEEARS e se já existe um produto de índices de vegetação pronto.

### Indicadores calculados

- **Calendário de cobertura:** meses com NDVI abaixo de 0,3 (solo descoberto).
- **Picos de NDVI por safra:** um pico por cultura; dois picos no ano indicam soja e safrinha.
- **Datas de emergência e colheita:** subida e queda do NDVI, comparadas com o ZARC.

### Nível de confiança

Depende de quantas **imagens limpas** existem no mês. Na estação chuvosa do Centro-Oeste e do Norte, pode haver uma ou nenhuma por mês. Nessas regiões o **Sentinel-1** (radar, que enxerga através das nuvens) deixa de ser complemento e passa a ser necessário. A rotação detectada também é comparada com o MapBiomas.

## Onde o produtor vê isso

**Etapa 2, calendário de cobertura.** Uma faixa mês a mês mostra quando o talhão fica verde e quando fica descoberto.

**Etapa 3, conferência da rotação.** Depois de informar a rotação, o produtor vê o que o satélite enxergou nos últimos anos e pode corrigir o que estiver diferente.

**Cartão da estratégia.** Exemplo: "Nos últimos 5 anos, seu milho foi plantado depois do fim da janela do ZARC em 2 safras."

## Caso hipotético: HLS junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Carlos planta grãos perto de Sorriso, no Mato Grosso, região de Cerrado na transição para a Amazônia.

- **Rotação informada:** soja (setembro a janeiro) e milho safrinha (janeiro a junho), todo ano.
- **Irrigação:** não tem.
- **Prioridades:** solo e renda altas; água média.
- **Mercado:** soja, milho e milheto para semente.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **HLS** | Dois picos de NDVI em todos os últimos 5 anos: a safrinha é feita sempre. Em 2 anos, porém, o milho emergiu depois de 10 de março, e o pico do milho foi 25% mais baixo. Solo descoberto de julho a setembro em todos os anos. |
| HLS (imagens limpas) | De novembro a fevereiro, de 0 a 2 imagens limpas por mês. |
| Sentinel-1 | Preenche novembro a fevereiro e confirma as datas de colheita da soja: nos 2 anos tardios, ela saiu no início de março. |
| MapBiomas | Classifica o talhão como soja em todos os anos; não separa a safrinha. |
| GPM IMERG | A chuva termina, em média, em meados de abril. |
| GLDAS / SMAP L4 | Nos anos de milho tardio, a zona das raízes já estava abaixo do normal no enchimento de grãos, em maio. |
| ZARC | Janela de menor risco para o milho safrinha termina no fim de fevereiro. |
| NASA POWER | Máximas acima de 35 °C em agosto e setembro, com o solo descoberto. |

### Onde os dados se completam

**A rotação informada está certa, mas o calendário não.** O Sr. Carlos faz safrinha todo ano, como disse. O HLS e o Sentinel-1 mostram, porém, que em 2 anos a soja foi colhida tarde e o milho foi plantado fora da janela do ZARC. O GLDAS e o SMAP L4 explicam por que esses milhos renderam menos: a água acabou antes do enchimento de grãos.

**O HLS sozinho não basta aqui.** Com quase nenhuma imagem limpa de novembro a fevereiro, as datas da soja vêm do Sentinel-1. A confiança do calendário é **alta** porque as duas fontes se completam; sem o radar, seria **baixa**.

**O solo descoberto pega o calor mais forte.** O HLS mostra solo nu de julho a setembro, e o POWER mostra máximas acima de 35 °C nesses meses. Solo exposto ao sol forte perde matéria orgânica e umidade.

### Regras ativadas

- **Plantio da safrinha fora da janela em anos de soja tardia** aumenta o peso de soja precoce e de uma regra condicional para a segunda cultura.
- **Solo descoberto no período mais quente** aumenta o peso das culturas de cobertura.
- **Prioridade alta em solo** aumenta o peso das culturas de raiz profunda, como a braquiária.

### Comparação das estratégias

| Critério | A: atual (soja → milho) | B: soja precoce → milho + braquiária | C: soja → milho até o fim de fevereiro, milheto depois disso |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●●○ |
| Solo | ●○○○○ | ●●●●● | ●●●●○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●●○○ |
| Erosão | ●●○○○ | ●●●●● | ●●●●○ |
| Forragem | ●○○○○ | ●●●●○ | ●●●○○ |
| Renda | ●●●○○ | ●●●●○ | ●●●●○ |

Com os pesos do Sr. Carlos (solo e renda altos), a **estratégia B** empata com a C. A ferramenta mostra as duas como recomendadas e explica a diferença.

### Cartão da estratégia B

> **Resumo:** usar soja de ciclo mais curto para garantir o milho dentro da janela e semear braquiária junto com o milho para cobrir o solo na seca.
>
> **Por que foi sugerida:** em 2 dos últimos 5 anos seu milho foi plantado depois da janela do ZARC e rendeu menos; e todo ano o solo fica descoberto nos meses mais quentes.
>
> **Evidências:** calendário real do talhão (HLS e Sentinel-1, confiança alta); falta de água no enchimento de grãos nos anos tardios (GLDAS e SMAP L4, confiança alta); janela de plantio (ZARC); calor com solo descoberto (POWER e HLS, confiança alta).
>
> **Benefícios:** milho dentro da janela com mais frequência, solo coberto na seca e palhada para o plantio direto da soja.
>
> **Lacunas:** não sabemos o efeito da soja precoce na sua produtividade nem o custo da semente.
>
> **Riscos para revisão local:** escolher com o agrônomo a cultivar de soja e o manejo da braquiária para não competir com o milho, e planejar a dessecação antes da soja seguinte.

## Conclusão

O HLS é o olho da ferramenta no talhão. Ele mostra a rotação que de fato aconteceu, as datas reais e o tempo de solo descoberto. Os dados de chuva e de solo explicam o que o HLS mostra. Nas regiões mais nubladas do país, ele precisa do Sentinel-1 para fechar o calendário, e isso aparece no nível de confiança.

## Limitações

- **Nuvens:** na estação chuvosa do Centro-Oeste e do Norte há poucas imagens limpas; o Sentinel-1 passa a ser necessário.
- **Escala:** inviável para o Brasil inteiro em 30 m; usar só nos pontos escolhidos e o MODIS no panorama nacional.
- **30 m:** bom para talhões médios e grandes; talhões muito pequenos ou estreitos ficam com bordas misturadas.
- **NDVI não identifica a cultura sozinho:** a curva sugere o tipo de ciclo, mas a cultura vem do produtor e do MapBiomas.
- **Tratamento:** máscara de nuvem, série suavizada, contagem de imagens limpas por mês e cruzamento com MapBiomas e Sentinel-1.
