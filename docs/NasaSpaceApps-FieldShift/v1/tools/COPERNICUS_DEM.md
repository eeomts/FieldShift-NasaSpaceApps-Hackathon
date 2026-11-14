# Copernicus DEM no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Copernicus DEM, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o Copernicus DEM aos outros datasets.

## O que é o Copernicus DEM

O Copernicus DEM é um **modelo de elevação global** do programa Copernicus. Ele vem da missão de radar **TanDEM-X** (agência espacial alemã, DLR, e Airbus), que mediu o relevo do planeta entre o fim de 2010 e o início de 2015.

Tem duas versões abertas:

- **GLO-30:** 1 segundo de arco, cerca de 30 m.
- **GLO-90:** 3 segundos de arco, cerca de 90 m.

É um **modelo de superfície** (DSM): mede o topo do que estiver no chão, inclusive árvores e construções. As altitudes usam o geoide **EGM2008**. Onde o radar falhou, os buracos foram preenchidos com outros modelos, entre eles o próprio SRTM.

## Por que usar

**1. Uma segunda medida do mesmo relevo.** O SRTM é o dado de relevo obrigatório do projeto (D-002). O Copernicus DEM vem de outra missão, outro radar (banda X, contra banda C do SRTM) e outra década. Quando os dois mostram a mesma encosta, a declividade ganha confiança. O TOPODATA não serve para isso, porque é derivado do SRTM.

**2. Mais recente.** O SRTM é de fevereiro de 2000. O Copernicus DEM é de 2011 a 2015. Represas, estradas e cortes de terreno feitos nesse intervalo aparecem nele.

**3. Já é a base dos produtos da NASA.** O OPERA RTC-S1, usado para o Sentinel-1, corrige o relevo com o Copernicus DEM. Usar o mesmo modelo deixa o processamento coerente.

**4. Camadas de qualidade.** O produto traz máscaras que dizem onde o pixel foi preenchido com outra fonte, onde foi editado e qual o erro estimado da altura.

## Como entra no projeto

### Harmonização

- **Acesso:** Copernicus Data Space Ecosystem; cópia aberta em Cloud Optimized GeoTIFF na AWS (Registry of Open Data); OpenTopography. Tiles de 1° × 1°.
- **Processamento:** o mesmo do SRTM (ver `SRTM.md`, seção 8): recortar a fazenda, reprojetar para UTM (SIRGAS 2000), suavizar levemente em áreas planas e calcular declividade, orientação e baixadas. Antes disso, **mascarar** pixels preenchidos e áreas com árvores altas, usando a máscara de preenchimento e um mapa de cobertura (MapBiomas ou ESA WorldCover).
- **Comparação:** calcular a diferença entre Copernicus DEM e SRTM em cada talhão. Diferenças grandes e localizadas apontam mudança no terreno, vegetação ou erro.

| Camada | O que é | Uso |
| --- | --- | --- |
| DEM (elevação) | Altitude da superfície, em metros | Declividade, orientação, baixadas |
| FLM (*filling mask*) | De onde veio cada pixel preenchido | Saber se o pixel é do TanDEM-X ou de outra fonte, como o SRTM |
| HEM (*height error mask*) | Erro estimado da altura | Descartar pixels pouco confiáveis |
| EDM (*editing mask*) | Pixels editados (água, litoral, aplainamento) | Não tirar declividade de áreas editadas |
| WBM (*water body mask*) | Corpos d'água | Separar represas e rios |

> Confirmar nas páginas oficiais a versão atual do GLO-30 (há lançamentos mais novos que o original), os nomes exatos das camadas auxiliares, a precisão vertical especificada e o texto de atribuição exigido pela licença (inclui a DLR e a Airbus). A licença é gratuita no mundo todo, com exceções que não incluem o Brasil.

### Indicadores calculados

- **Declividade confirmada:** percentual do talhão acima de 8% no Copernicus DEM e no SRTM, e se os dois concordam.
- **Mudança no terreno:** áreas com diferença acima de alguns metros entre os dois modelos, sem árvore no mapa de cobertura.
- **Caminho da água:** direção do escoamento e pontos onde a água converge dentro do talhão.

### Nível de confiança

Se o SRTM e o Copernicus DEM concordam na declividade, a confiança é **alta**. Se discordam, a ferramenta olha o motivo: árvore (os dois modelos medem a copa), pixel preenchido (FLM), represa ou corte novos. Um pixel do Copernicus DEM preenchido com SRTM **não conta** como segunda medida.

## Onde o produtor vê isso

**Etapa 2, mapa de risco de erosão.** A camada de declividade usa os dois modelos e mostra, no glossário, quando eles concordam.

**Cartão da estratégia.** Exemplo: "O setor leste do pivô tem declividade de 7% a 9%; os dois modelos de relevo concordam."

**Aviso de mudança.** Quando a diferença entre os modelos indica represa ou corte, a ferramenta pergunta ao produtor se a informação está certa.

## Caso hipotético: Copernicus DEM junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Rodrigo planta grãos num pivô central de 100 ha perto de Cristalina, em Goiás, no Cerrado. O pivô fica na borda de uma chapada.

