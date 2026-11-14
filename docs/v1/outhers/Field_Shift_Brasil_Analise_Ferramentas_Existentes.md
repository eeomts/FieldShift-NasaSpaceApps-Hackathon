# Field Shift Brasil — Análise das ferramentas existentes

Nov 14, 2026 · Complemento à Documentação do Projeto

## Objetivo

Este documento reúne as ferramentas que já fazem algo parecido com o nosso projeto, mostra as falhas que elas têm em comum e explica como essas falhas orientam a implementação. O escopo do projeto agora é o **Brasil inteiro**, não apenas Minas Gerais.

### O que muda com o escopo nacional

- **As ferramentas brasileiras viram concorrentes diretas.** ZARC, SATVeg, Agritempo, MapBiomas e Monitor de Secas cobrem o país todo, na mesma escala que a nossa. A diferença do nosso projeto precisa estar na explicação e no foco no produtor, não na cobertura.
- **Elas também ficam mais úteis como fonte.** Como já cobrem o Brasil inteiro, o ZARC e o MapBiomas podem ser usados para checar a aptidão das culturas e o histórico de uso do solo em qualquer região.
- **A diversidade aumenta.** O país tem biomas, climas e sistemas de produção muito diferentes, da soja no Cerrado ao café no Sudeste, do semiárido nordestino à Amazônia e aos Pampas. As regras de recomendação precisam funcionar em todos esses contextos, ou a ferramenta precisa dizer claramente onde não funciona.
- **O processamento fica mais pesado.** Calcular indicadores para todo o território exige uma grade maior e mais armazenamento. Pré-calcular os indicadores se torna ainda mais importante.

> **Aviso de verificação:** as informações abaixo foram levantadas sem pesquisa na web e refletem o conhecimento disponível até meados de 2026. Antes de usar na apresentação, a equipe deve abrir cada ferramenta e confirmar o que ela oferece hoje.

## Ferramentas analisadas

| Ferramenta | Quem faz | O que entrega | Para quem |
| --- | --- | --- | --- |
| ZARC | MAPA / Embrapa | Janelas de plantio por município, cultura e tipo de solo, com nível de risco climático | Produtores, bancos e seguradoras |
| SATVeg | Embrapa | Curvas de NDVI/EVI do MODIS desde 2000 para qualquer ponto do Brasil | Técnicos e pesquisadores |
| Agritempo | Embrapa | Dados de estações, mapas de chuva e temperatura, balanço hídrico | Técnicos e pesquisadores |
| MapBiomas | Rede de instituições | Mapas anuais de uso do solo em 30 m desde 1985 | Pesquisa, governo, sociedade |
| Monitor de Secas | ANA e parceiros | Mapa mensal da severidade da seca por região | Governo e gestão de recursos hídricos |
| Plataformas comerciais (FieldView, Cropwise, Aegro, Strider, OneSoil, EOS) | Empresas privadas | NDVI por talhão, clima, pragas, máquinas, gestão | Produtores tecnificados |
| Cover Crop Decision Tool | Midwest Cover Crops Council (EUA) | Espécies de cobertura com notas por objetivo do produtor | Produtores dos EUA e Canadá |
| COMET-Farm | USDA / Colorado State (EUA) | Comparação entre manejo atual e cenários alternativos, em carbono | Produtores e técnicos dos EUA |
| DSSAT | Consórcio científico | Simulação de produtividade, água e nitrogênio ao longo de sequências de culturas | Pesquisadores |
| Monitores globais (GEOGLAM, NASA Harvest, Crop Explorer) | Organizações internacionais | Condição das safras por país ou região | Governos e mercados |

## Falhas de cada ferramenta

| Ferramenta | Principais falhas | Qualidades a aproveitar |
| --- | --- | --- |
| ZARC | Escala do município; uma cultura por vez; não pensa em rotação; não explica o porquê do risco; ignora saúde do solo e prioridades do produtor | Credibilidade oficial; séries climáticas longas; o produtor já conhece |
| SATVeg | Pixel de 250 m mistura talhões; só mostra a curva, sem interpretar; não cruza com clima ou solo | Gratuito; série longa; mostra safra, safrinha e solo descoberto |
| Agritempo | Interface datada; estações mal distribuídas; é consulta, não decisão | Dados medidos no chão, úteis para validar satélite |
| MapBiomas | Anual, não capta bem safrinha e cobertura; agrupa culturas na mesma classe | Aberto e validado; melhor substituto do CDL americano para histórico |
| Monitor de Secas | Escala regional; diagnóstico sem recomendação | Combina indicadores com validação de especialistas locais |
| Plataformas comerciais | Pagas; feitas para o produtor de grande porte; foco na safra atual; recomendações caixa-preta; dúvidas sobre posse dos dados | Nível do talhão; interface caprichada; app no celular |
| Cover Crop Decision Tool | Só EUA e Canadá; notas por opinião de especialistas, sem dados de satélite do local; não compara com a rotação atual | Lógica de objetivos do produtor com notas por espécie, muito parecida com nossos sliders |
| COMET-Farm | Só EUA; mede apenas carbono; cadastro longo | Estrutura "manejo atual × alternativas" igual à nossa tela de comparação |
| DSSAT | Exige calibração, dados detalhados e treinamento; inviável para o produtor | Robustez científica; simula rotações |
| Monitores globais | Escala grande demais para a fazenda | Boa síntese visual de muitas fontes |

## As falhas juntas

Olhando as ferramentas em conjunto, as falhas se repetem. A matriz abaixo mostra quais ferramentas têm cada uma delas.

**Legenda:** ● tem a falha · ◐ tem em parte · ○ não tem · — não se aplica

