> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# Comparativo das ferramentas — análise do Yury

> 14/11/2026. Comparação de cada ferramenta do `tools/PROS-E-CONTRAS-FERRAMENTAS.md` com a arquitetura da aplicação (`application/architecture/README.md`, `INTEGRACAO-DE-DADOS.md`, `MOTOR-DE-ANALISE.md`). A pergunta é: **essa ferramenta alimenta algum cálculo do motor ou alguma tela que outra não alimente?** É uma opinião para a discussão; a decisão final vai para a D-010 no `context/DECISOES.md`.

## Resumo

Os vereditos do `PROS-E-CONTRAS` combinam bem com a arquitetura, bem mais do que a lista da D-009 (17 fontes no núcleo). Concordo com quase todos. Proponho três mudanças de veredito e três acréscimos:

- **Subir o IBGE PAM para 🟢 Essencial.** É barato e é a única fonte de renda que sobrou.
- **Baixar o Harvest Portal e o `crop-cycle-detection` para ⚪ Pitch.** A arquitetura já resolve o que eles fariam.
- **Usar o ZARC só na preparação**, para montar a base de culturas, e não ao vivo.
- **Acrescentar a base de culturas como 🟢 Essencial nº 1.** Todo o motor depende dela, e ela não existe ainda.
- **Acrescentar OpenTopoData, NASA GIBS e Nominatim**, que a arquitetura usa, mas o documento não avalia.
- **Definir o selo de confiança do MVP** a partir de "você disse × os dados", já que ERA5 e GLDAS saem.

## Como a arquitetura usa os dados

- O app trabalha **por ponto e sob demanda**, em duas velocidades: **rápida** (POWER, SoilGrids, SRTM) e **lenta, em fila** (AppEEARS e IMERG).
- O motor faz três cálculos:
  1. **Perfil:** só usa as respostas do produtor.
  2. **Retrato do solo:** usa o SoilGrids (peso 0,4) e as respostas.
  3. **Comparação de rotações:** filtro por graus-dia, geada e água; depois nota por critério (água, terra, erosão, pragas, renda, forragem) com os pesos das prioridades.
- **Os meses sem cobertura vêm do calendário que o produtor informa**; o NDVI só confirma.

## Ferramenta por ferramenta

| Ferramenta | Veredito do PROS-E-CONTRAS | Minha avaliação | Onde entra na arquitetura |
| --- | --- | --- | --- |
| **Base de culturas** | Não avaliada | 🟢 **Essencial nº 1** | Filtro (graus-dia, geada, água) e todos os critérios |
| NASA POWER | 🟢 | 🟢 Concordo | Filtro e critérios de água e erosão |
| SoilGrids | 🟢 | 🟢 Concordo | Retrato do solo |
| SRTM | 🟢 | 🟢 Concordo, com ressalva | Erosão e baixadas com geada |
| MODIS NDVI / VIIRS | 🟢 | 🟢 Concordo, com ressalva | "Você disse × os dados" (confirma o calendário) |
| AppEEARS | 🟢 | 🟢 Concordo | Caminho lento do NDVI e do SMAP L4 |
| **IBGE PAM** | 🟡 | ⬆️ **🟢 Essencial** | Critério de renda e geração de candidatas |
| GPM IMERG | 🟡 | 🟡 Concordo | Chuva forte no critério de erosão |
| SMAP L4 | 🟡 | 🟡 Concordo | Cartão "quantos dias o solo aguenta" |
| ZARC | 🟡 | 🟡 Concordo, mas como **preparação** | Janelas de plantio na base de culturas |
| earthaccess | 🟡 só com IMERG | 🟡 Concordo | Só serve ao IMERG |
| **crop-cycle-detection** | 🟡 | ⬇️ **⚪ Pitch** | O calendário já vem do produtor |
| **Harvest Portal (API)** | 🟡 | ⬇️ **⚪ Pitch** | Nenhuma cultura alternativa na tabela |
| Earthdata Search / CMR | ⚪ | ⚪ Concordo, mas o **login** é essencial | Conta Earthdata exigida pelo AppEEARS |
| INMET / CEMADEN | ⚪ | ⚪ Concordo | — |
| Embrapa Solos | ⚪ | ⚪ Concordo | — |
| GLDAS | 🔴 | 🔴 Concordo | Nenhum cálculo que POWER e SMAP L4 não cubram |
| ERA5 | 🔴 | 🔴 Concordo | Idem; o custo de acesso é alto |
| HLS | 🔴 | 🔴 Concordo | O calendário vem do produtor e o NDVI de 250 m confirma |
| FAO GAEZ v5 | 🔴 | 🔴 Concordo | A base de culturas faz o filtro; os cenários do motor cobrem o futuro |
| MapBiomas | 🔴 | 🔴 Concordo | O produtor informa a rotação |
| Harvest MCP | 🔴 | 🔴 Concordo | — |
| FIRMS | 🔴 | 🔴 Concordo (volta se a demo tiver Cerrado com fogo) | — |
| Sentinel-1 | 🔴 | 🔴 Concordo | — |
| **OpenTopoData** | Não avaliada | 🟢 Essencial (é o caminho do SRTM) | Conector rápido de relevo |
| **NASA GIBS** | Não avaliada | 🟡 Se der tempo | Camadas visuais do mapa |
| **Nominatim** | Não avaliada | 🟡 Se der tempo | Busca do campo por endereço |

