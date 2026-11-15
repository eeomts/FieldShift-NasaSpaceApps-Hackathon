# Registro de decisões — Field Shift Brasil

Lugar único para o que a equipe **já decidiu**, o que **está proposto** e o que **ainda está em aberto**. Os outros documentos explicam o desafio; este diz **o que vamos fazer e por quê**.

**Como usar**

- Cada decisão tem um número (`D-001`), um status, a data, quem decidiu, o motivo e as alternativas descartadas.
- Status possíveis:
  - **Decidido**: a equipe concordou.
  - **A confirmar**: aparece nos documentos, mas ninguém registrou como decisão de grupo.
  - **Em aberto**: falta decidir.
- Não apague uma decisão que mudou. Marque como **Substituída por D-0XX** e crie uma nova.
- Itens com **[verificar]** dependem de checagem numa fonte oficial.

---

## 1. Decisões registradas

### D-001 — Foco geográfico: Minas Gerais
- **Status:** **Substituída por D-008** (14/11/2026)
- **Origem:** títulos e conteúdo das primeiras versões de `bancos-de-dados-field-shift-brasil.md` (antes `-minas`), `BANCO_DE_DADOS_NASA.md` e `glossario-cientifico-ampliado-field-shift-brasil.md` (antes `-minas`)
- **Motivo provável:** contexto local da equipe; mostra os dados da NASA funcionando fora dos EUA, onde muitos recursos do desafio não existem.
- **Consequência:** 12 datasets da aba Resources ficam fora (ver D-003). As lacunas de solo, histórico de culturas e preços precisam ser preenchidas com fontes brasileiras ou mostradas ao usuário.

### D-002 — Classificação dos datasets
- **Status:** **Substituída por D-009** (14/11/2026). Antes: proposto (Gui, 14/11/2026).
- **Fonte:** `bancos-de-dados-field-shift-brasil.md`
- **Obrigatórios (6):** NASA POWER, GPM IMERG, SMAP, MODIS NDVI (MOD13Q1), SRTM, FAO GAEZ v5
- **Complementares (6):** Sentinel-2, Landsat 8/9, ECOSTRESS, GLDAS, ERA5, GRACE/GRACE-FO
- **Opcional (1):** GEDI L4A
- **Motivo:** os obrigatórios cobrem os indicadores básicos (clima, chuva, umidade, cobertura do solo, relevo e aptidão das culturas). Os complementares melhoram a precisão e o nível de confiança.

### D-003 — Datasets só dos EUA ficam fora
- **Status:** **Alterada pela D-010** (15/11/2026): continua valendo para as fazendas do Brasil; para as dos EUA, o Census (condados), o CDL e o NASS QuickStats entram. Antes: decidido (consequência direta de D-001, mantida em D-008; equivalentes revistos na D-009)
- **Itens:** Web Soil Survey, SSURGO/STATSGO2, CDL, PRISM, NAIP, NLCD, CoCoRaHS, NWIS, AMS Market News, NASS QuickStats, OpenET, LANDFIRE
- **Equivalentes brasileiros usados (D-009):** MapBiomas (histórico de culturas), IBGE PAM (estatísticas e valor da produção, que também serve ao critério de renda), INMET/CEMADEN (estações), ZARC (calendário e risco por cultura) e, como opcional, Embrapa Solos (solo). Ver `BANCO_DE_DADOS_NASA.md`.

### D-004 — Usar FAO GAEZ v5, não v4
- **Status:** Proposto (junto com D-002)
- **Motivo:** a v5 atualiza a linha de base para 2020 e tem resolução melhor.

### D-005 — GRACE só como contexto regional
- **Status:** **Substituída por D-009** (o GRACE saiu do projeto). Antes: proposto (junto com D-002)
- **Motivo:** a resolução real é de cerca de 3°. O GRACE responde "a água está diminuindo nesta bacia ou região?", mas não muda a recomendação para um talhão.

### D-006 — A ferramenta apoia, não decide
- **Status:** Decidido (exigência do próprio desafio)
- **Consequência:** a ferramenta mostra a incerteza e a origem de cada dado, deixa sempre um aviso visível e nunca usa linguagem prescritiva ("plante X").

