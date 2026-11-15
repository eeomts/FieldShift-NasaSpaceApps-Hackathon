> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# Prós e contras de cada ferramenta

> Documento para discussão da equipe (14/11/2026). Para cada fonte de dados e ferramenta de acesso estudada no repositório: o que é, o papel no Field Shift, prós, contras, custo para implementar em 48 h e um **veredito proposto**. O veredito é uma proposta, não uma decisão. **Cada ferramenta tem um espaço "Argumentos do time"** para quem concordar ou discordar escrever o motivo. A decisão final vai para o `context/DECISOES.md`.

## Como ler

**Critérios usados em todas as ferramentas:**

| Critério | Pergunta |
|---|---|
| Impacto na recomendação | Muda alguma estratégia sugerida ou algum cartão que o produtor vê? |
| Insubstituível | Alguma outra ferramenta da lista já entrega o mesmo? |
| Custo em 48 h | Login, formato do arquivo, volume, tempo de processamento |
| Escala | O dado diz algo sobre o talhão ou só sobre a região? |
| Risco na demo | Pode travar, demorar ou falhar ao vivo? |
| Avaliação | Está na lista oficial de recursos do desafio (conta no critério "Relevância")? |
| Cobertura | Funciona no Brasil inteiro? E fora dele? |

**Nível de evidência:**
- 🧪 **Testado ao vivo** em 14/11/2026 (chamada real à API).
- 📄 **Só documentação** (informação das notas do time ou das páginas oficiais, sem teste).

**Vereditos propostos:**
- 🟢 **Essencial:** sem ela a ferramenta não funciona.
- 🟡 **Se der tempo:** acrescenta evidência com custo baixo; entra depois do núcleo pronto.
- ⚪ **Pitch / próximo passo:** citar na apresentação como evolução, sem implementar.
- 🔴 **Cortar:** custo maior que o benefício no hackathon.

## Resumo

| Ferramenta | Tipo | Veredito proposto | Em uma frase |
|---|---|---|---|
| NASA POWER | Dado (clima) | 🟢 Essencial | Sozinha entrega ~70 % dos indicadores, sem login, testada |
| SoilGrids | Dado (solo) | 🟢 Essencial | Única fonte de solo por ponto com API |
| SRTM | Dado (relevo) | 🟢 Essencial | Declividade e erosão, barato |
| MODIS NDVI | Dado (vegetação) | 🟢 Essencial | Solo descoberto, pedido explícito do desafio |
| AppEEARS | Acesso | 🟢 Essencial | Caminho mais simples para MODIS (e SMAP) por ponto |
| GPM IMERG | Dado (chuva) | 🟡 Se der tempo | Chuva extrema mais fina, mas exige abrir NetCDF |
| SMAP L4 | Dado (umidade) | 🟡 Se der tempo | Um cartão forte ("quantos dias o solo aguenta") |
| ZARC | Dado (risco) | 🟡 Se der tempo | Validação oficial, reconhecida no Brasil |
| IBGE PAM | Dado (produção) | 🟡 Se der tempo | Mercado local por município |
| crop-cycle-detection | Biblioteca | 🟡 Se der tempo | Detecta safras no NDVI; uma regra simples resolve o MVP |
| NASA Harvest Portal (API) | Dado (mercado) | 🟡 Opcional, pré-processado | Tem Brasil, mas só nacional e só 4 culturas |
| earthaccess | Acesso | 🟡 Só se usar IMERG | Biblioteca para baixar e abrir arquivos da NASA |
| Earthdata Search / CMR | Acesso | ⚪ Uso da equipe | Para achar produtos, não para o app |
| GLDAS | Dado (umidade) | 🔴 Cortar | Repete o que POWER e SMAP L4 já dão |
| ERA5 | Dado (clima) | 🔴 Cortar | "Segunda opinião" cara de obter |
| HLS | Dado (vegetação 30 m) | 🔴 Cortar | Pesado; MODIS resolve a demo |
| FAO GAEZ v5 | Dado (aptidão) | 🔴 Cortar | Sem API; a base de culturas faz o filtro |
| MapBiomas | Dado (uso do solo) | 🔴 Cortar | O produtor informa a rotação |
| INMET / CEMADEN | Dado (estações) | ⚪ Pitch | Validação boa, limpeza cara |
| NASA Harvest MCP | Acesso (chat) | 🔴 Cortar | Lento e enche o contexto do agente |
| FIRMS | Dado (fogo) | 🔴 Cortar | Só para regiões com fogo |
| Sentinel-1 | Dado (radar) | 🔴 Cortar | Processamento de radar em 48 h é inviável |
| Embrapa Solos | Dado (solo) | ⚪ Pitch | Escala de mapa nacional; depende da Q-07 |
| GRACE, ECOSTRESS, Landsat | Dado | 🔴 Já fora (D-009) | Ainda citadas em alguns documentos |