## Detalhes por ferramenta

### Base de culturas (falta no documento)
O filtro de inviáveis (graus-dia, geada, água) e todos os critérios de nota (água, terra, pragas, forragem) dependem de uma lista de culturas com parâmetros: temperatura base, graus-dia do ciclo, demanda de água, tolerância a geada e seca, família botânica, valor forrageiro, se fixa nitrogênio. **Ela não existe ainda** (o `culturas.csv` é citado no `CONTEXTO-DESAFIO.md`, mas não está no repositório). Sem ela, POWER, SoilGrids e SRTM não têm com o que ser comparados.

### NASA POWER — 🟢
Concordo. Alimenta o filtro (graus-dia, geada, água) e os critérios de água e erosão, sem login e já testado. Também cobre a umidade do solo (`GWETROOT`) quando o SMAP L4 não entrar.

### SoilGrids — 🟢
Concordo. É a evidência de peso 0,4 no retrato do solo. O cache por célula é obrigatório, porque uma chamada levou 17 s e a API está em beta.

### SRTM — 🟢, com ressalva
Concordo, mas **um ponto só não dá declividade**. O OpenTopoData devolve a altitude do ponto; o conector precisa pedir de 4 a 8 pontos vizinhos (ou o polígono) para calcular a declividade. Isso deve estar no contrato do conector.

### MODIS NDVI / VIIRS — 🟢, com ressalva
Concordo. O papel na arquitetura é confirmar o calendário que o produtor informou ("você disse × os dados"). **O MODIS sai de operação no fim de 2026**; vale pedir já o **VIIRS (VNP13A1)** no AppEEARS, no mesmo fluxo, para não depender de um sensor que está sendo desligado.

### AppEEARS — 🟢
Concordo. É o caminho lento do NDVI e do SMAP L4, entregando CSV por ponto. Falta medir o tempo real de um pedido.

### IBGE PAM — ⬆️ de 🟡 para 🟢
Hoje o critério "Renda extra" do motor é só "culturas comerciais a mais", sem dado nenhum. O PAM é barato (API sem login, testada, volume pequeno) e é a **única fonte de renda que sobrou** desde que CONAB e CEPEA saíram. Também ajuda a **gerar candidatas**, porque mostra o que se planta e rende na microrregião.

### GPM IMERG — 🟡
Concordo. Melhora o critério de erosão (chuva forte nos meses de solo descoberto). Sem ele, a chuva diária do POWER resolve, com aviso de escala.

### SMAP L4 — 🟡
Concordo. Usa o mesmo fluxo do AppEEARS, então é o primeiro "se der tempo" da fila. Sem ele, o `GWETROOT` do POWER cobre.

### ZARC — 🟡, como preparação
Concordo com o veredito, mas o uso muda: **baixar uma vez e preencher a base de culturas** com as janelas de plantio por região. Assim o custo é de preparação e não há risco na demo.

### earthaccess — 🟡
Concordo. Só é necessário se o IMERG entrar.

### crop-cycle-detection — ⬇️ de 🟡 para ⚪
A arquitetura já tira os meses sem cobertura do calendário do produtor, e o NDVI só confirma. Uma regra simples (NDVI suavizado abaixo de um limiar) faz essa confirmação. Fica para o pitch como evolução.

