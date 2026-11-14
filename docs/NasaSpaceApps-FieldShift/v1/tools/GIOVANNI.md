# Giovanni no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Giovanni, como ele entra na ferramenta e o que muda para o produtor, com um caso hipotético que mostra a equipe testando uma hipótese para uma região do Sul.

## O que é

O Giovanni é uma ferramenta online do GES DISC, centro de dados da NASA, para **analisar dados sem baixar arquivos**. A equipe escolhe a variável, a área e o período, e o Giovanni devolve um mapa, uma série temporal ou outro gráfico, calculado no servidor.

Ele cobre principalmente dados de clima e de água: chuva do **GPM IMERG**, umidade do solo e evapotranspiração do **GLDAS**, e variáveis do **MERRA-2**. São justamente os produtos que dão o contexto climático de cada região do Brasil.

Usa o Earthdata Login.

## Por que usar

**1. Testa uma hipótese em minutos.** Antes de escrever código, a equipe pode perguntar "os verões de La Niña foram mais secos no planalto gaúcho?" e ver a resposta num gráfico. Se a hipótese não se sustenta, ninguém perde tempo pré-calculando um indicador.

**2. Médias e anomalias prontas.** O Giovanni calcula média no tempo, média na área, séries sazonais e diferenças entre períodos. São as mesmas contas que viram a climatologia e as anomalias da ferramenta.

**3. Compara duas fontes lado a lado.** Dá para pôr a chuva do IMERG e a do MERRA-2, ou a umidade do GLDAS em duas camadas, no mesmo gráfico. É uma conferência rápida da concordância entre fontes.

**4. Gera figuras para a apresentação.** Mapas e séries saem como imagem e também como arquivo de dados, o que ajuda a mostrar ao júri de onde vem cada número.

## Como entra no projeto

### Acesso

- **Endereço:** `giovanni.gsfc.nasa.gov`, no navegador, com Earthdata Login.
- **Fluxo:** escolher o tipo de gráfico, desenhar a área (ou digitar o retângulo), definir as datas, buscar a variável e mandar gerar.

| Tipo de gráfico | O que é | Uso no projeto |
| --- | --- | --- |
| Mapa de média no tempo | Média da variável em cada pixel no período | Ver o padrão espacial de chuva ou umidade num bioma |
| Série com média na área | Um valor por data, média do retângulo | Conferir sazonalidade e anos extremos de uma região |
| Série sazonal | Mesmo mês ou estação, ano a ano | Comparar o verão de vários anos |
| Diferença entre períodos | Um período menos outro | Anomalia de um ano em relação ao normal |
| Dispersão e correlação | Uma variável contra outra | Concordância entre IMERG e MERRA-2, ou entre camadas do GLDAS |
| Download do resultado | Imagem e dados (por exemplo, NetCDF ou CSV) | Guardar a evidência e a figura |

> Confirmar nas páginas oficiais a lista atual de tipos de gráfico, os formatos de download, as versões disponíveis de IMERG, GLDAS e MERRA-2 e os limites de tamanho de pedido. Em 2026 o GES DISC moveu parte dos serviços para o Earthdata Cloud, e algumas variáveis ficaram fora do ar por um tempo; conferir os avisos de manutenção.

### O que produz para o projeto

- **Hipóteses confirmadas ou descartadas** para cada região, antes de virar regra.
- **Valores de referência** para validar os indicadores pré-calculados: se o script da equipe e o Giovanni dão médias muito diferentes para a mesma área, há um erro no código.
- **Figuras** de mapas e séries para a apresentação e para o glossário.

### Como ajuda a medir a confiança

O Giovanni não entra no cálculo automático. Ele serve de **teste de concordância** feito pela equipe: quando IMERG, GLDAS e MERRA-2 mostram o mesmo padrão no Giovanni, a regra correspondente pode usar confiança alta. Quando discordam, a regra leva confiança média ou baixa e o motivo vai para o registro.

## Onde o produtor vê isso

O produtor **não usa** o Giovanni. O efeito chega de forma indireta:

- **Regras mais sólidas.** As regras que ativam culturas tolerantes à seca ou de cobertura foram conferidas antes com dados reais da região.
- **Gráficos de contexto.** Uma série de chuva ou de umidade gerada aqui pode aparecer no glossário ou na tela de "por que esta região é assim".
- **Avisos de incerteza.** Onde as fontes discordaram, o cartão mostra confiança menor.

