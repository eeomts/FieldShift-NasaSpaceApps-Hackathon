# GEDI no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o GEDI, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o GEDI aos outros datasets.

## O que é o GEDI

O GEDI (Global Ecosystem Dynamics Investigation) é um **lidar** instalado na Estação Espacial Internacional. Ele dispara pulsos de laser e mede o eco que volta da vegetação e do chão. Com isso estima a altura das árvores, a estrutura do dossel e a biomassa acima do solo.

Ele não gera uma imagem contínua. Mede **pontos** (footprints de cerca de 25 m) ao longo de faixas, com espaços entre elas. Pense numa amostragem, não num mapa. A órbita da Estação cobre todo o território brasileiro.

## Por que usar

O GEDI é um dado de **contexto**. Ele não diz qual cultura plantar, mas mostra o que existe em volta da lavoura, o que muda o risco de algumas estratégias.

**1. Vegetação ao redor do talhão.** Mostra se acima da lavoura há mata, pasto ou eucalipto, e se a mata ciliar abaixo está inteira ou com falhas. Isso explica de onde vem a enxurrada e para onde vai o solo perdido.

**2. Diferenciar o que o NDVI confunde.** Pasto, café, eucalipto e mata podem ter NDVI parecidos. A altura do dossel separa bem: pasto fica abaixo de 1 m, café entre 2 e 3 m, mata e eucalipto bem acima.

**3. Contexto de paisagem para a apresentação.** Ajuda a mostrar que a ferramenta olha a propriedade dentro da paisagem, não o talhão isolado.

**4. Fronteira agrícola.** Na borda da Amazônia e do Cerrado, a altura e a estrutura do dossel separam floresta íntegra, floresta degradada e áreas abertas, contexto que o NDVI sozinho não dá.

## Como entra no projeto

### Harmonização

- **Produtos:** L2A (altura do dossel, métricas `rh`), L2B (cobertura do dossel e perfil vertical), L4A (biomassa por footprint) e L4B (biomassa média em grade de 1 km).
- **Acesso:** L2A e L2B no LP DAAC; L4A e L4B no ORNL DAAC. Busca pelo Earthdata Search ou pela biblioteca `earthaccess`.
- **Processamento:** filtrar os footprints de boa qualidade (`quality_flag`), recortar a área de interesse e agregar por célula da grade comum (média, mediana e número de footprints).

| Variável | O que é | Uso |
| --- | --- | --- |
| `rh98` (L2A) | Altura do dossel (percentil 98 do retorno) | Separar pasto, café, eucalipto e mata |
| `cover` (L2B) | Fração de cobertura do dossel | Proteção do solo em encostas e matas ciliares |
| `agbd` (L4A) | Biomassa acima do solo por footprint | Contexto de vegetação nativa |
| L4B (grade 1 km) | Biomassa média por célula | Panorama nacional |

> Confirmar nas páginas oficiais os nomes das variáveis, o período disponível (o instrumento teve uma pausa entre 2023 e 2024) e as recomendações de filtragem por qualidade.

### Indicadores calculados

- **Cobertura arbórea a montante:** fração de footprints com dossel acima de 5 m na encosta acima do talhão.
- **Integridade da mata ciliar:** cobertura média do dossel na faixa ao longo do curso d'água abaixo do talhão.
- **Tipo de vegetação vizinha:** classificação simples por altura (rasteira, arbustiva, arbórea).

### Nível de confiança

Depende do **número de footprints** na área. Poucos pontos significam confiança baixa. O GEDI também é cruzado com o NDVI (HLS ou Sentinel-2) e com o MapBiomas: se a altura indica mata e o MapBiomas também, a confiança sobe.

## Onde o produtor vê isso

O produtor não vê a palavra "GEDI". Ele vê:

**Etapa 1, mapa da paisagem.** Uma camada "vegetação ao redor" mostra mata, pasto e lavoura em volta da propriedade.

**Cartão da estratégia, em "Por que foi sugerida".** Exemplo: "A encosta acima da sua lavoura é pasto sem árvores, então a água da chuva chega rápido ao seu talhão."

**Riscos para revisão local.** Quando a mata ciliar tem falhas, o cartão lembra que o solo perdido vai para o córrego e sugere conversar com o técnico sobre faixas de vegetação ou terraços.

## Caso hipotético: GEDI junto com os outros dados

> Caso inventado, com números ilustrativos.

### A produtora

A Sra. Maria tem uma pequena propriedade perto de Viçosa (MG), na Zona da Mata mineira, região de Mata Atlântica com relevo de morros.

