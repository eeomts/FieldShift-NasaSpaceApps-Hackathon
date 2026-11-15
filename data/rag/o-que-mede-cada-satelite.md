# O que mede cada satélite e cada base de dados

Cada seção explica uma fonte de dados usada pelo Field Shift: o que ela vê, em linguagem simples, e até onde dá para confiar nela.

## NASA POWER: clima do lugar

O NASA POWER é um serviço da NASA que entrega dados de clima para qualquer ponto do planeta: temperatura máxima e mínima, chuva, umidade do ar, vento e sol. A série começa em 1981, então dá para olhar mais de 40 anos e saber o que é normal em cada mês, com que frequência faltou chuva ou fez frio demais, e se o clima está mudando.

O Field Shift usa o NASA POWER para quase todos os indicadores de clima: risco de geada, dias de calor, veranico, balanço de água, graus-dia e cenários.

O limite do NASA POWER é o tamanho do quadrado: cada valor representa uma área de uns 50 por 60 km. A fazenda inteira, e às vezes o município, cai num quadrado só. Ele não enxerga a baixada fria nem a chuva que caiu só no vizinho. Além disso, o NASA POWER não é um termômetro instalado no campo: é um modelo que junta observações de satélites e estações para estimar o clima. A chuva é o ponto mais fraco, por isso o app compara com o GPM IMERG. Os dados dos últimos meses ainda podem ser corrigidos.

Como o produtor costuma dizer: o tempo, o clima da região, a temperatura, a chuva do ano, o inverno, o verão.

Fonte: NASA Langley Research Center, projeto POWER.

## GPM IMERG: chuva vista do espaço

O GPM IMERG é o produto de chuva da missão GPM, feita pela NASA com a agência espacial do Japão. Ele junta vários satélites que enxergam a chuva por micro-ondas e infravermelho e, na versão final, corrige o resultado com pluviômetros no chão. Entrega a chuva a cada meia hora, em quadrados de uns 10 km, desde 2000.

O Field Shift usa o GPM IMERG para veranicos, chuva forte, início e fim da época das águas e risco de erosão. Como ele mede a chuva de meia em meia hora, dá para saber se a chuva veio forte e de uma vez, que é a que mais leva terra. Ele também serve para conferir a chuva do NASA POWER: quando os dois concordam, a confiança sobe.

Os limites do GPM IMERG: é uma estimativa feita do espaço, não um pluviômetro no campo. A pancada de verão bem localizada fica "espalhada" no quadrado de 10 km. Em serras, o acerto é menor. Onde há poucos pluviômetros, a correção é mais fraca. E a versão corrigida demora uns 3 meses e meio para sair; antes disso, o app usa uma versão provisória e avisa.

Como o produtor costuma dizer: chuva, aguaceiro, chuva de pedra, pancada, chuva fina, quanto choveu.

Fonte: NASA e JAXA, missão GPM, produto IMERG versão 07.

## SMAP L4: água dentro do solo

O SMAP é um satélite da NASA que mede a umidade dos primeiros 5 cm do solo. O SMAP L4 junta essa medição com um modelo de computador e estima a umidade também na zona das raízes, até cerca de 1 metro de fundura. Entrega dados a cada 3 horas, em quadrados de 9 km, desde 2015.

O Field Shift usa o SMAP L4 para responder "como está a água no pé da planta nesta safra?". O app compara a umidade de agora com o normal da época e conta os dias de estresse, em que a terra ficou mais seca do que quase sempre fica. Com isso dá para dizer quantos dias sem chuva bastam para a água nas raízes ficar crítica naquela região.

Os limites do SMAP L4: só a camada de cima é medida; a parte da raiz é calculada. O quadrado de 9 km dá um valor regional, não do talhão, e o modelo usa um solo genérico, que pode ser diferente da terra do produtor. Em mata fechada e na Amazônia, a medição perde qualidade. E a série é curta, começa em 2015, então não serve para olhar décadas.

Como o produtor costuma dizer: umidade da terra, terra molhada, terra seca, o chão segurou água, a terra está com água por baixo.

Fonte: NASA, missão SMAP, produto SPL4SMGP (nível 4).

## MODIS e VIIRS: o verde da lavoura

O MODIS e o VIIRS são sensores em satélites da NASA e da NOAA que fotografam a Terra todo dia. Com essas imagens, eles calculam o NDVI, um número que mostra quanto de planta verde existe no lugar. A cada 16 dias sai uma imagem limpa, juntando os melhores dias sem nuvem. O MODIS tem dados desde 2000, em quadradinhos de 250 metros; o VIIRS continua o trabalho com quadradinhos de 500 metros.

O Field Shift usa o NDVI para montar a curva do ano: quando a lavoura sobe, quando chega ao máximo, quando é colhida e quanto tempo o campo fica sem verde. É daí que saem os meses de solo descoberto e a comparação entre anos bons e ruins.

Os limites: um quadradinho de 250 metros pode misturar lavoura, estrada e mata. Nuvem persistente atrapalha. A imagem de 16 dias atrasa eventos curtos. Palhada no chão aparece quase igual a terra pelada. E os satélites antigos do MODIS estão sendo desligados entre 2026 e 2027; o histórico continua valendo e os dados novos vêm do VIIRS.

