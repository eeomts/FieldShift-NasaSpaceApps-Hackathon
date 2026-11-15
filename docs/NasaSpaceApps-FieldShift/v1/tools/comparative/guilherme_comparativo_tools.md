> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# Análise das ferramentas × arquitetura do Field Shift

> Documento para discussão da equipe (14/11/2026). Cruza o `PROS-E-CONTRAS-FERRAMENTAS.md` com a arquitetura do projeto (`ARQUITETURA-COMPLETA.md`, `COLETA.md`, `INTEGRACAO-DE-DADOS.md`, `MOTOR-DE-ANALISE.md`, `DASHBOARD-E-CHAT.md`, `BANCO-DE-DADOS.md`) e com as documentações de cada ferramenta. As posições são **propostas**; a decisão final vai para a **D-010** no `context/DECISOES.md`.

## Sumário

1. [Critério usado](#1-critério-usado)
2. [Resumo](#2-resumo)
3. [Úteis (núcleo)](#3-úteis-núcleo)
4. [Complementares](#4-complementares)
5. [Pitch / próximo passo](#5-pitch--próximo-passo)
6. [Desnecessárias](#6-desnecessárias)
7. [Onde esta análise diverge do PROS-E-CONTRAS](#7-onde-esta-análise-diverge-do-pros-e-contras)
8. [Conflitos a resolver antes da D-010](#8-conflitos-a-resolver-antes-da-d-010)
9. [Ordem de implementação sugerida](#9-ordem-de-implementação-sugerida)

---

## 1. Critério usado

A arquitetura define as regras que decidem a classificação:

| Princípio da arquitetura | Consequência para as ferramentas |
|---|---|
| **Quem faz as contas é o motor** (perfil, retrato do solo, match das rotações) | A IA não busca números fora do motor. Ferramentas que levam a IA a calcular ficam de fora |
| **Sem ML** | Modelos pré-treinados ficam de fora; regras simples e MCDA ficam |
| **Meses descobertos vêm do calendário do produtor**; o satélite só confirma | O NDVI é evidência de confirmação, não a fonte principal |
| **Sem critério de mercado**; "renda extra" só conta culturas comerciais | Fontes de mercado só entram se a equipe criar esse critério |
| **Integração rápida:** POWER, SoilGrids, SRTM (OpenTopoData) | Essas três respondem na hora e formam o núcleo |
| **Integração lenta:** AppEEARS (e IMERG) | Pedidos assíncronos, sempre pré-calculados para a demo |
| **App global** (testado em 5 continentes) | Fontes só do Brasil viram camada extra para pontos brasileiros |

**Categorias:**

- 🟢 **Úteis:** sem elas, a coleta ou o motor não funcionam.
- 🟡 **Complementares:** melhoram um cálculo ou um cartão; entram depois do núcleo pronto.
- ⚪ **Pitch / próximo passo:** citar na apresentação como evolução, sem implementar.
- 🔴 **Desnecessárias:** repetem outra fonte, custam mais do que entregam ou contradizem a arquitetura.

**Nível de evidência** (herdado do `PROS-E-CONTRAS`): 🧪 testado ao vivo em 14/11/2026 · 📄 só documentação.

---

## 2. Resumo

| Ferramenta | Tipo | Classificação | Evidência | Em uma frase |
|---|---|---|---|---|
| NASA POWER | Clima | 🟢 Útil | 🧪 | Base de todo o clima do motor |
| SoilGrids | Solo | 🟢 Útil | 🧪 | Único solo global por ponto com API |
| SRTM (OpenTopoData) | Relevo | 🟢 Útil | 🧪 | Declividade e baixadas, barato |
| MODIS NDVI | Vegetação | 🟢 Útil (pré-calculado) | 📄 / 🧪 catálogo | Confirma os meses descobertos |
| AppEEARS | Acesso | 🟢 Útil | 🧪 | Caminho do MODIS e do SMAP por ponto |
| SMAP L4 | Umidade | 🟡 Complementar | 📄 / 🧪 catálogo | Mesmo pedido do MODIS, custo extra quase zero |
| GPM IMERG | Chuva | 🟡 Complementar | 🧪 catálogo | Chuva extrema e confiança POWER × IMERG |
| earthaccess | Acesso | 🟡 Só com IMERG | 📄 | Necessário só para o IMERG |
| crop-cycle-detection | Biblioteca | 🟡 Complementar | 📄 (teste local) | Começar com regra simples |
| ZARC | Risco (Brasil) | 🟡 Complementar, só Brasil | 📄 | Valida a janela da rotação |
| IBGE PAM | Produção (Brasil) | 🟡 Condicional, só Brasil | 📄 | Só se virar evidência em "renda extra" |
| FAO GAEZ v5 | Aptidão | ⚪ Pitch forte | 📄 | Cenários futuros; melhor candidata a subir |
| NASA Harvest Portal (API) | Mercado | ⚪ Pitch | 🧪 | Nacional, 4 culturas, licença incerta |
| INMET / CEMADEN | Estações (Brasil) | ⚪ Pitch | 📄 | No máximo um exemplo pré-calculado |
| Embrapa Solos | Solo (Brasil) | ⚪ Pitch | 📄 | Depende da Q-07 |
| HLS | Vegetação 30 m | ⚪ Pitch | 📄 / 🧪 catálogo | Evolução natural do MODIS |
| FIRMS | Fogo | ⚪ Condicional | 📄 | Só se a demo for no Cerrado com fogo |
| Earthdata Search / CMR | Acesso | ⚪ Uso da equipe | 🧪 CMR | Inventário, fora do app |
| GLDAS | Umidade | 🔴 Desnecessária | 📄 | Repete POWER e SMAP L4 |
| ERA5 / ERA5-Land | Clima | 🔴 Desnecessária | 📄 | Cara; a confiança vem de POWER × IMERG |
| MapBiomas | Uso do solo (Brasil) | 🔴 Desnecessária | 📄 | O produtor informa a rotação |
| Sentinel-1 | Radar | 🔴 Desnecessária | 📄 | Processar radar em 48 h é inviável |
| NASA Harvest MCP | Acesso (chat) | 🔴 Desnecessária | 📄 (teste local) | Contradiz "a IA nunca calcula" |
| Presto, Galileo, CropHarvest, crop-mask | ML | 🔴 Desnecessária | 📄 | A arquitetura descarta ML |
| MOD16A2 (ET real) | Evapotranspiração | 🔴 Proposta: cortar | — | ET₀ do POWER × Kc já atende |
| GRACE, ECOSTRESS, Landsat separado | — | 🔴 Já fora (D-009) | — | Ainda citadas em documentos |

**Datasets da lista oficial do desafio no núcleo:** POWER, SRTM e MODIS (3). Com SMAP L4 e IMERG, chegam a 5.

---

## 3. Úteis (núcleo)

| Ferramenta | Onde entra na arquitetura | Ponto de atenção |
|---|---|---|
| **NASA POWER** | Cálculo 3 (geada, água, graus-dia, ET₀), "Você disse × os dados mostram", cenários "e se" | Os últimos 2 a 3 meses são provisórios. Cache por célula para evitar o erro 429 |
| **SoilGrids** | Cálculo 2, retrato do solo (peso 0,4 na fusão de evidências) | **Devolve vazio em área urbana** (3 de 5 pontos urbanos vazios no teste). Os pontos da demo devem ser rurais, e o motor precisa cair para "só respostas do produtor" sem quebrar. Uma chamada levou 17 s: usar cache |
| **SRTM via OpenTopoData** | Critério "evitar erosão" (cobertura × declividade) e baixadas com risco de geada; altitude para o `site-elevation` do POWER | **Um ponto só não dá declividade.** Pedir uma pequena grade de vizinhos (ex.: 3×3) numa única chamada. ⚠️ Confirmar o limite de pontos por requisição |
| **MODIS NDVI (MOD13Q1)** | Cartão "meses descobertos" e conferência do calendário informado | **Confirma**, não decide. Entra pré-calculado. A série 2000–2025 é MODIS; para dados novos, usar o VIIRS do NOAA-20 (`VJ113A1`), porque o MODIS está em desligamento |
| **AppEEARS** | Caminho do MODIS e do SMAP por ponto, em CSV e com a qualidade decodificada | Assíncrono e com token de 48 h: nunca no caminho ao vivo |

Fora da lista de dados, também são obrigatórias para a arquitetura: **API do Claude** (coleta do texto livre e chat), **PostgreSQL + PostGIS** (cache, fila de jobs) e a **base de culturas própria** (ciclo, Kc, geada, calor, água, nitrogênio, família botânica).

---

## 4. Complementares

| Ferramenta | O que acrescenta | Condição para entrar |
|---|---|---|
| **SMAP L4** | Cartão "quantos dias o solo aguenta sem chuva" (critério água) | **Primeira a subir**: vem no mesmo pedido do AppEEARS que o MODIS. Sem ele, usar o `GWETROOT` do POWER |
| **GPM IMERG** | Chuva forte em solo descoberto (erosão), veranicos e a comparação POWER × IMERG para o nível de confiança | Segunda a subir, se alguém já souber abrir NetCDF com `xarray`. A versão Final tem meses de atraso |
| **earthaccess** | Login e download do IMERG | Só entra junto com o IMERG |
| **crop-cycle-detection** | Conta as safras e acha os meses descobertos no NDVI | Começar com a regra simples (NDVI suavizado abaixo do limiar) e trocar pela biblioteca se funcionar. É regra, não ML |
| **ZARC** | Confere se a janela da rotação está dentro do risco oficial | **Só Brasil.** Num app global, é camada extra para pontos brasileiros. Download único da tábua de risco |
| **IBGE PAM** | "Isso se planta e rende no seu município?" e quebra em anos secos | **Só Brasil** e **condicional**: o motor não tem critério de mercado. Só entra se a equipe decidir usá-la como evidência dentro de "renda extra" |

---

## 5. Pitch / próximo passo

| Ferramenta | Por que citar | Por que não implementar agora |
|---|---|---|
| **FAO GAEZ v5** | Cenários futuros de aptidão por cultura: é o tema central do "Field Shift" | Sem API; uma camada por cultura e cenário. **Melhor candidata a subir** se sobrar uma pessoa: basta a camada base (2001–2020) das culturas da demo, baixada uma vez |
| **NASA Harvest Portal (API)** | Programa oficial de agricultura da NASA; projeção até 2030 | Escala nacional; só soja, milho, trigo e arroz (as culturas atuais, não as alternativas); licença "não especificada"; 3 recursos quebrados; não está na lista oficial |
| **INMET / CEMADEN** | O desafio pede "satélite × medição em solo" | Limpeza e casamento de estações caros. No máximo um exemplo pré-calculado |
| **Embrapa Solos** | Nome do solo no padrão brasileiro (SiBCS) e restrições (coeso, arênico) | Sem API por ponto; depende da Q-07 |
| **HLS** | NDVI em 30 m, na escala do talhão | Pesado, com lacunas por nuvem. O MODIS e o calendário do produtor bastam para a demo |
| **FIRMS** | Evita sugerir palhada seca onde o entorno queima todo ano | Não muda a maioria das estratégias. Volta se a região da demo for Cerrado com fogo |
| **Earthdata Search / CMR** | Confirma nome, versão e período de cada produto | Uso da equipe, fora do app |

---

## 6. Desnecessárias

| Ferramenta | Motivo |
|---|---|
| **GLDAS** | Repete o `GWETROOT` do POWER e o SMAP L4; NetCDF e login |
| **ERA5 / ERA5-Land** | Conta no CDS, fila e arquivos pesados. A confiança pode vir de POWER × IMERG. O clima do GAEZ deriva dele |
| **MapBiomas** | O produtor já informa a rotação; processamento pesado; só Brasil |
| **Sentinel-1** | Processar radar em 48 h é inviável para a equipe |
| **NASA Harvest MCP** | Contradiz "a IA nunca calcula". Respostas grandes enchem o contexto do agente. O chat usa as ferramentas internas (`ver_ficha`, `consultar_indicador`, `comparar_estrategias`, `criar_cenario`, `atualizar_ficha`, `info_cultura`, `explicar_termo`) |
| **Presto, Galileo, CropHarvest, crop-mask** | São ML; a arquitetura descarta ML (sem dados de rotações reais para treinar, caixa-preta) |
| **MOD16A2 (ET real)** | Está na arquitetura, mas não foi avaliado no `PROS-E-CONTRAS`. Proposta: cortar, porque ET₀ do POWER × Kc da base de culturas atende o critério água |
| **GRACE, ECOSTRESS, Landsat separado** | Já saíram pela D-009 |

---

## 7. Onde esta análise diverge do PROS-E-CONTRAS

| Ferramenta | PROS-E-CONTRAS | Esta análise | Motivo |
|---|---|---|---|
| **NASA Harvest Portal (API)** | 🟡 Opcional, pré-processado | ⚪ Pitch | As 4 culturas são as atuais, não as alternativas; licença não especificada é risco para publicar; o motor não tem critério de mercado |
| **FAO GAEZ v5** | 🔴 Cortar (⚪ citar) | ⚪ Pitch **forte** | Único dado da lista que mostra o "shift" futuro por cultura. Uma camada base para a demo é viável |
| **IBGE PAM** | 🟡 Se der tempo | 🟡 **Condicional** | Depende de a equipe decidir como "renda extra" usa mercado. Só Brasil |
| **SMAP L4** | 🟡 Se der tempo | 🟡 **Primeira a subir** | Sai no mesmo pedido do AppEEARS que o MODIS |
| **MOD16A2** | Não avaliado | 🔴 Cortar | ET₀ do POWER já atende |

Nas demais ferramentas, esta análise **concorda** com o veredito proposto.

---

## 8. Conflitos a resolver antes da D-010

| # | Conflito | Onde corrigir |
|---|---|---|
| 1 | A arquitetura ainda lista **ECOSTRESS** e **HLS** na integração lenta; a D-009 e o `PROS-E-CONTRAS` tiram os dois | `INTEGRACAO-DE-DADOS.md`, `COLETA.md` |
| 2 | **MOD16A2** está na arquitetura, mas não foi avaliado | Incluir no `PROS-E-CONTRAS` e decidir |
| 3 | Os documentos "Field Shift **Brasil**" (D-008) e a arquitetura **global** (5 continentes) | Decidir: app global com extras para o Brasil (ZARC, PAM) ou só Brasil |
| 4 | O `testes-chat-sr-jose.md` testa GRACE, ECOSTRESS, MCP e Harvest | Refazer com as ferramentas internas do chat |
| 5 | O `referencia-apis-field-shift.md` (RAG) tem 13 trechos de Harvest e MCP e **não tem SoilGrids nem OpenTopoData** | Remover e acrescentar |
| 6 | O `SRTM.md` acessa o SRTM pelo AppEEARS; a arquitetura usa o OpenTopoData | Ajustar a seção 5 do `SRTM.md` |
| 7 | O `NASA_POWER_X_HARVEST_PORTAL.md` propõe a fórmula `clima × mercado`, que não existe no motor | Marcar como proposta descartada ou arquivar |
| 8 | O `MODIS_VIIRS.md` alerta para o fim do MODIS; a arquitetura cita só o `MOD13Q1` | Acrescentar o `VJ113A1` como continuidade |

---

## 9. Ordem de implementação sugerida

| Etapa | Ferramentas | Resultado |
|---|---|---|
| 1. Núcleo rápido | POWER, SoilGrids, OpenTopoData (SRTM) | Motor roda para qualquer ponto rural do mundo |
| 2. Núcleo lento | AppEEARS → MODIS NDVI (+ SMAP L4 no mesmo pedido) | Cartão "meses descobertos" e "quantos dias o solo aguenta", pré-calculados |
| 3. Se der tempo | GPM IMERG (+ earthaccess), crop-cycle-detection | Erosão por chuva forte; confiança POWER × IMERG; safras detectadas |
| 4. Extras Brasil | ZARC; PAM se houver decisão sobre "renda extra" | Validação oficial da janela de plantio |
| 5. Pitch | GAEZ v5, HLS, INMET/CEMADEN, Harvest Portal, Embrapa Solos, FIRMS | Evoluções citadas na apresentação |

---

**Argumentos do time:**
-