- **Rotação atual:** milho (outubro a fevereiro), feijão da seca (fevereiro a maio), pousio até outubro.
- **Irrigação:** não tem.
- **Prioridades:** solo e erosão altas; renda média.
- **Mercado:** milho, feijão e venda local de hortaliças.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| SRTM / TOPODATA | Declividade de 20 a 30% no talhão. |
| GPM IMERG | De 3 a 4 eventos por ano acima de 60 mm/dia entre novembro e janeiro. |
| GLDAS | Escoamento superficial alto em dezembro e janeiro. |
| HLS | Solo descoberto de junho a setembro. |
| **GEDI** | Encosta acima do talhão com dossel abaixo de 1 m em 90% dos footprints (pasto). Topo do morro com fragmento de mata de 15–20 m. Mata ciliar abaixo com cobertura de apenas 35%. |
| MapBiomas | Encosta acima é pastagem desde os anos 1990. |
| Embrapa Solos | Argissolo, com erodibilidade alta. |

### Onde os dados se completam

**De onde vem a água.** O SRTM mostra o declive e o GPM mostra a chuva forte. O GEDI acrescenta que a água vem de uma encosta de pasto sem árvores, então chega ao talhão rápido e em volume. O MapBiomas confirma que esse uso é antigo.

**Para onde vai o solo.** O GEDI mostra que a mata ciliar está falhada, então o solo perdido segue direto para o córrego.

**Onde o GEDI é fraco.** Na faixa ciliar havia só 6 footprints. A informação entra com confiança **média** e um pedido de conferência visual no Worldview ou no campo.

### Regras ativadas

- **Declividade alta e chuva extrema** aumentam o peso das culturas de cobertura.
- **Entrada de água a montante (GEDI)** aumenta o peso de práticas que seguram a água no talhão: plantio em nível e cobertura permanente.
- **Prioridade alta em solo** aumenta o peso das leguminosas de cobertura.

### Comparação das estratégias

| Critério | A: atual (milho → feijão → pousio) | B: milho → feijão → mucuna | C: milho + feijão-de-porco em faixas |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●○○○○ | ●●●●○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●●●● | ●●●●○ |
| Erosão | ●○○○○ | ●●●●○ | ●●●●● |
| Forragem | ●○○○○ | ●●○○○ | ●●○○○ |
| Renda | ●●●●○ | ●●●○○ | ●●●○○ |

Com os pesos da Sra. Maria (solo e erosão altos), a **estratégia C** fica em primeiro.

### Cartão da estratégia C

> **Resumo:** plantar em nível e manter faixas de feijão-de-porco entre o milho para segurar a água que desce da encosta.
>
> **Por que foi sugerida:** seu talhão é íngreme, recebe chuvas fortes e a encosta acima é pasto sem árvores, então a enxurrada chega rápido.
>
> **Evidências:** declividade de 20–30% (SRTM, confiança alta); chuvas extremas (GPM, confiança alta); encosta acima sem árvores (GEDI e MapBiomas, confiança alta); mata ciliar falhada (GEDI, confiança média).
>
> **Benefícios:** as faixas reduzem a velocidade da água, o feijão-de-porco fixa nitrogênio e protege o solo na seca.
>
> **Lacunas:** não sabemos se já há terraços ou curvas de nível no talhão.
>
> **Riscos para revisão local:** a água que vem da encosta vizinha não depende só de você. Vale conversar com o técnico da assistência técnica rural (ATER) do estado sobre terraços e com o vizinho sobre a encosta. A mata ciliar pode precisar de recomposição.

## Conclusão

O GEDI não muda a cultura escolhida, mas explica o risco em volta dela. Ele mostra a paisagem que o NDVI e o relevo sozinhos não mostram: de onde vem a água e o que protege, ou não, o solo e o córrego. Por ser uma amostragem, entra sempre como contexto, com peso menor na nota.

## Limitações

- **Amostragem, não mapa:** há espaços entre as faixas; áreas pequenas podem ter poucos ou nenhum footprint.
- **Nuvens bloqueiam o laser:** na estação chuvosa há menos dados válidos.
- **Série curta e com pausa:** dados a partir de 2019, com interrupção entre 2023 e 2024.
- **Peso na decisão:** baixo; serve de contexto e de reforço, não de base para a recomendação.
- **Tratamento:** filtrar por qualidade, contar os footprints por célula e cruzar com NDVI e MapBiomas.
