# Perguntas do onboarding: antes e depois

> Revisão de 14/11/2026, para o escopo **global** do Field Shift. Arquivo de referência: `data/onboarding/perguntas.yaml`.
>
> - **Antes:** versão alinhada com o app (`agroia/api/app/onboarding/schemas.py` e `agroia/web/src/onboarding/Passos.tsx`).
> - **Depois:** versão atual do `perguntas.yaml` (gerada a partir do próprio arquivo).
> - Idiomas: português (🇧🇷) e inglês (🇬🇧).
> - As perguntas sobre **culturas** (q8 e q26a) estão **em espera** até a Pessoa 1 terminar a nova base de culturas.

## Resumo das mudanças

### ❌ Saíram
| Pergunta | Por quê | Foi para |
|---|---|---|
| `q21_calcario` (“Já usou calcário?”) | Só servia para solo ácido tropical | `q21_correcao` |
| `q24_perdas.geada.ano`, `.chuva_forte.ano`, `.calor.ano`, `.seca.ano` | Com 7 perdas seriam 7 cópias da mesma pergunta | Uma só pergunta de ano, depois de qualquer “sim” |

### 🆕 Entraram
| Pergunta | Quando aparece |
|---|---|
| `q24_perdas.alagamento`: perda por alagamento ou encharcamento | Sempre |
| `q24_perdas.granizo`: perda por granizo | Sempre |
| `q24_perdas.salinidade`: perda porque a terra ficou salgada | Só em clima seco (zona B) ou com irrigação |

### 🔄 Mudou o funcionamento
| Pergunta | Antes | Depois |
|---|---|---|
| `q21` | `q21_calcario`, sim/não/não sei | `q21_correcao`, múltipla escolha: calcário · gesso · outra · não · não sei |
| `q2_area` | Rótulos só em hectare | Hectare ou acre conforme o país |
| `q5_local` | Toque no mapa ou GPS | + barra de pesquisa; calcula país, zona climática e hemisfério |
| `q24_perdas.geada` | Aparecia sempre | Some em clima tropical ou árido quente |
| `q8_texto` ⏸️ | Exemplo fixo do Brasil | Exemplo por zona climática |

### ✏️ Só texto
Todas as outras perguntas mudaram **só o texto**, para soar mais natural e servir fora do Brasil. Os ids e valores continuam os mesmos do app.

### ⚠️ O que o código precisa acompanhar
1. `q21_calcario` → `q21_correcao` (vira lista) em `schemas.py`, `perfil.py` e `Passos.tsx`.
2. `Perdas` ganha `alagamento`, `granizo` e `salinidade`.
3. `Local` ganha `pais`, `zona_climatica` e `hemisferio`.

---

## Antes

### Bloco 1: Quem é você

**`q1_quem`**  
- 🇧🇷 Quem está respondendo?  
- 🇬🇧 Who is answering?  
- Opções (pt): Sou o produtor · Sou técnico ou ajudo um produtor  
- Options (en): I am the farmer · I am a technician or help a farmer  

**`q2_area`**  
- 🇧🇷 Tamanho aproximado da área  
- 🇬🇧 Approximate size of the area  
- Opções (pt): Até 2 ha · 2 a 20 ha · 20 a 200 ha · 200 a 1.000 ha · Mais de 1.000 ha  
- Options (en): Up to 2 ha · 2 to 20 ha · 20 to 200 ha · 200 to 1,000 ha · More than 1,000 ha  

**`q3_tecnico`**  
- 🇧🇷 Você recebe visita de técnico agrícola?  
- 🇬🇧 Do you get visits from an agricultural technician?  
- Opções (pt): Sim · Às vezes · Não  
- Options (en): Yes · Sometimes · No  

**`q4_animais`**  
- 🇧🇷 Tem criação de animais?  
- 🇬🇧 Do you raise animals?  
- Opções (pt): Sim · Não  
- Options (en): Yes · No  


### Bloco 2: O campo

