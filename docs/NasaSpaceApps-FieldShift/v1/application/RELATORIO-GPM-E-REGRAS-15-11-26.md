# GPM IMERG no MVP e as regras do desafio (15/11/2026)

Relatório para o time analisar com calma. Nada daqui foi implementado.

- **Pergunta:** o GPM é necessário no MVP? Sem ele, o projeto continua dentro das regras do Field Shift?
- **Base:** `main` em `5c496f3`, texto oficial do desafio (`desafio-oficial-nasa-field-shift.md`), `DECISOES.md`, `REVISAO-SUBMISSAO-15-11-26.md`, `docs/submission/SUBMISSION.md` e o código de `agroai/`.
- **Teste de tela relacionado:** issue #57 (motor de rotação nas 6 fazendas da demo). Todos os itens bateram, e só NASA POWER, SRTM, SoilGrids e a base de culturas apareceram como fonte.

## Resumo

| Pergunta | Resposta |
|---|---|
| O GPM foi usado nos datasets (`data/`)? | Não. Nenhum arquivo de dado do GPM ou IMERG; só textos de planejamento. |
| O motor de rotação usa o GPM? | Não. Chuva, água, erosão, calor, geada e graus-dia vêm do NASA POWER. |
| O app usa o GPM em algum lugar? | Só o cartão de chuva do painel, e só com `EARTHDATA_TOKEN`. Sem token, cai para o NASA POWER. |
| O GPM é obrigatório no desafio? | Não. O desafio sugere ("You may explore ... GPM ..."). |
| Sem o GPM, estamos dentro das regras? | Sim. O app usa NASA POWER e SRTM, os dois citados no texto oficial. |
| O que já foi decidido? | Remover SMAP, NDVI e GPM da tela, da API e dos docs (REVISAO-SUBMISSAO, K-02). Ainda não implementado. |

## 1. Onde o GPM aparece hoje

### Dados (`data/`)
- Nenhum arquivo de dado do GPM ou IMERG.
- `data/arquitetura-tratamento/Field Shift Brasil — Tratamento de dados e arquitetura da base única.md` trata o IMERG como **integração opcional**: segunda fonte de chuva, confiança pela diferença com o POWER e erosividade R com célula de 11 km. A checklist do documento deixa em aberto "Se SMAP L4 e GPM IMERG entram na primeira versão".
- `data/rag/o-que-mede-cada-satelite.md` já diz que o app não usa GPM, SMAP e NDVI nesta versão (commit `86a8a30`).

### Código
- **API:** `agroai/api/app/services/satelite/satelite_service.py` (`_chuva_imerg`, cerca de 35 linhas) lê o `GPM_3IMERGDL` v07 pelo Earthdata (CMR e OPeNDAP). No mesmo serviço estão o SMAP L4 (`SPL4SMGP`) e o MODIS NDVI (`MOD13Q1`). A rota é `GET /fazenda/satelite` (`main.py:8,32`).
- **Fronts** (`agroai/web` e `agroai/web-demo`, cada um com as mesmas referências):
  - `pages/Dashboard.tsx`: chama `obterSatelite`, mostra os cartões de chuva, umidade e saúde da lavoura e o selo "Dados de satélite da NASA". O rodapé do gráfico do ano diz "NASA MODIS NDVI (MOD13Q1)".
  - `components/satelite/Satelite.tsx`
  - `api/satelite.ts`
  - `components/Paisagem.tsx`: a tela de entrar mostra "Umidade do solo · SMAP" e "Chuva da semana · GPM".
- **Chat:** `agroai/api/app/services/agente/fontes_status.py` marca o GPM IMERG como não usado. Pela decisão 3 da REVISAO-SUBMISSAO, isso fica.

### Como aparece na tela hoje (teste local, sem `EARTHDATA_TOKEN`)
- O cartão de chuva mostra "NASA POWER (PRECTOTCORR) · ~50 km", a reserva do serviço.
- Os cartões de umidade e de saúde da lavoura mostram "O servidor ainda não tem o acesso aos dados da NASA (Earthdata)".
- A tela de entrar continua prometendo SMAP e GPM.

### Documentos
- `SUBMISSION.md` e `README.md` já dizem que SMAP, NDVI e GPM "are not part of this version".
- `DECISOES.md` ainda coloca o GPM IMERG no núcleo: na D-002 (substituída) e na D-009 (vigente, linhas 73-75).

## 2. O GPM é necessário no MVP?

Não.

