# AgroAI: contexto do site

> **Para a IA que ler este arquivo:** este é o documento de produto do **AgroAI**, a solução da equipe para o desafio *Field Shift: Adapting Farms with NASA Data* (NASA Space Apps Challenge 2026). Use-o como fonte principal sobre **o que construir e com qual stack**.
>
> **Documentos relacionados** (repositório da equipe `FieldShift-NasaSpaceApps-Hackatnon`, pasta `docs/NasaSpaceApps-FieldShift/v1/`):
> | Arquivo | O que tem |
> |---|---|
> | `context/CONTEXTO-DESAFIO.md` | Texto oficial do desafio, requisitos, conceitos e indicadores |
> | `context/DECISOES.md` | Decisões da equipe (D-xxx), inconsistências e perguntas em aberto |
> | `context/Field Shift Brasil — Documentação do Projeto.md` | Metodologia (grade comum, pontuação, incerteza) e cartão de estratégia |
> | `context/BANCO_DE_DADOS_NASA.md` | Lista de datasets e ferramentas |
> | `application/ONBOARDING.md` | **Questionário do primeiro acesso: fonte oficial do onboarding** |
> | `tools/*.md` | Uma nota por fonte do núcleo da D-009 (NASA POWER, SMAP L4, GPM IMERG, MODIS, HLS, SRTM, SoilGrids, GLDAS, ERA5, AppEEARS, earthaccess etc.) com acesso, variáveis, latência e limitações |
> | `tools/ARQUITETURA-COMPLETA.md` | Fluxo "Analisar meu campo" passo a passo (coleta, harmonização, diagnóstico, filtro, mercado, estratégias, chat com MCP). O AgroAI usa esse fluxo e acrescenta o Dashboard diário e o chat |
> | `tools/NASA_HARVEST_PORTAL_*.md` | API e MCP do NASA Harvest Portal (dados de mercado por país) |
> | `application/DOR-DO-AGRICULTOR-E-CASO-DE-USO.md` | Dor do produtor e persona Dona Marta |
>
> Marcadores: **[decidir]** = equipe ainda não definiu · **[verificar]** = confirmar em fonte oficial antes de virar código.

---

## 0. Decisões que este documento assume

| # | Decisão | Status |
|---|---|---|
| S-1 | **Front-end em React** (Vite) consumindo uma **API REST em FastAPI (Python)** | Decidido (resposta da equipe: "Rest e FastAPI"; interpretado como React + FastAPI REST **[verificar]**) |
| S-2 | **LLM: Google Gemini API** (chave já disponível) | Decidido |
| S-3 | **Escopo: mundo todo** | Proposto. ⚠️ **Conflita com D-008 (Brasil inteiro)** em `DECISOES.md`. Registrar como **D-010** substituindo a D-008 (ver seção 12) |
| S-4 | **Login simples** (e-mail + senha, sem provedor externo) | Decidido |
| S-5 | **1 fazenda = 1 talhão**, indicado por **um ponto** no mapa (polígono fica para depois; resolve Q-06) | Decidido |
| S-6 | A ferramenta **apoia, não decide** (D-006) e é **explicável antes de precisa** (D-007) | Herdado de `DECISOES.md` |
| S-7 | **Fontes de dados seguem a D-009** (núcleo de 17 fontes). Única fonte nova: **Open-Meteo** para a previsão do tempo, que nenhuma fonte da D-009 cobre | Proposto |

---

## 1. Visão do produto

O **AgroAI** é um site em que o produtor:
1. **Faz login e responde o questionário da fazenda** (`ONBOARDING.md`): local, o que planta e quando, o que sabe do solo, perdas que já teve e prioridades.
2. **Acessa o Dashboard**: informações da região dele, atualizadas diariamente com dados da NASA. Inclui previsão do tempo, condição do solo, saúde da lavoura, alertas e a comparação de estratégias de rotação.
3. **Conversa com a AgroAI**: um assistente (Gemini) que conhece a fazenda dele (perfil, indicadores do dia e base de conhecimento) e responde em linguagem simples, citando a fonte de cada dado.

**Duas abas principais:** `Dashboard` e `AgroAI`.

**Pitch em uma frase:** *"Os dados de satélite da NASA, traduzidos para a fazenda de cada produtor, num painel diário e num assistente que conversa com ele, em qualquer lugar do mundo."*

