# Arquitetura da aplicação — visão geral

> Plano de 14/11/2026, com as escolhas atualizadas em 15/11/2026. Descreve como o app funciona, quais partes ele tem e em que ordem construir. Os detalhes de cada parte estão nos arquivos desta pasta; o código está em [`agroai/`](../../../../../agroai/README.md) e o andamento em [`ANDAMENTO.md`](../ANDAMENTO.md).

## Princípio

**Quem faz as contas é o motor de análise.** O dashboard e o chat só mostram e explicam os resultados dele. Assim nenhum número é inventado e todo número tem origem (fonte, período, resolução).

## Diagrama

```text
 Produtor
    │
    ▼
┌─────────────────────────┐      ┌──────────────────────────┐
│ 1. COLETA (onboarding)  │      │ Integração de dados      │
│ questionário + IA       │─────►│ externos (NASA POWER,    │
│ → análise do produtor   │ local│ SoilGrids, SRTM, NDVI…)  │
└───────────┬─────────────┘      └────────────┬─────────────┘
            │ ficha do produtor               │ indicadores
            ▼                                 ▼
        ┌────────────────────────────────────────┐
        │            MOTOR DE ANÁLISE            │
        │ perfil · retrato do solo · estratégias │
        └──────────┬───────────────────┬─────────┘
                   ▼                   ▼
        ┌──────────────────┐  ┌──────────────────────┐
        │ 2. DASHBOARD     │  │ 3. CHAT + CENÁRIOS   │
        │ insights         │◄─┤ perguntas e "e se?"  │
        └──────────────────┘  └──────────────────────┘
                   PostgreSQL + pgvector (guarda tudo)
```

O produtor enxerga três coisas: **o questionário, o dashboard e o chat**. A integração de dados externos e o motor trabalham sem ele ver.

O site tem duas versões com as mesmas telas: a completa (`agroai/web`, com login por e-mail e senha) e a de apresentação (`agroai/web-demo`, entrada só com o nome e questionário já preenchido com uma fazenda de exemplo, com o botão Skip All).

## Partes

| Parte | O que faz | Arquivo |
|---|---|---|
| **1. Coleta** | Onboarding: coleta as respostas do produtor, interpreta o texto livre com IA e gera a **ficha do produtor** | [COLETA.md](COLETA.md) |
| **Integração de dados externos** | Busca dados de clima, solo, relevo e vegetação do campo em segundo plano, com cache | [INTEGRACAO-DE-DADOS.md](INTEGRACAO-DE-DADOS.md) |
| **Motor de análise** | Perfil, retrato do solo (fusão de evidências), estratégias (filtro + pontuação) e cenários | [MOTOR-DE-ANALISE.md](MOTOR-DE-ANALISE.md) |
| **2. Dashboard** e **3. Chat + cenários** | O que o produtor vê e como conversa com os dados | [DASHBOARD-E-CHAT.md](DASHBOARD-E-CHAT.md) |
| **Banco de dados** | PostgreSQL e o modelo de dados | [BANCO-DE-DADOS.md](BANCO-DE-DADOS.md) |

O questionário em si está em [`../ONBOARDING.md`](../ONBOARDING.md).

## Stack

| Camada | Escolha | Status |
|---|---|---|
| Banco | **PostgreSQL 17 + pgvector** (base de conhecimento do chat). O PostGIS vem no compose, mas o código ainda não usa | Decidido |
| Backend, motor e integração de dados | Python + FastAPI, SQLAlchemy 2, Alembic | Decidido |
| Coleta lenta | `BackgroundTasks` do FastAPI (o solo do SoilGrids é buscado em segundo plano). A tabela de jobs + worker ficou para depois | Decidido |
| Frontend | React + Vite + TypeScript + Tailwind, site responsivo pensado primeiro para o celular, em português e inglês | Decidido |
| IA (texto livre e chat) | Gemini com uso de ferramentas, sem framework de agentes (D-011) | Decidido |
| Escopo geográfico | Brasil e EUA (D-008 e D-010) | Decidido |

**Por que Python no backend:** o cálculo é científico (pandas, numpy, rasterio para mapas como o GAEZ) e as bibliotecas da NASA (`earthaccess`) são em Python.

## Ordem de construção

1. **Coleta:** questionário, gravação das respostas, IA no texto livre e geração da ficha (perfil, calendário, retrato do solo).
2. **Integração rápida:** NASA POWER, SoilGrids e SRTM, disparados quando o produtor marca o local (pergunta 5).
3. **Motor:** indicadores e estratégias a partir da ficha.
4. **Dashboard** lendo a ficha e o motor.
5. **Chat** com as ferramentas; depois, os **cenários**.
6. **Integração lenta:** NDVI e SMAP. *(Era via AppEEARS, descartado em 15/11/2026; a ferramenta desta etapa está em aberto.)*

O chat vem depois de propósito: sem o motor, ele não tem o que consultar.

## O que precisamos providenciar

| Item | Para quê |
|---|---|
| Base de culturas com parâmetros e sinônimos (PT, EN) | Casar o texto livre; calcular as estratégias |
| Lista de equipamentos (categorias) | Pergunta 26b; filtro de culturas viáveis |
| 12 fotos de solo com origem e licença | Pergunta 19 |
| Glossário em linguagem simples | Dashboard e chat |
| Textos-modelo das explicações (por quê, evidência, benefícios, lacunas, riscos) | Dashboard e chat |
| Conta NASA Earthdata (gratuita) | SMAP, IMERG (o AppEEARS foi descartado em 15/11/2026) |
| Chave da API do Gemini | Texto livre e chat |
| Hospedagem | Backend, banco e frontend |

## Decisões pendentes

Resolvidas desde o plano: linguagem do backend (Python), framework do frontend (React), conta do produtor (e-mail e senha na versão completa; só o nome na de apresentação) e hospedagem (VPS da equipe com Docker, ver [`.deploy/README.md`](../../../../../.deploy/README.md)).

1. **Atualização da ficha:** refazer o questionário inteiro ou atualizar por partes (sugestão: por partes, pelo dashboard ou pelo chat).
2. **Pesos iniciais** das fontes e das prioridades (ver [MOTOR-DE-ANALISE.md](MOTOR-DE-ANALISE.md)). Hoje são propostas em `agroai/api/app/services/motor/parametros.py`, a validar.

---

Volta para o [README principal](../../../../../README.md).