- **Rotação atual:** soja (outubro a fevereiro), feijão irrigado (março a junho), pousio (julho a setembro).
- **Irrigação:** pivô central, com outorga de água limitada e conta de energia alta.
- **Prioridades:** água e renda altas; solo média.
- **Mercado:** soja, feijão e milho; há uma cerealista perto.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **Copernicus DEM** | O setor leste do pivô (cerca de 25 ha) tem declividade de 7% a 9%; o resto fica abaixo de 3%. Uma represa de 4 ha a jusante aparece no modelo. Uma linha de eucalipto no limite aparece como "morro" de 20 m. |
| SRTM | Mesma declividade no setor leste. A represa não aparece. |
| HLS | No feijão, o setor leste fica com NDVI menor; solo descoberto de julho a setembro em todo o pivô. |
| GPM IMERG | Quase nenhuma chuva de maio a setembro. |
| NASA POWER | Evapotranspiração de referência alta de julho a setembro. |
| GLDAS / SMAP L4 | Na região, zona das raízes abaixo do normal a partir de maio (valor regional, que não enxerga a irrigação). |
| MapBiomas | Classifica a área como agricultura irrigada e o limite como silvicultura. |

### Onde os dados se completam

**Duas missões mostram a mesma encosta.** O setor leste é inclinado no SRTM (2000) e no Copernicus DEM (2011–2015). São medidas independentes, então a confiança na declividade é **alta**. A lâmina do pivô escorre nessa parte, o que ajuda a explicar o feijão mais fraco ali (HLS).

**A represa explica a diferença.** O Copernicus DEM mostra uma represa que o SRTM não tem. A ferramenta trata a área como água, não como erro.

**O eucalipto não é morro.** A linha de árvores aparece como um "morro" porque os dois modelos medem a copa. O MapBiomas confirma a silvicultura, e a faixa sai do cálculo de declividade.

### Regras ativadas

- **Declividade acima de 7% confirmada por duas fontes, sob irrigação** aumenta o peso de cobertura do solo e de irrigação diferenciada por setor.
- **Prioridade alta em água** reduz a nota de estratégias que irrigam a área toda na seca.
- **Solo descoberto de julho a setembro** aumenta o peso das culturas de cobertura.

### Comparação das estratégias

| Critério | A: atual (soja → feijão irrigado → pousio) | B: soja → feijão irrigado → milheto de cobertura | C: soja → feijão irrigado só na parte plana; milheto e braquiária no setor leste |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●○○○ | ●●●●○ |
| Solo | ●●○○○ | ●●●●○ | ●●●●○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●●○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●●● |
| Forragem | ●○○○○ | ●●○○○ | ●●○○○ |
| Renda | ●●●●○ | ●●●●○ | ●●●●○ |

A B e a C rendem o mesmo nas contas da ferramenta: a C planta menos feijão, mas gasta menos água e energia. Com água e renda altas, a **estratégia C** fica em primeiro, pelas notas de água e erosão. A B fica em segundo.

### Cartão da estratégia C

> **Resumo:** uma opção é irrigar o feijão só na parte plana do pivô e, no setor leste, mais inclinado, semear milheto com braquiária para cobrir o solo.
>
> **Por que foi sugerida:** o setor leste tem declividade de 7% a 9%, a lâmina de irrigação escorre ali e o feijão rende menos; e todo o pivô fica descoberto de julho a setembro.
>
> **Evidências:** declividade (Copernicus DEM e SRTM, confiança alta); feijão mais fraco no setor leste (HLS, confiança alta); seca de maio a setembro (GPM IMERG e POWER, confiança alta).
>
> **Benefícios:** menos água e energia por saco de feijão, menos escoamento para a represa e palhada para a soja seguinte.
>
> **Lacunas:** não sabemos se o painel do pivô permite irrigar por setor nem o custo do milheto e da braquiária.
>
> **Riscos para revisão local:** conferir com o técnico do pivô a irrigação por setor e com o agrônomo a dessecação antes da soja; verificar se a outorga muda com a área irrigada.

## Conclusão

O Copernicus DEM não substitui o SRTM: os dois juntos dão mais confiança. Como vêm de missões diferentes, a concordância vale como confirmação, e a discordância vira pista de mudança no terreno ou de vegetação alta. No caso, a declividade confirmada justificou tratar o setor inclinado do pivô de outro jeito, ligando relevo, água e renda numa mesma recomendação.

## Limitações

- **Modelo de superfície:** mede o topo das árvores e construções, não o chão.
- **Pixels preenchidos:** parte dos buracos foi preenchida com SRTM e outros modelos; ali não há segunda medida.
- **Data fixa (2011–2015):** mudanças depois disso não aparecem.
- **30 m não capta microrrelevo:** terraços, curvas de nível e sulcos ficam de fora.
- **Ruído em áreas planas:** como no SRTM, exige suavização leve.
- **Tratamento:** mascarar árvores e pixels preenchidos, usar as camadas de erro, comparar com o SRTM e perguntar ao produtor quando a diferença indicar mudança no terreno.
