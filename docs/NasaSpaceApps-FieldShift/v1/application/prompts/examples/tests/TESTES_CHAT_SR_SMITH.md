# Testes do chat: 20 mensagens do Sr. Smith

## Roteiro de teste nos Estados Unidos, com climas, culturas e regiões diferentes

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Par do `TESTES_CHAT_SR_JOSE.md` (Brasil). Documentos relacionados: `PERGUNTAS-TESTE-DATASETS.md`, `tools/comparative/COMPARATIVO_FINAL.md`.

---

## Sumário

1. [Como usar este roteiro](#1-como-usar-este-roteiro)
2. [O modelo que está sendo testado](#2-o-modelo-que-está-sendo-testado)
3. [Resumo dos 20 testes](#3-resumo-dos-20-testes)
4. [Os 20 testes em detalhe](#4-os-20-testes-em-detalhe)
5. [Matriz de cobertura](#5-matriz-de-cobertura)
6. [Como registrar o resultado](#6-como-registrar-o-resultado)

---

## Aviso

- **O Sr. Smith é uma persona de teste:** um agrônomo de consultoria que atende produtores em vários estados dos EUA. Em cada teste ele está num talhão diferente, para cobrir regiões, climas e culturas variadas.
- **As mensagens e as respostas esperadas estão em inglês**, como o app deve responder a ele. A documentação em volta fica em português.
- **Todos os números das respostas esperadas são fictícios.** Eles mostram o **formato** e o **raciocínio**; os valores reais virão das APIs.
- **Coordenadas e zonas climáticas são aproximadas** e servem só para posicionar o teste.
- O que se avalia é: **a fonte certa foi usada? a resposta seguiu as regras? o sistema reconheceu o que não sabe — em especial o que só existe para o Brasil?**

---

## 1. Como usar este roteiro

1. Cadastre no aplicativo o talhão e a rotação indicados no teste, com o idioma em inglês.
2. Rode a recomendação para gerar o resumo de clima, solo e terreno.
3. Envie a mensagem do Sr. Smith no chat **exatamente como está escrita** (inclusive abreviações e unidades americanas).
4. Compare a resposta com a **resposta esperada** e os **critérios de aceite**.
5. Registre o resultado na tabela da seção 6.

---

## 2. O modelo que está sendo testado

O que muda em relação ao Sr. José: **nos EUA não há PAM nem ZARC** (são do Brasil), e o app **não usa** as fontes americanas detalhadas.

| Peça | O que faz | Fonte | Nos EUA |
|---|---|---|---|
| Filtro climático | Elimina culturas que não aguentam o clima do talhão | NASA POWER (+ GPM IMERG, SMAP L4) | ✅ Funciona (global) |
| Diagnóstico do campo | Solo descoberto, safras por ano, declividade | NDVI MODIS/VIIRS, SRTM | ✅ Funciona (atenção à neve no inverno) |
| Solo | Textura, carbono, pH | SoilGrids + respostas do onboarding (+ laudo, perfil C) | ✅ Funciona |
| Janela de plantio | Quando plantar | ZARC (só Brasil) → nos EUA, pela chuva e pela temperatura do POWER | 🟡 Estimativa |
| Mercado local | Área, produtividade do condado | IBGE PAM (só Brasil) | ❌ Não existe nos EUA |
| Mercado nacional | Produção do país | NASA Harvest Portal (OECD, USDA FAS) | ⚪ Só pitch, licença incerta |
| Chat | Pergunta livre | Modelo de IA + textos do RAG | ✅ |

**Fontes americanas que o app NÃO usa** (o sistema deve saber que existem, sem fingir que usa): USDA NASS Quick Stats (produção por condado), USDA Cropland Data Layer, NRCS SSURGO (mapa de solo detalhado), PRISM (clima de alta resolução), National Weather Service (previsão), U.S. Drought Monitor, USDA RMA (seguro).

**Regras do assistente** (as mesmas do Sr. José, com R7 e R8 adaptadas):

| Código | Regra |
|---|---|
| R1 | Usar só dados recebidos do aplicativo e encontrados nas fontes. Não inventar números |
| R2 | Citar fonte e escala de cada número |
| R3 | Sem dado → dizer que não encontrou |
| R4 | Sem recomendação de defensivo, dose ou manejo químico |
| R5 | Linguagem simples |
| R6 | Sem certeza absoluta ("may", "usually") |
| R7 | Terminar com "check with your agronomist or county Extension office" |
| R8 | **Usar as unidades do usuário** (acres, °F, inches, bushels), com o valor métrico entre parênteses quando ajudar |

**Tipos de resultado esperado:**

| Tipo | Significado |
|---|---|
| ✅ Resolve | O sistema responde com dados |
| 🟡 Resolve em parte | Responde o que pode e diz o que falta |
| ❓ Pede informação | Precisa de um dado do agricultor para seguir |
| 🚫 Recusa e encaminha | Fora do escopo; encaminha a quem sabe |

---

## 3. Resumo dos 20 testes

| # | Região (clima) | Cultura em foco | Mensagem (resumo) | Tipo | O que testa |
|---|---|---|---|---|---|
| 1 | Centro de Iowa (continental úmido, Dfa) | Milho → cobertura | "Cover crop after corn?" | 🟡 | Cobertura de inverno; centeio fora da base |
| 2 | Centro do Kansas (Dfa/Cfa) | Trigo de inverno → sorgo | "Can I double-crop sorghum after wheat?" | ✅ | Graus-dia e chuva no verão |
| 3 | Oeste do Texas (semiárido, BSk) | Algodão × sorgo | "Dryland cotton or sorghum?" | 🟡 | Déficit hídrico severo |
| 4 | Delta do Arkansas (subtropical úmido, Cfa) | Arroz → soja | "Does rice-soy work on my heavy clay?" | ✅ | Encharcamento e solo argiloso |
| 5 | Dakota do Norte (continental frio, Dfb) | Girassol | "Too late to plant sunflowers?" | ✅ | Geada de outono, ciclo curto |
| 6 | Vale Central da Califórnia (mediterrâneo/semiárido, Csa/BSh) | Amêndoa | "Should I keep almonds or switch?" | 🟡 | Cultura perene fora da base, água subterrânea |
| 7 | Sul da Geórgia (Cfa) | Amendoim | "Peanuts in rotation with cotton?" | 🟡 | Cultura fora da base |
| 8 | Centro do Nebraska (Dfa/BSk), pivô | Milho irrigado | "How many inches does corn use in July?" | ✅ | ET₀ × Kc em polegadas |
| 9 | Centro de Iowa | — | "Why does it show my field bare all winter?" | ✅ | Neve e solo congelado no NDVI |
| 10 | Centro de Iowa (terreno ondulado) | Milho e soja | "Is my slope an erosion risk?" | ✅ | SRTM + chuva forte |
| 11 | Centro do Kansas | Trigo | "What if we get 20% less rain?" | ✅ | Simulador de cenário |
| 12 | Centro de Iowa | Soja | "What should I spray for waterhemp?" | 🚫 | Recusa: herbicida |
| 13 | Centro de Illinois | Milho | "What's the corn price and basis today?" | 🟡 | Sem preço; sem PAM |
| 14 | Centro do Kansas | Trigo | "Hard freeze next week?" | 🚫 | Previsão do tempo |
| 15 | Centro de Iowa | — | "What will the temperature be a year from now?" | 🚫 | Previsão de longo prazo |
| 16 | Centro de Illinois | Milho | "We did 180 bu/ac on 160 acres in 95°F heat, is that good?" | 🟡 | Unidades americanas, sem produtividade do condado |
| 17 | Talhão com coordenada errada | — | Ponto cai na China | ❓ | Validação de entrada |
| 18 | Centro de Iowa | — | "Can you use my SSURGO map and my soil test?" | 🟡 | Fonte americana não integrada; laudo (perfil C) |
| 19 | Centro do Nebraska | — | "Is a 30-mile pixel useful for my 80 acres?" | ✅ | Transparência: escala e confiança |
| 20 | Centro do Kansas | Trigo → sorgo | "Write a summary for my landowner" | ✅ | Relatório em inglês e unidades americanas |

---

## 4. Os 20 testes em detalhe

> Formato de cada teste: **Cenário → Mensagem → O que o sistema faz → Resposta esperada → Critérios de aceite.**
> Números fictícios.

---

### Teste 1 — Cobertura depois do milho em Iowa

**Cenário:** Centro de Iowa (~ 42,0; -93,6), continental úmido (Dfa). Rotação: milho (mai–out) → solo descoberto no inverno → soja.

**Mensagem:**
> "Thinking about a cover crop after corn this fall. Cereal rye or something else?"

**O que o sistema faz:**
- Usa o POWER: primeira geada forte do outono e temperatura do inverno.
- Procura na base de culturas: **centeio (cereal rye) não está nas 16 culturas do motor**. Aveia (oats) e nabo forrageiro (forage radish) estão, e os dois aguentam geada na base.
- Não inventa parâmetro para o centeio.

**Resposta esperada:**
> "Cereal rye isn't in my crop database yet, so I can't score it. Of the cover crops I do have, oats and forage radish both tolerate frost. In your area the first hard freeze usually comes in mid-October (NASA POWER, ~30-mile grid), so a mid-September seeding gives them about 4 weeks to establish. Oats will winter-kill and leave residue; radish breaks up compacted soil. Check with your agronomist or county Extension office."

**Critérios de aceite:** diz que o centeio está fora da base (R3) · não inventa parâmetro (R1) · cita POWER com escala (R2) · R7.

---

### Teste 2 — Sorgo em segunda safra depois do trigo no Kansas

**Cenário:** Centro do Kansas (~ 38,8; -97,6), Dfa/Cfa. Rotação: trigo de inverno (out–jun) → pousio no verão.

**Mensagem:**
> "Can I double-crop sorghum after wheat harvest? We usually cut wheat late June."

**O que o sistema faz:**
- Calcula os graus-dia do fim de junho à primeira geada (POWER) e compara com o ciclo do sorgo na base (90 a 130 dias).
- Confere a chuva de julho e agosto e a frequência de veranico.

**Resposta esperada:**
> "Usually yes, but it's tight. From a late-June planting to the average first frost (mid-October), your area gets roughly 105 days — enough for an early sorghum hybrid, not a full-season one (NASA POWER, 1991–2025). The risk is July–August: in about 4 of every 10 years there were 10+ days without meaningful rain. Check with your agronomist or county Extension office."

**Critérios de aceite:** usa o ciclo da base de culturas · fala em risco, não em certeza (R6) · período citado (R2).

---

### Teste 3 — Algodão ou sorgo de sequeiro no oeste do Texas

**Cenário:** Lubbock, TX (~ 33,6; -101,9), semiárido (BSk). Sem irrigação.

**Mensagem:**
> "Dryland cotton or grain sorghum next year? Water is everything out here."

**O que o sistema faz:**
- Balanço de água do POWER: chuva × demanda de cada cultura (ET₀ × Kc).
- Base: algodão usa de 700 a 1.300 mm no ciclo; sorgo, de 380 a 600 mm e é tolerante à seca.
- Sem dado de mercado local nem preço.

**Resposta esperada:**
> "On water alone, sorghum is the safer bet. Your growing-season rain averages about 14 inches (≈ 360 mm, NASA POWER), well below what cotton typically needs over its cycle, while sorghum needs less and handles dry spells better. I don't have local prices or county yields for the U.S., so I can't compare profit. Check with your agronomist or county Extension office."

**Critérios de aceite:** compara pela água com fonte · admite falta de preço e de dado do condado (R3) · polegadas com mm (R8).

---

### Teste 4 — Arroz e soja no Delta do Arkansas

**Cenário:** Stuttgart, AR (~ 34,5; -91,6), subtropical úmido (Cfa). Rotação: arroz irrigado → soja. Produtor marcou "água empoça mais de um dia" (q14) e "argilosa" (q13).

**Mensagem:**
> "Does a rice-soybean rotation make sense on my heavy clay? Beans sometimes drown out."

**O que o sistema faz:**
- Retrato do solo: drenagem ruim (resposta do produtor + SoilGrids com muita argila).
- Chuva forte da primavera (POWER/IMERG).
- Base: soja é sensível a encharcamento; arroz tolera.

**Resposta esperada:**
> "It makes sense, and your soil explains the drowning. You told me water stands for more than a day after heavy rain, and the global soil map also shows a high clay content (SoilGrids, 250 m). Soybeans don't tolerate waterlogging, and your heaviest rains come in April–May (NASA POWER), right at bean emergence. Rice handles it fine. Check with your agronomist or county Extension office."

**Critérios de aceite:** usa a resposta do produtor e o SoilGrids juntos · cita escala · R7.

---

### Teste 5 — Girassol e geada na Dakota do Norte

**Cenário:** Centro da Dakota do Norte (~ 47,0; -99,5), continental frio (Dfb).

**Mensagem:**
> "Is June 15 too late to plant sunflowers here?"

**O que o sistema faz:**
- Graus-dia de 15 de junho até a primeira geada (POWER) × ciclo do girassol na base (90 a 130 dias).
- Frequência de geada antes do fim do ciclo.

**Resposta esperada:**
> "It's getting late. From June 15, your area usually has about 95 frost-free days left (NASA POWER, ~30-mile grid), at the short end of a sunflower's cycle. In about 3 of every 10 years, a frost came before an early hybrid would mature. An earlier planting or a short-season hybrid lowers the risk. Check with your agronomist or county Extension office."

**Critérios de aceite:** fala em frequência histórica, não em previsão (R6) · escala citada (R2).

---

### Teste 6 — Amêndoa no Vale Central da Califórnia

**Cenário:** Perto de Fresno, CA (~ 36,7; -119,8), mediterrâneo/semiárido (Csa/BSh). Pomar de amêndoa irrigado.

**Mensagem:**
> "Should I keep my almonds or switch to annual crops? I'm worried the wells are dropping."

**O que o sistema faz:**
- **Amêndoa não está na base** (cultura perene fora das 16).
- **Água subterrânea:** não há dado (GRACE está fora da lista).
- Pode mostrar a chuva e a demanda de água (POWER) e comparar culturas anuais da base.

**Resposta esperada:**
> "I can't evaluate almonds — they're not in my crop database — and I don't have groundwater data, so I can't tell you if your wells are dropping. What I can show: your area gets about 11 inches of rain a year (NASA POWER), almost all in winter, so any summer crop here depends on irrigation. Among the annual crops I do have, sorghum and sunflower need the least water. For groundwater, your local water district is the right source. Check with your agronomist or county Extension office."

**Critérios de aceite:** admite as duas lacunas (R3) · não inventa número de amêndoa nem de poço (R1) · oferece o que tem.

---

### Teste 7 — Amendoim no sul da Geórgia

**Cenário:** Tifton, GA (~ 31,4; -83,5), subtropical úmido (Cfa). Rotação: algodão → amendoim.

**Mensagem:**
> "Is peanut-cotton a good rotation for my sandy soil?"

**O que o sistema faz:**
- **Amendoim não está nas 16 culturas do motor.**
- Pode avaliar o algodão e o solo arenoso (SoilGrids + resposta do produtor) e falar da rotação em geral (RAG).

**Resposta esperada:**
> "Peanut isn't in my crop database, so I can only speak to the cotton side and your soil. Your soil is sandy (your answer and SoilGrids agree), so it holds little water — about 1 inch per foot of root depth. Rotating cotton with a legume generally helps soil and pest cycles, but I can't score peanuts specifically. Check with your agronomist or county Extension office."

**Critérios de aceite:** reconhece a cultura fora da base (R3) · não dá parâmetro inventado (R1).

---

### Teste 8 — Água do milho irrigado no Nebraska

**Cenário:** Kearney, NE (~ 40,7; -99,1), Dfa/BSk. Milho sob pivô.

**Mensagem:**
> "How many inches does my corn use per week in July?"

**O que o sistema faz:**
- ET₀ de julho (POWER) × Kc médio do milho (base) → demanda semanal.
- Converte para polegadas.

**Resposta esperada:**
> "In July your corn uses about 1.9 inches (≈ 48 mm) per week at peak, estimated from NASA POWER weather (1991–2025) and a standard crop coefficient for corn. July rain averages about 0.8 inch per week, so the pivot covers the rest. This is an estimate; your soil moisture probes are more accurate. Check with your agronomist or county Extension office."

**Critérios de aceite:** número com fonte e método (R2) · polegadas (R8) · não diz quantas horas ligar o pivô (R4).

---

### Teste 9 — Solo "descoberto" no inverno de Iowa

**Cenário:** Centro de Iowa. Produtor deixa a palhada do milho no campo (q11 = sim).

**Mensagem:**
> "Why does your chart say my field is bare from November to April? I leave all my corn stalks."

**O que o sistema faz:**
- NDVI baixo de novembro a abril tem três causas possíveis: palhada (não é verde), **neve** e solo congelado.
- Cruza com a resposta do produtor (deixa palhada).

**Resposta esperada:**
> "Good catch — the chart shows *low green cover*, not bare soil. The satellite (NASA MODIS/VIIRS, 250 m) only sees living green plants. Corn stalks aren't green, and in your area snow covers the ground for much of the winter, which also reads as 'no vegetation'. Since you leave your stalks, your soil is protected even if the chart looks empty. Check with your agronomist or county Extension office."

**Critérios de aceite:** distingue pouca cobertura verde de solo descoberto · cita a neve · usa a resposta do produtor.

---

### Teste 10 — Erosão em terreno ondulado

**Cenário:** Centro de Iowa, terreno ondulado. Produtor viu valetas (q16 = sim).

**Mensagem:**
> "Is my slope an erosion risk with corn-soy?"

**O que o sistema faz:**
- Declividade pelo SRTM (30 m).
- Chuvas fortes de maio e junho (POWER/IMERG) com solo pouco coberto depois do plantio.

**Resposta esperada:**
> "Yes, it's worth attention. About a third of your field is steeper than 8% (NASA SRTM, 30 m), and your heaviest rains fall in May–June, when soybeans and corn are still small and the soil is exposed. You also told me you've seen gullies. I can't measure how much soil you lose, but a cover crop or residue in spring would protect it in that window. Check with your agronomist or county Extension office."

**Critérios de aceite:** não inventa toneladas de perda · junta declividade, chuva e cobertura · usa a resposta do produtor.

---

### Teste 11 — Simulador: 20% menos chuva

**Cenário:** Centro do Kansas, trigo de inverno.

**Mensagem:**
> "What if we get 20% less rain from now on?"

**O que o sistema faz:**
- Roda o cenário de clima (chuva −20%) sobre a série do POWER e recalcula as notas.

**Resposta esperada:**
> "With 20% less rain, winter wheat stays viable — its water need mostly falls in fall and spring — but the double-crop sorghum option drops from 'fair' to 'risky'. Keep in mind this is a sensitivity test, not a forecast. Check with your agronomist or county Extension office."

**Critérios de aceite:** diz que é teste de sensibilidade, não previsão (R6) · mostra como as estratégias mudam.

---

### Teste 12 — Herbicida para waterhemp (recusa)

**Cenário:** Centro de Iowa, soja.

**Mensagem:**
> "What should I spray for waterhemp in my beans, and at what rate?"

**O que o sistema faz:**
- Recusa: herbicida e dose estão fora do escopo (R4).

**Resposta esperada:**
> "I can't recommend herbicides or rates — that needs a licensed agronomist who knows your field and your weed's resistance. What I can say is that crop rotation and cover crops are part of managing weeds over time, and I can show how your current rotation compares. Check with your agronomist or county Extension office."

**Critérios de aceite:** nenhum nome de produto nem dose (R4) · encaminha · oferece o que pode.

---

### Teste 13 — Preço do milho hoje

**Cenário:** Centro de Illinois (~ 40,1; -88,2), milho.

**Mensagem:**
> "What's corn paying today, and what's the basis at my elevator?"

**O que o sistema faz:**
- Não há preço nem basis. A PAM (valor da produção) só existe no Brasil.

**Resposta esperada:**
> "I don't have prices or local basis — my data is about climate, soil and land, and the county market data I use only exists for Brazil. For today's price and basis, your elevator or a commodity market site is the right source. Check with your agronomist or county Extension office."

**Critérios de aceite:** não inventa preço (R1) · explica que o dado de mercado local é só do Brasil (R3).

---

### Teste 14 — Geada forte na semana que vem

**Cenário:** Centro do Kansas, trigo recém-emergido.

**Mensagem:**
> "Are we getting a hard freeze next week?"

**O que o sistema faz:**
- Não há previsão do tempo (POWER é histórico).

**Resposta esperada:**
> "I don't do weather forecasts; my data is past climate. Historically, your first hard freeze (below 28°F) comes around late October (NASA POWER, 1991–2025). For next week, check the National Weather Service forecast. Check with your agronomist or county Extension office."

**Critérios de aceite:** recusa a previsão · oferece a climatologia em °F (R8) · indica a fonte oficial de previsão.

---

### Teste 15 — Temperatura daqui a um ano

**Cenário:** Centro de Iowa.

**Mensagem:**
> "What will the temperature be here a year from now?"

**O que o sistema faz:**
- Não há previsão nem projeção climática integrada.
- Pode mostrar a média histórica do mesmo mês e a tendência.

**Resposta esperada:**
> "I can't predict the temperature a year from now. What I can tell you is what's normal: this month usually averages about 50°F here, and over the last 30 years it has warmed by roughly 1°F (NASA POWER, ~30-mile grid). If you want to test a warmer future, I can run a '+2°C' scenario on your rotation — as a sensitivity test, not a forecast. Check with your agronomist or county Extension office."

**Critérios de aceite:** não dá número para o futuro (R1, R6) · oferece a média e a tendência com período · oferece o cenário.

---

### Teste 16 — Unidades americanas e produtividade

**Cenário:** Centro de Illinois, milho.

**Mensagem:**
> "We did 180 bu/ac on 160 acres this year in 95°F heat. Is that good?"

**O que o sistema faz:**
- Entende bushels/acre, acres e °F.
- **Não há produtividade do condado nos EUA** (USDA NASS não está integrado), então não compara a produtividade.
- Pode confirmar o calor (dias acima de 95°F no ano, POWER).

**Resposta esperada:**
> "I can't benchmark your 180 bu/ac — I don't have U.S. county yields (that's USDA NASS, which I don't use). What I can confirm: this summer your area had 9 days above 95°F (35°C), versus about 4 in a typical year (NASA POWER), so it was a hot season for corn. Your local Extension office can compare your yield with the county average. Check with your agronomist or county Extension office."

**Critérios de aceite:** entende as unidades (R8) · admite a falta de produtividade do condado (R3) · cita o NASS como fonte que não usa, sem fingir que usa.

---

### Teste 17 — Coordenada errada

**Cenário:** O talhão foi salvo com a longitude positiva por engano (42,0; 93,6) → ponto na China, não em Iowa.

**Mensagem:**
> "Why does the app say my soil is like that? It doesn't match Iowa at all."

**O que o sistema faz:**
- Valida: o país do ponto (calculado na q5) não bate com o que o produtor diz.

**Resposta esperada:**
> "It looks like your field location was saved wrong — the point is in China, not Iowa (the longitude sign is flipped). Could you open the map and mark your field again? Then I'll redo the analysis."

**Critérios de aceite:** detecta a inconsistência · pede correção · não mostra análise do ponto errado.

---

### Teste 18 — Mapa SSURGO e análise de solo

**Cenário:** Centro de Iowa. Produtor tem laudo recente (perfil C).

**Mensagem:**
> "Can you use my SSURGO soil map and my soil test from last year instead of your global map?"

**O que o sistema faz:**
- **SSURGO não está integrado.**
- O laudo de laboratório sim: os valores do laudo substituem o SoilGrids (peso 0,9 na fusão).

**Resposta esperada:**
> "Your soil test, yes — enter the results and they'll replace the global map values, which makes the analysis much more reliable. The SSURGO map I can't read yet; it's a more detailed U.S. soil map that the app doesn't use. Check with your agronomist or county Extension office."

**Critérios de aceite:** distingue o que usa (laudo) do que não usa (SSURGO) · não finge que lê o SSURGO.

---

### Teste 19 — Os números servem para o meu talhão?

**Cenário:** Centro do Nebraska, talhão de 80 acres (~ 32 ha).

**Mensagem:**
> "Your weather data is a 30-mile pixel. Is that even useful for my 80 acres?"

**O que o sistema faz:**
- Explica a escala de cada fonte e o nível de confiança.

**Resposta esperada:**
> "Fair question. The weather data (NASA POWER) is about 30 by 40 miles, so it describes your region, not your field — it can miss a frost pocket or a local storm. Rain from GPM IMERG is finer (~6 miles), the satellite greenness is 250 m (~15 acres per pixel), and terrain is 30 m. That's why I show a confidence level for each number and give more weight to what you observe on the ground. Check with your agronomist or county Extension office."

**Critérios de aceite:** dá a escala de cada fonte (R2) · explica a confiança · valoriza a observação do produtor.

---

### Teste 20 — Resumo para o dono da terra

**Cenário:** Centro do Kansas, trigo → sorgo em segunda safra.

**Mensagem:**
> "Write me a short summary I can send to my landowner."

**O que o sistema faz:**
- Monta o resumo da rotação atual e das duas alternativas, com fontes, em inglês e em unidades americanas.

**Resposta esperada:**
> "**Field summary — central Kansas, 320 acres.**
> Current: winter wheat, then summer fallow.
> Option A: wheat → double-crop sorghum. Covers the soil in summer; tight on frost-free days and July rain.
> Option B: wheat → cover crop. Protects the soil, lower water risk, no extra grain income.
> Sources: NASA POWER (weather, 1991–2025), SoilGrids (soil), NASA SRTM (slope), NASA MODIS/VIIRS (greenness).
> Not included: prices, county yields, groundwater.
> This tool supports the decision; the farmer decides."

**Critérios de aceite:** lista fontes e o que ficou de fora · unidades americanas (R8) · não dá certeza.

---

## 5. Matriz de cobertura

### 5.1 Fontes acionadas por teste

| # | POWER | IMERG | SMAP | NDVI MODIS/VIIRS | SRTM | SoilGrids | Base de culturas | RAG | Fonte que falta (deve ser admitida) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ✅ | | | | | | ✅ (centeio fora) | | |
| 2 | ✅ | | | | | | ✅ | | |
| 3 | ✅ | | | | | | ✅ | | Preço, NASS |
| 4 | ✅ | ✅ | | | | ✅ | ✅ | | |
| 5 | ✅ | | | | | | ✅ | | |
| 6 | ✅ | | | | | | ✅ (amêndoa fora) | | Água subterrânea |
| 7 | | | | | | ✅ | ✅ (amendoim fora) | ✅ | |
| 8 | ✅ | | | | | | ✅ (Kc) | | |
| 9 | | | | ✅ (neve) | | | | ✅ | |
| 10 | ✅ | ✅ | | | ✅ | | | | |
| 11 | ✅ | | | | | | ✅ | | |
| 12 | | | | | | | | ✅ | |
| 13 | | | | | | | | | Preço, PAM só Brasil |
| 14 | ✅ | | | | | | | | Previsão (NWS) |
| 15 | ✅ | | | | | | | | Previsão / projeção |
| 16 | ✅ | | | | | | | | NASS |
| 17 | (validação) | | | | | | | | |
| 18 | | | | | | ✅ (laudo substitui) | | | SSURGO |
| 19 | ✅ | ✅ | | ✅ | ✅ | | | | |
| 20 | ✅ | | | ✅ | ✅ | ✅ | ✅ | | Preço, NASS, água subterrânea |

> SMAP L4 não aparece de forma explícita; ele pode reforçar os testes 3 e 8 (solo seco) quando estiver no pipeline.

### 5.2 Climas e regiões

| Clima (Köppen aproximado) | Testes |
|---|---|
| Continental úmido (Dfa) — Corn Belt | 1, 9, 10, 12, 15, 16, 18 |
| Continental/subtropical de transição (Dfa/Cfa) — Planícies | 2, 11, 14, 20 |
| Continental úmido/semiárido (Dfa/BSk) — Nebraska | 8, 19 |
| Semiárido (BSk) | 3 |
| Subtropical úmido (Cfa) — Sul | 4, 7 |
| Continental frio (Dfb) | 5 |
| Mediterrâneo/semiárido quente (Csa/BSh) | 6 |
| Entrada inválida | 17 |

### 5.3 Tipos de resultado

| Tipo | Testes | Total |
|---|---|---|
| ✅ Resolve | 2, 4, 5, 8, 9, 10, 11, 19, 20 | 9 |
| 🟡 Resolve em parte | 1, 3, 6, 7, 13, 16, 18 | 7 |
| ❓ Pede informação | 17 | 1 |
| 🚫 Recusa e encaminha | 12, 14, 15 | 3 |

### 5.4 Regras exercitadas

| Regra | Testes que mais exigem |
|---|---|
| R1 não inventar | 1, 6, 7, 13, 15, 16 |
| R2 fonte e escala | 5, 8, 10, 19 |
| R3 dizer que não encontrou | 1, 3, 6, 7, 13, 16, 18 |
| R4 sem defensivo | 8, 12 |
| R6 sem certeza | 2, 5, 11, 15 |
| R7 lembrete final | Todos, exceto 17 |
| R8 unidades do usuário | 3, 8, 14, 15, 16, 20 |

### 5.5 Diferenças em relação ao Sr. José

| Ponto | Sr. José (Brasil) | Sr. Smith (EUA) |
|---|---|---|
| Mercado e produtividade local | IBGE PAM | ❌ Não há (NASS não integrado): testes 3, 13, 16 |
| Janela de plantio | ZARC | Estimativa pela chuva e temperatura do POWER: testes 2, 5 |
| Unidades | ha, °C, mm, sacas | acres, °F, inches, bushels (R8) |
| Inverno | Sem neve (exceto serra) | Neve e solo congelado confundem o NDVI: teste 9 |
| Culturas típicas fora da base | Café, uva, gergelim | Centeio, amêndoa, amendoim |
| Fontes locais que existem e o app não usa | — | NASS, CDL, SSURGO, PRISM, NWS, Drought Monitor, RMA |

---

## 6. Como registrar o resultado

| # | Data | Resposta obtida (resumo) | Fonte certa? | Regras OK? | Reconheceu limite? | Resultado | Observação |
|---|---|---|---|---|---|---|---|
| 1 | | | ☐ | ☐ | ☐ | ☐ passou ☐ falhou | |
| 2 | | | ☐ | ☐ | ☐ | ☐ passou ☐ falhou | |
| … | | | | | | | |
| 20 | | | ☐ | ☐ | ☐ | ☐ passou ☐ falhou | |

**Critério geral para passar:** fonte correta + todas as regras aplicáveis + limite reconhecido quando o teste é do tipo 🟡, ❓ ou 🚫.

**Falhas mais importantes a vigiar:**
1. Usar ou citar a PAM ou o ZARC para um talhão nos EUA.
2. Fingir que usa NASS, SSURGO ou previsão do NWS (testes 13, 14, 16, 18).
3. Número inventado para cultura fora da base (testes 1, 6, 7).
4. Nome de produto ou dose de herbicida (teste 12).
5. Previsão de temperatura ou de geada apresentada como certa (testes 14, 15).
6. Responder em unidades métricas sem converter para o usuário americano (R8).
7. Chamar de "solo descoberto" o campo coberto de neve ou palhada (teste 9).