### 1.1 Princípios
- **Linguagem do produtor:** termos técnicos sempre com explicação de uma frase.
- **Toda informação com fonte e data:** dataset, data real do dado e resolução.
- **Incerteza visível:** confiança alta/média/baixa por indicador e por estratégia.
- **Apoio, não ordem:** sem linguagem prescritiva ("plante X"). Aviso fixo no Dashboard e no chat.
- **Mobile first**, multilíngue (**PT, EN e ES** no mínimo).
- **Funciona no mundo todo com dados globais.** Fontes nacionais (ex.: brasileiras) entram como **enriquecimento opcional** quando o ponto cai naquele país.

### 1.2 Alinhamento com o desafio
O núcleo do desafio é **comparar pelo menos 3 estratégias de rotação, incluindo a atual**, explicando para cada uma: **por que foi sugerida, evidência, benefícios, lacunas e riscos para revisão local**. Dashboard e chat sozinhos não cumprem isso. Por isso existem o **card "Estratégias de rotação"** (5.2, card 9) e o **comando no chat** (6.5).

| Requisito do desafio | Onde aparece no AgroAI |
|---|---|
| Dados de observação da Terra da NASA | Todos os cards + contexto do chat |
| Solo, características das culturas | Onboarding (bloco 4) + SoilGrids + base de culturas |
| Prioridades do produtor | Onboarding (bloco 6) |
| Comparar ≥ 3 rotações, com a atual | Card 9 + comando no chat |
| Por que / evidência / benefícios / lacunas / riscos | Cartão de cada estratégia + respostas do chat |
| Solo descoberto, estações vulneráveis | Cards 4, 5 e 10 |
| Explicar termos científicos | Botão "O que isso significa?" + chat |
| Satélite × medição em campo | "De onde vem?" + cruzamento das perdas lembradas pelo produtor (onboarding, bloco 5) |
| Apoio, não substituição | Aviso fixo |

---

## 2. Usuários

Perfis definidos em `ONBOARDING.md`:

| Perfil | Quem é | Efeito no AgroAI |
|---|---|---|
| **A: Experiência** | Pequeno produtor, sem técnico frequente, só observa o solo | Linguagem mais simples; usa dados globais; sugere testes simples |
| **B: Observador** | Já fez algum teste ou sabe a textura | Combina o que informa com os dados globais |
| **C: Com laudo** | Tem análise de solo de laboratório | Valores do laudo substituem os modelados; confiança maior |
| **D: Técnico** | Extensionista que preenche pelo produtor | Mais detalhe técnico na tela |

Modificadores: **irrigação** e **criação de animais**.

**Fazendas de demonstração:** usar 2 ou 3 pontos em **países/climas contrastantes**, para provar que a recomendação muda com o local. Sugestão: Cerrado brasileiro (Dona Marta), um ponto semiárido irrigado nos EUA (ex.: alfafa em Nevada, como a foto do desafio) e um ponto de clima temperado ou tropical em outro continente **[decidir]**.

---

## 3. Mapa do site

```text
/                  Página inicial (o que é + Entrar / Criar conta)
/login             Login (e-mail + senha)
/cadastro          Criar conta
/onboarding        Questionário da fazenda (só no primeiro acesso; pode pular e voltar)
/dashboard         Aba 1
/agroia            Aba 2
/fazenda           Ver/editar respostas do questionário
```

Rotas protegidas: `/onboarding`, `/dashboard`, `/agroia` e `/fazenda`. Sem onboarding concluído, o usuário vai para `/onboarding`.

---

## 4. Onboarding

**Fonte oficial: `application/ONBOARDING.md`.** Não duplicar aqui. Resumo do que importa para o site:

- 6 blocos, até 5 minutos, respostas **Sim / Não / Não sei**, figuras para terreno e solo.
- **Local = 1 ponto no mapa** (pergunta 5). Tem botão "usar meu GPS".
- **Texto livre interpretado por IA** nas perguntas **8** (o que planta e quando), **26a** (culturas que não plantaria) e **26b** (equipamentos). Fluxo: `texto → Gemini extrai JSON → casa com a base → produtor confirma item a item`. A IA **só devolve itens que existem na base** ou "não encontrado". Se o Gemini falhar, o produtor escolhe de uma lista com ícones.
- **Histórico de perdas com ano** (bloco 5): o back-end procura o evento nos dados NASA e mostra se confirma ("Em 2021 o NASA POWER registrou 3 noites abaixo de 0 °C em julho no seu local").
- **Saídas:** perfil A–C + papel (produtor/técnico) + modificadores, calendário confirmado, retrato provisório do solo, histórico de perdas, prioridades (até 3), culturas excluídas, equipamentos, próximo passo sugerido.

