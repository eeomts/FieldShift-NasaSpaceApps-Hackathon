# Arquitetura da aplicação — visão geral

> Plano de 14/11/2026. Descreve como o app funciona, quais partes ele tem e em que ordem construir. Os detalhes de cada parte estão nos arquivos desta pasta.

## Princípio

**Quem faz as contas é o motor de análise.** O dashboard e o chat só mostram e explicam os resultados dele. Assim nenhum número é inventado e todo número tem origem (fonte, período, resolução).

## Diagrama

```
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
                   PostgreSQL + PostGIS (guarda tudo)
```

O produtor enxerga três coisas: **o questionário, o dashboard e o chat**. A integração de dados externos e o motor trabalham sem ele ver.

## Partes

| Parte | O que faz | Arquivo |
|---|---|---|
| **1. Coleta** | Onboarding: coleta as respostas do produtor, interpreta o texto livre com IA e gera a **ficha do produtor** | [COLETA.md](COLETA.md) |
| **Integração de dados externos** | Busca dados de clima, solo, relevo e vegetação do campo em segundo plano, com cache | [INTEGRACAO-DE-DADOS.md](INTEGRACAO-DE-DADOS.md) |
| **Motor de análise** | Perfil, retrato do solo (fusão de evidências), estratégias (filtro + pontuação) e cenários | [MOTOR-DE-ANALISE.md](MOTOR-DE-ANALISE.md) |
| **2. Dashboard** e **3. Chat + cenários** | O que o produtor vê e como conversa com os dados | [DASHBOARD-E-CHAT.md](DASHBOARD-E-CHAT.md) |
| **Banco de dados** | PostgreSQL + PostGIS e o modelo de dados | [BANCO-DE-DADOS.md](BANCO-DE-DADOS.md) |

O questionário em si está em [`../ONBOARDING.md`](../ONBOARDING.md).

## Stack

| Camada | Escolha | Status |
|---|---|---|
| Banco | **PostgreSQL + PostGIS** | Decidido |
| Backend, motor e integração de dados | Python + FastAPI | Proposto |
| Fila da coleta lenta | Tabela de jobs no próprio Postgres + um worker | Proposto |
| Frontend | PWA mobile-first | A definir o framework |
| IA (texto livre e chat) | Gemini com chamada de ferramentas (`GEMINI_MODEL`); embeddings `gemini-embedding-001` | Decidido (D-013) |

**Por que Python no backend:** o cálculo é científico (pandas, numpy, rasterio para mapas como o GAEZ) e as bibliotecas da NASA (`earthaccess`) são em Python.

## Ordem de construção

1. **Coleta:** questionário, gravação das respostas, IA no texto livre e geração da ficha (perfil, calendário, retrato do solo).
2. **Integração rápida:** NASA POWER, SoilGrids e SRTM, disparados quando o produtor marca o local (pergunta 5).
3. **Motor:** indicadores e estratégias a partir da ficha.
4. **Dashboard** lendo a ficha e o motor.
5. **Chat** com as ferramentas; depois, os **cenários**.
6. **Integração lenta:** NDVI e SMAP via AppEEARS.

O chat vem depois de propósito: sem o motor, ele não tem o que consultar.

## O que precisamos providenciar

| Item | Para quê |
|---|---|
| Base de culturas com parâmetros e sinônimos (PT, EN, ES) | Casar o texto livre; calcular as estratégias |
| Lista de equipamentos (categorias) | Pergunta 26b; filtro de culturas viáveis |
| 12 fotos de solo com origem e licença | Pergunta 19 |
| Glossário em linguagem simples | Dashboard e chat |
| Textos-modelo das explicações (por quê, evidência, benefícios, lacunas, riscos) | Dashboard e chat |
| Conta NASA Earthdata (gratuita) | AppEEARS, SMAP, IMERG |
| Chave da API do Gemini (`GEMINI_API_KEY`) | Texto livre, chat e embeddings |
| Hospedagem | Backend, banco e frontend |

## Decisões pendentes

1. **Linguagem do backend:** Python serve para a equipe?
2. **Framework do frontend.**
3. **Conta do produtor:** e-mail, celular ou sem cadastro (dados salvos no aparelho)? Cadastro costuma ser uma barreira para o pequeno produtor.
4. **Atualização da ficha:** refazer o questionário inteiro ou atualizar por partes (sugestão: por partes, pelo dashboard ou pelo chat).
5. **Pesos iniciais** das fontes e das prioridades (ver [MOTOR-DE-ANALISE.md](MOTOR-DE-ANALISE.md)).
6. **Hospedagem.**