**Com o núcleo proposto, o projeto usa 3 datasets da NASA da lista oficial** (POWER, SRTM e MODIS) e chega a 5 com SMAP L4 e IMERG. Isso já atende o critério de relevância.

---

## 1. Fontes de dados

### NASA POWER
**O que é:** API da NASA com clima diário, mensal e climatológico por ponto (temperatura, chuva, umidade, radiação, vento, umidade do solo), desde 1981. 🧪

**Papel no Field Shift:** base de quase todos os indicadores: geada, calor, graus-dia, ET₀, balanço hídrico, tendência de chuva e temperatura.

| Prós | Contras |
|---|---|
| Sem login, JSON por ponto | Célula de ~0,5° (~55 km): campos vizinhos têm o mesmo valor |
| Testada em 5 continentes: 5 de 5 pontos, ~1,5 s, série 2001–2024 completa | Os últimos 2–3 meses são provisórios |
| Um único pedido traz várias variáveis | Chuva menos detalhada que a do IMERG (suaviza extremos) |
| Comunidade `AG` pensada para agricultura | Limite de requisições não documentado (há erro 429) |
| Está na lista oficial do desafio | |

**Custo em 48 h:** baixo. **Sem ela:** não existe ferramenta.
**Veredito proposto:** 🟢 Essencial.

**Argumentos do time:**
-

---

### SoilGrids (ISRIC)
**O que é:** mapa global de propriedades do solo em 250 m (argila, areia, carbono, pH, densidade, água disponível), com API por ponto. 🧪

**Papel no Field Shift:** o "nível 0" do retrato do solo, quando o produtor não sabe nada do próprio solo.

| Prós | Contras |
|---|---|
| Sem login, JSON por ponto | **Devolve vazio em área urbana** (máscara deles); testado: 3 de 5 pontos urbanos vazios, 4 de 4 rurais OK |
| Única fonte de solo com API por ponto da lista | Uma chamada levou 17 s; API em fase beta, limite de uso a confirmar |
| Informa a incerteza do valor | É modelo, não medição: pode diferir muito de uma análise de solo |
| Cobertura global | **Não está na lista oficial do desafio** |

**Custo em 48 h:** baixo (exige cache). **Sem ela:** só sobra o que o produtor responde no questionário.
**Veredito proposto:** 🟢 Essencial.

**Argumentos do time:**
-

---

### SRTM (elevação)
**O que é:** modelo de elevação da NASA em 30 m, de 2000. 🧪 (via OpenTopoData)

**Papel no Field Shift:** declividade (erosão) e baixadas sujeitas a geada.

| Prós | Contras |
|---|---|
| Não muda: baixa uma vez ou consulta por ponto | Retrato de 2000 |
| Testado via OpenTopoData: 5 de 5 pontos em ~1 s, sem login | Pelo caminho oficial (LP DAAC/AppEEARS) exige Earthdata Login |
| 30 m: a única fonte do núcleo na escala do talhão | Com um ponto só, não dá declividade: precisa de vizinhos ou do polígono |
| Está na lista oficial do desafio | |

**Custo em 48 h:** baixo. **Sem ele:** o critério de erosão fica sem relevo.
**Veredito proposto:** 🟢 Essencial.

**Argumentos do time:**
-

---

### MODIS NDVI (MOD13Q1) e VIIRS
**O que é:** índice de vegetação a cada 16 dias, 250 m, desde 2000. O VIIRS é o sucessor do MODIS. 📄 (produtos confirmados no catálogo do AppEEARS 🧪)

