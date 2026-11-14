# Registro de decisões — Field Shift Minas

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
- **Status:** A confirmar
- **Origem:** títulos e conteúdo de `bancos-de-dados-field-shift-minas.md`, `BANCO_DE_DADOS_NASA.md` e `glossario-cientifico-ampliado-field-shift-minas.md`
- **Motivo provável:** contexto local da equipe; mostra os dados da NASA funcionando fora dos EUA, onde muitos recursos do desafio não existem.
- **Consequência:** 12 datasets da aba Resources ficam fora (ver D-003). As lacunas de solo, histórico de culturas e preços precisam ser preenchidas com fontes brasileiras ou mostradas ao usuário.

### D-002 — Classificação dos datasets
- **Status:** Proposto (Gui, 14/11/2026). Falta confirmar com a equipe.
- **Fonte:** `bancos-de-dados-field-shift-minas.md`
- **Obrigatórios (6):** NASA POWER, GPM IMERG, SMAP, MODIS NDVI (MOD13Q1), SRTM, FAO GAEZ v5
- **Complementares (6):** Sentinel-2, Landsat 8/9, ECOSTRESS, GLDAS, ERA5, GRACE/GRACE-FO
- **Opcional (1):** GEDI L4A
- **Motivo:** os obrigatórios cobrem os indicadores básicos (clima, chuva, umidade, cobertura do solo, relevo e aptidão das culturas). Os complementares melhoram a precisão e o nível de confiança.

### D-003 — Datasets só dos EUA ficam fora
- **Status:** Decidido (consequência direta de D-001)
- **Itens:** Web Soil Survey, SSURGO/STATSGO2, CDL, PRISM, NAIP, NLCD, CoCoRaHS, NWIS, AMS Market News, NASS QuickStats, OpenET, LANDFIRE
- **Equivalentes brasileiros possíveis:** MapBiomas (histórico de culturas), IBGE PAM (estatísticas), CONAB/CEPEA (preços), Embrapa Solos (solo), INMET/CEMADEN (estações), ANA HidroWeb (água), ZARC (calendário e risco por cultura), TOPODATA (relevo). Ver `BANCO_DE_DADOS_NASA.md`.

### D-004 — Usar FAO GAEZ v5, não v4
- **Status:** Proposto (junto com D-002)
- **Motivo:** a v5 atualiza a linha de base para 2020 e tem resolução melhor.

### D-005 — GRACE só como contexto regional
- **Status:** Proposto (junto com D-002)
- **Motivo:** a resolução real é de cerca de 3°. O GRACE responde "a água está diminuindo em Minas?", mas não muda a recomendação para um talhão.

### D-006 — A ferramenta apoia, não decide
- **Status:** Decidido (exigência do próprio desafio)
- **Consequência:** a ferramenta mostra a incerteza e a origem de cada dado, deixa sempre um aviso visível e nunca usa linguagem prescritiva ("plante X").

### D-007 — Explicável antes de preciso
- **Status:** A confirmar
- **Origem:** `CONTEXTO-DESAFIO.md`, seção 9
- **Proposta:** regras e pontuação multicritério transparentes, alimentadas por indicadores calculados dos dados. IA (ou "SI") entra para achar padrões e redigir explicações, sem inventar números.
- **Alternativa:** um modelo de aprendizado de máquina que recomenda direto. É mais difícil de explicar e de validar em 48 h.

---

## 2. Inconsistências encontradas nos documentos

Precisam ser resolvidas antes de virar código.

