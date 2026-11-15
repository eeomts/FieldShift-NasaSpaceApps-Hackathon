# Revisão da documentação de submissão (15/11/2026)

Relatório para análise do time. Nada daqui foi implementado.

- **Alvo:** commits `99dd85b..92688b7`: `README.md`, `README.pt-BR.md`, `docs/01` a `08`, `docs/README.md`, `docs/submission/SUBMISSION.md`, `.gitignore`. O roteiro do vídeo, `video-30s-prompt.md`, entrou como referência.
- **Referência:** o *Project Submission Guide* oficial do Space Apps 2026 (cópia local em `docs/NasaSpaceApps-FieldShift/v1/examples/`, ignorada pelo Git).
- **Como foi feita:** três revisores independentes (cético, purista e negócio), com uma rodada de giro entre eles. Depois o arquiteto conferiu cada achado no código.
- **Prazo da submissão:** domingo, 15/11, 23:59.

## Resumo

| | |
|---|---|
| Veredito dos 3 revisores | Juntar só depois de corrigir |
| Achados | 1 crítico, 5 altos, 5 médios e 7 baixos, mais 2 novos do arquiteto |
| Arquiteto | 17 procedem (2 em parte) e 1 não procede |
| Implementação | **Não feita.** Fica para depois da análise do time |

Os números do motor citados nos docs foram conferidos contra o código e estão corretos:
- pesos das fontes de solo e perfil A/B/C;
- graus-dia, frio, calor e água;
- pesos das prioridades e dos critérios;
- 17 culturas no Brasil e 18 nos EUA;
- ZARC em 3 estados;
- web-demo na porta 5174, com Skip All e a fazenda de Story County (Iowa).

## Decisões já tomadas pelo usuário nesta revisão

1. **Satélite:** remover tudo de SMAP, NDVI e GPM IMERG da tela, da API e dos docs.
2. **O que não muda:** `data/rag` e `DECISOES.md` ficam como estão.
3. **Chat:** como a base de conhecimento continua citando SMAP e NDVI, as entradas de `agroai/api/app/services/agente/fontes_status.py` ficam. Elas fazem o chat dizer que o app não usa esses dados.
4. **Vídeo:** usa clipes **gerados** com IA. As ferramentas ainda não foram informadas.
5. **README em português:** o `README.md` em inglês deixa de ter link para o `README.pt-BR.md`.

## Achados

### Crítico

**K-01. Campos obrigatórios ainda com `[TODO]`**
- **Onde:** `SUBMISSION.md:19,23,46`, `README.md:7,82` e `docs/07-ai-use.md:27`.
- **O que falta:** o link do demo, o link do projeto final, a ferramenta de IA do vídeo e a equipe.
- **Por que é crítico:** o guia exige todos os campos preenchidos e links públicos sem login. Vídeo com mais de 30 s ou deck com mais de 7 slides sai do Global Judging.
- **Frase prematura:** "carries a visible watermark" fala de um vídeo que ainda não existe. Além disso, o roteiro (`video-30s-prompt.md:44`) pede "no watermarks", então a marca d'água tem de entrar na edição, em cada clipe gerado.
- **Texto provisório para o projeto final:** `https://github.com/eeomts/FieldShift-NasaSpaceApps-Hackathon`. Confirmar antes, numa janela anônima, que o repositório está público.

### Altos

**K-02. Os docs não batem com a tela sobre o satélite**
- **O problema:** os docs dizem que SMAP, NDVI e GPM "não fazem parte desta versão". Mas o painel, nos fronts `web` e `web-demo`, mostra esses dados pela rota `GET /fazenda/satelite` quando há `EARTHDATA_TOKEN`.
- **Decisão:** remover tudo. O mapa da remoção está abaixo, nos pacotes F1 e B1.
- **Registro:** a D-009 ainda coloca GPM, SMAP e MODIS no núcleo (`DECISOES.md:73-75`). A remoção não tem registro em nenhuma decisão.

**K-03. "What if" e "Scenarios" descrevem algo que não existe**
- **O problema:** o chat tem 5 ferramentas e nenhuma recebe parâmetro de cenário. O prompt também recusa previsão (`prompt.py`, regra 6).
- **Onde:** `README.md:22`, `01-overview.md:25`, `02-how-it-works.md:11-12`, `docs/README.md:22`, `04-methodology.md:99-101`, `05-limitations-roadmap.md:27` e `SUBMISSION.md:15,34`.
- **Texto proposto:** "explains the comparison, the farm's climate and crop parameters, citing the source". A seção "Scenarios" sai.

