# Perguntas do onboarding: antes e depois

> Arquivo de referência: `data/onboarding/perguntas.yaml`. Idiomas: português (🇧🇷) e inglês americano (🇺🇸).
>
> - **Antes:** versão alinhada com o app antes da revisão para escopo global (ids do `schemas/onboarding.py`).
> - **Depois:** versão atual do `perguntas.yaml`, gerada a partir do próprio arquivo: 23 perguntas em 6 partes, como na versão revisada pelo time em 14/11/2026, com as correções do relatório.
> - **O que foi corrigido e por quê:** `data/onboarding/relatorio-revisao-questionario.md`.
> - As perguntas sobre **culturas** (8 e 22) estão **em espera** até a nova base de culturas.

## Resumo das mudanças

| Antes | Depois |
|---|---|
| 26 perguntas soltas em 6 blocos | 23 perguntas numeradas em 6 partes; algumas perguntas do app ficam juntas numa tela |
| 5 perguntas separadas sobre sinais do solo (14 a 18) | Uma tela (pergunta 14) em **grade**: uma linha por sinal, com Sim / Não / Não sei |
| Cor e jeito da terra em duas perguntas | Uma tela (pergunta 15), em dois grupos |
| “Já usou calcário?” (sim/não) | “Você já fez alguma correção no solo?”: calcário · gesso · outra (com campo de texto) · nunca fiz · não sei |
| 4 perguntas de perda (geada, chuva forte, calor, seca), cada uma com o seu “lembra o ano?” | Uma tela de múltipla escolha com 7 eventos (+ alagamento, granizo, salinidade) e **um ano ao lado de cada evento marcado** |
| Geada e salinidade sempre visíveis | Aparecem conforme o local (ver relatório, item 1) |
| Área só em hectares | Hectare ou acre conforme o país |
| Local: toque no mapa ou GPS | + barra de pesquisa; o app calcula país, zona climática e hemisfério |
| “Tem o resultado em mãos?” → perfil C | + **valores do laudo**; o perfil C precisa de pelo menos 2 valores |
| Pergunta 1 “técnico” → perfil D | Pergunta 1 define o papel (produtor ou técnico); o perfil vai de A a C |
| — | Resumo final: perfil, calendário anual, retrato do solo, até 3 próximos passos, botão “Ver minha fazenda” |

---

## Antes

### Bloco 1: Quem é você

**`q1_quem`**  
- 🇧🇷 Quem está respondendo?  
- 🇺🇸 Who is answering?  
- Opções (pt): Sou o produtor · Sou técnico ou ajudo um produtor  
- Options (en): I am the farmer · I am a technician or help a farmer  

**`q2_area`**  
- 🇧🇷 Tamanho aproximado da área  
- 🇺🇸 Approximate size of the area  
- Opções (pt): Até 2 ha · 2 a 20 ha · 20 a 200 ha · 200 a 1.000 ha · Mais de 1.000 ha  
- Options (en): Up to 2 ha · 2 to 20 ha · 20 to 200 ha · 200 to 1,000 ha · More than 1,000 ha  

**`q3_tecnico`**  
- 🇧🇷 Você recebe visita de técnico agrícola?  
- 🇺🇸 Do you get visits from an agricultural technician?  
- Opções (pt): Sim · Às vezes · Não  
- Options (en): Yes · Sometimes · No  

**`q4_animais`**  
- 🇧🇷 Tem criação de animais?  
- 🇺🇸 Do you raise animals?  
- Opções (pt): Sim · Não  
- Options (en): Yes · No  


### Bloco 2: O campo

**`q5_local`**  
- 🇧🇷 Onde fica o seu campo?  
- 🇺🇸 Where is your field?  
- *Toque no mapa ou GPS. Guarda lat, lon e nome do lugar.*  

**`q6_irrigacao`**  
- 🇧🇷 Tem irrigação?  
- 🇺🇸 Do you have irrigation?  
- Opções (pt): Sim · Só em parte · Não  
- Options (en): Yes · Only partly · No  

**`q7_terreno`**  
- 🇧🇷 Como é o terreno?  
- 🇺🇸 What is the terrain like?  
- Opções (pt): Plano · Levemente inclinado · Bem inclinado  
- Options (en): Flat · Gently sloping · Steep  


### Bloco 3: O que você planta

