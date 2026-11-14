# Comparativo final das ferramentas

> 14/11/2026. Consolida as três análises sobre as ferramentas do projeto e propõe a lista final para a **D-010**:
> - **PROS-E-CONTRAS:** `tools/PROS-E-CONTRAS-FERRAMENTAS.md`
> - **Yury:** `tools/comparative/YURY-COMPARATIVO_tool.md`
> - **Guilherme:** `tools/comparative/guilherme_comparativo_tools.md`
>
> Legenda: 🟢 essencial · 🟡 se der tempo · ⚪ pitch / próximo passo · 🔴 fora

## 1. Resultado em uma tabela

| Ferramenta | PROS-E-CONTRAS | Yury | Guilherme | **Final** | Por quê |
|---|---|---|---|---|---|
| **Base de culturas** (própria) | não avaliada | 🟢 nº 1 | 🟢 (obrigatória) | 🟢 **nº 1** | Todo o motor depende dela, e ela ainda não existe |
| NASA POWER | 🟢 | 🟢 | 🟢 | 🟢 | Unânime |
| SoilGrids | 🟢 | 🟢 | 🟢 | 🟢 | Unânime. Fallback para "só respostas do produtor" em área urbana |
| SRTM via OpenTopoData | 🟢 | 🟢 | 🟢 | 🟢 | Unânime. Pedir uma **grade de vizinhos** (ex.: 3×3) para calcular declividade |
| NDVI (MODIS + VIIRS) | 🟢 | 🟢 (preferir VIIRS) | 🟢 (VIIRS para dados novos) | 🟢 | MODIS para o histórico; **VIIRS como continuidade** (ver §3) |
| AppEEARS + conta Earthdata | 🟢 | 🟢 | 🟢 | 🟢 | Unânime. A conta Earthdata entra na preparação |
| **IBGE PAM** | 🟡 | **🟢** | 🟡 condicional | **🟢 (pontos no Brasil)** | Ver §2.1 |
| SMAP L4 | 🟡 | 🟡 primeira a subir | 🟡 primeira a subir | 🟡 **1º da fila** | Sai no mesmo pedido do AppEEARS que o NDVI |
| GPM IMERG + earthaccess | 🟡 | 🟡 | 🟡 | 🟡 **2º da fila** | Unânime. Exige abrir NetCDF |
| **ZARC** | 🟡 | 🟡 **como preparação** | 🟡 só Brasil | 🟡 **preparação** | Ver §2.2 |
| **crop-cycle-detection** | 🟡 | ⚪ | 🟡 (regra simples primeiro) | **Regra simples no MVP; biblioteca ⚪** | Os três concordam em começar pela regra simples |
| Nominatim | não avaliada | 🟡 | — | 🟡 | Busca do campo por endereço |
| NASA GIBS | não avaliada | 🟡 | — | 🟡 | Camadas visuais no mapa |
| **NASA Harvest Portal (API)** | 🟡 opcional | ⚪ | ⚪ | ⚪ | 2 de 3. Só as culturas atuais, escala nacional, licença incerta |
| **FAO GAEZ v5** | 🔴 (⚪ citar) | 🔴 | ⚪ **forte** | ⚪ **forte** | Ver §2.3 |
| **HLS** | 🔴 (⚪ citar) | 🔴 | ⚪ | ⚪ | Mesmo efeito prático: não implementa, cita como evolução |
| **FIRMS** | 🔴 | 🔴 (volta com Cerrado) | ⚪ condicional | ⚪ **condicional** | Volta se a região da demo tiver fogo frequente |
| INMET / CEMADEN | ⚪ | ⚪ | ⚪ | ⚪ | Unânime |
| Embrapa Solos | ⚪ | ⚪ | ⚪ | ⚪ | Unânime (depende da Q-07) |
| Earthdata Search / CMR | ⚪ | ⚪ | ⚪ | ⚪ uso da equipe | Unânime |
| GLDAS | 🔴 | 🔴 | 🔴 | 🔴 | Unânime |
| ERA5 / ERA5-Land | 🔴 | 🔴 | 🔴 | 🔴 | Unânime |
| MapBiomas | 🔴 | 🔴 | 🔴 | 🔴 | Unânime |
| Sentinel-1 | 🔴 | 🔴 | 🔴 | 🔴 | Unânime |
| Harvest MCP | 🔴 | 🔴 | 🔴 | 🔴 | Unânime |
| Presto, Galileo, CropHarvest, crop-mask | — | — | 🔴 | 🔴 | São ML; a arquitetura descarta ML |
| MOD16A2 (ET real) | — | — (cita que não é necessário) | 🔴 | 🔴 | ET₀ do POWER × Kc da base de culturas já atende |
| GRACE, ECOSTRESS, Landsat separado | 🔴 | 🔴 | 🔴 | 🔴 | Já fora pela D-009 |