### D-007 — Explicável antes de preciso
- **Status:** A confirmar
- **Origem:** `CONTEXTO-DESAFIO.md`, seção 9
- **Proposta:** regras e pontuação multicritério transparentes, alimentadas por indicadores calculados dos dados. IA (ou "SI") entra para achar padrões e redigir explicações, sem inventar números.
- **Alternativa:** um modelo de aprendizado de máquina que recomenda direto. É mais difícil de explicar e de validar em 48 h.

### D-008 — Escopo geográfico: Brasil inteiro
- **Status:** **Ampliada pela D-010** (15/11/2026): o Brasil inteiro continua no escopo, e os EUA entram. Antes: decidido (equipe, 14/11/2026)
- **Substitui:** D-001
- **Motivo:** [a equipe deve registrar aqui o motivo da mudança]. A análise das ferramentas existentes mostra o que muda com o escopo nacional: ver `docs/NasaSpaceApps-FieldShift/v1/others/Field_Shift_Brasil_Analise_Ferramentas_Existentes.md`.
- **Consequências:**
  - A D-003 continua valendo: os 12 datasets só dos EUA ficam fora, e os equivalentes brasileiros passam a ser usados em escala nacional.
  - Os indicadores passam a ser separados por **bioma** (mapa de biomas do IBGE) e por região.
  - O processamento fica mais pesado: os indicadores do panorama nacional devem ser **pré-calculados** numa grade comum. Dados de 30 m (HLS) entram só nos pontos escolhidos e nas regiões de demonstração.
  - As regras de recomendação precisam funcionar em todos os biomas, ou a ferramenta precisa dizer claramente onde não funciona.
  - Os documentos com "Minas" no nome ou no escopo foram atualizados; os casos hipotéticos em cidades de MG continuam como exemplos.

### D-009 — Fontes de dados e ferramentas do MVP
- **Status:** Decidido (equipe, 14/11/2026)
- **Substitui:** D-002 e D-005
- **Motivo:** com 48 h e escopo nacional, cada fonte precisa ter um papel que nenhuma outra cubra. Fontes repetidas, sem escala útil para o talhão ou só de estudo saíram. As notas de cada fonte estão em `tools/`.
- **Núcleo (17), em `tools/`:**
  - **Clima:** NASA POWER; ERA5 (segunda opinião independente)
  - **Chuva:** GPM IMERG
  - **Água no solo:** GLDAS (série longa); SMAP L4 (zona das raízes, situação atual), no lugar do SMAP L3
  - **Vegetação:** MODIS NDVI (panorama nacional); HLS (talhão), no lugar de Landsat e Sentinel-2 separados
  - **Relevo:** SRTM
  - **Aptidão:** FAO GAEZ v5
  - **Solo:** SoilGrids (fonte final ainda em Q-07)
  - **Uso do solo e histórico:** MapBiomas
  - **Validação:** ZARC; INMET/CEMADEN
  - **Contexto regional e renda:** IBGE PAM
  - **Acesso:** Earthdata Search (login), earthaccess (código), AppEEARS (séries por ponto)
- **Opcionais (3), em `tools/extras/`:** FIRMS (risco de fogo; volta ao núcleo se a demo tiver Cerrado ou borda da Amazônia), Sentinel-1 (só se a demo tiver região muito nublada na safra), Embrapa Solos (depende da Q-07).
- **Fora do projeto (19):** Landsat e Sentinel-2 (já estão no HLS), SMAP L3 (substituído pelo L4), MERRA-2 (o POWER deriva dele), ECOSTRESS (passagens irregulares), GEDI e GRACE/GRACE-FO (só contexto, sem efeito no talhão), Copernicus DEM e TOPODATA (o SRTM basta; o TOPODATA deriva dele), ESA WorldCover e MODIS Land Cover (o MapBiomas cobre), CHIRPS (o IMERG cobre e as estações são as mesmas), ANA HidroWeb (irrigação fora do foco), CONAB/CEPEA (o IBGE PAM cobre a renda), Giovanni, Worldview e Harmony/OPeNDAP (o earthaccess e o AppEEARS cobrem), NASA Harvest e ARSET (referência e estudo, não fonte). **O NASA Harvest está em revisão: ver a proposta abaixo.**
- **Consequência:** as notas das fontes que saíram foram apagadas e as citações a elas foram tiradas dos documentos do projeto. Os documentos que descrevem a lista oficial do desafio continuam citando todos os datasets dela.