**`q8_texto`**  
- 🇧🇷 Conte do seu jeito o que você planta, e quando.  
- 🇺🇸 Tell us in your own words what you plant, and when.  
- *Exemplo fixo: “planto milho e feijão juntos na época das águas, depois mandioca, e tem um pedaço de capim pras vacas”*  

**`q8_culturas (cartão por cultura)`**  
- 🇧🇷 Você planta {cultura}? · Ocupa o campo o ano todo (perene) · De que mês a que mês? · É plantado junto com {outra_cultura}? · Ocupa o campo todo ou uma parte?  
- 🇺🇸 Do you grow {cultura}? · Takes up the field all year (perennial) · From which month to which month? · Is it planted together with {outra_cultura}? · Does it take up the whole field or part of it?  

**`q9_meses_vazios`**  
- 🇧🇷 Nesses meses o campo fica sem nada?  
- 🇺🇸 Is the field left bare in these months?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q10_pos_colheita`**  
- 🇧🇷 Depois da colheita, o que acontece com o campo?  
- 🇺🇸 What happens to the field after harvest?  
- Opções (pt): Fica parado · Vira pasto · Planto outra coisa · Planto algo pra cobrir o solo  
- Options (en): It is left idle · It becomes pasture · I plant something else · I plant a cover crop  

**`q11_palha`**  
- 🇧🇷 Deixa a palha ou o resto da cultura no campo?  
- 🇺🇸 Do you leave the straw or crop residue on the field?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  


### Bloco 4: O que você sabe do seu solo

**`q12_analise`**  
- 🇧🇷 Já fez análise de solo em laboratório?  
- 🇺🇸 Have you ever had a laboratory soil test?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q12_tem_resultado`**  
- 🇧🇷 Tem o resultado em mãos?  
- 🇺🇸 Do you have the results at hand?  
- *Só se q12 = sim*  

**`q12_ano`**  
- 🇧🇷 De que ano?  
- 🇺🇸 From which year?  
- *Só se q12 = sim*  

**`q13_textura`**  
- 🇧🇷 A terra é mais arenosa, argilosa ou meio-termo?  
- 🇺🇸 Is the soil more sandy, clayey, or in between?  
- Opções (pt): Mais arenosa · Meio-termo · Mais argilosa · Não sei  
- Options (en): Mostly sandy · In between · Mostly clayey · I don't know  