**Concordância:** das 30 linhas, **24 têm consenso** entre as três análises. As 6 divergências estão resolvidas na seção 2.

## 2. As divergências e como foram resolvidas

### 2.1 IBGE PAM: 🟢 para pontos no Brasil
- **Yury:** sobe para 🟢, porque o critério "renda extra" do motor não tem nenhum dado sem ele, e ele é barato.
- **Guilherme:** condicional, porque o motor não tem critério de mercado definido.
- **Resolução:** os dois apontam o mesmo problema: **"renda extra" hoje não tem evidência**. O desafio cita "market suitability" e "supplemental income" explicitamente, então o critério precisa de dado. A PAM é a única fonte barata que sobrou. **Fica 🟢 para pontos no Brasil**, como evidência do critério renda: *"essa cultura tem produção registrada e valor de produção no seu município"*. Fora do Brasil, o critério usa só o que o produtor informa (pergunta 26a) e diz isso no cartão.
- **Limite a deixar claro:** culturas de cobertura (crotalária, braquiária) quase não aparecem na PAM; para elas, "sem dado de mercado", nunca zero.

### 2.2 ZARC: só na preparação
- **Yury:** usar só para montar a base de culturas, não ao vivo.
- **Guilherme:** complementar, só Brasil.
- **Resolução:** a proposta do Yury resolve também a preocupação do Guilherme. As janelas de plantio do ZARC são baixadas **uma vez** e entram na base de culturas como janela de referência por região. Sem custo ao vivo e sem risco na demo.

### 2.3 FAO GAEZ v5: ⚪ pitch forte
- **PROS-E-CONTRAS e Yury:** 🔴, porque a base de culturas faz o filtro e os cenários do motor cobrem o futuro.
- **Guilherme:** ⚪ forte, porque é o único dado da lista que mostra o "shift" futuro por cultura.
- **Resolução:** **⚪ pitch forte**. Não entra no MVP, mas é a **primeira ferramenta a subir** se sobrar uma pessoa: basta a camada base das culturas da demo, baixada uma vez.

### 2.4 Harvest Portal: ⚪
2 de 3 análises pedem ⚪. As 4 culturas da tabela (soja, milho, trigo, arroz) são as que o produtor já planta, não as alternativas que o motor sugere. Fica como menção no pitch.

### 2.5 crop-cycle-detection: regra simples primeiro
As três análises concordam no essencial: **o MVP usa uma regra simples** (NDVI suavizado abaixo de um limiar confirma os meses descobertos). A biblioteca entra só se a regra simples funcionar e sobrar tempo. Fica ⚪ como evolução.

### 2.6 HLS e FIRMS
Diferença só de nome (🔴 com "citar no pitch" × ⚪). Ficam ⚪; o FIRMS volta se a região da demo tiver fogo frequente.

## 3. Pontos novos trazidos pelas análises

| Ponto | Origem | Decisão |
|---|---|---|
| **Base de culturas é a peça nº 1** | Yury, Guilherme | Adotado. É a primeira entrega |
| **SRTM precisa de vizinhos** para declividade | Yury, Guilherme | Adotado. O conector pede uma grade 3×3 numa chamada; confirmar o limite de pontos do OpenTopoData |
| **Continuidade MODIS → VIIRS** | Yury (`VNP13A1`), Guilherme (`VJ113A1`) | Adotado. O `VNP13A1.002` foi visto no catálogo do AppEEARS no teste de 14/11; o `VJ113A1` precisa ser confirmado. A data de desligamento do MODIS vem da nota `MODIS_VIIRS.md` **[verificar]** |
| **Selo de confiança sem ERA5/GLDAS** | Yury | Adotado (ver §4) |
| **SoilGrids vazio em área urbana** | Guilherme | Adotado. Pontos da demo rurais; o motor cai para "só respostas do produtor" |
| **Infra obrigatória**: API do Claude, PostgreSQL + PostGIS | Guilherme | Adotado (entra na lista de preparação) |
| **Conta Earthdata Login** | Yury | Adotado (preparação) |