**`q5_local`**  
- 🇧🇷 Onde fica o seu campo?  
- 🇬🇧 Where is your field?  
- *Toque no mapa ou GPS. Guarda lat, lon e nome do lugar.*  

**`q6_irrigacao`**  
- 🇧🇷 Tem irrigação?  
- 🇬🇧 Do you have irrigation?  
- Opções (pt): Sim · Só em parte · Não  
- Options (en): Yes · Only partly · No  

**`q7_terreno`**  
- 🇧🇷 Como é o terreno?  
- 🇬🇧 What is the terrain like?  
- Opções (pt): Plano · Levemente inclinado · Bem inclinado  
- Options (en): Flat · Gently sloping · Steep  


### Bloco 3: O que você planta

**`q8_texto`**  
- 🇧🇷 Conte do seu jeito o que você planta, e quando.  
- 🇬🇧 Tell us in your own words what you plant, and when.  
- *Exemplo fixo: “planto milho e feijão juntos na época das águas, depois mandioca, e tem um pedaço de capim pras vacas”*  

**`q8_culturas (cartão por cultura)`**  
- 🇧🇷 Você planta {cultura}? · Ocupa o campo o ano todo (perene) · De que mês a que mês? · É plantado junto com {outra_cultura}? · Ocupa o campo todo ou uma parte?  
- 🇬🇧 Do you grow {cultura}? · Takes up the field all year (perennial) · From which month to which month? · Is it planted together with {outra_cultura}? · Does it take up the whole field or part of it?  

**`q9_meses_vazios`**  
- 🇧🇷 Nesses meses o campo fica sem nada?  
- 🇬🇧 Is the field left bare in these months?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q10_pos_colheita`**  
- 🇧🇷 Depois da colheita, o que acontece com o campo?  
- 🇬🇧 What happens to the field after harvest?  
- Opções (pt): Fica parado · Vira pasto · Planto outra coisa · Planto algo pra cobrir o solo  
- Options (en): It is left idle · It becomes pasture · I plant something else · I plant a cover crop  

**`q11_palha`**  
- 🇧🇷 Deixa a palha ou o resto da cultura no campo?  
- 🇬🇧 Do you leave the straw or crop residue on the field?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  


### Bloco 4: O que você sabe do seu solo

**`q12_analise`**  
- 🇧🇷 Já fez análise de solo em laboratório?  
- 🇬🇧 Have you ever had a laboratory soil test?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q12_tem_resultado`**  
- 🇧🇷 Tem o resultado em mãos?  
- 🇬🇧 Do you have the results at hand?  
- *Só se q12 = sim*  

**`q12_ano`**  
- 🇧🇷 De que ano?  
- 🇬🇧 From which year?  
- *Só se q12 = sim*  

**`q13_textura`**  
- 🇧🇷 A terra é mais arenosa, argilosa ou meio-termo?  
- 🇬🇧 Is the soil more sandy, clayey, or in between?  
- Opções (pt): Mais arenosa · Meio-termo · Mais argilosa · Não sei  
- Options (en): Mostly sandy · In between · Mostly clayey · I don't know  

