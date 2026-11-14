# ARSET no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o ARSET, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o ARSET aos outros datasets.

## O que é o ARSET

O ARSET (Applied Remote Sensing Training) é o **programa de treinamentos** da NASA em sensoriamento remoto aplicado. Faz parte da área de Ciências Aplicadas da NASA e ensina a usar dados de satélite em agricultura, água, desastres, uso da terra, qualidade do ar e clima.

Ele **não é um dataset**. É uma escola gratuita, quase toda online. Cada treinamento costuma ter:

- **Aulas gravadas** e slides.
- **Exercícios práticos** com passo a passo, muitas vezes em Google Earth Engine, Python ou QGIS.
- **Perguntas e respostas** das turmas, publicadas junto com o material.

Os cursos têm três níveis: introdutório, intermediário e avançado. Vários são oferecidos também em **espanhol**, o que ajuda quem ainda não domina o inglês técnico. Na área de agricultura há, por exemplo, cursos de sensoriamento remoto para aplicações agrícolas e de classificação de culturas com radar e imagens ópticas.

## Por que usar

**1. Aprender rápido o que importa.** Num hackathon de 48 horas, ninguém tem tempo de ler manuais inteiros. O ARSET vai direto ao uso: como baixar, como calcular NDVI, como ler umidade do solo, como juntar radar e óptico.

**2. Scripts prontos para adaptar.** Os exercícios trazem código funcionando. A equipe troca a área de estudo e as datas e ganha uma base testada, em vez de começar do zero.

**3. Mesma "língua" da NASA.** Os cursos usam os mesmos datasets e ferramentas do projeto (Earthdata, AppEEARS, Giovanni, SMAP, IMERG, MODIS, Landsat). Isso reduz erros de unidade, de versão e de interpretação.

**4. Material para a apresentação.** Os slides explicam conceitos com figuras claras. Servem de referência para o glossário da ferramenta, sempre com a fonte citada.

## Como entra no projeto

### Harmonização

Não há variáveis a baixar. O ARSET entra no **processo de trabalho** da equipe:

- **Escolher o curso pelo problema:** cada integrante faz o treinamento ligado à sua parte (chuva, solo, vegetação, radar).
- **Reaproveitar o exercício:** copiar o script, trocar a região para o Brasil e a grade para a grade comum do projeto.
- **Registrar a origem:** cada script adaptado guarda no cabeçalho o nome do treinamento, o ano e o que foi mudado.

| Recurso | O que é | Uso |
| --- | --- | --- |
| Gravações e slides | Aula completa do curso | Aprender o conceito e o dataset |
| Exercícios | Passo a passo com código | Base dos scripts do projeto |
| Perguntas e respostas | Dúvidas comuns respondidas | Evitar erros já conhecidos |
| Versões em espanhol | Mesmo conteúdo, outro idioma | Facilitar o estudo da equipe |

> Confirmar nas páginas oficiais o endereço atual do ARSET (o portal de Ciências Aplicadas vem migrando conteúdo), quais cursos têm versão em espanhol ou português, a licença de reúso do código dos exercícios e se há certificado de conclusão.

### Indicadores calculados

O ARSET não gera indicadores. Ele acelera a construção destes:

- **Calendário de cobertura** (NDVI de MODIS e HLS).
- **Áreas irrigadas e ciclos por ano** (radar Sentinel-1 com imagens ópticas).
- **Umidade do solo e chuva** (SMAP e IMERG), com os cuidados de cada produto.

### Nível de confiança

Um script do ARSET é **ponto de partida, não garantia**. Os exercícios usam regiões e datas de exemplo, quase nunca no Brasil. A equipe precisa:

- conferir se a versão do dataset do exercício ainda é a atual;
- testar o script adaptado num lugar conhecido, comparando com MapBiomas ou com o produtor;
- não tratar o resultado como validado só porque veio de um curso da NASA.

## Onde o produtor vê isso

**Em lugar nenhum, diretamente.** O ARSET fica nos bastidores. O produtor vê o que ele ajudou a construir: o calendário de cobertura, o mapa de áreas irrigadas, o glossário.

**Página "Sobre os dados".** Os treinamentos usados aparecem como referência de método.

**Pitch.** Mostrar que a equipe aprendeu com o programa oficial da NASA e adaptou o material ao Brasil reforça o uso responsável dos dados.

## Caso hipotético: ARSET junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

Uma integrante da equipe faz, na versão em espanhol, o curso intermediário do ARSET de classificação de culturas com radar e imagens ópticas. Ela adapta o exercício para mapear pivôs e contar ciclos por ano. O teste é na fazenda da Sra. Rosa, perto de Itapeva, no Sudoeste Paulista, região de transição entre Mata Atlântica e Cerrado com muitos pivôs centrais.

