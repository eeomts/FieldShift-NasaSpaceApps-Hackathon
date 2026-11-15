# Metodologia dos indicadores do Field Shift

Cada seção explica um indicador ou um cálculo do Field Shift: como ele é feito, o que significa para a lavoura e o que ele não consegue dizer.

## Risco de geada

O risco de geada do Field Shift mostra com que frequência, nos anos passados, a noite ficou fria o bastante para prejudicar a lavoura no local do campo. O app olha mais de 40 anos de temperaturas diárias do NASA POWER, desde 1981, e conta os dias em que a temperatura mínima do ar ficou abaixo de 2 °C. Esse limite pode mudar conforme a cultura, porque cada planta aguenta um frio diferente, e a fase da lavoura também conta: a planta em flor costuma sofrer mais.

O resultado aparece por mês, por exemplo: "em julho, houve noites com risco de geada em 6 de cada 10 anos". Isso é o que aconteceu no passado, não a previsão para amanhã, e não quer dizer que a planta vai morrer.

O risco de geada tem um limite importante: o dado do NASA POWER cobre um quadrado de uns 50 km. Ele não enxerga a baixada fria do sítio, onde o ar gelado escorre e se acumula. Por isso o app também usa o relevo do SRTM para apontar baixadas, e pergunta ao produtor se ele já perdeu safra por geada. Se a memória do produtor e o dado não batem, isso aparece como uma diferença a investigar, nunca como "você está errado".

Como o produtor costuma dizer: geada, friagem, queimou de frio, a geada torrou, frio de matar planta, noite de gelo.

Fonte: NASA POWER (temperatura mínima diária); Field Shift, motor de análise; FAO, Frost protection: fundamentals, practice and economics.

## Dias de calor forte

Os dias de calor forte do Field Shift mostram quantas vezes, em cada mês, a temperatura máxima do ar passou do limite de calor da cultura no local do campo, olhando a série do NASA POWER desde 1981. Quando a cultura não tem um limite próprio na base, o app usa 35 °C como ponto de partida. Calor demais na hora errada atrapalha a planta: na floração, por exemplo, ele pode fazer a flor cair ou o grão não encher direito.

O indicador de dias de calor conta dias, não usa só a média do mês. Uma média de 28 °C pode esconder uma semana de 38 °C, e é essa semana que machuca. Por isso o app mostra a média, a máxima e o número de dias acima do limite, separados.

Cada cultura tem a sua tolerância: o feijão sofre a partir de uns 30 °C, enquanto o milheto e o guandu aguentam até perto de 40 °C. O calor sozinho também não prova dano: a planta com água no solo aguenta mais que a planta em seca. Quando o produtor conta que já perdeu safra por calor, o app procura aquele ano nos dados da NASA para mostrar o que aconteceu.

Como o produtor costuma dizer: calorão, sol rachando, mormaço, a planta cozinhou, esturricou, queimou de sol.

Fonte: NASA POWER (temperatura máxima diária); base de culturas do Field Shift; Field Shift, motor de análise.

## Veranico

Veranico é uma sequência de dias sem chuva no meio da época das águas. O Field Shift conta como veranico um período de 10 dias ou mais seguidos com menos de 1 mm de chuva por dia, dentro da estação chuvosa do lugar. O app usa a chuva do GPM IMERG, que enxerga quadrados de uns 10 km, e compara com a chuva do NASA POWER.

O veranico importa porque a chuva do mês pode parecer boa no total e mesmo assim ter um buraco de duas semanas bem na fase em que a planta mais precisa de água. O app mostra em que meses o veranico costuma acontecer e quantas vezes aconteceu nos últimos anos. Isso ajuda a escolher culturas e datas de plantio que fujam desse período, ou culturas que aguentam melhor a seca.

O veranico também depende do solo: em terra arenosa, poucos dias sem chuva já secam a zona das raízes; em terra argilosa, a reserva dura mais. Por isso o app cruza o veranico com a umidade do solo do SMAP L4 e com a textura da terra.

Como o produtor costuma dizer: veranico, estiagem no meio das águas, a chuva sumiu, parou de chover na hora errada, secou tudo em janeiro.

Fonte: NASA GPM IMERG; NASA POWER; Field Shift, motor de análise.

## Chuva forte

O indicador de chuva forte do Field Shift conta os dias em que choveu muito mais do que o normal no local. O app olha a série de chuva diária e marca os dias acima do percentil 95, ou seja, os 5% de dias mais chuvosos da história daquele lugar. Assim o limite se ajusta à região: chuva forte no Semiárido é diferente de chuva forte na Amazônia.