Ao terminar, a API dispara o **processamento inicial** da fazenda (seção 7). O front mostra "Preparando os dados da sua fazenda…" e abre o Dashboard quando ficar pronto.

---

## 5. Aba 1: Dashboard

### 5.1 Estrutura
1. Cabeçalho: "Bom dia, Marta" · local · "Dados de 14/11/2026".
2. **Faixa de alertas** (até 3, por prioridade).
3. **Cards** em grade (uma coluna no celular).
4. Rodapé fixo: *"Informações para apoiar sua decisão. Confirme com um técnico agrícola e com a sua experiência."*

Cada card tem: valor principal em frase simples · mini gráfico (se fizer sentido) · **"O que isso significa?"** · **"De onde vem?"** (dataset, data do dado, resolução, confiança) · **"Perguntar à AgroAI"** (abre o chat com a pergunta já escrita).

### 5.2 Cards (todos globais)

| # | Card | O que mostra | Fonte | Frequência real do dado |
|---|---|---|---|---|
| 1 | **Previsão do tempo** | 7 dias: máx/mín, chuva, vento; dias de risco destacados | **Open-Meteo** (não é NASA; global, gratuito, sem chave). Ver 5.3 | Várias vezes por dia |
| 2 | **Clima recente vs. normal** | Últimos 30 dias de chuva e temperatura vs. média histórica | **NASA POWER** (diário desde 1981) | Diário, com **2 a 7 dias de atraso** (`tools/NASA_POWER.md`) |
| 3 | **Umidade do solo** | Superfície e zona das raízes vs. normal (anomalia) | **SMAP L4** (9 km, 3-horário) e NASA POWER `GWETTOP/GWETROOT` como reserva | Poucos dias de atraso (`tools/SMAP_L4.md`) |
| 4 | **Saúde da lavoura** | NDVI do ponto no ano vs. anos anteriores; **períodos de solo descoberto** marcados | **MODIS MOD13Q1** (250 m, 16 dias) via AppEEARS; HLS (30 m) opcional | A cada 16 dias (MODIS) |
| 5 | **Fique de olho** | Alertas de geada, calor, chuva forte, seca e erosão, ligados à fase da cultura | Regras (5.4) sobre previsão + POWER + SMAP + perfil | Diário |
| 6 | **Seu solo** | Textura, carbono orgânico, pH. Mostra lado a lado o que o produtor informou e o modelo | **SoilGrids** (250 m) + onboarding | Estático |
| 7 | **Relevo e erosão** | Declividade do ponto e vizinhança; risco com chuva forte | **SRTM** (30 m) + chuva (POWER/IMERG) + resposta 7/16 do onboarding | Estático + mensal |
| 8 | **Água no solo ao longo dos anos** | Umidade do solo em série longa: os anos secos e a tendência | **GLDAS** (série longa, D-009) | Mensal (1 a 2 meses de atraso) |
| 9 | **Estratégias de rotação** | Atual + 2 alternativas, nota por prioridade, selo de confiança; detalhe com por que / evidência / benefícios / lacunas / riscos | Indicadores + base de culturas + **FAO GAEZ** (aptidão) + **Harvest Portal** (mercado, por país) + prioridades. Fluxo em `ARQUITETURA-COMPLETA.md` | Recalcula quando o perfil muda ou 1×/mês |
| 10 | **Calendário da fazenda** | 12 meses com as culturas e faixas de risco (geada, calor, seca, solo descoberto) | Perfil + climatologia POWER | Mensal |

**Enriquecimento regional (opcional):** se o ponto estiver no Brasil, acrescentar ZARC (janela de plantio), MapBiomas (histórico de uso) e INMET (estação próxima). Nos EUA: CDL, SSURGO e OpenET. A arquitetura deve prever um "plugin por país", mas o MVP roda só com fontes globais.