**Papel no Field Shift:** mostrar quando o campo fica descoberto e confirmar o calendário que o produtor informou.

| Prós | Contras |
|---|---|
| O desafio pede explicitamente "quando os campos ficam descobertos" | Pixel de 250 m mistura o talhão pequeno com os vizinhos |
| Série longa (2000–) e limpa | Exige Earthdata Login |
| Pelo AppEEARS chega em CSV por ponto (sem abrir HDF) | Pedido assíncrono: minutos, não segundos |
| Evidência visual forte para o pitch | Transição MODIS → VIIRS em andamento |
| Está na lista oficial do desafio | |

**Custo em 48 h:** médio. Pré-calcular os pontos da demo elimina o risco ao vivo.
**Veredito proposto:** 🟢 Essencial (pré-calculado para a demo).

**Argumentos do time:**
-

---

### GPM IMERG
**O que é:** chuva por satélite, 0,1° (~10 km), a cada 30 min, desde 1998. 🧪 (catálogo CMR)

**Papel no Field Shift:** chuva extrema e veranicos com mais detalhe que o POWER.

| Prós | Contras |
|---|---|
| Cerca de 5× mais fino que o POWER | **Não está no AppEEARS**: precisa de earthaccess + xarray para abrir NetCDF/HDF5 |
| A versão Final inclui pluviômetros | Exige Earthdata Login |
| Bom para o critério de erosão (chuva forte em solo descoberto) | A versão Final tem meses de atraso (o catálogo indicava até 30/09/2025) |
| Está na lista oficial do desafio | Sem endpoint simples por ponto encontrado |
| Comparar com o POWER alimenta o nível de confiança | Menor acerto em relevo complexo |

**Custo em 48 h:** alto para quem nunca abriu NetCDF. **Sem ele:** usa a chuva do POWER e avisa a escala.
**Veredito proposto:** 🟡 Se der tempo.

**Argumentos do time:**
-

---

### SMAP L4 (umidade da zona das raízes)
**O que é:** umidade do solo de 0 a 1 m, 9 km, a cada 3 h, desde 2015. 📄 (catálogo CMR e AppEEARS 🧪)

**Papel no Field Shift:** "quantos dias o solo aguenta sem chuva"; anomalias de umidade.

| Prós | Contras |
|---|---|
| Mede a camada que a raiz usa (o L3 só vê 5 cm) | Série curta (2015–) para climatologia |
| Está no AppEEARS: CSV por ponto | Exige Earthdata Login; pedido assíncrono |
| Cartão de alto impacto no Semiárido | Pixel de 9 km |
| Está na lista oficial do desafio | O POWER já tem umidade do solo (`GWETROOT`), mais grosseira |

**Custo em 48 h:** médio (mesmo fluxo do MODIS). **Sem ele:** usa o `GWETROOT` do POWER.
**Veredito proposto:** 🟡 Se der tempo.

**Argumentos do time:**
-

---

### ZARC (MAPA / Embrapa)
**O que é:** zoneamento oficial de risco climático: janelas de plantio por município, cultura, tipo de solo e ciclo. 📄

**Papel no Field Shift:** validar se a janela de plantio sugerida está dentro do risco aceito.

| Prós | Contras |
|---|---|
| Régua oficial que produtor, agrônomo e banco reconhecem | Escala do município |
| Tábua de risco em CSV nos dados abertos do MAPA | Uma cultura por vez; não pensa em rotação |
| Credibilidade no pitch | Só Brasil |
| | Não está na lista oficial do desafio |
| | Nomes de colunas e classes de solo a confirmar |

**Custo em 48 h:** baixo a médio (download único). **Sem ele:** a janela vem só dos limites de clima da base de culturas.
**Veredito proposto:** 🟡 Se der tempo.

**Argumentos do time:**
-

---

### IBGE PAM (Produção Agrícola Municipal)
**O que é:** área, produção, rendimento e valor da produção por cultura e município, desde 1974, via API do SIDRA. 📄

**Papel no Field Shift:** mercado local ("isso se planta e rende na minha região?") e perdas em anos secos.