## 4. Selo de confiança do MVP

Proposta do Yury, adotada:

| Nível | Quando |
|---|---|
| **Alta** | O produtor e o dado concordam, **ou** duas fontes independentes concordam (ex.: chuva POWER × IMERG) |
| **Média** | Só há o dado regional (POWER, SoilGrids, NDVI 250 m), sem confirmação |
| **Baixa** | O produtor e o dado discordam, **ou** a escala do dado é muito maior que o campo |

## 5. Lista final proposta para a D-010

| Prioridade | Ferramentas |
|---|---|
| 🟢 **Essencial** | Base de culturas (com as janelas do ZARC), NASA POWER, SoilGrids, SRTM via OpenTopoData (grade de vizinhos), NDVI pelo AppEEARS (MODIS + VIIRS), IBGE PAM (pontos no Brasil) |
| 🟢 **Infra e preparação** | Conta Earthdata Login, API do Claude, PostgreSQL + PostGIS |
| 🟡 **Se der tempo, nesta ordem** | SMAP L4 → GPM IMERG (+ earthaccess) → Nominatim → NASA GIBS → crop-cycle-detection |
| ⚪ **Pitch** | FAO GAEZ v5 (primeira a subir), Harvest Portal, HLS, INMET/CEMADEN, Embrapa Solos, FIRMS (condicional), Earthdata Search/CMR (uso da equipe) |
| 🔴 **Fora** | GLDAS, ERA5, MapBiomas, Sentinel-1, Harvest MCP, modelos de ML (Presto, Galileo, CropHarvest, crop-mask), MOD16A2, GRACE, ECOSTRESS, Landsat separado |

**Datasets da lista oficial do desafio no núcleo:** POWER, SRTM e MODIS/VIIRS (3). Com SMAP L4 e IMERG, chegam a 5.

## 6. Escopo: Brasil ou global

O Guilherme apontou o conflito entre os documentos "Field Shift **Brasil**" (D-008) e a arquitetura **global**. A lista final já resolve na prática:

- **O núcleo é global** (POWER, SoilGrids, SRTM, NDVI): o motor funciona em qualquer ponto rural do mundo.
- **PAM e ZARC são camadas extras para pontos no Brasil**.
- **A demo é no Brasil**, com regiões contrastantes (Q-01).

Proposta: registrar isso na D-010 como "núcleo global, extras brasileiros, demo no Brasil", o que mantém a D-008 válida para a demo e para o pitch.

## 7. Documentos a ajustar depois da D-010

Juntando os conflitos levantados pelo Yury e pelo Guilherme:

| # | Ajuste | Onde |
|---|---|---|
| 1 | Tirar ECOSTRESS, HLS, MOD16, GAEZ, GRACE e WorldCover da integração e das pendências | `application/architecture/INTEGRACAO-DE-DADOS.md`, `COLETA.md` |
| 2 | Acrescentar o VIIRS como continuidade do MODIS | `INTEGRACAO-DE-DADOS.md`, `MODIS_VIIRS.md` |
| 3 | Trocar o acesso do SRTM para OpenTopoData com grade de vizinhos | `SRTM.md` §5 |
| 4 | Refazer os testes que dependem de GRACE, ECOSTRESS, Harvest e MCP (testes 6, 11, 15 e 17) | `application/prompts/examples/tests/TESTES_CHAT_SR_JOSE.md` |
| 5 | Tirar os trechos de Harvest e MCP e incluir SoilGrids e OpenTopoData | `tools/REFERENCIA_APIS.md` (referência do time, **fora do RAG do produto**) |
| 6 | Marcar a fórmula `clima × mercado` como proposta descartada | `tools/NASA_POWER_X_HARVEST_PORTAL.md` |
| 7 | Atualizar o nome do arquivo de testes e o padrão de nomes | `tools/PROS-E-CONTRAS-FERRAMENTAS.md` |
| 8 | Registrar a D-010 e marcar a D-009 como substituída | `context/DECISOES.md` |