### 5.3 "Atualizado diariamente com a NASA": o que é verdade
- **A NASA não oferece previsão do tempo simples.** Os dados NASA são de **observação** e chegam com atraso: POWER leva 2 a 7 dias e o **IMERG Final leva cerca de 3,5 meses**. Para chuva recente, usar **IMERG Late/Early** (`tools/GPM_IMERG.md`). A **previsão vem do Open-Meteo**, e a tela diz isso: *"Previsão: Open-Meteo · Histórico, solo e vegetação: NASA"*.
- **O job roda todo dia**, mas cada card mostra a **data real do dado**, não a do processamento.
- **Demo:** pré-processar e guardar em cache as fazendas de demonstração. AppEEARS é assíncrono e pode demorar.

### 5.4 Regras de alerta (versão inicial)
Limiares de partida, a ajustar por cultura pela base de culturas **[verificar com fonte agronômica]**.

| Alerta | Condição | Exemplo |
|---|---|---|
| Geada | Previsão Tmin ≤ 2 °C nos próximos 7 dias **e** cultura sensível no campo | "Risco de geada na quinta (mín. 1 °C). Seu feijão está em fase sensível." |
| Calor | Previsão Tmax ≥ limiar da cultura em floração/enchimento | "3 dias acima de 35 °C quando a soja enche os grãos." |
| Chuva forte | Previsão > 50 mm/dia **ou** > percentil 95 local | "Chuva forte no sábado. Seu terreno é inclinado: risco de erosão." |
| Seca | Anomalia de umidade (z) ≤ −1 **e** pouca chuva prevista | "Solo mais seco que o normal e pouca chuva nos próximos 7 dias." |
| Solo descoberto | Mês sem cultura **e** início da estação chuvosa local | "Campo sem cobertura e as chuvas estão começando." |

Prioridade: risco à lavoura atual > risco ao solo > oportunidades. Para o Hemisfério Sul e o Norte, usar **meses locais** (a climatologia do ponto define as estações, não o calendário fixo).

---

## 6. Aba 2: AgroAI (chat com Gemini)

### 6.1 Contexto de cada resposta
Perfil e indicadores de **uma** fazenda são pequenos e **entram direto no prompt**. A **busca (RAG)** é usada para a **base de conhecimento**.

```text
Pergunta do produtor
   ├─► [1] Perfil da fazenda (JSON do banco)
   ├─► [2] Snapshot do dia (indicadores, alertas, estratégias, com fonte/data/confiança)
   ├─► [3] Top-k trechos da base de conhecimento (busca vetorial)
   └─► [4] Histórico recente da conversa
                       │
                       ▼
       Gemini (instruções do sistema + [1..4]) ─► resposta + fontes + sugestões
```

**Function calling do Gemini (recomendado se der tempo):** ferramentas como `serie_historica(variavel, inicio, fim)`, `comparar_rotacoes(prioridades)`, `previsao(dias)`, `buscar_evento(tipo, ano)` e `mercado(cultura, pais)`. A última consulta o **Harvest Portal** pela API (ou pelo MCP `https://mcp.harvestportal.org/mcp`, como em `ARQUITETURA-COMPLETA.md`; **[verificar]** suporte a MCP no SDK do Gemini). O modelo busca o dado sob demanda e a API devolve **números calculados pelo nosso código**, nunca pelo modelo.

### 6.2 Base de conhecimento (para indexar)
| Conteúdo | Fonte |
|---|---|
| Fichas de culturas (com sinônimos PT/EN/ES), plantas de cobertura, rotação, manejo do solo | FAO ECOCROP, FAO-56, FAO GAEZ, extensão rural (Embrapa, USDA NRCS, etc.) |
| Explicação dos dados e termos | `tools/*.md`, glossário da equipe, `CONTEXTO-DESAFIO.md` |
| Limitações de cada dataset | Seções "limitações" de `tools/*.md` |

Pequena e bem escolhida (20 a 50 documentos), respeitando licenças. Indexar por idioma ou usar embeddings multilíngues.

### 6.3 Regras de comportamento (prompt de sistema)
1. Responder no **idioma do usuário**, em linguagem simples, adaptada ao **perfil A–C** e ao **papel** (produtor ou técnico).
2. **Usar só números presentes no contexto.** Se não houver, dizer "não tenho essa informação" e sugerir onde conseguir.
3. **Citar fonte e data:** "(NASA SMAP L4, dado de 12/11)".
4. Dizer a **escala** quando relevante: "esse dado cobre cerca de 9 km ao redor do seu campo".
5. Em sugestões de rotação, sempre: **por que · evidência · benefícios · o que não sabemos · o que conferir com o técnico**.
6. **Nunca prescrever:** sem "plante X", sem dosagem de adubo ou agrotóxico (encaminhar ao técnico).
7. Fora do tema agricultura/fazenda: responder curto e voltar ao tema.
8. Terminar com **2 ou 3 perguntas sugeridas** (viram botões).