Como o produtor costuma dizer: lavoura verde, lavoura bonita, a roça fechou, a planta amarelou, a lavoura murchou.

Fonte: NASA, produtos MOD13Q1 (MODIS) e VJ113A1 (VIIRS).

## SRTM: o relevo do terreno

O SRTM é um mapa de altitude de quase todo o planeta, feito em 2000 por um radar levado no ônibus espacial Endeavour. Ele mostra a altura do chão em quadradinhos de 30 metros.

O Field Shift usa o SRTM para três coisas. Primeiro, a declividade, ou seja, quanto o terreno é inclinado, que entra no risco de erosão. Segundo, as baixadas, onde o ar frio desce e se acumula nas noites de geada. Terceiro, a altitude média do campo, que ajuda a corrigir os dados de clima do NASA POWER.

O app também compara o SRTM com o que o produtor responde sobre o terreno (plano, levemente inclinado ou bem inclinado).

Os limites: o SRTM é um retrato de 2000, então o que mudou depois não aparece. Ele mede o topo das coisas, então mata alta pode parecer morro. Quadradinhos de 30 metros não enxergam terraço, curva de nível nem sulco pequeno. Em terreno muito plano, pode mostrar inclinação falsa. E o relevo sozinho não mede erosão nem geada: ele é uma das pistas.

Como o produtor costuma dizer: morro, ladeira, baixada, várzea, chapada, encosta, terreno plano, terreno em pé.

Fonte: NASA e NGA, Shuttle Radar Topography Mission (SRTM), versão 3.

## SoilGrids: mapa mundial do solo

O SoilGrids é um mapa mundial de solo feito pelo ISRIC, um centro de pesquisa da Holanda. Não é da NASA, mas é aberto. Ele não mede o solo por satélite: usa centenas de milhares de amostras de solo coletadas em campo no mundo todo e um modelo de computador que estima o solo onde ninguém coletou, olhando clima, relevo, vegetação e rochas.

O SoilGrids dá números em quadradinhos de 250 metros e em várias profundidades: quanto de argila, de areia, de carbono (ligado à matéria orgânica), o pH (acidez) e quanta água a terra segura. O Field Shift usa esses números no retrato do solo, para textura, água disponível e acidez.

Os limites: é uma estimativa, não uma análise de laboratório, e pode errar muito onde há poucas amostras, como na Amazônia. O SoilGrids mostra o próprio grau de incerteza, e o app usa isso. Ele também não enxerga o manejo recente, como calcário ou compactação nova. No Field Shift, o SoilGrids tem o menor peso entre as pistas sobre o solo: a observação do produtor e o laudo valem mais.

Como o produtor costuma dizer: tipo de terra, terra argilosa, terra de areia, terra ácida, terra forte, terra fraca.

Fonte: ISRIC World Soil Information, SoilGrids 2.0.

## Tamanho do quadrado: escala dos dados

Todo dado de satélite ou de modelo vem em quadrados, e cada quadrado tem um só valor. Esse tamanho é a escala, ou resolução. No Field Shift, os quadrados vão de 30 metros a mais de 50 km: o SRTM tem 30 metros; o MODIS, 250 metros; o SoilGrids, 250 metros; o VIIRS, 500 metros; o SMAP L4, 9 km; o GPM IMERG, cerca de 10 km; o NASA POWER, cerca de 50 km.

Isso importa porque um quadrado grande mostra a média da região, não o que acontece num canto do sítio. O clima de 50 km não sabe da baixada fria nem da chuva que caiu só no vizinho. O app sempre diz de que tamanho é o quadrado de cada número, e trata o dado grande como "contexto da região".

Mostrar o mapa mais bonito, com quadradinhos menores, não cria informação nova: se o dado veio de 9 km, ele continua sendo de 9 km. Por isso o que o produtor vê no campo, como água empoçada, frio na baixada ou chuva no pluviômetro, é tão importante: ele enxerga o que o satélite não enxerga.

Como o produtor costuma dizer: o satélite vê meu sítio?, isso é da minha terra ou da região?, aqui é diferente do vizinho.

Fonte: Field Shift, glossário científico (escala espacial); notas técnicas de cada fonte no repositório do projeto.

## Por que o app compara várias fontes

O Field Shift não confia em uma fonte só. Para cada pergunta importante, ele procura pelo menos duas pistas diferentes e compara. A chuva do NASA POWER é comparada com a do GPM IMERG. A umidade do SMAP L4 é comparada com o balanço de água calculado pelo clima. O solo do SoilGrids é comparado com o que o produtor observa e com a análise de laboratório. O relevo do SRTM é comparado com a resposta sobre o terreno.

Quando as fontes concordam, a confiança sobe. Quando discordam, o app não esconde: mostra os dois resultados lado a lado e explica a diferença. Muitas vezes a diferença vem da escala, porque o satélite vê a região e o produtor vê o campo.

Mesmo quando duas fontes concordam, isso não é prova. Algumas usam parte dos mesmos dados por trás, então não são totalmente independentes. Por isso o app fala em "confiança alta", e não em "certeza", e sempre indica o que poderia ser conferido no campo para tirar a dúvida.

Como o produtor costuma dizer: quem está certo?, o satélite errou?, o que eu vejo é diferente, conferir.

Fonte: Field Shift, motor de análise (fusão de evidências e nível de confiança).