### D-010 — O app também aceita fazendas nos EUA
- **Status:** Decidido (Augusto, 15/11/2026; avisar a equipe)
- **Amplia:** D-008 (escopo) · **Altera:** D-003 (datasets só dos EUA)
- **Motivo:** o desafio Field Shift é da NASA, e os dados da NASA (POWER, SMAP, MODIS/VIIRS pelo AppEEARS) e o SoilGrids cobrem os EUA do mesmo jeito que o Brasil. Muda só a parte das fontes nacionais.
- **Fontes dos EUA, no lugar das brasileiras** (detalhes em `data/README.md`, seção "EUA"):
  - **Município (IBGE)** → **condado** (Census TIGERweb), `data/eua/condados/`, chave `condado_id` (FIPS de 5 dígitos).
  - **ZARC** → datas usuais de plantio e colheita do **USDA NASS** por estado, `data/eua/nass/datas_plantio.csv`. É mais grosso: por estado, sem risco em %, sem tipo de solo nem ciclo, edição de 2010.
  - **IBGE PAM** → **NASS QuickStats** por condado, `data/eua/nass/producao_condado.csv`, sem o valor da produção.
  - **MapBiomas** → **CDL** (Cropland Data Layer), usado para conferir a rotação dos pontos da demo.
- **Consequências:**
  - O backend liga a fazenda ao condado nos EUA (`condado_id`) e ao município no Brasil (`municipio_id`).
  - Mandioca, milheto, feijão-caupi e as plantas de cobertura não têm datas nem produção nos EUA: a ferramenta precisa dizer isso, em vez de mostrar zero.
  - A demo ganha três pontos nos EUA (`data/demo/pontos_demo_eua.csv`): Story County (IA), Ness County (KS) e Tift County (GA).

#### Revisão proposta da D-009 — NASA Harvest volta ao projeto
- **Status:** Proposto (14/11/2026). Falta confirmar com a equipe.
- **Origem:** documentos do Guilherme em `tools/` (`NASA_POWER_X_HARVEST_PORTAL.md`, `NASA_HARVEST_PORTAL_API.md`, `NASA_HARVEST_PORTAL_API_GUIA.md`, `NASA_HARVEST_PORTAL_MCP.md`, `NASA_HARVEST_PORTAL_MCP_IMPLEMENTACAO.md`, `NASA_HARVEST.md`). Eles mostram usos concretos do NASA Harvest que a D-009 não tinha considerado; ela o tratava só como referência para o pitch.
- **Proposta:** o NASA Harvest volta ao projeto em três papéis:
  1. **Harvest Portal como contexto de mercado.** As tabelas do portal (FAO, OECD) dão produção e tendência **do país**. Elas aparecem como contexto ("o mercado nacional dessa cultura cresce ou encolhe"), mas **não** formam a nota de mercado. A fonte principal da renda continua sendo o **IBGE PAM**, que tem dados **por município**. Sem dado no portal, a ferramenta mostra "mercado não verificado", nunca nota zero.
  2. **Harvest Portal MCP no chat.** Se o chat do produtor for construído (ver `application/architecture/DASHBOARD-E-CHAT.md`), o assistente consulta o portal pelo MCP para responder perguntas de mercado com fonte, sem inventar números. Risco: a página oficial não lista as funções do servidor; confirmar antes de implementar.
  3. **`crop-cycle-detection` (GitHub do NASA Harvest).** Código pronto para detectar os ciclos de cultura em séries de NDVI. Usado com o MODIS (panorama) e o HLS (talhão) para mostrar a rotação real e o tempo de solo descoberto, sem escrever o método do zero. Conferir a licença e o esforço de adaptação.