A chuva forte importa por dois motivos. Primeiro, ela pode encharcar a terra e prejudicar a lavoura. Segundo, e muito importante para o solo, ela arranca a terra quando o chão está sem cobertura. Por isso o app cruza a chuva forte com os meses em que o campo fica descoberto e com a inclinação do terreno.

A chuva do Field Shift vem do GPM IMERG, que mede a chuva a cada meia hora em quadrados de uns 10 km, e é comparada com o NASA POWER. Uma pancada de verão bem localizada pode não aparecer inteira nesses quadrados, então o pluviômetro do produtor, quando existe, vale mais.

Como o produtor costuma dizer: toró, temporal, chuvarada, pancada, tromba d'água, a chuva levou tudo.

Fonte: NASA GPM IMERG; NASA POWER; Field Shift, motor de análise.

## Déficit hídrico e balanço de água

O déficit hídrico do Field Shift mostra quando a chuva não dá conta da água que a lavoura precisa. A conta é um balanço simples: de um lado, a chuva do período; do outro, a água que o ar "puxa" do solo e das plantas, chamada evapotranspiração. O app calcula essa demanda com o método da FAO, usando temperatura, umidade do ar, vento e sol do NASA POWER, e ajusta para cada cultura e fase com o coeficiente de cultura da base.

Quando a demanda passa da chuva por vários dias, a reserva do solo vai baixando. Se a reserva acaba, a planta passa sede. O app mostra o déficit por mês e destaca os meses em que a fase mais sensível da cultura cai num período de pouca água.

O balanço de água do app é uma aproximação. Ele não sabe exatamente quanta água o solo do produtor guarda, quanto escorre na enxurrada ou quanto vem da irrigação. Por isso o resultado é chamado de "aproximação pelo clima", não de diagnóstico da raiz. Quando há dado de umidade do SMAP L4, o app compara os dois.

Como o produtor costuma dizer: falta d'água, seca, a terra não segura água, a chuva não dá, a lavoura passou sede.

Fonte: NASA POWER; FAO-56 (evapotranspiração de referência e coeficiente de cultura); Field Shift, motor de análise.

## Água nas raízes

O indicador de água nas raízes mostra se a umidade do solo, até cerca de 1 metro de fundura, está acima, dentro ou abaixo do normal para aquela época. O dado vem do SMAP L4 da NASA, que junta a medição do satélite na camada de cima do solo com um modelo que estima o que acontece mais embaixo, onde a raiz trabalha.

O app compara a umidade de agora com a média do mesmo período desde 2015. Também conta os dias de estresse: dias em que a água nas raízes ficou entre as mais baixas já registradas no local. Com isso o app pode dizer, por exemplo: "na sua região, 8 dias sem chuva em fevereiro já bastam para a água nas raízes ficar crítica".

A água nas raízes é um valor regional, de quadrados de uns 9 km, e o solo do modelo é genérico. Estar "abaixo do normal" também não quer dizer que a planta está sofrendo: se a época já é seca, o normal já é pouco. Em mata fechada e na Amazônia o dado é menos confiável.

Como o produtor costuma dizer: a terra está seca por baixo, umidade no pé da planta, a raiz não acha água, o chão secou fundo.

Fonte: NASA SMAP L4 (umidade da zona das raízes); Field Shift, motor de análise.

## Meses de solo descoberto

Os meses de solo descoberto mostram em que época do ano o campo fica sem planta verde por cima. O Field Shift usa o NDVI, um índice que os satélites MODIS e VIIRS calculam a cada 16 dias desde 2000 e que mede o quanto de planta verde existe no lugar. Quando o NDVI fica abaixo de 0,25, o app marca aquele período como "pouca cobertura verde".

O app também junta o que o produtor contou no calendário: o que planta, de que mês a que mês e o que acontece depois da colheita. Os meses vazios aparecem destacados para ele confirmar.

O solo descoberto importa porque a chuva forte bate direto no chão e leva a terra, e o sol resseca e queima a matéria orgânica. O cuidado é que palha no chão também protege, mas aparece no satélite quase igual a terra pelada. Por isso o app pergunta se o produtor deixa a palhada e só fala em "solo descoberto" quando os dois sinais combinam.

Como o produtor costuma dizer: terra pelada, chão limpo, campo parado, terra sem nada, pousio, entressafra.

Fonte: NASA MODIS (MOD13Q1) e VIIRS (VJ113A1); Embrapa, plantas de cobertura; Field Shift, motor de análise.

## Risco de erosão