| Prós | Contras |
|---|---|
| Escala do município, ~60 culturas | Só Brasil |
| API JSON sem login | Anual, com atraso de cerca de um ano |
| Volume pequeno: dá para guardar tudo | Não tem preço do dia nem comprador local |
| Valor da produção serve ao critério de renda | Culturas de cobertura (crotalária, braquiária) quase não aparecem |
| | Não está na lista oficial do desafio |

**Custo em 48 h:** baixo. **Sem ele:** o critério de renda depende só do que o produtor informa.
**Veredito proposto:** 🟡 Se der tempo (é a fonte de mercado mais útil).

**Argumentos do time:**
-

---

### NASA Harvest Portal (API CKAN)
**O que é:** catálogo de dados de mercado, comércio e segurança alimentar (OCDE, FAO, FMI, Banco Mundial). 🧪

**Papel proposto pela equipe:** nota de mercado, cruzada com a PAM.

**O que o teste ao vivo mostrou (14/11/2026):**
- 86 datasets; nenhum cita o Brasil no título, mas **o Brasil aparece dentro de datasets globais**.
- **OECD Crop Production:** área, produção e produtividade **nacionais e anuais** de **soja, milho, trigo e arroz**, com projeção até 2030. Ex.: soja 2030 = 149,3 milhões de t em 40,3 milhões de ha.
- A mesma tabela mistura centenas de indicadores sem relação (PIB, saúde, educação).
- 3 tabelas marcadas como consultáveis devolvem "Not found" (FAOSTAT Trade Matrix, FAOSTAT Land Use, preço da soja do FMI).
- 30 s para 10 mil linhas; licença "não especificada" nos dados da OCDE.

| Prós | Contras |
|---|---|
| Programa da NASA: soma no pitch | Escala **nacional**: não diz nada sobre o mercado da região do produtor |
| Projeção até 2030 é um bom cartão de contexto | Só 4 culturas; **nenhuma das alternativas típicas** (sorgo, milheto, feijão, braquiária, crotalária, mandioca) |
| API sem login | Lento, tabelas misturadas, recursos quebrados |
| | Licença não especificada |
| | **Não está na lista oficial do desafio**; os dados são da OCDE/FAO, não observação da NASA |

**Custo em 48 h:** baixo se pré-processado; alto se ao vivo.
**Veredito proposto:** 🟡 Opcional: baixar uma vez as ~300 linhas do Brasil (4 culturas, 2010–2030) e usar só num cartão de contexto nacional. Sem chamada ao vivo.

**Argumentos do time:**
-

---

### GLDAS
**O que é:** modelo de superfície da NASA com umidade do solo em camadas, evaporação e temperatura, 0,25°, mensal, desde 2000. 📄

**Papel proposto:** explicar o que acontece abaixo da superfície; série longa de umidade.

| Prós | Contras |
|---|---|
| Série longa (2000–), várias camadas de solo | Repete o que o `GWETROOT` do POWER e o SMAP L4 já dão |
| Leve depois de agregado | NetCDF + Earthdata Login |
| Está na lista oficial (NLDAS/GLDAS) | É modelo, não observação |

**Custo em 48 h:** médio a alto. **Sem ele:** POWER + SMAP L4 cobrem a umidade.
**Veredito proposto:** 🔴 Cortar.

**Argumentos do time:**
-

---

### ERA5 / ERA5-Land
**O que é:** reanálise climática europeia (Copernicus), horária, 0,1–0,25°, desde 1940. 📄

**Papel proposto:** segunda opinião independente do POWER.

| Prós | Contras |
|---|---|
| Independente do POWER (que deriva do MERRA-2) | Conta no Copernicus CDS + biblioteca `cdsapi` |
| Série muito longa; temperatura do solo | Arquivos GRIB/NetCDF horários, pesados |
| Está na lista oficial do desafio | Pedidos ao CDS entram em fila e podem demorar |
| | A confiança pode vir de POWER × IMERG sem ele |

**Custo em 48 h:** alto. **Sem ele:** confiança pela comparação POWER × IMERG.
**Veredito proposto:** 🔴 Cortar.

**Argumentos do time:**
-

---