### Harvest Portal (API) — ⬇️ de 🟡 para ⚪
A tabela da OCDE tem só soja, milho, trigo e arroz, em escala nacional. **Nenhuma das culturas alternativas** que o motor sugere (sorgo, milheto, feijão, braquiária, crotalária) aparece. Um cartão de contexto nacional não muda nenhuma estratégia; vale como menção no pitch.

### Earthdata Search / CMR — ⚪
Concordo que o app não precisa dele. Mas a **conta Earthdata Login é essencial**, porque o AppEEARS exige. Criar a conta deve estar na lista de preparação.

### INMET / CEMADEN e Embrapa Solos — ⚪
Concordo.

### GLDAS, ERA5, HLS, FAO GAEZ v5, MapBiomas — 🔴
Concordo. Nenhum alimenta um cálculo do motor que já não esteja coberto:
- **GLDAS:** a umidade vem do POWER e do SMAP L4.
- **ERA5:** era a segunda opinião sobre o clima, mas o acesso é caro; ver o selo de confiança abaixo.
- **HLS:** o calendário vem do produtor e o NDVI de 250 m confirma.
- **GAEZ:** a base de culturas faz o filtro de aptidão, e os **cenários do motor** (chuva −20 %, +2 °C) cobrem o tema do futuro.
- **MapBiomas:** o produtor informa a rotação.

### Harvest MCP, FIRMS, Sentinel-1 — 🔴
Concordo. O FIRMS volta se a demo tiver uma região do Cerrado com fogo frequente.

### OpenTopoData, NASA GIBS e Nominatim (faltam no documento)
A arquitetura já usa os três (`INTEGRACAO-DE-DADOS.md`), mas o `PROS-E-CONTRAS` não os avalia:
- **OpenTopoData:** é o caminho escolhido para o SRTM, então é 🟢.
- **NASA GIBS:** camadas visuais para o mapa; 🟡.
- **Nominatim:** busca do campo por endereço; 🟡.

## Selo de confiança

Com ERA5 e GLDAS fora e o IMERG só "se der tempo", sobra pouca comparação entre fontes para medir a confiança. A arquitetura já tem a saída: **"você disse × os dados"**, a concordância entre o que o produtor informa e o que o satélite mostra. Proposta para o MVP:

- **Alta:** o produtor e o dado concordam, ou duas fontes independentes concordam.
- **Média:** só há o dado regional (POWER, SoilGrids, NDVI de 250 m), sem confirmação.
- **Baixa:** o produtor e o dado discordam, ou a escala do dado é muito maior que o campo.

## Ajustes em outros documentos

- **D-009 × este comparativo:** a D-009 tem 17 fontes no núcleo; o `PROS-E-CONTRAS` propõe 5 mais as "se der tempo". O resultado da discussão precisa virar a **D-010**. Até lá, as notas de `tools/` continuam dizendo que GLDAS, ERA5, HLS, GAEZ e MapBiomas são do núcleo.
- **`INTEGRACAO-DE-DADOS.md`:** as pendências ainda pedem acesso a GAEZ, GRACE e ESA WorldCover, que saem pelas duas propostas. O catálogo do AppEEARS cita ECOSTRESS, SMAP L3 e MOD16 (evapotranspiração), que não são necessários, porque o POWER já dá a ET₀.
- **`PROS-E-CONTRAS-FERRAMENTAS.md`:** cita o nome antigo `testes-chat-sr-jose.md` (agora `TESTES_CHAT_SR_JOSE.md`) e usa hífens no nome, enquanto o resto de `tools/` usa sublinhado.

## MVP proposto

| Prioridade | Ferramentas |
| --- | --- |
| 🟢 Essencial | Base de culturas (com as janelas do ZARC), NASA POWER, SoilGrids, SRTM via OpenTopoData (com pontos vizinhos), NDVI pelo AppEEARS (de preferência VIIRS), IBGE PAM, conta Earthdata Login |
| 🟡 Se der tempo, nesta ordem | SMAP L4 (mesmo fluxo do AppEEARS), GPM IMERG com earthaccess, NASA GIBS, Nominatim |
| ⚪ Pitch | Harvest Portal, `crop-cycle-detection`, GAEZ e cenários futuros, HLS, INMET/CEMADEN, Embrapa Solos |
| 🔴 Fora | GLDAS, ERA5, MapBiomas, Harvest MCP, FIRMS, Sentinel-1 |

Com esse núcleo, o projeto usa **3 datasets da NASA da lista oficial** (POWER, SRTM e MODIS/VIIRS), e chega a 5 com SMAP L4 e IMERG.