O risco de erosão do Field Shift junta três coisas: a inclinação do terreno, a chuva forte e os meses em que o solo fica descoberto. Quanto mais inclinado o campo, mais forte a chuva e mais tempo o chão fica sem cobertura nos meses de chuva, maior o risco de a enxurrada levar a terra boa de cima.

A inclinação vem do SRTM, um mapa de relevo da NASA com quadradinhos de 30 metros. A chuva forte vem do GPM IMERG. A cobertura vem do NDVI dos satélites MODIS e VIIRS e do calendário que o produtor confirmou. O app também usa a resposta do produtor sobre valetas e água barrenta saindo do campo.

O risco de erosão é um sinal de atenção, não uma medida da terra perdida. O app nunca diz "você perdeu 10 toneladas de solo", porque não mede isso. Ele diz algo como: "este campo junta inclinação, chuva forte em janeiro e terra pelada em janeiro; vale proteger o solo nesse período". Nas estratégias, ganha mais ponto quem cobre o solo justamente nos meses de chuva forte.

Como o produtor costuma dizer: a chuva levou a terra, enxurrada, voçoroca, valeta, sulco, água barrenta, terra lavada.

Fonte: NASA SRTM; NASA GPM IMERG; NASA MODIS/VIIRS; Embrapa, conservação do solo; Field Shift, motor de análise.

## Declividade do terreno

A declividade é a inclinação do terreno, medida em porcentagem: 8% quer dizer que o chão sobe 8 metros a cada 100 metros andados. O Field Shift calcula a declividade com o SRTM, um mapa de altitude da NASA feito por radar a partir do ônibus espacial em 2000, com quadradinhos de 30 metros.

O app usa a classificação da Embrapa: até 3% é plano, de 3% a 8% é suave ondulado, de 8% a 20% é ondulado, de 20% a 45% é forte ondulado, e acima disso é montanhoso. Ele mostra a inclinação média, a maior inclinação e quanto do campo passa de 8%.

A declividade entra no risco de erosão e também ajuda a achar baixadas, onde o ar frio se acumula nas noites de geada. O app compara o mapa com a resposta do produtor sobre o terreno (plano, levemente inclinado ou bem inclinado). O SRTM tem limites: é um retrato do ano 2000, não enxerga terraço, curva de nível nem sulco pequeno, e em lugar muito plano pode mostrar inclinação que não existe.

Como o produtor costuma dizer: morro, ladeira, terreno em pé, encosta, baixada, várzea, chapada, terreno plano.

Fonte: NASA SRTM; Embrapa, Sistema Brasileiro de Classificação de Solos (classes de relevo).

## Retrato do solo

O retrato do solo é o resumo que o Field Shift monta sobre a terra do produtor: drenagem, textura, matéria orgânica, compactação e erosão. Ele nasce juntando várias pistas, cada uma com um peso de confiança. A análise de laboratório vale mais (0,9), depois o teste de campo guiado (0,7), depois o que o produtor observa nas perguntas (0,5) e por fim o mapa global SoilGrids (0,4). Responder "não sei" não conta contra nada: só marca que ali falta informação.

Exemplo da drenagem: o produtor diz que a água fica empoçada mais de um dia (aponta drenagem ruim, peso 0,5); a figura da terra cinza que gruda também aponta drenagem ruim (0,5); o SoilGrids diz drenagem moderada (0,4). A soma dá drenagem ruim, com confiança média. O app então mostra: "o mapa global sugere drenagem moderada, mas você viu água empoçada; no seu campo vale o que você vê".

O retrato do solo nunca esconde quando as fontes discordam. Ele mostra as duas e sugere um teste simples, como o teste do tato, para subir a confiança.

Como o produtor costuma dizer: como é a minha terra, terra boa, terra fraca, terra cansada, terra que encharca.

Fonte: Field Shift, motor de análise (fusão de evidências); ISRIC SoilGrids 2.0.

## Nível de confiança

O nível de confiança do Field Shift diz o quanto dá para acreditar em cada número mostrado: alto, médio ou baixo. Ele não é uma probabilidade; é uma classificação com regras abertas.

A confiança sobe quando o dado é fino (quadrados pequenos, perto do tamanho do campo), quando a série de anos é longa e quando fontes diferentes concordam. Por exemplo, se a chuva do NASA POWER e a do GPM IMERG contam a mesma história, e o produtor lembra do mesmo ano de seca, a confiança sobe. A confiança cai quando o dado é de um quadrado grande, quando a série é curta, quando há muita nuvem nas imagens ou quando as fontes discordam.