**K-04. O projeto final é só o repositório**
- **O problema:** não há deploy do web-demo nem capturas de tela. Para rodar o app, o jurado precisa de Docker, Postgres, uv e Node, e sem a chave do Gemini não vê o chat.
- **Proposta:** 3 a 5 capturas no README, em `docs/img/`: o questionário com Skip All, o painel, a comparação e o chat respondendo com a fonte.
- **No `08-run-locally.md`:** dizer o que se vê sem as chaves.
- **Link:** colocar a URL do app, se for publicado.

**K-05. "Enforced in the code" é exagero** (o arquiteto o rebaixou para médio, porque procede só em parte)
- **Onde:** `07-ai-use.md:17`. Só o prompt e o desenho das ferramentas garantem que a IA não invente número; nada no código confere os números da resposta.
- **Texto proposto:** "Scores are computed in code, outside the model; the model only gets numbers through tool results, and the prompt forbids it from producing numbers of its own. The answer text is not checked number by number."

**K-06. O link para o README em português** (passa a médio, porque o link vai sair)
- **O problema:** o README em português expõe os "Pontos em aberto" do time.
- **Linhas desatualizadas:**
  - `README.pt-BR.md:145` fala em "duas D-010", mas a segunda virou D-013;
  - `README.pt-BR.md:144` diz que a Open-Meteo não está no `DECISOES.md`, o que procede. O comentário no Dashboard cita uma "D-014" que não existe.
- **Decisão:** tirar o link de `README.md:7`.

### Médios

**K-07. A declaração de uso de IA está incompleta**
- **Vídeo:** trocar "edited" por "generated and edited with AI tools [ferramentas]" e acrescentar "watermark on every AI-generated clip". Os lugares são `07-ai-use.md:25,27`, `SUBMISSION.md:46` e `README.md:75`.
- **Metadados:** nenhum commit do intervalo tem Co-Authored-By, então não prometer metadado de commit. Como metadado, usar a descrição do vídeo no YouTube: "Contains AI-generated footage".
- **Dados:** declarar se o catálogo e as evidências tiveram apoio de IA. Isso depende de confirmação do time.

**K-08. Faltam referências**
- As fontes tipográficas Bricolage Grotesque e DM Sans (Google Fonts, licença SIL OFL), em `06-references.md` e `SUBMISSION.md:61-64`.
- A música e a voz do vídeo, se forem de banco, com fonte e licença.

**K-09. O roteiro do vídeo promete o que o app não faz**
- Arquivo: `video-30s-prompt.md`.
- **"40 years"** (linhas 14 e 66) deve virar "30 years of climate normals (NASA POWER, 1991-2020)".
- **"e se" e "24/7"** saem. No lugar, perguntas que o chat responde, como "How much rain does my farm get in January?".
- **A mensagem de voz** não existe no app. Tem de ser digitada.
- **Os selos MODIS, SMAP e GPM** passam a ser NASA POWER e SRTM.
- **O arquivo** está em português na raiz do repositório. Mover para `docs/NasaSpaceApps-FieldShift/v1/` ou apagar depois da gravação.

**K-11. Falta um exemplo concreto**
- **Proposta:** um parágrafo "Example (demo farm, Story County, Iowa)" no `SUBMISSION.md`, com a rotação atual, as 2 alternativas e o porquê.
- **Regra:** os números só podem ser copiados da tela do web-demo, com a fonte.

**A-01 (novo). O chat não liga seguindo o `08-run-locally.md`**
- **O problema:** o comando `env $(grep -v '^#' .env.dev) ...` exporta `GEMINI_API_KEY` vazio, e isso vence o `.env`. Quem seguir os docs nunca liga o chat.
- **Proposta:** mostrar o comando com `GEMINI_API_KEY=<key>`.
- **Linhas 28-29:** separar em Option A e Option B. Dois `cd` seguidos quebram quando colados juntos.

**A-02 (novo). As janelas de plantio dos EUA já funcionam**
- **O que acontece no código:** o motor já aplica as janelas de semeadura do USDA Handbook 628 às culturas de venda dos EUA (`candidatas.py:94-120`).
- **Onde corrigir:** `05-limitations-roadmap.md:19`, `06-references.md:22`, `SUBMISSION.md:38`, `README.pt-BR.md:123` e `04-methodology.md:68`. Os quatro primeiros dizem que esses dados ainda não são lidos, e o 04 só cita a janela das culturas de cobertura.

### Baixos

- **K-10:** os materiais linkados estão em português. Avisar uma vez em `docs/README.md:32` e marcar "(in Portuguese)" em `06-references.md:27-30,34` e em `04-methodology.md:109,116`.
- **K-12:** dizer o que vai para o Gemini. Proposta de seção "What is sent to Gemini" no `07-ai-use.md`:
  - no questionário, só o texto livre, o hemisfério e o idioma;
  - no chat, as mensagens, um resumo sem nome, e-mail nem coordenada, e os resultados das ferramentas, com o local arredondado a 0,1 grau.