**`q14_encharca`**  
- 🇧🇷 Depois de chuva forte, a água fica empoçada mais de um dia?  
- 🇬🇧 After heavy rain, does water stay pooled for more than a day?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q15_casca`**  
- 🇧🇷 Quando seca, a terra forma uma casca na superfície?  
- 🇬🇧 When it dries, does the soil form a crust on the surface?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q16_erosao`**  
- 🇧🇷 Já viu a chuva levando terra (valetas, água barrenta saindo do campo)?  
- 🇬🇧 Have you seen rain washing soil away (gullies, muddy water leaving the field)?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q17_dura`**  
- 🇧🇷 A terra fica muito dura pra cavar ou arar?  
- 🇬🇧 Is the soil very hard to dig or plough?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q18_minhocas`**  
- 🇧🇷 Encontra minhocas quando cava?  
- 🇬🇧 Do you find earthworms when you dig?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q19_cor`**  
- 🇧🇷 Com qual cor a sua terra mais se parece?  
- 🇬🇧 Which colour does your soil look most like?  
- Opções (pt): Preta ou marrom bem escura · Marrom · Vermelha · Amarelada · Cinza ou com manchas cinza · Clara ou esbranquiçada · Não sei  
- Options (en): Black or very dark brown · Brown · Red · Yellowish · Grey or grey-mottled · Pale or whitish · I don't know  

**`q19_jeito`**  
- 🇧🇷 E na mão, ela parece mais com qual?  
- 🇬🇧 And in your hand, which one does it look most like?  
- Opções (pt): Solta, escorre entre os dedos · Fofa, em grumos pequenos · Gruda e molda quando molhada · Torrões duros que não se desfazem · Racha quando seca · Muita pedra ou cascalho · Não sei  
- Options (en): Loose, runs through the fingers · Crumbly, in small clumps · Sticky and mouldable when wet · Hard clods that don't break apart · Cracks when dry · Lots of stones or gravel · I don't know  

**`q20_partes_piores`**  
- 🇧🇷 Tem partes do campo onde a lavoura sempre vai pior?  
- 🇬🇧 Are there parts of the field where the crop always does worse?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q21_calcario`**  
- 🇧🇷 Já usou calcário?  
- 🇬🇧 Have you ever used lime?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q22_adubo`**  
- 🇧🇷 Usa adubo ou esterco?  
- 🇬🇧 Do you use fertiliser or manure?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  


### Bloco 5: O que você tem sentido no clima

**`q23_chuva_mudou`**  
- 🇧🇷 Sente que a chuva mudou nos últimos anos?  
- 🇬🇧 Do you feel the rain has changed in recent years?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q24_perdas.geada`**  
- 🇧🇷 Já perdeu safra por geada?  
- 🇬🇧 Have you ever lost a harvest to frost?  
- *Se sim: “Lembra mais ou menos o ano?” / “Do you roughly remember the year?”*  

**`q24_perdas.chuva_forte`**  
- 🇧🇷 Já perdeu safra por chuva forte?  
- 🇬🇧 Have you ever lost a harvest to heavy rain?  
- *Se sim: pergunta do ano*  

**`q24_perdas.calor`**  
- 🇧🇷 Já perdeu safra por calor intenso?  
- 🇬🇧 Have you ever lost a harvest to extreme heat?  
- *Se sim: pergunta do ano*  

**`q24_perdas.seca`**  
- 🇧🇷 Já perdeu safra por falta de chuva?  
- 🇬🇧 Have you ever lost a harvest to lack of rain?  
- *Se sim: pergunta do ano*  


### Bloco 6: O que é importante pra você

**`q25_prioridades`**  
- 🇧🇷 O que é mais importante pra você? Escolha até 3.  
- 🇬🇧 What matters most to you? Choose up to 3.  
- Opções (pt): Economizar água · Melhorar a terra · Evitar erosão · Renda extra · Comida pros animais · Menos praga  
- Options (en): Save water · Improve the soil · Prevent erosion · Extra income · Feed for the animals · Fewer pests  

**`q26a_texto`**  
- 🇧🇷 Tem alguma cultura que você não plantaria? Por quê?  
- 🇬🇧 Is there any crop you would not grow? Why?  
- *Exemplo: “não planto soja, não tenho onde vender”. Motivos: Mercado · Costume · Já deu errado · Outro*  

**`q26b_texto`**  
- 🇧🇷 Que máquinas e equipamentos você tem ou consegue usar?  
- 🇬🇧 Which machines and equipment do you have or can use?  
- *Exemplo: “tenho trator pequeno e plantadeira, colheita é na mão”*  

---

## Depois

Legenda: 🆕 pergunta nova · 🔄 pergunta reformulada · ⏸️ em espera

### Bloco 1: Quem é você