- **Motivo:** o `crop-cycle-detection` e o MCP resolvem partes do produto (calendário de cobertura e chat com fontes) com material pronto. Como fonte de mercado, o portal é fraco para o Brasil porque só tem dados nacionais; por isso fica como contexto. De quebra, o projeto passa a usar mais de uma fonte da NASA com papéis claros, o que ajuda no pitch.
- **Alternativa descartada:** usar o Harvest Portal como fonte principal da nota de mercado (proposta original de `NASA_POWER_X_HARVEST_PORTAL.md`). Mercado nacional não representa o mercado local do produtor, e o IBGE PAM cobre esse papel melhor.
- **Se aprovada:**
  - O NASA Harvest sai da lista "Fora do projeto" e entra no núcleo, na linha **Contexto regional e renda** (portal, como contexto), na linha **Vegetação** (`crop-cycle-detection`) e numa nova linha **Chat** (MCP).
  - **Feito em 14/11/2026 (independe da aprovação):** os arquivos foram renomeados para o padrão `<NOME>.md`: `NASA_HARVEST.md` (GitHub), `NASA_HARVEST_PORTAL_API.md`, `NASA_HARVEST_PORTAL_API_GUIA.md`, `NASA_HARVEST_PORTAL_MCP.md`, `NASA_HARVEST_PORTAL_MCP_IMPLEMENTACAO.md` e `NASA_POWER_X_HARVEST_PORTAL.md`. O `arquitetura-completa-field-shift.md` foi para `application/architecture/ARQUITETURA-COMPLETA.md`. As citações a nomes antigos foram corrigidas.
  - Ainda em aberto: o `fluxo-aplicativo-power-harvest-mcp.md` e o `comunicacao-entre-apis.md` são citados, mas não existem no repositório.
### D-010 — Escopo do catálogo de culturas: Brasil e EUA
- **Status:** Decidido (Yury, Pessoa 1, 15/11/2026) para o catálogo de culturas. Falta a equipe rever a D-003 para as outras fontes.
- **Motivo:** o questionário já foi revisado para escopo global e testado em fazendas dos EUA (`data/onboarding/relatorio-revisao-questionario.md`), e os testes de chat do produtor americano (`TESTES_CHAT_SR_SMITH.md`) pedem culturas que o catálogo do Brasil não tem ou trata com outro sistema (centeio de cobertura, trigo de inverno, arroz inundado, amendoim).
- **Consequências:**
  - Novo catálogo `data/catalogo/eua/`, no mesmo formato do Brasil, com `codigo_nass` e `calendario_usda` no lugar de `codigo_pam` e `nome_zarc`. Guia em `data/catalogo/eua/README.md`; construído pelo agente `agroia-dataset-eua`.
  - Para o catálogo dos EUA, entram fontes que a D-003 deixava de fora: USDA NASS QuickStats (no lugar da PAM), USDA Agricultural Handbook 628 e RMA (no lugar do ZARC), extensão das universidades land-grant e USDA-ARS/NRCS (no lugar da Embrapa).
  - A régua das colunas qualitativas, a regra de confiança e as regras do motor são as mesmas do Brasil (`data/catalogo/evidencias/README.md`), para as notas serem comparáveis.
  - **Em aberto com a equipe:** se a D-003 cai também para solo (SSURGO), histórico de culturas (CDL) e clima (PRISM) nos pontos dos EUA.
  - **Resolvido (15/11):** o id `arroz_irrigado` entrou no `agroia/base/culturas.json` (commit f910193). "arroz irrigado", "arroz de várzea", "flooded rice" e afins casam com ele; "arroz" e "rice" sozinhos ficam ambíguos e o app pede que o produtor escolha (não decide pelo país).
  - **Decisões da revisão dos lotes 1 e 2 dos EUA (15/11, `reviews/lotes-1-2-eua 15_11_26/`), valem para os dois catálogos:**
    - a água não elimina cultura de sequeiro, só marca "água no limite" (regra 1 do motor); só o arroz irrigado sem várzea ou irrigação é eliminado;
    - graus-dia: o motor compara a mediana local; nas coberturas não elimina;
    - `tmax_critica_c` só gera aviso na fase sensível; vazio nas coberturas que morrem ou são manejadas antes de florescer;
    - perenes forrageiras (`pastagem`, `alfafa`) não usam ciclo nem graus-dia (`vazio_nao_se_aplica`); água anual;
    - colunas novas de janela, região e texto para o produtor (`semeadura_*`, `manejo_*`, `tipo_manejo`, `condicao_semeadura`, `estados_validos`, `lacuna_informacao`, `risco_revisao_local`); no Brasil entram vazias até haver fonte;
    - aveia e nabo dos EUA continuam com semeadura em agosto e setembro: a janela e a condição impedem que sejam sugeridos depois do milho ou da soja colhidos em outubro;
    - critério de `estudo_unico` escrito (1 local, 1 ano ou 1 cultivar); o sorgo dos EUA fica `media`;
    - ervilhaca dos EUA só no Corn Belt (Sudeste em arranjo regional); centeio com palhada típica 0,97 t/ha; girassol e amendoim com a palhada medida na região.