O app mostra a confiança de cada indicador separado, e não uma só para tudo, porque uma estratégia pode ter boa base no clima e base fraca no solo. Ele também aponta o elo mais fraco e o que fazer para melhorar, como uma análise de solo ou um pluviômetro. Quando não há dado, aparece "sem dados suficientes", nunca zero.

Como o produtor costuma dizer: dá pra confiar?, isso é certo?, de onde saiu esse número?, é chute?

Fonte: Field Shift, motor de análise; Field Shift, glossário científico (incerteza e validação local).

## Nota das estratégias de rotação

A nota das estratégias é como o Field Shift compara a rotação atual do produtor com outras possíveis. Primeiro o app monta candidatas: preencher o mês vazio com planta de cobertura, trocar por uma cultura que aguenta mais a seca ou incluir uma leguminosa. Depois tira as inviáveis: a cultura que não fecha o ciclo na janela, que corre risco alto de geada, que precisa de mais água do que tem, que o produtor não plantaria ou para a qual falta máquina.

Cada estratégia que sobra ganha uma nota de 0 a 1 em seis critérios: economizar água, melhorar a terra, evitar erosão, menos praga, renda extra e comida pros animais. As prioridades do produtor dão o peso: a primeira escolha vale 0,5, a segunda 0,3, a terceira 0,2. O app mostra a rotação atual e as 2 melhores.

A nota das estratégias não usa inteligência artificial nem caixa-preta. Toda nota se abre até o dado de origem, e é daí que sai o "por que foi sugerida". A nota é um apoio para conversar e decidir; quem decide é o produtor.

Como o produtor costuma dizer: o que plantar depois?, o que dá mais certo aqui?, rodar a lavoura, trocar de cultura, qual a melhor opção?

Fonte: Field Shift, motor de análise (análise multicritério).

## Graus-dia e janela de plantio

Graus-dia é uma forma de medir o calor acumulado que a planta recebe até fechar o ciclo. Cada cultura tem uma temperatura base, abaixo da qual ela praticamente para de crescer: 10 °C para o milho e a soja, 0 °C para o trigo, por exemplo. A conta de cada dia é a temperatura média do dia menos a temperatura base; se der negativo, conta zero. O Field Shift soma os graus-dia com a temperatura do NASA POWER e compara com quanto cada cultura precisa: o milho, por exemplo, precisa de 1.500 a 1.900 graus-dia. Nas plantas de cobertura, a conta vai até o corte na floração, e não até o grão.

Por exemplo: se o campo fica vazio de abril a julho, o app verifica se uma planta de cobertura ou uma safrinha consegue crescer nesse tempo com o frio daquela época. Se a soma ficar abaixo de 90% do mínimo da cultura, a estratégia é descartada antes da comparação; entre 90% e 100%, ela fica marcada como "no limite", para conferir no local.

A janela de plantio também considera o risco de geada e de falta de chuva nas fases sensíveis, e os dados do ZARC, o zoneamento de risco climático do Ministério da Agricultura, quando disponíveis. A conta de graus-dia é feita pelo clima da região; variedades precoces ou tardias podem mudar o resultado, por isso o produtor confirma as datas.

Como o produtor costuma dizer: dá tempo de plantar?, fecha o ciclo?, época de plantio, plantar no tarde, safrinha, janela.

Fonte: NASA POWER; base de culturas do Field Shift; MAPA, Zoneamento Agrícola de Risco Climático (ZARC); Field Shift, motor de análise.

## Cenários: e se?

Um cenário no Field Shift é rodar a mesma análise trocando alguma coisa, para ver o que muda. Não é uma previsão do futuro, é um teste de sensibilidade: mostra o quanto cada estratégia depende do clima ou dos recursos.

Há três tipos de cenário. No cenário de clima, o produtor pode testar, por exemplo, chuva 20% menor ou temperatura 2 °C maior. No cenário de rotação, testa um calendário diferente, como "e se eu plantar sorgo em vez de milho?". No cenário de recursos, testa uma mudança na fazenda, como "e se eu tiver irrigação em parte do campo?".

O app refaz as contas e mostra como a nota de cada estratégia sobe ou desce. Uma estratégia que continua boa mesmo com menos chuva é mais segura do que uma que só funciona em ano bom. Cada cenário fica salvo e aparece no painel e no chat. O cenário de clima usa a série do NASA POWER como base, e a diferença é aplicada sobre ela.

Como o produtor costuma dizer: e se chover menos?, e se esquentar?, e se eu plantar outra coisa?, e se der seca?, ano ruim.

Fonte: Field Shift, motor de análise (cenários); NASA POWER.
