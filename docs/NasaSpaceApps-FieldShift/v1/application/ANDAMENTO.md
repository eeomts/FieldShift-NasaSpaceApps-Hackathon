# Andamento - AgroAI

Atualizado: 15-11-26

| Frente | Status | PR / branch | Observação |
|---|---|---|---|
| Chat v1 (RAG, clima NASA POWER, agente, tela) | feito | #28, #29, #30 | escopo só lavoura; chat sabe quais fontes o app usa |
| Motor de rotação D1 + D2 + D3 (base, comparação, rota, chat, tela) | feito | #39, #41 | migration 0006; constantes propostas em `motor/parametros.py` |
| Motor: regras 13 (estados válidos) e 1 (água nunca elimina) | feito | #43 (Yury) | arranjos regionais da regra 13 ainda não lidos |
| Catálogos BR (17) e EUA (18), ZARC GO/RS/BA, PAM, equipamentos | feito | #43 | dados prontos; o motor ainda não lê ZARC, PAM nem as colunas de janela |
| Solo (SoilGrids + retrato do solo + card "Sua terra") | em revisão | `feat/solo-soilgrids` | subir e abrir PR |
| Motor v2, pacote A: regras 2, 10, 11, 12, 13 (arranjos), 15, 16 | pendente | — | só backend, sem migration |
| Motor v2, pacote B: ZARC (Z1–Z8) e NASS datas de plantio (EUA) | pendente | — | depende do solo (Z3); muda contrato e tela |
| Motor v2, pacote C: palhada local pela PAM (regra 6) | pendente | — | — |
| Regra 7 (sensibilidade do Kc) | pendente | — | depois do v1 |

## Decisões desta etapa
- 15-11-26: motor com as 3 regras de candidatas do `MOTOR-DE-ANALISE.md`; pesos 0,5/0,3/0,2 + 0,05 para os não escolhidos; declividade pelo SRTM (q7 como reserva); Brasil + EUA.
- 15-11-26: fórmulas e limites sem número na documentação ficam como propostas em `parametros.py`, a validar com o Yury.
- 15-11-26: geada só na fase de floração (terço do meio do ciclo).
- 15-11-26: modelo do chat no local: `gemini-3.5-flash-lite`.
- 15-11-26: ordem do que falta: solo → pacote A → pacote B → pacote C.

## Dados usados
- Nesta versão o app usa NASA POWER (clima), SRTM (relevo) e SoilGrids (solo), mais a previsão da Open-Meteo. Umidade do solo (SMAP) e NDVI ficaram fora; o AppEEARS foi descartado em 15/11/2026.

## Pendências
- Yury: validar as propostas de `parametros.py` e criar `tmin_critica_c` por cultura (geada do trigo exagerada).
- Pedro: categorias de equipamento que faltam; fotos de solo no lugar das amostras de cor.
- Equipe: duas D-010 no `DECISOES.md`: renumerar uma.
- Augusto: confirmar pontos da demo (caixas do `ToDo/` desmarcadas). O AppEEARS foi descartado em 15/11/2026 (D-009): não há mais pedido a fazer.
- PR #46 (docs sem espanhol) aberto.
- Faturamento do Gemini antes da demo.

## Pendente de produção
- Migrations 0003 em diante (rodam no start); `GEMINI_API_KEY` no `producao.env`; mover para o compose na VPS (último passo).

## Onde paramos
Passo 1: testes da branch do solo, commit dos docs, push e PR. Depois, plano e contrato do pacote A (`app/services/motor/catalogo.py` passa a ler as colunas de janela e texto; `filtro.py` regras 2, 11, 12).
