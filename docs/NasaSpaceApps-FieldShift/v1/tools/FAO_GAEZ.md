# FAO GAEZ v5 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o FAO GAEZ v5, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o GAEZ aos outros datasets.

## O que é o FAO GAEZ

O GAEZ (Global Agro-Ecological Zones) é o sistema de **zoneamento agroecológico global** da FAO, feito com o IIASA (Instituto Internacional de Análise de Sistemas Aplicados). Não é da NASA, mas é aberto e é um dos seis datasets obrigatórios do projeto (D-002).

Ele cruza clima, solo e relevo com as exigências de cada cultura e responde: **esta cultura é apta para este lugar? Quanto ela pode render?** Faz isso para dezenas de culturas, com e sem irrigação e em diferentes níveis de manejo.

A **versão 5** foi lançada em abril de 2025. Em relação à v4 (D-004):

- **Linha de base 2001–2020**, no lugar de uma base centrada em 2010.
- **Resolução de cerca de 1 km** (30 segundos de arco) nas camadas principais de aptidão e produtividade.
- **Cenários futuros** com modelos climáticos recentes: três cenários de emissão (SSP1-2.6, SSP3-7.0 e SSP5-8.5), cinco modelos climáticos e quatro períodos, de 2021–2040 a 2081–2100.
- **Clima vindo do AgERA5**, uma versão agrícola diária derivada do ERA5.

## Por que usar

**1. Filtro de bom senso.** Antes de mostrar uma estratégia, a ferramenta checa se as culturas dela são aptas para o local. Isso evita sugerir uma cultura que o clima ou o solo não aceitam.

**2. Olha para o futuro.** O desafio fala em adaptar a fazenda. O GAEZ mostra como a aptidão pode mudar nas próximas décadas, segundo os cenários do IPCC. É o único dataset da lista que faz isso por cultura.

**3. Junta clima e solo num só número.** O índice de aptidão já considera chuva, temperatura, solo e relevo. Para o produtor, "aptidão boa" é mais fácil de entender que dez variáveis.

**4. Cobertura nacional e uniforme.** O mesmo método vale do Pampa a Roraima, o que permite comparar regiões no panorama nacional (D-008).

## Como entra no projeto

### Harmonização

- **Acesso:** plataforma geoespacial do GAEZ v5 (data.apps.fao.org/gaez), com download das camadas em GeoTIFF. A documentação do modelo está no wiki do projeto no GitHub.
- **Processamento:** baixar só as culturas usadas nas estratégias (soja, milho, sorgo, trigo, feijão, pastagens e outras), recortar o Brasil e reamostrar para a grade comum. Guardar a linha de base e um ou dois cenários futuros, não todos.

| Camada | O que é | Uso |
| --- | --- | --- |
| Índice de aptidão | Nota de aptidão da cultura, em sequeiro ou irrigada | Filtro das estratégias |
| Classe de aptidão | De "muito alta" a "não apta" | Texto simples para o produtor |
| Produtividade atingível | Rendimento possível com um nível de manejo | Comparar culturas no mesmo lugar |
| Restrições de solo e terreno | O que limita a cultura no local | Explicar por que a aptidão é baixa |
| Cenários futuros | Aptidão em 2041–2060 e outros períodos | Mostrar o "shift" esperado |

> Confirmar nas páginas oficiais a lista de culturas da v5, os níveis de manejo disponíveis, os nomes das camadas no portal, se existe API ou só download, e qual base de solo a v5 usa.

### Indicadores calculados

- **Aptidão atual por cultura:** classe na linha de base 2001–2020.
- **Mudança de aptidão:** diferença entre a linha de base e 2041–2060, por cenário.
- **Concordância entre modelos:** em quantos dos cinco modelos climáticos a aptidão cai.

### Nível de confiança

O GAEZ é uma **referência regional de modelo**, não uma medição do talhão. Três cuidados:

- **O clima do GAEZ deriva do ERA5.** GAEZ e ERA5 nunca contam como confirmações independentes sobre o clima.
- **O solo é regional.** Para textura no ponto, o SoilGrids ou a análise de solo valem mais (ver Q-07).
- **Cenários futuros divergem.** A ferramenta mostra a mudança só quando a maioria dos modelos concorda, e sempre como "possível", nunca como certeza.

O ZARC, do Ministério da Agricultura e da Embrapa, é a comparação brasileira mais próxima para o presente. Se GAEZ e ZARC concordam sobre uma cultura, a confiança sobe.

## Onde o produtor vê isso

**Etapa 1, perfil do local.** "Culturas com aptidão boa na sua região", com o selo "estimativa regional da FAO".

**Cartão da estratégia, em "Evidências".** A aptidão de cada cultura da estratégia aparece ao lado das outras fontes.

**Aba "E no futuro?".** Uma linha simples: "Em alguns cenários de clima para 2041–2060, a aptidão para cevada na sua região cai de alta para média." Com o aviso de que é cenário, não previsão.

## Caso hipotético: GAEZ junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Sra. Ingrid planta grãos perto de Guarapuava, no Centro-Sul do Paraná, a cerca de 1.000 m de altitude, região de Mata Atlântica com campos e araucárias.