### HLS (Landsat + Sentinel-2 harmonizados, 30 m)
**O que é:** reflectância de superfície em 30 m a cada 2–3 dias, desde 2013/2015. 📄 (no catálogo do AppEEARS 🧪)

**Papel proposto:** NDVI no nível do talhão.

| Prós | Contras |
|---|---|
| 30 m: enxerga o talhão de verdade | Nuvem na estação chuvosa: muitas lacunas |
| Disponível no AppEEARS | Exige máscara de nuvem, suavização e muito mais dados que o MODIS |
| Landsat está na lista oficial | Série curta comparada ao MODIS |
| | Para a demo, o MODIS + o calendário do produtor bastam |

**Custo em 48 h:** alto. **Sem ele:** MODIS (250 m) + calendário informado pelo produtor.
**Veredito proposto:** 🔴 Cortar (⚪ citar no pitch como evolução).

**Argumentos do time:**
-

---

### FAO GAEZ v5
**O que é:** aptidão agroclimática por cultura (~1 km), com cenários futuros. 📄

**Papel proposto:** filtro de aptidão das culturas e "para onde a aptidão vai" com o clima.

| Prós | Contras |
|---|---|
| Cenários futuros: tema central do desafio | **Sem API encontrada**: só download de GeoTIFF |
| Referência internacional | Escala regional (~1 km), com clima de modelo |
| Está na lista oficial do desafio | Exige baixar uma camada por cultura e por cenário |
| | Os limites de clima da base de culturas fazem o mesmo filtro no MVP |

**Custo em 48 h:** alto. **Sem ele:** filtro pelos limites de temperatura, água e geada da base de culturas.
**Veredito proposto:** 🔴 Cortar (⚪ citar os cenários futuros no pitch).

**Argumentos do time:**
-

---

### MapBiomas
**O que é:** mapas anuais de uso e cobertura do solo do Brasil em 30 m, desde 1985, incluindo fogo. 📄

**Papel proposto:** histórico de uso do talhão e do entorno.

| Prós | Contras |
|---|---|
| Aberto, validado, específico do Brasil | O produtor já informa a rotação no questionário |
| Histórico longo | Anual: não capta bem safrinha e cobertura |
| | GeoTIFF ou Google Earth Engine: processamento pesado |
| | Só Brasil; não está na lista oficial |

**Custo em 48 h:** alto. **Sem ele:** o calendário vem do produtor e o NDVI confirma.
**Veredito proposto:** 🔴 Cortar.

**Argumentos do time:**
-

---

### INMET / CEMADEN (estações)
**O que é:** dados medidos em estações meteorológicas e pluviômetros no Brasil. 📄

**Papel proposto:** validar o satélite com medição no chão.

| Prós | Contras |
|---|---|
| Medição real: o desafio pede "satélite × medição em solo" | Estações mal distribuídas; muitas falhas nas séries |
| Mostra extremos que o satélite suaviza | Download em ZIP com um CSV por estação; API do INMET pede cadastro e token |
| | Limpar e casar estações com campos leva tempo |
| | Só Brasil |

**Custo em 48 h:** alto. **Sem ele:** a comparação satélite × solo fica explicada no glossário e no pitch.
**Veredito proposto:** ⚪ Pitch (ou um único exemplo pré-calculado para a demo).

**Argumentos do time:**
-

---

### Extras: FIRMS, Sentinel-1, Embrapa Solos

| Ferramenta | O que é | Prós | Contras | Veredito |
|---|---|---|---|---|
| **FIRMS** | Focos de fogo por satélite (MODIS/VIIRS) | Evita sugerir palhada onde queima todo ano | Só relevante em algumas regiões; não muda a maioria das estratégias | 🔴 Cortar (volta se a demo tiver Cerrado com fogo) |
| **Sentinel-1** | Radar que vê através das nuvens | Funciona na estação chuvosa da Amazônia | Processar radar em 48 h é inviável para a equipe | 🔴 Cortar |
| **Embrapa Solos** | Mapa de classes de solo do Brasil | Nome do solo fiel à realidade brasileira | Escala de mapa nacional; não tem API por ponto | ⚪ Pitch (depende da Q-07) |

