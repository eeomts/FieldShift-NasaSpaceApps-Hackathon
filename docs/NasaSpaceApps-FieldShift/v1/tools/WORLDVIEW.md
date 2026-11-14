# Worldview no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Worldview, como ele entra na ferramenta e o que muda para o produtor, com um caso hipotético que mostra a equipe conferindo visualmente os dados de uma região do Cerrado.

## O que é

O Worldview é o visualizador de imagens de satélite da NASA, aberto no navegador. Ele mostra o planeta **dia a dia**, com imagens em cor verdadeira e centenas de camadas: focos de fogo, aerossóis e fumaça, nuvens, chuva, temperatura da superfície, índices de vegetação e outras.

As imagens vêm do GIBS (Global Imagery Browse Services), o serviço de mosaicos da NASA. A maior parte das camadas aparece poucas horas depois da passagem do satélite, e o arquivo histórico permite voltar muitos anos.

Não precisa de login para navegar.

## Por que usar

**1. Ver com os próprios olhos.** Um indicador diz "solo descoberto em agosto". No Worldview, a equipe vai até agosto daquele ano e vê a região marrom e sem verde. Isso pega erros de processamento que uma tabela não mostra.

**2. Contexto de um dia específico.** Fumaça, nuvem, enchente ou queimada num dia preciso aparecem na imagem. Ajuda a entender por que uma série teve um valor estranho naquela data.

**3. Comparar duas datas.** O modo de comparação põe duas datas lado a lado ou com uma cortina deslizante. Ótimo para mostrar a mesma região na safra e na seca.

**4. Figuras e animações para a apresentação.** O Worldview exporta imagens e animações de uma área. É uma forma rápida e honesta de mostrar ao júri o problema real, com dados da NASA.

## Como entra no projeto

### Acesso

- **Endereço:** `worldview.earthdata.nasa.gov`, no navegador.
- **Fluxo:** escolher a data na linha do tempo, adicionar camadas, aproximar a região e, se quiser, comparar datas, animar ou exportar.

| Recurso / camada | O que é | Uso no projeto |
| --- | --- | --- |
| Cor verdadeira (MODIS Terra/Aqua, VIIRS) | Imagem diária "como o olho vê" | Ver solo descoberto, lavoura verde, nuvem e fumaça |
| Focos de fogo (FIRMS) | Pontos de fogo ativo | Conferir as queimadas apontadas pelo FIRMS |
| Aerossóis e fumaça | Profundidade óptica de aerossóis | Saber se a fumaça atrapalhou as imagens ópticas |
| Índices de vegetação | NDVI e EVI em mosaico | Comparação visual entre datas |
| Modo de comparação | Duas datas lado a lado ou com cortina | Safra contra seca, ano normal contra ano seco |
| Exportar imagem e animação | Recorte da área como imagem ou GIF | Figuras para a apresentação e o glossário |
| Link permanente | URL que guarda data, camadas e área | Registrar exatamente o que foi visto |

> Confirmar nas páginas oficiais os nomes atuais das camadas, quais têm histórico longo, se as camadas do HLS estão disponíveis para o Brasil e quais formatos de exportação existem. As camadas do GIBS são imagens para visualização, não valores científicos para cálculo.

### O que produz para o projeto

- **Conferência visual** dos indicadores pré-calculados nas regiões de demonstração.
- **Explicação de valores estranhos** nas séries (fumaça, nuvem, enchente).
- **Figuras e animações** para o pitch e para o glossário da ferramenta.
- **Links permanentes** guardados no registro, para qualquer pessoa da equipe abrir a mesma vista.

### Como ajuda a medir a confiança

O Worldview não entra no cálculo. Ele é uma **conferência humana**: quando um indicador e a imagem do dia concordam, a equipe ganha segurança na regra. Quando discordam, o indicador vai para revisão antes de aparecer para o produtor. Também mostra quando a fumaça pode ter derrubado a qualidade das imagens de um mês, o que reduz a confiança do NDVI naquele período.

## Onde o produtor vê isso

O produtor **não usa** o Worldview dentro da ferramenta. O efeito aparece de dois jeitos:

- **Imagens de contexto.** Uma imagem de cor verdadeira da região, na safra e na seca, pode aparecer na Etapa 2 ou no glossário, com a fonte citada.
- **Menos erros.** Indicadores conferidos visualmente chegam ao cartão com menos chance de estarem errados.

Se o produtor quiser, a ferramenta pode oferecer um link para abrir a própria região no Worldview. Isso ajuda a criar confiança: ele vê que os dados são públicos.

## Caso hipotético: Worldview no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como a ferramenta ajuda a conferir os dados de uma região.

### A região

A equipe usa o entorno de **Rio Verde (GO)**, no Cerrado, como região de demonstração. O produtor fictício é o Sr. Wagner.

- **Rotação atual:** soja (outubro a fevereiro), milho safrinha (fevereiro a julho), pousio até outubro.
- **Irrigação:** só um pivô pequeno, fora do talhão analisado.
- **Prioridades:** solo e renda altas; água média.
- **Mercado:** soja, milho e sorgo.

### O que os dados pré-calculados mostram (hipotético)

| Dataset | O que encontra |
| --- | --- |
| HLS | Solo descoberto de agosto a setembro na maioria dos anos. Em 2024, NDVI estranhamente baixo também em julho. |
| GLDAS / SMAP L4 | Zona das raízes abaixo do normal a partir de junho. |
| GPM IMERG | Seca de maio a setembro. |
| FIRMS | Poucos focos no município; um aglomerado em agosto de 2024 a cerca de 30 km. |
| NASA POWER | Máximas acima de 34 °C em setembro. |

### O que a equipe faz no Worldview

1. **Abre julho de 2024** em cor verdadeira, sobre Rio Verde. A região aparece coberta por uma névoa cinza.
2. **Liga a camada de aerossóis.** O valor está alto em toda a região, e os focos do FIRMS mostram queimadas a centenas de quilômetros, ao norte. É fumaça transportada.
3. **Compara com julho de 2023** usando a cortina. Em 2023 a imagem é limpa e as lavouras de milho aparecem verdes.
4. **Exporta uma animação** de fevereiro a outubro de um ano normal, mostrando o verde da safrinha sumindo e o solo marrom da seca.
5. **Guarda os links permanentes** no registro do indicador.

### Onde o Worldview fez diferença

**O NDVI baixo de julho de 2024 era fumaça, não colheita.** A máscara de nuvem do HLS deixou passar parte da fumaça fina, que derrubou o NDVI. Sem a conferência, a ferramenta diria que o milho foi colhido mais cedo. A equipe marca julho de 2024 como mês de qualidade baixa e o tira do cálculo do calendário.

**O padrão geral se confirma.** Nos outros anos, a imagem mostra o mesmo que o HLS: solo descoberto em agosto e setembro. A confiança do calendário de cobertura continua **alta**, agora com a exceção explicada.

**A animação vira o começo do pitch.** Em 10 segundos, o júri vê o problema que a ferramenta trata: meses de solo exposto ao sol forte, antes das primeiras chuvas. Isso sustenta, no comparador, as estratégias com cobertura do solo na seca, que a ferramenta apresenta como opções a discutir com o agrônomo.

## Conclusão

O Worldview é o "olhar de conferência" da equipe. Ele não gera números, mas mostra se os números fazem sentido no mundo real, explica valores estranhos causados por fumaça ou nuvem e produz as imagens mais fáceis de entender para quem não é especialista. Para um projeto que precisa ser explicável, ver a imagem é parte da evidência.

## Limitações

- **Imagem não é medição:** as camadas do GIBS são para ver, não para calcular; os valores vêm dos produtos originais.
- **Resolução diária grossa:** a cor verdadeira do MODIS e do VIIRS tem de 250 m a 1 km; talhões pequenos não aparecem bem.
- **Nuvens:** na estação chuvosa do Centro-Oeste e do Norte, muitos dias ficam sem vista do solo.
- **Trabalho manual:** serve para conferir regiões de demonstração, não o Brasil inteiro.
- **Tratamento:** usar o Worldview para conferência visual e figuras, guardar o link permanente de cada vista e marcar os meses afetados por fumaça ou nuvem no nível de confiança.