## Caso hipotético: Giovanni no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como a ferramenta ajuda a testar uma hipótese regional.

### A região

A equipe escolhe o planalto do **norte do Rio Grande do Sul, perto de Passo Fundo**, como região de demonstração do Sul. O produtor fictício é o Sr. Ivo.

- **Rotação atual:** soja no verão (novembro a março), trigo no inverno (junho a outubro).
- **Irrigação:** não tem.
- **Prioridades:** renda e solo altas; água média.
- **Mercado:** soja, trigo, milho e aveia.

### A hipótese

Alguém da equipe lembra que os verões de La Niña costumam ser secos no Sul. Se isso aparecer nos dados, a ferramenta pode mostrar ao produtor o risco de déficit hídrico na soja e o valor de diversificar o verão com milho em parte da área.

### O que a equipe faz no Giovanni

1. **Série com média na área** da chuva diária do GPM IMERG, acumulada por mês, de 2001 a 2025, num retângulo de cerca de 1° em volta de Passo Fundo.
2. **Série sazonal** de dezembro a fevereiro, ano a ano, para ver os verões mais secos.
3. **Mesma série** para a umidade na zona das raízes do GLDAS, para ver se a falta de chuva chegou ao solo.
4. **Mapa de diferença** de um verão seco em relação à média, para ver se o padrão cobre todo o planalto ou só um ponto.
5. **Comparação** da chuva do IMERG com a do MERRA-2 no mesmo retângulo.

### O que aparece (hipotético)

| Fonte | O que mostra |
| --- | --- |
| GPM IMERG | Em 4 dos 25 verões, a chuva de dezembro a fevereiro ficou mais de 40% abaixo da média. |
| GLDAS | Nesses mesmos verões, a zona das raízes caiu abaixo do percentil 20 em janeiro. |
| MERRA-2 | Concorda com o IMERG em 3 dos 4 verões secos. |
| Mapa de diferença | O déficit cobre todo o planalto, não só o retângulo. |
| NASA POWER (fora do Giovanni) | Temperaturas mínimas abaixo de 2 °C em vários dias de junho e julho; risco de geada no inverno. |
| HLS (fora do Giovanni) | Pouco solo descoberto: soja e trigo cobrem o talhão quase o ano todo. |

### O que a equipe conclui

**A hipótese se sustenta, com ressalvas.** Os verões secos são raros, mas fortes, e atingem o solo, não só a chuva. IMERG, GLDAS e MERRA-2 concordam na maioria dos casos: confiança **alta** para "verões secos ocasionais" e **média** para atribuir cada um à La Niña, porque o Giovanni mostra a seca, não a causa.

**O Sul é diferente do Cerrado.** Aqui o solo quase não fica descoberto, então a regra de "solo descoberto longo" não é ativada. O que pesa é o risco no verão e a geada no inverno. Isso confirma o argumento da demo: os mesmos dados levam a sugestões diferentes em regiões diferentes.

**Regra registrada.** "Verão com déficit hídrico em 4 ou mais de cada 25 anos" passa a aumentar o peso de estratégias que diversificam o verão. No comparador do Sr. Ivo, isso favorece, por exemplo, alternar soja e milho em parte da área e manter o trigo ou a aveia no inverno. A decisão final continua com o produtor e o agrônomo.

## Conclusão

O Giovanni é o laboratório rápido da equipe. Ele não alimenta a ferramenta direto, mas evita que regras sejam escritas com base em impressão. Em poucos minutos, mostra se uma hipótese sobre chuva ou umidade se sustenta numa região, se as fontes concordam e qual figura explica isso na apresentação.

## Limitações

- **Catálogo focado em clima e água:** não tem HLS, MODIS NDVI na resolução do talhão nem dados de solo.
- **Resolução dos produtos:** IMERG (~10 km), GLDAS (~28 km) e MERRA-2 (~50 km) são regionais; o resultado vale para a região, não para o talhão.
- **Interface manual:** não serve para gerar indicadores para todo o Brasil; isso fica com os scripts.
- **Mudanças no serviço:** a migração do GES DISC para o Earthdata Cloud pode tirar variáveis do ar temporariamente.
- **Correlação não é causa:** o Giovanni mostra a seca, não prova o motivo.
- **Tratamento:** usar o Giovanni para testar hipóteses e validar os números dos scripts, registrar a concordância entre fontes e baixar as figuras com a data e a versão de cada produto.