**Saída estruturada:** pedir ao Gemini resposta em JSON com esquema (`texto`, `fontes[]`, `sugestoes[]`, `tabela?`) para o front renderizar com segurança **[verificar suporte a response schema no modelo escolhido]**.

### 6.4 Perguntas de teste
- "Vai dar geada essa semana?"
- "Meu solo está seco?"
- "O que eu posso plantar depois da soja?" → **comparação de 3 estratégias**
- "Em 2021 perdi o milho por seca, os dados mostram isso?"
- "O que é NDVI?"
- "Os últimos anos foram mais secos aqui?"
- Em inglês/espanhol: "Should I add a cover crop after harvest?" / "¿Cuándo es mejor sembrar aquí?"

### 6.5 Exemplo
> **Dona Marta:** o que posso plantar depois da soja?
>
> **AgroAI:** Seu campo fica sem nada de abril a outubro. No satélite (NASA MODIS, 2001–2025) ele aparece sem cobertura nesses meses quase todo ano, e as chuvas fortes de novembro (NASA POWER) chegam com a terra exposta.
>
> | | Atual (soja → vazio) | Soja → milheto | Soja → milho + capim |
> |---|---|---|---|
> | Solo | piora | melhora | melhora muito |
> | Erosão | alta | baixa | baixa |
> | Água | pouca | pouca | média, com risco |
> | Confiança | alta | média | média-baixa |
>
> **Para conversar com seu técnico:** milheto depois da soja. **Por quê:** protege a terra e aguenta pouca chuva. **O que não sei:** se há semente na sua região. **Confira:** a data limite de plantio antes de a chuva acabar.
>
> *Quem decide é você.* [Como planto milheto?] [E o milho com capim?]

---

## 7. Dados e atualização

### 7.1 Fluxo
```text
Onboarding concluído ─► processamento inicial (background task)
   ├─ NASA POWER diário 1981→hoje: climatologia, tendências, GDD, geada, calor, ET0
   ├─ SoilGrids (uma vez) · SRTM (uma vez) · FAO GAEZ (uma vez)
   ├─ MODIS NDVI histórico via AppEEARS (assíncrono) → calendário de solo descoberto
   ├─ SMAP L4 recente · GLDAS (série longa de umidade)
   ├─ cruza perdas lembradas (bloco 5) com os dados
   └─ gera snapshot + estratégias

Todo dia (cron, ex.: 05:00 UTC) ─► para cada fazenda
   ├─ previsão 7 dias (Open-Meteo)
   ├─ dias novos do POWER · SMAP L4 mais recente · IMERG Late
   ├─ NDVI novo, se houver
   ├─ recalcula anomalias e avalia alertas
   └─ salva SnapshotDia
```

**Cache por célula de grade:** fazendas no mesmo pixel compartilham o dado (POWER ~0,5°, SMAP 9 km, GLDAS ~0,25°). Chave do cache = `(dataset, célula, data)`.

### 7.2 Acesso às fontes
| Fonte | Como | Login | Nota |
|---|---|---|---|
| NASA POWER | REST por ponto | Não | `tools/NASA_POWER.md` |
| SMAP L4, MODIS, HLS, GPM IMERG | `earthaccess` (Python) / AppEEARS API | **Earthdata Login** (gratuito) | `tools/EARTHACCESS.md`, `tools/APPEEARS.md` |
| GLDAS | earthaccess | Earthdata | `tools/GLDAS.md` |
| ERA5 (segunda opinião, opcional) | Copernicus CDS | Conta CDS | `tools/ERA5.md` |
| Harvest Portal | API CKAN (`datastore_search`) / MCP | Não | `tools/NASA_HARVEST_PORTAL_API.md` |
| SRTM | AppEEARS / earthaccess | Earthdata | `tools/SRTM.md` |
| SoilGrids | REST por ponto | Não | `tools/SOILGRIDS.md` |
| FAO GAEZ v5 | Download de rasters | Não | `tools/FAO_GAEZ.md` (D-004) |
| Open-Meteo | REST por ponto | Não | Previsão |