**Argumentos do time:**
-

---

### Já fora pela D-009, mas ainda citadas em documentos

| Ferramenta | Por que saiu | Onde ainda aparece |
|---|---|---|
| **GRACE / GRACE-FO** | Resolução real de ~300 km; não muda a recomendação do talhão | `testes-chat-sr-jose.md` (teste 11), notas do Harvest |
| **ECOSTRESS** | Passagens irregulares; não serve para série | `testes-chat-sr-jose.md`, `NASA_POWER_X_HARVEST_PORTAL.md` |
| **Landsat** (separado) | Já está dentro do HLS | Exemplo do "seu Antônio" (I-2) |

**Argumentos do time:**
-

---

## 2. Ferramentas de acesso e bibliotecas

### AppEEARS
**O que é:** serviço da NASA que extrai séries temporais de vários produtos (MODIS, SMAP, HLS, NASADEM, ECOSTRESS) para pontos ou polígonos. 🧪 (catálogo com 193 produtos)

| Prós | Contras |
|---|---|
| **Entrega CSV por ponto**: ninguém precisa abrir HDF | Earthdata Login; token de 48 h |
| Um pedido traz vários produtos | Assíncrono: envia, espera, baixa |
| Decodifica a qualidade de cada valor | Tempo de resposta não documentado (medir) |

**Veredito proposto:** 🟢 Essencial (é o caminho do MODIS e do SMAP).

**Argumentos do time:**
-

---

### earthaccess (biblioteca Python)
**O que é:** biblioteca para login, busca e download de produtos do Earthdata. 📄

| Prós | Contras |
|---|---|
| Automatiza login e download | Baixa **arquivos** (NetCDF/HDF), que alguém precisa saber abrir (xarray) |
| Necessária para o IMERG (que não está no AppEEARS) | Sem o IMERG, não tem uso no MVP |

**Veredito proposto:** 🟡 Só se o IMERG entrar.

**Argumentos do time:**
-

---

### Earthdata Search e CMR
**O que é:** o Earthdata Search é o site de busca de produtos da NASA; o CMR é a API de catálogo por trás dele (devolve JSON dizendo **quais arquivos existem**, não os dados). 🧪 (CMR)

| Prós | Contras |
|---|---|
| Confirma nome, versão e período de cada produto | Não entrega indicador nenhum |
| Útil para a equipe explorar | O app não precisa dele se usar AppEEARS e APIs diretas |

**Veredito proposto:** ⚪ Uso da equipe, fora do app.

**Argumentos do time:**
-

---

### NASA Harvest MCP (chat)
**O que é:** servidor MCP que deixa um assistente de IA consultar o Harvest Portal. 📄 (o time testou localmente)

| Prós | Contras |
|---|---|
| O agente pergunta sobre qualquer cultura em linguagem livre | Herda os limites do Harvest: nacional, 4 culturas, tabelas misturadas |
| Integração pronta com a API do Claude (MCP connector) | Respostas grandes e lentas **enchem o contexto** do agente |
| | Pode trazer números sem relação com a pergunta |

**Veredito proposto:** 🔴 Cortar. Se o Harvest entrar, entra pré-processado (ver acima).

**Argumentos do time:**
-

---

### crop-cycle-detection (NASA Harvest, GitHub)
**O que é:** biblioteca que detecta ciclos de safra e períodos de solo descoberto numa série de NDVI. 📄 (o time testou localmente)

| Prós | Contras |
|---|---|
| Método publicado pela NASA Harvest: forte no pitch | Mais uma dependência para instalar e entender |
| Atende "bare-field periods" e "seasonal transitions" | Uma regra simples (NDVI suavizado abaixo de um limiar) resolve o MVP |
| Conta como "SI" analítica | |

**Veredito proposto:** 🟡 Se der tempo (começar com a regra simples e trocar se funcionar).

**Argumentos do time:**
-

---

## Como registrar a decisão

1. Cada pessoa escreve o argumento no espaço da ferramenta (ou comenta no PR).
2. Na discussão, cada ferramenta fica com um veredito final.
3. O resultado vira a **D-010** no `context/DECISOES.md`, substituindo a lista de fontes da D-009.