**`q1_quem`**  
- 🇧🇷 Quem está respondendo?  
- 🇬🇧 Who's filling this in?  
- Opções (pt): Eu sou o produtor · Sou técnico ou estou ajudando um produtor  
- Options (en): I'm the farmer · I'm an extension agent, or I'm helping a farmer  

**`q2_area`**  
- 🇧🇷 Mais ou menos, qual o tamanho da sua área?  
- 🇬🇧 Roughly how big is your farm?  
- Opções (pt): Até 2 ha · De 2 a 20 ha · De 20 a 200 ha · De 200 a 1.000 ha · Mais de 1.000 ha  
- Options (en): Up to 2 ha · 2 to 20 ha · 20 to 200 ha · 200 to 1,000 ha · More than 1,000 ha  
- Em países que usam **acre** (EUA, Reino Unido, Índia, Paquistão, Bangladesh, Mianmar, Libéria): Até 5 acres · De 5 a 50 acres · De 50 a 500 acres · De 500 a 2.500 acres · Mais de 2.500 acres. Botão para trocar ha / acre.  

**`q3_tecnico`**  
- 🇧🇷 Algum técnico agrícola ou agrônomo costuma visitar a sua propriedade?  
- 🇬🇧 Does an extension agent or agronomist ever visit your farm?  
- Opções (pt): Sim · Às vezes · Não  
- Options (en): Yes · Sometimes · No  

**`q4_animais`**  
- 🇧🇷 Você cria animais?  
- 🇬🇧 Do you keep any livestock?  
- Opções (pt): Sim · Não  
- Options (en): Yes · No  


### Bloco 2: O campo

**`q5_local`**  
- 🇧🇷 Onde fica a sua propriedade?  
- 🇬🇧 Where is your farm?  
- *Barra de pesquisa por nome (ex.: “Ex.: Sorriso, Mato Grosso” / “E.g.: Nakuru, Kenya”), toque no mapa ou GPS.*  
- *Guarda lat, lon e nome e **calcula país, zona climática (Köppen) e hemisfério**.*  
- *Ajuda: “Procure o nome da cidade ou da região, ou toque no mapa. É com esse ponto que buscamos os dados da NASA.” / “Search for your town or area, or tap the map. We use that spot to pull NASA data.”*  

**`q6_irrigacao`**  
- 🇧🇷 Você irriga a lavoura?  
- 🇬🇧 Do you irrigate?  
- Opções (pt): Sim · Só uma parte · Não  
- Options (en): Yes · Only part of the farm · No  

**`q7_terreno`**  
- 🇧🇷 Como é o terreno?  
- 🇬🇧 Is your land flat or sloping?  
- Opções (pt): Plano · Um pouco inclinado · Bem inclinado (morro)  
- Options (en): Flat · Gentle slope · Steep (hillside)  


### Bloco 3: O que você planta

**`q8_texto`** ⏸️  
- 🇧🇷 Conte do seu jeito o que você planta, e quando.  
- 🇬🇧 Tell us in your own words what you plant, and when.  
- *Exemplo **muda conforme a zona climática** do local:*  
- &nbsp;&nbsp;`Af_Am`: “planto mandioca e milho juntos e tenho um pedaço de capim para o gado”  
- &nbsp;&nbsp;`Aw_As`: “planto milho e feijão juntos na estação chuvosa e, depois da colheita, o campo fica parado na seca”  
- &nbsp;&nbsp;`B`: “planto sorgo e feijão-caupi quando chegam as chuvas; o resto do ano o campo fica parado”  
- &nbsp;&nbsp;`C`: “planto soja no verão e trigo no inverno”  
- &nbsp;&nbsp;`D`: “planto trigo na primavera e colho no fim do verão; no inverno o campo fica parado”  
- &nbsp;&nbsp;`padrao`: “planto milho na estação das chuvas e, depois da colheita, deixo o campo parado”  