| # | Onde | Problema | Sugestão |
|---|---|---|---|
| I-1 | `CONTEXTO-DESAFIO.md` §13 × `bancos-de-dados-field-shift-minas.md` | O MVP do contexto usa **SoilGrids + HLS** para solo e vegetação. A classificação de Minas usa **GAEZ v5 + MODIS** e não cita SoilGrids. | Decidir a fonte de solo (ver Q-07) e atualizar o documento que ficar desatualizado. |
| I-2 | `desafio-field-shift-...-explicado-do-zero.md` Parte 3 | O exemplo do "seu Antônio" cita **NDVI do Landsat** como evidência, mas o plano de Minas usa **MODIS** como obrigatório e Landsat como complementar. | Alinhar o exemplo quando a demo for definida. |
| I-3 | `BANCO_DE_DADOS_NASA.md` e `dataset_nasa_miasgerais-focus.md` | Os dois arquivos são quase idênticos. O segundo ainda não foi commitado. | Manter um só. |
| I-4 | `BANCO_DE_DADOS_NASA.md` §3 | Diz que o NASA POWER "já é usado no app em Streamlit", mas não existe app nem stack definida. | Corrigir o texto ou registrar a stack quando ela for decidida (Q-09). |
| I-5 | `explicado-do-zero.md` Parte 5 | Fala do repositório `nasa-space-app`, mas o repositório é `FieldShift`. | Atualizar o nome. |
| I-6 | `README.md` | A linha do título está repetida três vezes e não há descrição do projeto. | Reescrever quando o escopo fechar. |

---

## 3. Perguntas em aberto

Ordenadas pelo quanto travam o resto. As primeiras definem o problema; as últimas, a solução.

### Entender o problema

**Q-01 — Qual região de Minas e qual sistema de produção vamos usar na demo?**
Minas tem realidades muito diferentes, e a escolha muda os dados, as culturas e a história contada:
- **Triângulo Mineiro / Alto Paranaíba:** soja → milho safrinha, plantio direto. Rotação anual clássica, com muitos dados.
- **Noroeste (Unaí, Paracatu):** grãos e irrigação por pivô. Tema forte de água, ligado a GRACE e balanço hídrico.
- **Norte de Minas:** semiárido, agricultura familiar, sorgo, feijão e mandioca. Tema forte de seca e de pequeno produtor.
- **Sul de Minas / Zona da Mata:** café em relevo acidentado. ⚠️ Café é **perene**, então não há rotação no sentido clássico. A ferramenta precisaria tratar de culturas intercalares ou de áreas anuais da propriedade.

**Q-02 — Quem é o usuário da demo?** Agricultor familiar, médio ou grande produtor, ou técnico da extensão rural (ex.: Emater-MG)? Isso muda a linguagem, o dispositivo (celular ou computador) e o tipo de prioridade.

**Q-03 — Qual é a rotação atual do caso de exemplo?** Precisamos de um "seu Antônio" mineiro concreto: local, culturas, meses e problemas.

**Q-04 — O que significa "SI" no texto oficial?** A suposição é inteligência artificial e técnicas estatísticas. **[verificar]** no Space Apps Connect.

**Q-05 — Quais são as regras e os critérios de avaliação de 2026?** Formato da submissão, idioma (o júri global provavelmente avalia em inglês), vídeo ou slides, prazo. **[verificar]** no site oficial.

### Delimitar a solução

**Q-06 — O campo será indicado por ponto ou por polígono?** Ponto é muito mais simples. Polígono permite análise dentro do talhão, mas a maioria dos dados obrigatórios tem resolução maior que um talhão.

**Q-07 — Qual será a fonte de solo?** GAEZ v5 (cerca de 1 km, aptidão), SoilGrids (250 m, propriedades por ponto via API) ou Embrapa Solos (classes, mais fiel à realidade local). Resolve I-1.

**Q-08 — Quais critérios de comparação entram?** O desafio cita água, saúde do solo, erosão, pragas, renda, forragem, fixação de nitrogênio e mercado. Quais entram no MVP, e como medimos cada um?

**Q-09 — Qual será o formato e a stack?** App web, mapa interativo ou relatório? Ficou adiado de propósito até as perguntas acima estarem respondidas.

**Q-10 — Vamos usar LLM no produto?** Por exemplo, para reescrever as explicações em linguagem simples ou responder perguntas. Se sim, com que garantia de que não inventa números?

**Q-11 — Como vamos validar?** ZARC (janelas de plantio por município), estações do INMET e a conversa com algum agrônomo ou extensionista real.

---

## 4. Histórico

| Data | Mudança |
|---|---|
| 14/11/2026 | Registro criado. Decisões D-001 a D-007 levantadas dos documentos existentes; inconsistências e perguntas em aberto listadas. |