- **K-13:** incluir Run Locally e Submission na tabela de documentação do `README.md`.
- **K-14:** o passo a passo de execução está repetido em 3 lugares. É aceitável; o problema real é o A-01.
- **K-15:** em `05-limitations-roadmap.md:17`, trocar por "cites NASA POWER; slope from SRTM appears through the rotation comparison".
- **K-16:** padronizar "AgroAI | Field Shift" e "English and Portuguese" em `01-overview.md:20`.
- **K-17:** em `01-overview.md:11`, tirar "soil moisture, vegetation".
- **K-18:** o "Last updated" escrito à mão. **Não procede.**

## Pacotes de implementação (pendentes)

### F1: `agroai-frontend` (nos dois fronts, `agroai/web` e `agroai/web-demo`)

- **`pages/Dashboard.tsx`:**
  - sai a chamada `obterSatelite`, junto com os cartões "Rain on your field", SMAP e NDVI;
  - sai o selo "NASA satellite data";
  - o alerta passa a usar só a previsão;
  - o rodapé do gráfico do ano deixa de citar o MODIS e passa a citar o calendário do produtor.
- **`components/satelite/Satelite.tsx`:** o arquivo também tem a previsão do tempo. A previsão vai para um `components/previsao/Previsao.tsx` novo, e o resto sai.
- **`api/satelite.ts`:** apagar.
- **`api/tipos.ts`:** apagar os tipos de satélite (linhas 298-346).
- **`Paisagem.tsx`:** os destaques passam a ser "NASA POWER" e "SRTM".
- **`Entrar.tsx`:** "NASA data translated for your field."
- **Verificação:** `npx tsc -p tsconfig.json --noEmit` nos dois fronts.

### B1: `agroai-backend`

- **Apagar:** `routers/satelite.py`, `schemas/satelite.py`, `services/satelite/`, `services/integracao/earthdata.py` e `tests/test_satelite.py`.
- **Editar:** `main.py:8,32`, `core/config.py:29-30`, `.env.example:20-22` e `tests/conftest.py:9`.
- **Não mexer:** `fontes_status.py` fica como está.
- **Banco e VPS:** não precisa de migration, porque não há tabela de satélite (o cache fica em memória), e não há nada para rodar na VPS.
- **Verificação:** pytest no banco de teste.

### Docs (só texto)

1. `SUBMISSION.md`
2. `README.md`
3. `docs/README.md`
4. `01-overview.md`
5. `02-how-it-works.md`
6. `03-nasa-data.md`
7. `04-methodology.md`
8. `05-limitations-roadmap.md`
9. `06-references.md`
10. `07-ai-use.md`
11. `08-run-locally.md`
12. `README.pt-BR.md`
13. `video-30s-prompt.md`
14. `agroai/README.md` e `agroai/web-demo/README.md`

Prioridade: `SUBMISSION.md`, `README.md`, `07-ai-use.md` e `video-30s-prompt.md`.

**Ordem:** F1 e B1 podem ser feitos em paralelo. No deploy, o front sobe junto ou antes, para não chamar uma rota que não existe mais. Os docs são independentes.

## Pendente com o time

- [ ] Link público do vídeo, que deve ter no máximo 30 s e legenda em inglês se a fala não for em inglês.
- [ ] URL pública do web-demo, se houver, ou confirmação de que o projeto final é só o repositório.
- [ ] Nome da equipe e dos integrantes.
- [ ] Ferramentas de IA do vídeo e marca d'água em cada clipe gerado.
- [ ] Se o catálogo e as evidências tiveram apoio de IA.
- [ ] Capturas de tela do app.
- [ ] Registrar no `DECISOES.md` a remoção de SMAP, NDVI e GPM, porque a D-009 ainda os coloca no núcleo.
- [ ] Antes de deixar o repositório público, conferir que o `JWT_SECRET` de `agroai/api/.env.dev` e `.env.test` não é o da VPS.

## Riscos de quando for implementar

- O painel perde o cartão "Rain on your field" e o alerta "Biggest rain this month", que usava a chuva do NASA POWER como reserva.
- O que testar na tela:
  - o painel com e sem ponto no mapa;
  - o alerta com e sem chuva forte prevista;
  - o gráfico do ano sem NDVI;
  - o layout em computador e no celular;
  - os destaques da tela de entrar;
  - a pergunta "o que é NDVI?" no chat, que deve responder com a ressalva de que o app não usa esse dado.
- No fim, rodar um grep de `SMAP|NDVI|IMERG|GPM|what if|Scenario` nos `.md` da submissão.
