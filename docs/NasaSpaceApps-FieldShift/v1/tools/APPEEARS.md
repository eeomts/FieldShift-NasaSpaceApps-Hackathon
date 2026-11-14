# AppEEARS no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o AppEEARS, como ele entra na ferramenta e o que muda para o produtor, com um caso hipotético que mostra a equipe montando os dados de um talhão na borda da Amazônia.

## O que é

O AppEEARS (Application for Extracting and Exploring Analysis Ready Samples) é um serviço do LP DAAC, centro de dados da NASA e do USGS. Ele **extrai só o pedaço que interessa** de vários produtos de satélite: em vez de baixar imagens inteiras, a equipe envia pontos ou um polígono e um período, e recebe de volta a série de valores já recortada.

Há dois tipos de pedido:

- **Ponto:** uma lista de coordenadas. A saída é uma tabela CSV com a série de cada ponto e a qualidade de cada valor.
- **Área:** um polígono. A saída são rasters recortados, em GeoTIFF ou NetCDF4.

Funciona pelo navegador e por uma API. Usa o mesmo Earthdata Login do resto do projeto.

## Por que usar

**1. Feito para o tamanho de um talhão.** O projeto precisa de séries por talhão e por região de demonstração, não de cenas inteiras. O AppEEARS entrega exatamente isso, o que economiza download e processamento.

**2. Vários produtos no mesmo pedido.** MODIS (NDVI do MOD13Q1), HLS e SMAP L4 podem sair juntos, para os mesmos pontos e datas. A comparação entre fontes, base do nível de confiança, fica mais simples.

**3. Qualidade já traduzida.** Junto com os valores vêm as camadas de qualidade (nuvem, sombra, confiabilidade do pixel) e tabelas que explicam cada código. Filtrar valores ruins vira uma regra simples.

**4. Pedidos repetíveis.** Um pedido pode ser salvo como JSON e reenviado pela API. Trocar o talhão ou o ano é só trocar coordenadas e datas.

## Como entra no projeto

### Acesso

- **Navegador:** `appeears.earthdatacloud.nasa.gov`, com Earthdata Login.
- **API:** base `https://appeears.earthdatacloud.nasa.gov/api/`. O resumo do fluxo (login com token, campos do pedido, formato de datas) está na tabela abaixo.

| Endpoint / campo | O que é | Uso no projeto |
| --- | --- | --- |
| `POST /login` | Gera o token de acesso | Autenticar scripts |
| `GET /product` e `GET /product/{id}` | Lista produtos e camadas | Achar o nome exato da camada (ex.: NDVI do `MOD13Q1.061`) |
| `POST /task` | Envia o pedido | Ponto (`task_type: "point"`) ou área (`"area"`) |
| `params.dates[]` | Período, em `MM-DD-AAAA`, com opção de recorrência anual | Mesma estação em vários anos |
| `params.coordinates[]` | Pontos com `id` e `category` | Um ponto por talhão, com a região na categoria |
| `params.geo` | Polígono em GeoJSON | Talhão desenhado pelo produtor ou região de demonstração |
| `GET /task/{id}` | Situação do pedido | Esperar até ficar pronto |
| `GET /bundle/{id}` | Arquivos prontos | Baixar CSV, GeoTIFF ou NetCDF4 |

> Confirmar nas páginas oficiais os limites de número de pontos e de tamanho de área por pedido, por quanto tempo os resultados ficam guardados, a lista atual de produtos e versões (por exemplo, HLS 2.0 e a versão vigente do SMAP L4) e se o Sentinel-1 continua fora do catálogo.

### O que produz para o projeto

- **Séries por talhão:** NDVI (MODIS 250 m e HLS 30 m), umidade do solo (SMAP L4), na mesma tabela.
- **Rasters das regiões de demonstração:** recortes do HLS para mapas de solo descoberto e de vigor.
- **Insumo para o calendário de cobertura:** a série de NDVI por talhão vira os meses de solo descoberto, os picos por safra e as datas de emergência e colheita.

### Como ajuda a medir a confiança

A saída de ponto traz, para cada data, a qualidade do pixel. A ferramenta conta quantas **observações boas** sobraram por mês e por fonte. Se o mês tem várias observações limpas e as fontes concordam, a confiança é alta. Se o mês só tem valores marcados como nuvem, o indicador fica sem dado ou com confiança baixa.

### Escala: o AppEEARS não é o caminho para o Brasil inteiro

O panorama nacional é pré-calculado numa grade comum (D-008). Para isso, rasters grandes vêm por `earthaccess`. O AppEEARS fica com os **pontos e polígonos**: o talhão do produtor e as regiões de demonstração.

## Onde o produtor vê isso

O produtor **não vê** o AppEEARS. O efeito aparece nos resultados:

- **Etapa 2, calendário de cobertura e de água no solo:** as faixas mês a mês do talhão vêm das séries extraídas aqui.
- **Etapa 3, conferência da rotação:** o que o satélite viu nos últimos anos, para o produtor confirmar ou corrigir.
- **Evidências do cartão:** "solo descoberto de julho a setembro (HLS e MODIS, confiança alta)".

## Caso hipotético: AppEEARS no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como a ferramenta ajuda a montar os dados de um talhão.

### O produtor

O Sr. Adão planta grãos perto de **Paragominas (PA)**, na borda da Amazônia, numa área de pastagem antiga convertida para lavoura.

- **Rotação informada:** soja (dezembro a abril) e milho safrinha (abril a agosto) em parte da área; o resto fica em pousio.
- **Irrigação:** não tem.
- **Prioridades:** solo alto; renda e água médias.
- **Mercado:** soja, milho e venda de forragem para pecuaristas vizinhos.

### O que a equipe faz no AppEEARS

1. **Pedido de ponto** com três pontos no talhão e um ponto de controle na mata vizinha, de 2016 a 2025, com MOD13Q1 (NDVI), HLSL30 e HLSS30 e SMAP L4.
2. **Pedido de área** com o polígono do talhão, só HLS, para gerar o mapa de solo descoberto.
3. **Filtro de qualidade:** mantém só valores sem nuvem e sem sombra, segundo as tabelas de qualidade que vêm junto.
4. **Contagem de observações boas** por mês e por fonte, salva ao lado de cada indicador.

### O que cada dataset mostra (extraído pelo AppEEARS)

| Dataset | O que encontra (hipotético) |
| --- | --- |
| HLS | De janeiro a abril, de 0 a 1 imagem limpa por mês. De junho a outubro, várias por mês, com NDVI abaixo de 0,3 na parte em pousio. |
| MODIS (MOD13Q1) | Composições de 16 dias preenchem melhor a estação chuvosa, mas em 250 m o pixel mistura talhão e mata. |
| SMAP L4 | Zona das raízes seca a partir de julho, com recuperação só em dezembro. |
| Sentinel-1 (fora do AppEEARS) | Opcional (`extras/`), acionado aqui porque a região é muito nublada: fecha a estação chuvosa. Vem de outra fonte. |
| GPM IMERG (fora do AppEEARS) | Estação seca bem marcada de julho a novembro. |

### Onde o AppEEARS fez diferença

**A contagem de imagens mostrou onde o HLS falha.** Com 0 ou 1 imagem limpa por mês na safra da soja, as datas de plantio e colheita não podem vir só do HLS. A equipe marca essas datas com confiança **baixa** até juntar o Sentinel-1; com o radar, ela sobe para **média**.

**O ponto de controle ajudou a ler o MODIS.** O NDVI do MODIS no talhão ficou mais alto que o do HLS na seca. O ponto na mata mostrou por quê: o pixel de 250 m inclui parte da mata vizinha. Para este talhão, o calendário de cobertura usa o HLS, e o MODIS só entra na comparação regional.

**O pousio é longo e seco.** HLS e SMAP L4 apontam a mesma coisa: a parte sem safrinha fica descoberta e seca de julho a novembro. Essa evidência reforça, no comparador, as estratégias com cobertura do solo, como milho com braquiária ou milheto depois da soja.

### O que vai para o cartão

> **Evidências:** solo descoberto de julho a novembro na parte em pousio (HLS, confiança alta); zona das raízes seca na mesma época (SMAP L4, confiança alta); datas da soja com poucas imagens limpas (HLS e Sentinel-1, confiança média).
>
> **Lacunas:** o pixel do MODIS mistura talhão e mata; por isso, o calendário do talhão usa o HLS.

## Conclusão

O AppEEARS é a forma mais direta de levar os produtos da NASA até o talhão. Ele entrega séries prontas, com a qualidade de cada valor, para vários datasets ao mesmo tempo. Isso alimenta o calendário de cobertura e a comparação entre fontes. Para o Brasil inteiro, ele cede lugar ao `earthaccess`; para o talhão, é a ferramenta principal.

## Limitações

- **Limites por pedido:** número de pontos e tamanho de área são limitados; regiões grandes precisam ser divididas ou ir por outro caminho.
- **Fila de processamento:** pedidos grandes podem levar horas; não serve para resposta em tempo real ao produtor.
- **Catálogo limitado:** não tem Sentinel-1 nem dados de outras agências; IMERG e GLDAS vêm por outras ferramentas.
- **Formato de data americano:** `MM-DD-AAAA`, fonte comum de erro.
- **Resultados expiram:** os arquivos ficam disponíveis por um tempo limitado e precisam ser guardados pela equipe.
- **Tratamento:** usar o AppEEARS para pontos e polígonos, filtrar pela qualidade, contar observações boas por mês e completar com Sentinel-1 nas regiões nubladas.