> As duas decisões acima ficaram com o mesmo número (D-010). Não foram renumeradas para não quebrar as citações; as próximas seguem da D-011.

### D-011 — Escopo confirmado: Brasil e EUA
- **Status:** Decidido (equipe, 15/11/2026)
- **Confirma:** as duas D-010 (fazendas e catálogo dos EUA), que tinham sido decididas por uma pessoa só. **Responde em parte:** Q-01 (os países estão definidos; as regiões e as fazendas da demo, não).
- **Motivo:** os dados da NASA cobrem os dois países do mesmo jeito, o app e o questionário já aceitam qualquer ponto do mapa, e o júri do Space Apps é global.
- **Consequências:**
  - Toda tela e todo texto do chat funcionam em português e inglês, com as unidades do país (hectare e mm no Brasil; acre e polegada nos EUA).
  - Onde uma fonte só existe num país (ZARC e PAM no Brasil; NASS e CDL nos EUA), a ferramenta diz que o dado não existe para aquele país, em vez de mostrar zero.
  - Em aberto com a equipe: se a D-003 cai também para solo (SSURGO) e clima (PRISM) nos EUA.

### D-012 — Usuário-alvo: pequeno e médio produtor e técnico agrícola
- **Status:** Decidido (equipe, 15/11/2026)
- **Responde:** Q-02.
- **Quem:** agricultores de pequeno e médio porte e os técnicos agrícolas e agrônomos que os atendem (Emater, ATER, cooperativas, extensão rural nos EUA). O grande produtor não é o foco: em geral ele já tem consultoria e agricultura de precisão.
- **Consequências:**
  - Linguagem simples, sem jargão, e celular primeiro (o produtor usa o app no campo).
  - O técnico precisa ver a origem de cada número e poder ajudar um produtor: o questionário já pergunta quem está respondendo (pergunta 1).
  - O caso de exemplo da demo (Q-03) deve ser de um pequeno ou médio produtor.

### D-013 — IA do produto: Gemini
- **Status:** Decidido (equipe, 15/11/2026)
- **Responde:** Q-10 e a dúvida do README ("o código usa Gemini, mas a arquitetura fala em Claude").
- **Onde:** leitura do texto livre do questionário, chat AgroIA (com ferramentas) e embeddings da base de conhecimento. Modelos em `agroia/api/app/core/config.py` (`GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`).
- **Garantia contra número inventado:** o chat só repete números que vieram de uma ferramenta na mesma conversa e diz a fonte e o período (regras do `services/agente/prompt.py`). Sem chave, o questionário usa a lista reserva e o chat responde que está indisponível.
- **Alternativa descartada:** API do Claude, que estava proposta em `application/architecture/`. Os documentos de arquitetura foram atualizados.
- **Cuidado:** cada mensagem gasta a cota do Gemini. No desenvolvimento, a chave fica vazia no `.env.dev`.

### D-014 — Previsão do tempo: Open-Meteo
- **Status:** Decidido (equipe, 15/11/2026)
- **Altera:** D-009 (é a única fonte fora do núcleo) · **Resolve:** S-7 do `application/site-contexto.md`.
- **Motivo:** a NASA não publica previsão do tempo. Os dados dela são observações com atraso (POWER de 2 a 7 dias, IMERG Late de cerca de 1 dia). A Open-Meteo cobre o Brasil e os EUA por ponto, sem chave.
- **Consequências:**
  - O Dashboard volta a ter a previsão dos próximos 7 dias, com a fonte escrita na tela: *"Previsão: Open-Meteo · Histórico, solo e vegetação: NASA"*.
  - A licença dos dados é CC BY 4.0: a tela precisa dar o crédito à Open-Meteo. O plano gratuito é para uso não comercial. **[verificar]** os limites de uso na página oficial antes do deploy.
  - O chat continua sem fazer previsão (regra 6 do prompt) até a equipe decidir o contrário.