| Falha | ZARC | SATVeg | Agritempo | MapBiomas | Monitor de Secas | Comerciais | Cover Crop Tool | COMET-Farm | DSSAT | Globais |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Entrega dado sem interpretação | ○ | ● | ● | ● | ◐ | ◐ | ○ | ○ | ◐ | ◐ |
| 2. Recomenda sem explicar o porquê | ● | — | — | — | — | ● | ◐ | ○ | — | — |
| 3. Ignora as prioridades do produtor | ● | ● | ● | ● | ● | ◐ | ○ | ◐ | ● | ● |
| 4. Não compara rotações ou estratégias | ● | ● | ● | ● | ● | ● | ◐ | ○ | ○ | ● |
| 5. Escala inadequada para a decisão na fazenda | ● | ● | ● | ◐ | ● | ○ | ◐ | ○ | ○ | ● |
| 6. Não mostra a incerteza do resultado | ◐ | ● | ● | ◐ | ◐ | ● | ◐ | ◐ | ◐ | ◐ |
| 7. Barreira de acesso (pago, técnico ou fora do Brasil) | ○ | ◐ | ◐ | ○ | ○ | ● | ● | ● | ● | ○ |

**O que a matriz mostra:** nenhuma ferramenta escapa de todas as falhas. As brasileiras e gratuitas entregam dados ou regras sem explicação e sem olhar para o produtor. As que olham para o produtor são pagas, técnicas demais ou não funcionam no Brasil. As falhas 3 e 4 (prioridades do produtor e comparação de estratégias) são quase universais, e são exatamente o centro do desafio Field Shift.

Em resumo, as ferramentas existentes caem em dois grupos:

- **Entregam dados sem interpretação:** quem consulta precisa saber ler uma curva de NDVI ou um mapa de seca para tirar alguma conclusão.
- **Entregam resultado sem explicação:** dizem o que fazer, mas não mostram o raciocínio nem consideram a situação de quem pergunta.

Nos dois casos falta o elo entre o dado e a decisão daquele produtor. É esse elo que o nosso projeto pretende construir, para produtores de todo o Brasil.

## Como isso orienta a implementação

Cada falha comum vira um requisito do nosso projeto.

| Falha comum | Requisito do Field Shift | Onde aparece na ferramenta |
| --- | --- | --- |
| 1. Dado sem interpretação | Todo indicador vem com uma frase em linguagem simples dizendo o que ele significa para aquele local | Glossário e textos dos cartões |
| 2. Recomendação sem explicação | Toda sugestão mostra quais indicadores a motivaram e quais regras foram aplicadas | Campos "Por que foi sugerida" e "Evidências" do cartão |
| 3. Ignora prioridades do produtor | O produtor informa sua situação e prioridades, e elas definem os pesos da nota final | Perfil do produtor e sliders de prioridade |
| 4. Não compara estratégias | A rotação atual aparece lado a lado com duas alternativas | Tela de comparação |
| 5. Escala inadequada | Cada indicador informa a resolução de origem e avisa quando o valor é regional | Grade comum e avisos de escala |
| 6. Incerteza escondida | Cada indicador tem nível de confiança, e a confiança baixa aparece no cartão | Metodologia, etapa de incerteza |
| 7. Barreira de acesso | Gratuita, em português, pensada para quem tem pouca experiência com tecnologia e válida para todo o país | Design centrado no produtor |

### Cuidados para não repetir as mesmas falhas

- **Não virar caixa-preta.** Se usarmos IA para redigir explicações, ela só pode descrever indicadores e regras já calculados, nunca inventar justificativas.
- **Não esconder a escala.** Uma explicação personalizada pode passar a impressão de que o dado é da fazenda do produtor. O aviso de escala precisa aparecer junto da explicação, não só no glossário.
- **Não exigir demais do produtor.** Pedir só o essencial no início e o resto quando for necessário, para não repetir a barreira de uso das ferramentas técnicas.
- **Não depender só de satélite para explicar.** Os dados da NASA mostram condições; a ligação entre condição e prática vem das regras agronômicas (GAEZ, ZARC, literatura da Embrapa). Essa camada precisa estar explícita.

### O que aproveitar das ferramentas existentes

- **ZARC:** fonte para checar janelas de plantio e aptidão das culturas de cada família.
- **SATVeg e MapBiomas:** dados de NDVI e histórico de uso do solo já processados para o Brasil, úteis para validar as hipóteses das regiões de demonstração em diferentes biomas.
- **Cover Crop Decision Tool:** referência para a lógica de objetivos com notas por cultura.
- **COMET-Farm:** referência para a estrutura de comparação entre o manejo atual e as alternativas.
- **Monitor de Secas:** referência para combinar dados com validação local.

## Posicionamento para o pitch

> As ferramentas que existem hoje entregam dados sem interpretação ou recomendações sem explicação, e nenhuma compara estratégias de rotação considerando as prioridades do produtor. O Field Shift liga os dados da NASA à decisão de cada produtor brasileiro, mostrando o porquê de cada sugestão, o quanto podemos confiar nela e o que precisa ser confirmado no campo.

## Próximos passos

- [ ] Abrir cada ferramenta e confirmar as informações deste documento
- [ ] Tirar capturas de tela das principais para usar na apresentação
- [ ] Conversar com produtores ou agrônomos de regiões diferentes do Brasil sobre o que usam hoje e o que sentem falta
- [ ] Redefinir as regiões de demonstração para representar biomas diferentes do país
- [ ] Avaliar se dados do MapBiomas e do SATVeg entram como fontes complementares
- [ ] Detalhar o funcionamento das perguntas do produtor e atualizar a seção de implementação