- **O desafio não exige.** O texto oficial pede "a decision-support tool that uses NASA Earth observations". Os satélites aparecem como sugestão: "You may explore NASA datasets such as SMAP, ECOSTRESS, GPM, Landsat, MODIS, NASA POWER, GRACE and GRACE-FO, and SRTM or other NASA elevation products". As orientações vêm com "You may (but are not required to)".
- **O motor não depende dele.** A comparação de rotações usa só o NASA POWER para clima e chuva. Os 6 testes da issue #57 bateram sem nenhum dado do GPM.
- **Pôr o IMERG no motor é trabalho grande.** Seria preciso a segunda fonte de chuva, a regra de confiança e a erosividade em 11 km. Isso não cabe no prazo da submissão.

## 3. Sem o GPM, estamos dentro das regras?

Sim. O app usa dois dados da NASA que estão no texto oficial e na aba Resources:

| Fonte da NASA | Citada no desafio? | Uso no app |
|---|---|---|
| NASA POWER | Sim, pelo nome e na aba Resources | Todo o motor: chuva, ET0 (FAO-56), calor, geada, graus-dia, dias de chuva forte. Também a chuva dos últimos 30 dias no painel. |
| SRTM 30 m | Sim ("SRTM or other NASA elevation products") | Declividade medida, usada na nota de erosão |

Cada número do motor aparece na tela com a fonte e o período (conferido na issue #57).

### Pontos de atenção para o pitch
1. **O NASA POWER é um produto modelado.** Ele combina reanálise e satélite; não é uma imagem direta. Como o desafio o cita pelo nome, isso não tira o projeto das regras. Ainda assim, vale apresentar o SRTM como observação direta de satélite e o POWER como os 30 anos de clima da NASA (1991-2020).
2. **O maior risco é prometer o que não usa.** Um jurado que vir "Chuva da semana · GPM" na tela de entrar e só NASA POWER no resto do app pode ler isso como exagero. A remoção decidida na REVISAO-SUBMISSAO resolve isso.
3. **No roadmap, o GPM pode continuar.** O `SUBMISSION.md` já lista "satellite data (SMAP, NDVI, GPM IMERG) in the analysis and the chat" como próximo passo. É honesto e mostra que a equipe sabe onde o GPM entraria.

## 4. A decisão já tomada e o que falta

A REVISAO-SUBMISSAO (decisão 1 e K-02) definiu: **remover tudo de SMAP, NDVI e GPM IMERG da tela, da API e dos docs.** Este relatório não muda essa decisão.

Pendente na `main` em `5c496f3`:

- [ ] **F1 (front, nos dois fronts):**
  - `Dashboard.tsx` sem os cartões de satélite e sem o selo;
  - a previsão sai de `Satelite.tsx` para um componente próprio;
  - apagar `api/satelite.ts` e os tipos de satélite;
  - `Paisagem.tsx` com "NASA POWER" e "SRTM" no lugar de SMAP e GPM.
- [ ] **B1 (API):**
  - apagar `routers/satelite.py`, `schemas/satelite.py`, `services/satelite/`, `services/integracao/earthdata.py` e `tests/test_satelite.py`;
  - ajustar `main.py`, `core/config.py`, `.env.example` e `tests/conftest.py`;
  - não precisa de migration nem de nada na VPS.
- [ ] **`DECISOES.md`:** registrar uma decisão nova dizendo que SMAP, NDVI e GPM ficam fora do MVP e voltam no roadmap. A D-009 deve apontar para ela. Hoje a remoção não tem registro.
- [ ] **No fim:** grep de `SMAP|NDVI|IMERG|GPM` nos `.md` da submissão e nas telas.

### Um detalhe a decidir junto com o F1
O alerta "Maior chuva do mês" e o cartão "Chuva no seu campo" usam a chuva do NASA POWER como reserva. A REVISAO-SUBMISSAO prevê que os dois saiam junto com o satélite. Como essa chuva vem do NASA POWER, uma fonte que o app de fato usa, dá para manter o cartão só com o POWER e tirar apenas o caminho do IMERG. Fica para o time escolher. Os dois caminhos estão dentro das regras.

## 5. Outros achados do teste da issue #57 (para a mesma rodada de ajustes)
- Os tiles do OpenStreetMap no mapa do questionário vêm com "Access blocked" (HTTP 403). A busca e o GPS funcionam.
- A linha de fonte mostra um id interno: "(números para GA, arranjo georgia)".
- Há textos de outra região: girassol com "Dakota do Norte" numa fazenda de Iowa; trevo com "antes do milho" numa fazenda de algodão.
- A classe aparece invertida: "baixo classe", "médio classe".
- O critério Renda escreve "1 culturas" e "2 cultura(s)".