---

## 2. Inconsistências encontradas nos documentos

Precisam ser resolvidas antes de virar código.

| # | Onde | Problema | Sugestão |
|---|---|---|---|
| I-1 | `CONTEXTO-DESAFIO.md` §13 × `bancos-de-dados-field-shift-brasil.md` | O MVP do contexto usa **SoilGrids + HLS** para solo e vegetação. A classificação dos bancos de dados usa **GAEZ v5 + MODIS** e não cita SoilGrids. | Decidir a fonte de solo (ver Q-07) e atualizar o documento que ficar desatualizado. |
| I-2 | `desafio-field-shift-...-explicado-do-zero.md` Parte 3 | O exemplo do "seu Antônio" cita **NDVI do Landsat** como evidência, mas o plano de dados usa **MODIS** no panorama e **HLS** no talhão; o Landsat não é usado como fonte separada (D-009). | Alinhar o exemplo quando a demo for definida. |
| I-3 | `BANCO_DE_DADOS_NASA.md` e `dataset_nasa_miasgerais-focus.md` | Os dois arquivos eram idênticos. | **Resolvido (14/11/2026):** o segundo foi removido. |
| I-4 | `BANCO_DE_DADOS_NASA.md` §3 | Diz que o NASA POWER "já é usado no app em Streamlit", mas não existe app nem stack definida. | **Resolvido (14/11/2026):** a frase foi tirada na revisão da D-009. A stack continua em aberto (Q-09). |
| I-5 | `explicado-do-zero.md` Parte 5 | Fala do repositório `nasa-space-app`, mas o repositório é `FieldShift`. | Atualizar o nome. |
| I-6 | `README.md` | A linha do título está repetida três vezes e não há descrição do projeto. | Reescrever quando o escopo fechar. |
| I-7 | `docs/NasaSpaceApps-FieldShift/v1/.pdf/` | Os três PDFs ainda têm "Minas" no nome e no conteúdo, e não acompanham a mudança de escopo (D-008). | **Resolvido (14/11/2026):** os PDFs de bancos de dados e do glossário foram gerados de novo a partir dos `.md` e renomeados para `Brasil`; o do explicado-do-zero não mudou. |

---

## 3. Perguntas em aberto

Ordenadas pelo quanto travam o resto. As primeiras definem o problema; as últimas, a solução.

### Entender o problema

**Q-01 — Quais regiões e sistemas de produção vamos usar na demo?** *Em parte respondida pela D-011 (15/11): Brasil e EUA. Faltam as regiões e as fazendas.*
Com o escopo nacional (D-008), a demo fica mais forte mostrando **duas ou três regiões contrastantes**, em que os mesmos dados levam a recomendações diferentes. Candidatas:
- **Cerrado (MT, GO, Alto Paranaíba/MG, MATOPIBA):** soja → milho safrinha, plantio direto. Rotação anual clássica, com muitos dados; solo descoberto longo na seca e risco de fogo no entorno.
- **Semiárido (sertão da BA, PE, CE, Norte de Minas):** agricultura familiar, feijão, milho, sorgo e mandioca. Tema forte de veranico, seca e pequeno produtor.
- **Sul (PR, RS, SC):** soja no verão e trigo, aveia ou milho no inverno. Pouco solo descoberto; temas de geada e diversificação.
- **Borda da Amazônia (norte do MT, sul do PA, RO):** fronteira agrícola, muitas nuvens na safra (exige Sentinel-1) e contexto de desmatamento.
- **Sudeste serrano (Sul de Minas, Zona da Mata, ES):** café em relevo acidentado. ⚠️ Café é **perene**, então não há rotação no sentido clássico. A ferramenta precisaria tratar de culturas intercalares ou de áreas anuais da propriedade.