Credenciais (Earthdata, Gemini) só em variáveis de ambiente no back-end.

---

## 8. Arquitetura técnica

### 8.1 Stack
| Camada | Escolha |
|---|---|
| Front-end | **React + Vite + TypeScript**, React Router, Tailwind, **Leaflet** (mapa), **Recharts** (gráficos), **i18next** (PT/EN/ES) |
| API | **FastAPI** (Python 3.11+), Pydantic, Uvicorn |
| Dados científicos | pandas, xarray, numpy, `earthaccess`, httpx |
| Banco | **PostgreSQL + pgvector** (para o hackathon, SQLite + vetores em memória/FAISS também serve **[decidir]**) |
| Autenticação | E-mail + senha com hash (bcrypt/argon2) + **JWT** no header `Authorization: Bearer` |
| Jobs | APScheduler dentro da API, ou cron chamando `python -m jobs.diario` |
| LLM | **Gemini API** via SDK `google-genai`. Modelo **[decidir/verificar]**: uma versão "Flash" para chat e extração (rápida e barata); "Pro" só se a qualidade não bastar |
| Embeddings | **Gemini embeddings** (multilíngue) **[verificar nome do modelo atual]** |
| Hospedagem | Front: Vercel/Netlify · API: Render/Railway/Fly **[decidir]** |

### 8.2 Endpoints REST
```text
POST /auth/register                 {email, senha, nome, idioma}  → {token}
POST /auth/login                    {email, senha}                → {token}
GET  /me                                                          → usuário

POST /onboarding/interpretar        {campo: "culturas"|"excluidas"|"equipamentos", texto, idioma}
                                                                  → itens casados com a base (Gemini)
PUT  /fazenda                       respostas do questionário     → fazenda (dispara processamento)
GET  /fazenda                                                     → fazenda + status do processamento

GET  /dashboard                                                   → SnapshotDia mais recente
GET  /dashboard/serie/{variavel}?inicio&fim                       → série para gráfico
GET  /estrategias                                                 → 3 estratégias com cartões
GET  /culturas?q=&idioma=                                         → base de culturas (para o fallback com ícones)

POST /chat                          {conversa_id?, mensagem}      → {resposta, fontes[], sugestoes[]}
GET  /chat/{conversa_id}                                          → histórico
```

### 8.3 Estrutura de pastas
```text
agroia/
├── web/                     # React
│   └── src/
│       ├── pages/           # Login, Cadastro, Onboarding, Dashboard, AgroAI, Fazenda
│       ├── components/      # Card, AlertBar, StrategyCard, Calendar12, MapPicker, ChatBox
│       ├── api/             # cliente REST
│       └── i18n/            # pt.json, en.json, es.json
├── api/                     # FastAPI
│   ├── main.py
│   ├── auth/
│   ├── routers/             # auth, onboarding, fazenda, dashboard, estrategias, chat
│   ├── fontes/              # clientes: power.py, smap.py, modis.py, imerg.py, soilgrids.py, srtm.py, gldas.py, gaez.py, harvest.py, openmeteo.py
│   ├── indicadores/         # climatologia, anomalias, gdd, geada, calor, et0, balanço, solo descoberto
│   ├── alertas/             # regras da seção 5.4
│   ├── rotacao/             # geração, filtro de viabilidade, pontuação MCDA, cartões
│   ├── llm/                 # cliente Gemini, prompts, esquemas JSON, RAG
│   └── models/              # SQLAlchemy/Pydantic
├── jobs/                    # processamento inicial e diário
├── conhecimento/            # documentos da base RAG
├── base/                    # culturas.json (com sinônimos PT/EN/ES), equipamentos.json
└── dados_demo/              # cache das fazendas de demonstração
```