**`q8_culturas (cartão por cultura)`** ⏸️  
- 🇧🇷 Você planta {cultura}? · Ocupa o campo o ano todo (perene) · De que mês a que mês? · É plantado junto com {outra_cultura}? · Ocupa o campo todo ou uma parte?  
- 🇬🇧 Do you grow {cultura}? · Takes up the field all year (perennial) · From which month to which month? · Is it planted together with {outra_cultura}? · Does it take up the whole field or part of it?  
- *Sem mudança.*  

**`q9_meses_vazios`**  
- 🇧🇷 Nesses meses a terra fica sem nada plantado?  
- 🇬🇧 Is the land left bare in these months?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q10_pos_colheita`**  
- 🇧🇷 E depois da colheita, o que acontece com a área?  
- 🇬🇧 What happens to the field after harvest?  
- Opções (pt): Fica parada · Vira pasto · Planto outra coisa · Planto algo para cobrir a terra  
- Options (en): It's left fallow · It's grazed · I plant another crop · I sow a cover crop  

**`q11_palha`**  
- 🇧🇷 Você deixa a palha e os restos da colheita no campo?  
- 🇬🇧 Do you leave the stubble and crop residue on the field?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  


### Bloco 4: O que você sabe do seu solo

**`q12_analise`**  
- 🇧🇷 Você já fez análise de solo em laboratório?  
- 🇬🇧 Have you ever had your soil tested in a lab?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q12_tem_resultado`**  
- 🇧🇷 Ainda tem o resultado?  
- 🇬🇧 Do you still have the results?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Só se q12 = sim*  

**`q12_ano`**  
- 🇧🇷 De que ano é?  
- 🇬🇧 What year was it?  
- *Só se q12 = sim*  

**`q13_textura`**  
- 🇧🇷 A sua terra é mais arenosa, mais argilosa ou meio-termo?  
- 🇬🇧 Is your soil sandy, clay, or somewhere in between?  
- Opções (pt): Mais arenosa · Meio-termo · Mais argilosa (barro) · Não sei  
- Options (en): Sandy · In between (loam) · Clay · Not sure  

**`q14_encharca`**  
- 🇧🇷 Depois de uma chuva forte, a água fica empoçada por mais de um dia?  
- 🇬🇧 After a heavy rain, does water sit on the field for more than a day?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q15_casca`**  
- 🇧🇷 Quando a terra seca, forma uma casca dura por cima?  
- 🇬🇧 When the soil dries out, does it form a hard crust on top?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q16_erosao`**  
- 🇧🇷 Já viu a chuva levar terra embora (valetas, água barrenta saindo do campo)?  
- 🇬🇧 Have you seen the rain wash soil away — gullies, or muddy water running off the field?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q17_dura`**  
- 🇧🇷 A terra fica dura demais para cavar ou arar?  
- 🇬🇧 Is the soil too hard to dig or plow?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q18_minhocas`**  
- 🇧🇷 Quando você cava, encontra minhocas?  
- 🇬🇧 When you dig, do you find earthworms?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q19_cor`**  
- 🇧🇷 Com qual destas cores a sua terra mais se parece?  
- 🇬🇧 Which of these colors looks most like your soil?  
- Opções (pt): Preta ou marrom bem escura · Marrom · Vermelha · Amarelada · Cinza ou com manchas cinza · Clara ou esbranquiçada · Não sei  
- Options (en): Black or very dark brown · Brown · Red · Yellowish · Gray, or gray-mottled · Pale or whitish · Not sure  

**`q19_jeito`**  
- 🇧🇷 E quando você pega um punhado na mão, ela fica mais como qual destas?  
- 🇬🇧 And when you pick up a handful, which does it feel most like?  
- Opções (pt): Solta, escorre entre os dedos · Fofa, em grumos pequenos · Gruda e dá para moldar molhada · Torrões duros que não se desfazem · Racha quando seca · Muita pedra ou cascalho · Não sei  
- Options (en): Loose — runs through your fingers · Crumbly, in small lumps · Sticky — you can mold it when wet · Hard clods that won't break up · Cracks open when dry · Lots of stones or gravel · Not sure  

**`q20_partes_piores`**  
- 🇧🇷 Tem partes da área onde a lavoura sempre vai pior?  
- 🇬🇧 Are there patches where the crop always does worse?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q21_correcao`** 🔄 (antes `q21_calcario`)  
- 🇧🇷 Você já fez alguma correção na terra?  
- 🇬🇧 Have you ever treated your soil to correct it?  
- Opções (pt): Calcário (para terra ácida) · Gesso agrícola (para terra com sal) · Outra correção · Não · Não sei  
- Options (en): Lime (for acid soil) · Gypsum (for salty soil) · Something else · No · Not sure  
- *Pode marcar mais de uma. Em clima seco (zona B) ou com irrigação, o **gesso aparece primeiro**.*  

