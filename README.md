# Field Shift · AgroIA

Projeto da equipe para o **NASA Space Apps Challenge 2026**, desafio **[Field Shift: Adapting Farms with NASA Data](docs/NasaSpaceApps-FieldShift/v1/desafio-oficial-nasa-field-shift.md)**.

## O problema

Clima mudando, chuva irregular, falta de água e solo se desgastando tornam difícil escolher **o que plantar e quando**. O desafio pede uma ferramenta de apoio à decisão que use dados de satélite da NASA, o solo local, as características das culturas e as prioridades do produtor. Ela deve **comparar pelo menos 3 estratégias de rotação de culturas, incluindo a atual**, e explicar o porquê, a evidência, os benefícios, as lacunas e os riscos de cada uma.

## A solução: AgroIA

Um site em que o produtor:

1. **Responde um questionário curto** sobre a fazenda: local, o que planta e quando, o que sabe do solo e suas prioridades.
2. **Acompanha um Dashboard** com clima, umidade do solo, saúde da lavoura, alertas e a comparação de estratégias de rotação, tudo a partir de dados da NASA.
3. **Conversa com a AgroIA**, um assistente que conhece a fazenda dele e explica os dados em linguagem simples, citando a fonte.

> A ferramenta **apoia, não decide**. A palavra final é do produtor e do técnico local.

## Status

🟡 **Fase de documentação e planejamento.** Ainda não há código. Antes de começar a programar, a equipe precisa resolver os pontos em aberto listados no fim deste README.

## Estrutura do repositório

```text
docs/NasaSpaceApps-FieldShift/v1/
├── desafio-oficial-nasa-field-shift.md   # texto oficial do desafio
├── context/                              # o problema e as decisões
│   ├── DECISOES.md                       # ⭐ decisões da equipe (D-xxx) e perguntas em aberto (Q-xx)
│   ├── CONTEXTO-DESAFIO.md               # requisitos, conceitos e indicadores
│   ├── Field Shift Brasil — Documentação do Projeto.md   # metodologia
│   └── BANCO_DE_DADOS_NASA.md            # datasets e ferramentas
├── application/                          # o produto
│   ├── site-contexto.md                  # especificação do AgroIA (telas, chat, API, dados)
│   ├── ONBOARDING.md                     # questionário do primeiro acesso
│   ├── DOR-DO-AGRICULTOR-E-CASO-DE-USO.md   # dores do produtor + caso da Dona Marta
│   └── architecture/                     # arquitetura: coleta, integração de dados, motor, dashboard/chat, banco
├── tools/                                # uma nota por fonte de dados (NASA POWER, SMAP L4, GPM IMERG, MODIS, HLS, SRTM...)
│   └── extras/                           # fontes opcionais
├── others/                               # análise de ferramentas existentes
├── .md/                                  # guias de estudo (explicado do zero, glossário, bancos de dados)
└── .pdf/                                 # versões em PDF dos guias
```

## Por onde começar

1. **Novo no tema?** Leia [o desafio explicado do zero](docs/NasaSpaceApps-FieldShift/v1/.md/desafio-field-shift-nasa-space-apps-explicado-do-zero.md).
2. **Para entender o que já foi decidido:** [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md).
3. **Para entender o que vamos construir:** [`site-contexto.md`](docs/NasaSpaceApps-FieldShift/v1/application/site-contexto.md) e [`architecture/README.md`](docs/NasaSpaceApps-FieldShift/v1/application/architecture/README.md).
4. **Para saber como acessar cada dado:** a nota da fonte em [`tools/`](docs/NasaSpaceApps-FieldShift/v1/tools/).

## Dados principais (D-009)

| Para quê | Fonte |
|---|---|
| Clima | NASA POWER, ERA5 |
| Chuva | GPM IMERG |
| Água no solo | SMAP L4, GLDAS |
| Vegetação (NDVI) | MODIS, HLS |
| Relevo | SRTM |
| Solo e aptidão | SoilGrids, FAO GAEZ v5 |
| Mercado | NASA Harvest Portal |
| Brasil (uso do solo, validação) | MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM |
| Acesso | Earthdata, earthaccess, AppEEARS |

## Stack (proposta)

**Back-end:** Python + FastAPI · **Banco:** PostgreSQL + PostGIS · **Front-end:** web, pensado primeiro para celular · **IA:** LLM com uso de ferramentas (o motor de análise faz as contas; a IA só explica).

## Pontos em aberto

Há conflitos entre documentos que precisam de decisão da equipe antes do código:

- **Escopo:** Brasil inteiro (D-008) ou mundo todo (`site-contexto.md`)?
- **IA:** Gemini (`site-contexto.md`) ou Claude (`architecture/README.md`)?
- **Front-end:** React ou outro framework?
- **Demo:** quais regiões e fazendas de exemplo (Q-01 a Q-03)?

A lista completa está em [`DECISOES.md`](docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md), seção 3.

## Como contribuir

- Trabalhe numa branch (`docs/...`, `feat/...`) e abra um PR para a `main`.
- Decisões novas entram no `DECISOES.md` com número, status e motivo. Uma decisão que mudou não é apagada: ela é marcada como **Substituída**.
- Itens com **[verificar]** precisam ser confirmados na fonte oficial antes de virar código ou entrar no pitch.