**Q-02 — Quem é o usuário da demo?** *Respondida pela D-012 (15/11): pequeno e médio produtor e técnico agrícola.* Agricultor familiar, médio ou grande produtor, ou técnico da extensão rural (Emater ou ATER estadual)? Isso muda a linguagem, o dispositivo (celular ou computador) e o tipo de prioridade.

**Q-03 — Qual é a rotação atual do caso de exemplo?** *Em aberto (15/11): a equipe ainda não escolheu o caso.* Precisamos de um "seu Antônio" concreto para cada região da demo: local, culturas, meses e problemas.

**Q-04 — O que significa "SI" no texto oficial?** A suposição é inteligência artificial e técnicas estatísticas. **[verificar]** no Space Apps Connect.

**Q-05 — Quais são as regras e os critérios de avaliação de 2026?** *Em andamento (15/11): a equipe está lendo as regras de submissão.* Formato da submissão, idioma (o júri global provavelmente avalia em inglês), vídeo ou slides, prazo. **[verificar]** no site oficial.

### Delimitar a solução

**Q-06 — O campo será indicado por ponto ou por polígono?** Ponto é muito mais simples. Polígono permite análise dentro do talhão, mas a maioria dos dados obrigatórios tem resolução maior que um talhão.

**Q-07 — Qual será a fonte de solo?** GAEZ v5 (cerca de 1 km, aptidão), SoilGrids (250 m, propriedades por ponto via API) ou Embrapa Solos / PronaSolos (classes, mais fiel à realidade brasileira, mas com escala variável entre regiões). Resolve I-1.

**Q-08 — Quais critérios de comparação entram?** O desafio cita água, saúde do solo, erosão, pragas, renda, forragem, fixação de nitrogênio e mercado. Quais entram no MVP, e como medimos cada um?

**Q-09 — Qual será o formato e a stack?** App web, mapa interativo ou relatório? Ficou adiado de propósito até as perguntas acima estarem respondidas.

**Q-10 — Vamos usar LLM no produto?** *Respondida pela D-013 (15/11): sim, Gemini.* Por exemplo, para reescrever as explicações em linguagem simples ou responder perguntas. Se sim, com que garantia de que não inventa números?

**Q-11 — Como vamos validar?** ZARC (janelas de plantio por município), estações do INMET e a conversa com algum agrônomo ou extensionista real.

---

## 4. Histórico

| Data | Mudança |
|---|---|
| 14/11/2026 | Registro criado. Decisões D-001 a D-007 levantadas dos documentos existentes; inconsistências e perguntas em aberto listadas. |
| 14/11/2026 | **D-008:** escopo muda para o Brasil inteiro e substitui a D-001. Atualizados D-003, D-005, I-1, I-2, Q-01 a Q-03 e Q-07; I-3 resolvido; I-7 criado. Arquivos renomeados de `-minas` para `-brasil`. |
| 14/11/2026 | **D-009:** fontes do MVP definidas (17 no núcleo, 3 opcionais, 19 fora). Substitui D-002 e D-005; D-003, D-008 e I-2 ajustados. |
| 14/11/2026 | Proposta de revisão da D-009: NASA Harvest volta como contexto de mercado (Harvest Portal), no chat (MCP) e na detecção de ciclos (`crop-cycle-detection`). A confirmar com a equipe. |
| 15/11/2026 | **D-010:** o app também aceita fazendas nos EUA. Amplia a D-008 e altera a D-003 (Census, CDL e NASS QuickStats entram para as fazendas dos EUA). |
| 15/11/2026 | **D-010:** catálogo de culturas abre para os EUA (`data/catalogo/eua/`), com fontes americanas só para esse catálogo. D-003 a rever pela equipe para as outras fontes. |
| 15/11/2026 | **D-011 a D-014:** escopo Brasil e EUA confirmado pela equipe; usuário-alvo é o pequeno e médio produtor e o técnico agrícola; a IA é o Gemini; a Open-Meteo entra para a previsão do tempo. Q-02 e Q-10 respondidas; Q-01 em parte; Q-05 em andamento. Documentos de arquitetura passam de Claude para Gemini. |