**`q14_encharca`**  
- 🇧🇷 Depois de chuva forte, a água fica empoçada mais de um dia?  
- 🇺🇸 After heavy rain, does water stay pooled for more than a day?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q15_casca`**  
- 🇧🇷 Quando seca, a terra forma uma casca na superfície?  
- 🇺🇸 When it dries, does the soil form a crust on the surface?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q16_erosao`**  
- 🇧🇷 Já viu a chuva levando terra (valetas, água barrenta saindo do campo)?  
- 🇺🇸 Have you seen rain washing soil away (gullies, muddy water leaving the field)?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q17_dura`**  
- 🇧🇷 A terra fica muito dura pra cavar ou arar?  
- 🇺🇸 Is the soil very hard to dig or plough?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q18_minhocas`**  
- 🇧🇷 Encontra minhocas quando cava?  
- 🇺🇸 Do you find earthworms when you dig?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q19_cor`**  
- 🇧🇷 Com qual cor a sua terra mais se parece?  
- 🇺🇸 Which colour does your soil look most like?  
- Opções (pt): Preta ou marrom bem escura · Marrom · Vermelha · Amarelada · Cinza ou com manchas cinza · Clara ou esbranquiçada · Não sei  
- Options (en): Black or very dark brown · Brown · Red · Yellowish · Grey or grey-mottled · Pale or whitish · I don't know  

**`q19_jeito`**  
- 🇧🇷 E na mão, ela parece mais com qual?  
- 🇺🇸 And in your hand, which one does it look most like?  
- Opções (pt): Solta, escorre entre os dedos · Fofa, em grumos pequenos · Gruda e molda quando molhada · Torrões duros que não se desfazem · Racha quando seca · Muita pedra ou cascalho · Não sei  
- Options (en): Loose, runs through the fingers · Crumbly, in small clumps · Sticky and mouldable when wet · Hard clods that don't break apart · Cracks when dry · Lots of stones or gravel · I don't know  

**`q20_partes_piores`**  
- 🇧🇷 Tem partes do campo onde a lavoura sempre vai pior?  
- 🇺🇸 Are there parts of the field where the crop always does worse?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q21_calcario`**  
- 🇧🇷 Já usou calcário?  
- 🇺🇸 Have you ever used lime?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q22_adubo`**  
- 🇧🇷 Usa adubo ou esterco?  
- 🇺🇸 Do you use fertiliser or manure?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  


### Bloco 5: O que você tem sentido no clima

**`q23_chuva_mudou`**  
- 🇧🇷 Sente que a chuva mudou nos últimos anos?  
- 🇺🇸 Do you feel the rain has changed in recent years?  
- Opções (pt): Sim / Não / Não sei  
- Options (en): Yes / No / I don't know  

**`q24_perdas.geada`**  
- 🇧🇷 Já perdeu safra por geada?  
- 🇺🇸 Have you ever lost a harvest to frost?  
- *Se sim: “Lembra mais ou menos o ano?” / “Do you roughly remember the year?”*  

**`q24_perdas.chuva_forte`**  
- 🇧🇷 Já perdeu safra por chuva forte?  
- 🇺🇸 Have you ever lost a harvest to heavy rain?  
- *Se sim: pergunta do ano*  

**`q24_perdas.calor`**  
- 🇧🇷 Já perdeu safra por calor intenso?  
- 🇺🇸 Have you ever lost a harvest to extreme heat?  
- *Se sim: pergunta do ano*  

**`q24_perdas.seca`**  
- 🇧🇷 Já perdeu safra por falta de chuva?  
- 🇺🇸 Have you ever lost a harvest to lack of rain?  
- *Se sim: pergunta do ano*  


### Bloco 6: O que é importante pra você

**`q25_prioridades`**  
- 🇧🇷 O que é mais importante pra você? Escolha até 3.  
- 🇺🇸 What matters most to you? Choose up to 3.  
- Opções (pt): Economizar água · Melhorar a terra · Evitar erosão · Renda extra · Comida pros animais · Menos praga  
- Options (en): Save water · Improve the soil · Prevent erosion · Extra income · Feed for the animals · Fewer pests  

**`q26a_texto`**  
- 🇧🇷 Tem alguma cultura que você não plantaria? Por quê?  
- 🇺🇸 Is there any crop you would not grow? Why?  
- *Exemplo: “não planto soja, não tenho onde vender”. Motivos: Mercado · Costume · Já deu errado · Outro*  

**`q26b_texto`**  
- 🇧🇷 Que máquinas e equipamentos você tem ou consegue usar?  
- 🇺🇸 Which machines and equipment do you have or can use?  
- *Exemplo: “tenho trator pequeno e plantadeira, colheita é na mão”*  

---

## Depois

### Parte 1 — Quem é você?

**1. Quem está respondendo?**  
🇺🇸 *Who's filling this in?*  
<sub>Campos no app: `q1_quem`</sub>  
- Sou o produtor · Sou técnico ou estou ajudando um produtor  

**2. Qual o tamanho aproximado da sua propriedade?**  
🇺🇸 *Roughly how big is your farm?*  
<sub>Campos no app: `q2_area`</sub>  
- Até 2 ha · De 2 a 20 ha · De 20 a 200 ha · De 200 a 1.000 ha · Mais de 1.000 ha  
- *Em países que usam acre (US, GB, IN, PK, BD, MM, LR): Até 5 acres · De 5 a 50 acres · De 50 a 500 acres · De 500 a 2.500 acres · Mais de 2.500 acres. Botão para trocar ha / acre.*  

**3. Você recebe visitas de técnicos agrícolas ou agrônomos?**  
🇺🇸 *Do extension agents or agronomists visit your farm?*  
<sub>Campos no app: `q3_tecnico`</sub>  
- Sim · Às vezes · Não  

**4. Você cria animais?**  
🇺🇸 *Do you keep any livestock?*  
<sub>Campos no app: `q4_animais`</sub>  
- Sim · Não  


### Parte 2 — Sua propriedade

**5. Onde fica a sua propriedade?**  
🇺🇸 *Where is your farm?*  
<sub>Campos no app: `q5_local`</sub>  
- *Barra de pesquisa, toque no mapa ou GPS. Única pergunta obrigatória.*  
- *O app calcula sozinho o país, a zona climática (Köppen) e o hemisfério.*  

**6. Você irriga sua lavoura?**  
🇺🇸 *Do you irrigate your crops?*  
<sub>Campos no app: `q6_irrigacao`</sub>  
- Sim, toda a propriedade · Somente uma parte · Não  

**7. Como é o terreno?**  
🇺🇸 *Is your land flat or sloping?*  
<sub>Campos no app: `q7_terreno`</sub>  
- Plano · Um pouco inclinado · Bem inclinado (morro)  


### Parte 3 — O que você planta?

**8. Conte do seu jeito o que você planta, e quando.**  
🇺🇸 *Tell us in your own words what you plant, and when.*  
<sub>Campos no app: `q8_texto`, `q8_culturas` (cartões)</sub>  
- Campo de texto livre + botão “Separar com a AgroIA” (ex.: “planto milho na estação das chuvas e, depois da colheita, deixo o campo parado”)  
- *⏸️ Em espera até a nova base de culturas. Exemplo muda conforme a zona climática.*  

**9. Nos períodos sem plantio, a terra fica descoberta?**  
🇺🇸 *When nothing is planted, is the soil left bare?*  
<sub>Campos no app: `q9_meses_vazios`</sub>  
- Sim / Não / Não sei  
- *Só aparece quando sobram meses sem cultura no calendário.*  
- *Em clima com inverno de neve (zona D), mostra a ajuda: “Se nesses meses o campo fica coberto de neve ou de palhada, conte como coberto (responda "não").”*  

**10. Depois da colheita, o que acontece com a área?**  
🇺🇸 *What happens to the field after harvest?*  
<sub>Campos no app: `q10_pos_colheita`</sub>  
- Fica parada · Vira pasto · Planto outra coisa · Planto algo para cobrir o solo  

**11. Você deixa a palha e os restos da colheita no campo?**  
🇺🇸 *Do you leave the stubble and crop residue on the field?*  
<sub>Campos no app: `q11_palha`</sub>  
- Sim / Não / Não sei  


### Parte 4 — Conhecendo seu solo

**12. Você já fez análise de solo em laboratório?**  
🇺🇸 *Have you ever had your soil tested in a lab?*  
<sub>Campos no app: `q12_analise`, `q12_tem_resultado`, `q12_laudo`, `q12_ano`</sub>  
- Sim / Não / Não sei  
- *Ainda tem o resultado?*: Sim / Não / Não sei  
- *Só se respondeu Sim na análise de solo.*  
- *Valores do laudo (preencha os que tiver)*: pH em água · Argila (%) · Matéria orgânica (g/dm³) · Fósforo (P) (mg/dm³) · Potássio (K) (mg/dm³) · CTC (cmolc/dm³) · Saturação por bases (V%) (%)  
- *Só se ainda tem o resultado. Com pelo menos dois valores, a análise usa o seu laudo no lugar dos mapas globais. Se a matéria orgânica vier em %, multiplique por 10.*  
- *De que ano é?*: lista de anos · Não lembro  
- *Só se respondeu Sim na análise de solo. Lista de anos + "Não lembro".*  

**13. Como você descreveria a terra da sua propriedade?**  
🇺🇸 *How would you describe the soil on your farm?*  
<sub>Campos no app: `q13_textura`</sub>  
- Mais arenosa · Meio-termo · Mais argilosa (barro) · Não sei  

**14. Quais destas situações você já percebeu no seu solo?**  
🇺🇸 *Which of these have you noticed in your soil?*  
<sub>Campos no app: `q14_encharca`, `q15_casca`, `q16_erosao`, `q17_dura`, `q18_minhocas`</sub>  
- A água fica empoçada por mais de um dia depois de chuva forte → Sim / Não / Não sei  
- A terra forma uma casca dura quando seca → Sim / Não / Não sei  
- A chuva leva terra embora (erosão, valetas ou água barrenta) → Sim / Não / Não sei  
- A terra fica muito dura para cavar ou arar → Sim / Não / Não sei  
- Encontro minhocas quando cavo *(sinal bom)* → Sim / Não / Não sei  
- Botão: “Não sei responder nenhuma”  

**15. Com qual destas opções você mais identifica a sua terra?**  
🇺🇸 *Which of these looks most like your soil?*  
<sub>Campos no app: `q19_cor`, `q19_jeito`</sub>  
- *Cor*: Preta ou marrom bem escura · Marrom · Vermelha · Amarelada · Cinza ou com manchas cinza · Clara ou esbranquiçada · Não sei  
- *Aparência ao toque*: Solta, escorre entre os dedos · Fofa, em pequenos grumos · Gruda e dá para moldar quando molhada · Torrões duros que não se desfazem · Racha quando seca · Pedregosa, com muito cascalho · Não sei  

**16. Existem partes da propriedade onde a lavoura sempre produz pior?**  
🇺🇸 *Are there parts of the farm where the crop always does worse?*  
<sub>Campos no app: `q20_partes_piores`</sub>  
- Sim / Não / Não sei  

**17. Você já fez alguma correção no solo?**  
🇺🇸 *Have you ever treated your soil to correct it?*  
<sub>Campos no app: `q21_correcao`</sub>  
- Calcário (para terra ácida) · Gesso agrícola (para terra com sal) · Outra correção + campo para escrever · Nunca fiz · Não sei  
- *Pode marcar mais de uma. Em clima seco (zona B ou mediterrâneo Csa/Csb), o gesso aparece primeiro.*  

**18. Você utiliza adubo ou esterco?**  
🇺🇸 *Do you use fertilizer or manure?*  
<sub>Campos no app: `q22_adubo`</sub>  
- Sim / Não / Não sei  


### Parte 5 — Clima e perdas de safra

**19. Você sente que as chuvas mudaram nos últimos anos?**  
🇺🇸 *Do you feel the rains have changed over the last few years?*  
<sub>Campos no app: `q23_chuva_mudou`</sub>  
- Sim / Não / Não sei  

**20. Quais destes eventos já fizeram você perder uma safra?**  
🇺🇸 *Have any of these ever cost you a crop?*  
<sub>Campos no app: `q24_perdas`</sub>  
- Geada · Chuva forte ou temporal · Alagamento ou encharcamento · Chuva de granizo · Calor intenso · Seca ou falta de chuva · Salinidade do solo (manchas brancas, planta queimando) · Nunca perdi uma safra por esses motivos · Não sei  
- *Pode marcar mais de um. Em cada um, diga mais ou menos o ano.*  
- ***Geada** some só onde o histórico do NASA POWER nunca teve noite abaixo de 2 °C (sem o POWER, some só em clima tropical).*  
- ***Salinidade** só aparece em clima seco (zona B) ou com irrigação em clima mediterrâneo (Csa/Csb).*  
- *Ao lado de cada evento marcado: “Lembra mais ou menos em que ano aconteceu?” (lista de anos + “Não lembro”).*  


### Parte 6 — Suas prioridades

**21. O que é mais importante para você? Escolha até 3.**  
🇺🇸 *What matters most to you? Pick up to 3.*  
<sub>Campos no app: `q25_prioridades`</sub>  
- Economizar água · Melhorar a terra · Evitar erosão · Ganhar uma renda extra · Produzir comida para os animais · Ter menos pragas  

**22. Tem alguma cultura que você não plantaria? Por quê?**  
🇺🇸 *Is there any crop you would not grow? Why?*  
<sub>Campos no app: `q26a_texto`</sub>  
- Campo de texto livre + botão “Separar com a AgroIA” (ex.: “não planto soja, não tenho onde vender”)  
- *⏸️ Em espera até a nova base de culturas. Motivos: Mercado · Costume · Já deu errado · Outro.*  

**23. Que máquinas e equipamentos você tem ou consegue utilizar?**  
🇺🇸 *What machinery or equipment do you have or can get access to?*  
<sub>Campos no app: `q26b_texto`</sub>  
- Campo de texto livre + botão “Separar com a AgroIA” (ex.: “tenho um trator pequeno e uma plantadeira; a colheita é na mão”)  
- *Botão “Separar com a AgroIA”; os equipamentos viram etiquetas removíveis e também podem ser adicionados por uma lista.*  


### Resumo final

Mostra: Perfil da propriedade · Calendário anual de culturas · Retrato do solo · Próximos passos recomendados (até 3 próximos passos).  
Botão: **Ver minha fazenda**  