### 8.4 Modelo de dados (resumo)
```yaml
Usuario:     { id, email, senha_hash, nome, idioma, criado_em }
Fazenda:     { id, usuario_id, lat, lon, pais, regiao, perfil: A|B|C|D,
               irrigacao, animais, terreno, respostas_onboarding (JSON),
               prioridades[≤3], culturas_excluidas[{cultura_id, motivo}],
               equipamentos[], status_processamento }
Calendario:  { fazenda_id, itens[{cultura_id, inicio_mes, fim_mes, consorcio_com[], perene, texto_original}] }
Cultura:     { id, nomes{pt[], en[], es[]}, familia, tipos[], ciclo_dias, perene, sensivel_geada,
               tmax_critico, demanda_agua_mm, kc{}, fixa_n, raiz_profunda, equipamento_min[] }
SnapshotDia: { fazenda_id, data, previsao[], clima_30d{}, umidade_solo{}, ndvi{}, solo{}, relevo{},
               agua_solo_historico{}, alertas[], fontes[{dataset, data_dado, resolucao, confianca}] }
Estrategia:  { fazenda_id, calculada_em, nome, eh_atual, sequencia[], notas{}, confianca,
               por_que, evidencias[], beneficios[], lacunas[], riscos[] }
Conversa:    { id, usuario_id, mensagens[{papel, texto, fontes[], criado_em}] }
Trecho:      { id, doc, idioma, texto, embedding }
```

---

## 9. Motor de estratégias (resumo)
Detalhe em `Field Shift Brasil — Documentação do Projeto.md` (Metodologia):
1. Indicadores mensais por ponto (grade comum, passo mensal; cada um guarda a resolução de origem).
2. Candidatas a partir das 4 famílias (fixadoras de N, cobertura, raiz profunda, tolerantes à seca) que **cabem nas janelas climáticas do local** (GDD, geada, calor, água), checadas com o **FAO GAEZ**.
3. Filtro por restrições do produtor (culturas excluídas, equipamentos, irrigação).
4. Nota por critério (água, solo, nitrogênio, erosão, forragem, renda, pragas), ponderada pelas **prioridades** escolhidas.
5. Atual + 2 alternativas **diferentes entre si**.
6. Cartão com textos gerados por **template** a partir dos números. O Gemini só reescreve em linguagem simples, sem alterar números.
7. **Perenes** (café, frutíferas, pastagem): em vez de trocar de cultura, sugerir cobertura nas entrelinhas e manejo do solo.

---

## 10. Privacidade e segurança
- Localização da fazenda é dado pessoal. **Ao Gemini vão só coordenadas arredondadas, culturas e indicadores**, nunca nome ou e-mail.
- Chaves (Gemini, Earthdata) só no back-end, em `.env` fora do git.
- Senhas com hash; JWT com expiração.
- Permitir apagar a conta e os dados.
- Avisar no cadastro para que os dados são usados.

---

## 11. Escopo do hackathon

### MVP (precisa funcionar na demo)
1. Cadastro/login simples.
2. Onboarding com os blocos 1, 2, 3 e 6 completos (bloco 4 e 5 simplificados, se faltar tempo) e interpretação por Gemini na pergunta 8.
3. **2 ou 3 fazendas de demonstração** em países diferentes, com dados em cache.
4. Dashboard com os cards **1, 2, 3, 4, 5 e 9**.
5. Chat AgroAI com perfil + snapshot + base pequena, citando fontes, em PT e EN.
6. Comparação de 3 rotações no Dashboard **e** no chat.
7. Aviso "apoio, não substituição" visível.

### Se sobrar tempo
Cards 6, 7, 8 e 10 · job diário em produção · function calling · cruzamento das perdas lembradas · espanhol · enriquecimento por país (Brasil: ZARC/MapBiomas) · simulador "e se chover menos?" · exportar relatório.

### Fora do escopo
App nativo · vários talhões por fazenda · polígono do talhão · sensores em campo · preços de mercado · dosagem de insumos.

---

## 12. Pendências e conflitos
0. **Aprovar a Open-Meteo** como fonte de previsão (S-7). É a única fonte fora da D-009.
1. **Registrar D-010 "Escopo: mundo todo"** em `DECISOES.md`, substituindo a D-008. Consequências: D-003 deixa de ser "fora" e vira "enriquecimento só para os EUA"; as fontes brasileiras da D-009 (MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM) viram enriquecimento só para o Brasil; a demo usa pontos em países diferentes; base de culturas e textos em PT/EN/ES.
2. **Confirmar se "Rest" = React** (S-1).
3. **Modelo Gemini e de embeddings:** escolher e verificar nomes atuais e limites da cota gratuita.
4. **Fonte de solo (Q-07):** este documento assume **SoilGrids** (global, API por ponto) + GAEZ para aptidão. Fecha a inconsistência I-1.
5. **Escolher as fazendas de demonstração** (seção 2).
6. **Banco:** PostgreSQL + pgvector ou SQLite no hackathon.
7. **Idioma da apresentação:** júri global provavelmente em inglês **[verificar]** (Q-05).