**`q22_adubo`**  
- 🇧🇷 Você usa adubo ou esterco?  
- 🇬🇧 Do you use fertilizer or manure?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  


### Bloco 5: O que você tem sentido no clima

**`q23_chuva_mudou`**  
- 🇧🇷 Você sente que a chuva mudou nos últimos anos?  
- 🇬🇧 Do you feel the rains have changed over the last few years?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  

**`q24_perdas.geada`**  
- 🇧🇷 Já perdeu a colheita por geada?  
- 🇬🇧 Have you ever lost a crop to frost?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- ***Não aparece** em clima tropical ou árido quente (Af, Am, Aw, As, BWh, BSh).*  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.chuva_forte`**  
- 🇧🇷 Já perdeu a colheita por chuva forte ou temporal?  
- 🇬🇧 Have you ever lost a crop to heavy rain or storms?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.alagamento`** 🆕  
- 🇧🇷 Já perdeu a colheita porque a área alagou ou ficou encharcada?  
- 🇬🇧 Have you ever lost a crop to flooding or waterlogging?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.granizo`** 🆕  
- 🇧🇷 Já perdeu a colheita por chuva de granizo (pedra)?  
- 🇬🇧 Have you ever lost a crop to hail?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.calor`**  
- 🇧🇷 Já perdeu a colheita por calor forte?  
- 🇬🇧 Have you ever lost a crop to extreme heat?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.seca`**  
- 🇧🇷 Já perdeu a colheita por seca ou falta de chuva?  
- 🇬🇧 Have you ever lost a crop to drought?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  

**`q24_perdas.salinidade`** 🆕  
- 🇧🇷 Já perdeu a colheita porque a terra ficou salgada (manchas brancas, planta queimando)?  
- 🇬🇧 Have you ever lost a crop because the soil turned salty (white crust, scorched plants)?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / Not sure  
- ***Só aparece** em clima seco (zona B) ou com irrigação.*  
- *Se sim: “Lembra mais ou menos o ano?” / “Roughly what year was it?”*  


### Bloco 6: O que é importante pra você

**`q25_prioridades`**  
- 🇧🇷 O que é mais importante para você? Escolha até 3.  
- 🇬🇧 What matters most to you? Pick up to 3.  
- Opções (pt): Economizar água · Melhorar a terra · Evitar erosão · Ganhar uma renda extra · Comida para os animais · Menos praga  
- Options (en): Save water · Build up the soil · Stop erosion · Extra income · Feed for my animals · Fewer pests  

**`q26a_texto`** ⏸️  
- 🇧🇷 Tem alguma cultura que você não plantaria? Por quê?  
- 🇬🇧 Is there any crop you would not grow? Why?  
- *Exemplo: “não planto soja, não tenho onde vender”. Motivos: Mercado · Costume · Já deu errado · Outro*  

**`q26b_texto`**  
- 🇧🇷 Que máquinas e ferramentas você tem ou consegue usar?  
- 🇬🇧 What machinery or equipment do you have or can get access to?  
- *Exemplo: “tenho um trator pequeno e uma plantadeira; a colheita é na mão” / “I have a small tractor and a planter; we harvest by hand”*  
