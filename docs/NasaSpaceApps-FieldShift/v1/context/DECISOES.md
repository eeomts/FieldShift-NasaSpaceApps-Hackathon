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
- **Status:** Decidido (consequência direta de D-001, mantida em D-008; equivalentes revistos na D-009)
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
- **Status:** Decidido (equipe, 14/11/2026)
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
- **Fora do projeto (19):** Landsat e Sentinel-2 (já estão no HLS), SMAP L3 (substituído pelo L4), MERRA-2 (o POWER deriva dele), ECOSTRESS (passagens irregulares), GEDI e GRACE/GRACE-FO (só contexto, sem efeito no talhão), Copernicus DEM e TOPODATA (o SRTM basta; o TOPODATA deriva dele), ESA WorldCover e MODIS Land Cover (o MapBiomas cobre), CHIRPS (o IMERG cobre e as estações são as mesmas), ANA HidroWeb (irrigação fora do foco), CONAB/CEPEA (o IBGE PAM cobre a renda), Giovanni, Worldview e Harmony/OPeNDAP (o earthaccess e o AppEEARS cobrem), NASA Harvest e ARSET (referência e estudo, não fonte).
- **Consequência:** as notas das fontes que saíram foram apagadas e as citações a elas foram tiradas dos documentos do projeto. Os documentos que descrevem a lista oficial do desafio continuam citando todos os datasets dela.

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
| I-7 | `docs/NasaSpaceApps-FieldShift/v1/.pdf/` | Os três PDFs ainda têm "Minas" no nome e no conteúdo, e não acompanham a mudança de escopo (D-008). | Gerar de novo a partir dos `.md` atualizados. |

---

## 3. Perguntas em aberto

Ordenadas pelo quanto travam o resto. As primeiras definem o problema; as últimas, a solução.

### Entender o problema

**Q-01 — Quais regiões e sistemas de produção vamos usar na demo?**
Com o escopo nacional (D-008), a demo fica mais forte mostrando **duas ou três regiões contrastantes**, em que os mesmos dados levam a recomendações diferentes. Candidatas:
- **Cerrado (MT, GO, Alto Paranaíba/MG, MATOPIBA):** soja → milho safrinha, plantio direto. Rotação anual clássica, com muitos dados; solo descoberto longo na seca e risco de fogo no entorno.
- **Semiárido (sertão da BA, PE, CE, Norte de Minas):** agricultura familiar, feijão, milho, sorgo e mandioca. Tema forte de veranico, seca e pequeno produtor.
- **Sul (PR, RS, SC):** soja no verão e trigo, aveia ou milho no inverno. Pouco solo descoberto; temas de geada e diversificação.
- **Borda da Amazônia (norte do MT, sul do PA, RO):** fronteira agrícola, muitas nuvens na safra (exige Sentinel-1) e contexto de desmatamento.
- **Sudeste serrano (Sul de Minas, Zona da Mata, ES):** café em relevo acidentado. ⚠️ Café é **perene**, então não há rotação no sentido clássico. A ferramenta precisaria tratar de culturas intercalares ou de áreas anuais da propriedade.

**Q-02 — Quem é o usuário da demo?** Agricultor familiar, médio ou grande produtor, ou técnico da extensão rural (Emater ou ATER estadual)? Isso muda a linguagem, o dispositivo (celular ou computador) e o tipo de prioridade.

**Q-03 — Qual é a rotação atual do caso de exemplo?** Precisamos de um "seu Antônio" concreto para cada região da demo: local, culturas, meses e problemas.

**Q-04 — O que significa "SI" no texto oficial?** A suposição é inteligência artificial e técnicas estatísticas. **[verificar]** no Space Apps Connect.

**Q-05 — Quais são as regras e os critérios de avaliação de 2026?** Formato da submissão, idioma (o júri global provavelmente avalia em inglês), vídeo ou slides, prazo. **[verificar]** no site oficial.

### Delimitar a solução

**Q-06 — O campo será indicado por ponto ou por polígono?** Ponto é muito mais simples. Polígono permite análise dentro do talhão, mas a maioria dos dados obrigatórios tem resolução maior que um talhão.

**Q-07 — Qual será a fonte de solo?** GAEZ v5 (cerca de 1 km, aptidão), SoilGrids (250 m, propriedades por ponto via API) ou Embrapa Solos / PronaSolos (classes, mais fiel à realidade brasileira, mas com escala variável entre regiões). Resolve I-1.

**Q-08 — Quais critérios de comparação entram?** O desafio cita água, saúde do solo, erosão, pragas, renda, forragem, fixação de nitrogênio e mercado. Quais entram no MVP, e como medimos cada um?

**Q-09 — Qual será o formato e a stack?** App web, mapa interativo ou relatório? Ficou adiado de propósito até as perguntas acima estarem respondidas.

**Q-10 — Vamos usar LLM no produto?** Por exemplo, para reescrever as explicações em linguagem simples ou responder perguntas. Se sim, com que garantia de que não inventa números?

**Q-11 — Como vamos validar?** ZARC (janelas de plantio por município), estações do INMET e a conversa com algum agrônomo ou extensionista real.

---

## 4. Histórico

| Data | Mudança |
|---|---|
| 14/11/2026 | Registro criado. Decisões D-001 a D-007 levantadas dos documentos existentes; inconsistências e perguntas em aberto listadas. |
| 14/11/2026 | **D-008:** escopo muda para o Brasil inteiro e substitui a D-001. Atualizados D-003, D-005, I-1, I-2, Q-01 a Q-03 e Q-07; I-3 resolvido; I-7 criado. Arquivos renomeados de `-minas` para `-brasil`. |
| 14/11/2026 | **D-009:** fontes do MVP definidas (17 no núcleo, 3 opcionais, 19 fora). Substitui D-002 e D-005; D-003, D-008 e I-2 ajustados. |