- **Rotação atual:** soja (outubro a março) e cevada (junho a outubro), todo ano.
- **Irrigação:** não tem.
- **Prioridades:** renda e solo altas; nitrogênio média.
- **Mercado:** soja, cevada para malte, trigo e milho, pela cooperativa da região.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **GAEZ v5 (base 2001–2020)** | Aptidão alta para soja, milho, trigo e cevada em sequeiro. |
| **GAEZ v5 (2041–2060, SSP3-7.0)** | Cevada cai de alta para média em 4 dos 5 modelos; milho e soja ficam estáveis; trigo cai pouco. |
| ZARC | Janelas de baixo risco para soja, milho, trigo e cevada no município. |
| ERA5-Land | Mais dias acima de 30 °C em outubro em 2001–2020 que em 1981–2000. Não conta como fonte separada do GAEZ. |
| INMET (estação mais próxima) | Mesma tendência de outubros mais quentes, de forma independente. |
| NASA POWER | Geadas frequentes de junho a agosto; chuva bem distribuída. |
| SoilGrids | Solo argiloso, carbono médio. |
| HLS | Solo coberto quase o ano todo. |
| MapBiomas | Soja todo verão há mais de 15 anos. |

### Onde os dados se completam

**Hoje está tudo bem.** GAEZ e ZARC concordam: as culturas atuais são aptas. Confiança **alta** para o presente.

**O risco está no futuro e na repetição.** O GAEZ mostra que a cevada pode perder aptidão com o calor na fase final do ciclo. A estação do INMET confirma, de forma independente, que outubros quentes ficaram mais comuns. O ERA5 mostra o mesmo, mas como o clima do GAEZ deriva dele, não reforça a confiança. Confiança **média** para a mudança futura.

**A soja repetida pesa no solo.** O MapBiomas mostra soja todo verão. Sem rotação no verão, doenças e pragas se acumulam e a palhada é pouca.

**O GAEZ não cobre tudo.** Não há camada para ervilhaca, uma leguminosa de inverno comum no Sul. Essa parte vem da literatura técnica e entra como lacuna.

### Regras ativadas

- **Mesma cultura de verão por muitos anos** aumenta o peso de estratégias que alternam soja e milho.
- **Queda de aptidão futura com concordância entre modelos** aumenta o peso de estratégias que dependem menos da cevada.
- **Prioridade média em nitrogênio** dá peso a leguminosas de inverno.

### Comparação das estratégias

| Critério | A: atual (soja → cevada) | B: soja → cevada ou trigo, com aveia e ervilhaca em 1 de cada 3 invernos | C: soja e milho alternados no verão; trigo ou cevada no inverno, com ervilhaca antes do milho |
| --- | --- | --- | --- |
| Água | ●●●○○ | ●●●○○ | ●●●○○ |
| Solo | ●●○○○ | ●●●●○ | ●●●●● |
| Nitrogênio | ●○○○○ | ●●●●○ | ●●●○○ |
| Erosão | ●●●○○ | ●●●●○ | ●●●●○ |
| Forragem | ●●○○○ | ●●●○○ | ●●○○○ |
| Renda | ●●●●○ | ●●●○○ | ●●●●○ |

Com os pesos da Sra. Ingrid (renda e solo altas, nitrogênio média), a **estratégia C** fica em primeiro. A B fixa mais nitrogênio, mas perde em renda e em solo.

### Cartão da estratégia C

> **Resumo:** uma opção é alternar soja e milho no verão, manter trigo ou cevada no inverno e semear ervilhaca no inverno que antecede o milho.
>
> **Por que foi sugerida:** o talhão tem soja todo verão há mais de 15 anos, e alguns cenários de clima indicam que a cevada pode perder aptidão nas próximas décadas.
>
> **Evidências:** aptidão atual de todas as culturas (GAEZ v5 e ZARC, confiança alta); queda futura da cevada (GAEZ v5, 4 de 5 modelos, confiança média); outubros mais quentes (INMET, confiança média); soja repetida (MapBiomas, confiança alta).
>
> **Benefícios:** a rotação no verão quebra ciclos de doenças, o milho deixa mais palhada, a ervilhaca reduz a necessidade de adubo nitrogenado no milho e a fazenda depende menos de uma só cultura de inverno.
>
> **Lacunas:** o GAEZ não tem camada para ervilhaca; não sabemos os contratos com a cooperativa nem o histórico de doenças do talhão.
>
> **Riscos para revisão local:** verificar com o agrônomo a época de dessecação da ervilhaca antes do milho, o ajuste de adubação e se a janela do milho no verão atrasa o inverno seguinte.

## Conclusão

O GAEZ v5 é o filtro e a bússola da ferramenta. Como filtro, garante que nenhuma estratégia sugira cultura inapta. Como bússola, mostra para onde a aptidão pode ir com a mudança do clima, que é o centro do desafio. Ele trabalha em escala regional e com clima derivado do ERA5, então precisa do ZARC, das estações e do produtor para virar evidência no talhão.

## Limitações

- **Escala regional:** cerca de 1 km; não vê diferenças dentro da fazenda.
- **Modelo de aptidão, não de manejo:** não considera rotação, doenças, mercado ou custo.
- **Clima derivado do ERA5:** não é fonte climática independente.
- **Cenários futuros são incertos:** os modelos divergem; nunca devem aparecer como previsão.
- **Culturas faltando:** algumas coberturas usadas no Brasil não têm camada própria.
- **Tratamento:** usar como filtro e contexto, comparar com o ZARC, mostrar a concordância entre modelos e marcar o futuro como cenário.