- **Rotação atual:** soja no verão (outubro a fevereiro) e feijão irrigado no inverno (maio a agosto), todo ano.
- **Irrigação:** pivô central, com água de um córrego.
- **Prioridades:** água e renda altas; solo média.
- **Mercado:** soja, feijão e trigo, vendidos para cerealistas da região.

### O que cada dataset diz sobre o local

| Fonte | O que encontra (hipotético) |
| --- | --- |
| **Script adaptado do ARSET (Sentinel-1 + Sentinel-2)** | O pivô aparece em todos os anos, com dois ciclos por ano: soja e feijão de inverno. Solo descoberto em setembro. |
| HLS | Confirma os dois picos de NDVI no círculo do pivô. |
| MapBiomas | Classe de pivô central na mesma área; confirma o mapeamento do script. |
| NASA POWER | Evapotranspiração de referência alta em agosto e setembro. |
| GPM IMERG / CHIRPS | Quase sem chuva de junho a agosto; o feijão de inverno depende só do pivô. |
| ECOSTRESS | Evapotranspiração alta no pivô em julho e agosto, contra o entorno seco. |
| ANA HidroWeb | Vazão baixa no córrego da região em agosto nos anos secos. |
| ZARC | Janela para trigo de sequeiro no outono no município. |

### Onde os dados se completam

**O script funcionou, e foi conferido.** O mapa feito com o exercício adaptado bate com o MapBiomas e com o HLS. Só depois disso a equipe passa a usá-lo em outras regiões. Confiança **alta** para o mapeamento nesta área.

**O feijão de inverno usa água no pior momento.** POWER e ECOSTRESS mostram demanda alta em agosto; a ANA mostra o córrego mais baixo nesse mesmo mês. A demanda do pivô e a oferta do córrego se cruzam no mês crítico.

**O solo fica nu em setembro.** O script e o HLS mostram solo descoberto entre o feijão e a soja.

### Regras ativadas

- **Irrigação no mês de menor vazão** aumenta o peso de estratégias que reduzem o uso do pivô.
- **Solo descoberto antes da soja** aumenta o peso de culturas de cobertura.
- **Prioridade alta em água** dá peso a culturas de inverno de sequeiro.

### Comparação das estratégias

| Critério | A: atual (soja → feijão irrigado) | B: soja → feijão irrigado → milheto de cobertura | C: soja → feijão irrigado e trigo de sequeiro em anos alternados, com cobertura antes da soja |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●○○○ | ●●●●○ |
| Solo | ●●○○○ | ●●●●○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●○○○○ | ●●○○○ | ●●○○○ |
| Renda | ●●●●○ | ●●●●○ | ●●●○○ |

Com os pesos da Sra. Rosa (água e renda altas, solo média), a **estratégia C** fica em primeiro. Ela perde um pouco em renda, mas o ganho em água pesa mais.

### Cartão da estratégia C

> **Resumo:** uma opção é alternar, ano sim, ano não, o feijão irrigado de inverno com trigo de sequeiro, e manter uma cultura de cobertura antes da soja.
>
> **Por que foi sugerida:** o feijão de inverno usa o pivô justamente em agosto, quando o córrego da região costuma estar mais baixo, e o solo fica descoberto em setembro.
>
> **Evidências:** dois ciclos por ano no pivô (script adaptado do ARSET, HLS e MapBiomas, confiança alta); demanda alta de água em agosto (POWER e ECOSTRESS, confiança alta); vazão baixa nos anos secos (ANA, confiança média para o córrego específico); janela do trigo (ZARC).
>
> **Benefícios:** metade dos invernos sem irrigação pesada, menos gasto com energia e solo coberto antes da soja.
>
> **Lacunas:** não sabemos a outorga de água da fazenda nem o custo de energia do pivô.
>
> **Riscos para revisão local:** confirmar com o agrônomo a cultivar de trigo e a época de plantio; verificar a outorga e a vazão real do córrego; avaliar o impacto na renda nos anos sem feijão.

## Conclusão

O ARSET é a sala de aula da equipe. Ele encurta o caminho entre "temos os dados" e "sabemos usar os dados", e entrega scripts que já funcionam. O valor real aparece quando a equipe adapta o material ao Brasil e confere o resultado com fontes locais, como MapBiomas e ANA. Um script de curso só vira evidência depois desse teste.

## Limitações

- **Não é dataset:** não gera dados próprios.
- **Exemplos fora do Brasil:** os exercícios usam outras regiões e precisam de adaptação.
- **Material pode envelhecer:** versões de datasets e de bibliotecas mudam depois do curso.
- **Pouco em português:** a maior parte está em inglês, parte em espanhol.
- **Tempo:** mesmo curto, um curso consome horas do hackathon.
- **Tratamento:** escolher só os cursos ligados ao problema, registrar a origem de cada script, conferir versões e validar o resultado numa área conhecida antes de usar.
