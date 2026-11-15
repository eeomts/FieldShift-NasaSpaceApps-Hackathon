# Plano do motor de rotação v1

> 15/11/2026. Base: `MOTOR-DE-ANALISE.md` (cálculo 3), `data/rag/metodologia-indicadores.md` e as "Regras para o motor" em `data/catalogo/evidencias/README.md` (Yury, 14/11).

## Decisões do usuário (15/11)
- Candidatas: as 3 regras do `MOTOR-DE-ANALISE.md` (janela vazia, troca por tolerante à seca, incluir leguminosa) + a rotação atual.
- Pesos: prioridades 0,5 / 0,3 / 0,2 reescaladas; cada critério não escolhido vale 0,05. Sem prioridade: 1/6 cada.
- Declividade: SRTM (satélite); a resposta q7 (plano/leve/inclinado) fica como reserva quando o SRTM falhar.
- Escopo: Brasil + EUA. O motor escolhe o catálogo pelo país do ponto.

## O que o motor faz
```
fazenda (calendário, prioridades, restrições, local)
  -> país e município/condado (malhas IBGE e Census)
  -> clima da célula (NASA POWER, 1991–2020) + graus-dia por mês + declividade (SRTM)
  -> candidatas -> filtro -> notas 0–1 em 6 critérios -> peso das prioridades
  -> atual + 2 melhores, cada uma com "por que", evidências (número + fonte), alertas, confiança e lacunas
```
A IA não participa de nenhum número. O chat só explica o que o motor devolveu.

## PR D1 — Base do motor (sem rota)
- **Catálogo do motor** (`app/services/motor/catalogo.py`): lê `data/catalogo/culturas.csv` (BR) e `data/catalogo/eua/culturas.csv` (EUA, quando existir); só essas culturas são candidatas. Família botânica e `tipos` do CSV. Cultura do calendário fora do catálogo: entra na rotação atual, mas sem nota ("sem dados suficientes").
- **`arroz_irrigado`** entra em `agroai/base/culturas.json` (regra 8).
- **País e município**: ponto-em-polígono nas malhas `data/brasil/municipios/municipios.geojson` e `data/eua/condados/condados.geojson` (shapely). Migration `0006`: `fazenda.pais` (`BR`|`US`|null) e `fazenda.codigo_local` (IBGE 7 dígitos ou FIPS 5), calculados ao salvar o local.
- **Graus-dia** (regra 2): GD = soma de max(0, Tmed − Tb), sem teto, a partir da série DIÁRIA do POWER. Ao baixar a célula, gravar a soma mensal para cada Tb inteiro de 0 a 20 °C (`clima_mensal.gd_por_tb` JSONB ou tabela própria). Mesma conta do `data/catalogo/scripts/gd_nasa_power.py`.
- **SRTM** (`app/services/integracao/srtm.py`): OpenTopoData `srtm30m`, grade 3×3 (~30 m) em volta do ponto, declividade pelo método de Horn, classes da Embrapa (plano < 3 %, suave 3–8, ondulado 8–20, forte 20–45, montanhoso > 45). Cache por ponto arredondado. Falhou: usa q7 e marca a fonte.
- **Testes** sem rede: catálogo, país (pontos da demo BR e EUA), GD contra o script dos dados, declividade com grade simulada.

## PR D2 — O motor (funções puras + testes)
`app/services/motor/`:
- **Candidatas** (`candidatas.py`): rotação atual sempre; (1) cada cultura do catálogo que caiba na janela vazia (ciclo mínimo ≤ dias da janela); (2) troca da cultura principal (a de ciclo mais longo) por uma `tolerante_seca`; (3) uma `fixadora_n` na janela ou no lugar de uma cultura. Sem repetidas; no máximo ~30.
- **Filtro** (`filtro.py`), cada eliminação com o motivo:
  - Excluída pelo produtor (q26a). Equipamento: a cultura precisa de pelo menos um equipamento listado em `cultura_equipamentos.csv` para plantio e para colheita entre os que o produtor tem (q26b); se ele não respondeu, não filtra.
  - Graus-dia na janela < 90 % do `graus_dia_ciclo_min` elimina; 90–100 % "no limite térmico, validar localmente" (regra 2). Mandioca: só o teste de frio (regra 9).
  - Água (regra 1): demanda ETc = Kc × ET0 no ciclo (Kc inicial/médio/final por terços do ciclo) contra a chuva do mesmo período (média 1991–2020). **Proposta:** chuva < 50 % da ETc elimina; 50–80 % "água no limite". Com irrigação (q6 sim) não filtra; "parte" marca alerta. Perenes: anual.
  - Geada: cultura `sensivel_geada` é eliminada se em mais de 30 % dos anos houve dia de geada em algum mês do ciclo (`ARQUITETURA-COMPLETA.md`).
  - Arroz irrigado: só com irrigação ou várzea (regra 8).
- **Critérios 0–1** (`criterios.py`). Propostas, a validar com os pesquisadores:
  - **Água:** 1 − (ETc da rotação no ano ÷ chuva do ano), limitado a 0–1.
  - **Terra:** 0,4 × (meses cobertos ÷ 12) + 0,3 × biomassa (classe 0–1) + 0,3 × (1 se tem fixadora de N).
  - **Erosão:** parcela dos dias de chuva forte que caem em mês coberto, penalizada pela declividade: 1 − (1 − parcela) × fator (plano 0,25; suave 0,5; ondulado 0,75; forte ou mais 1,0).
  - **Pragas:** alternância de famílias botânicas: (famílias distintas − 1) ÷ (culturas − 1); 0 com uma cultura só; desconta repetição seguida da mesma família.
  - **Renda:** culturas comerciais na rotação: 0 → 0; 1 → 0,5; 2 → 0,8; 3+ → 1.
  - **Animais:** maior `valor_forrageiro` da rotação (baixo 0,3; médio 0,6; alto 1). Vazio: critério ignorado e peso redistribuído (regra 5).
- **Peso e ordem** (`pontuacao.py`): pesos da decisão do usuário; soma ponderada; atual + 2 melhores diferentes entre si.
- **Explicação** (`explicacao.py`): para cada estratégia, o "por que" (critérios que mais subiram em relação à atual), as evidências (cada número com fonte e período), os alertas, a confiança (a menor das culturas, regra 10: confiança baixa mostra faixa) e as lacunas.
- **Testes** com fazendas sintéticas e os 3 pontos da demo BR (+ EUA quando houver catálogo).

## PR D3 — Rota, chat e tela (contrato aprovado em 15/11)
```
GET /fazenda/estrategias            (Authorization: Bearer)
200 -> Analise
401 sem login
404 "Fazenda não encontrada."
422 "Marque o local da fazenda para comparar rotações."
    "Ainda não temos as culturas desta região na base."
    "Cadastre o que você planta para comparar rotações."
503 "Não consegui os dados de clima da NASA agora. Tente de novo em alguns minutos."
```
```ts
type Criterio = "agua" | "terra" | "erosao" | "pragas" | "renda" | "animais";
interface Evidencia { texto: string; valor: number | string | null; unidade: string | null; fonte: string; periodo: string | null }
interface ItemEstrategia { cultura_id: string | null; nome: string; inicio_mes: number | null; fim_mes: number | null; perene: boolean }
interface NotaCriterio { criterio: Criterio; nota: number | null; explicacao: string; evidencias: Evidencia[] }
interface Resultado {
  id: string; nome: string;
  origem: "atual" | "janela" | "tolerante_seca" | "leguminosa";
  itens: ItemEstrategia[];
  nota_final: number | null;            // 0 a 1 (a tela mostra 0 a 100 pontos)
  notas: NotaCriterio[];                // na ordem de Criterio
  por_que: string[]; onde_piora: string[];
  alertas: { codigo: string; texto: string }[];
  confianca: "alta" | "media" | "baixa";
  lacunas: string[];
}
interface Analise {
  pais: "BR" | "US";
  atual_e_a_melhor: boolean;
  pesos: Record<Criterio, number>;
  atual: Resultado;
  melhores: Resultado[];                // 0 a 2
  eliminadas: { nome: string; motivos: string[] }[];
  fontes: string[];
  gerado_em: string;                    // ISO 8601 UTC
}
```
- Cálculo na hora (sem cache da análise); a 1ª vez numa região baixa o NASA POWER (10–30 s).
- Chat: ferramenta `comparar_estrategias()` (sem argumentos) lê a análise; fonte nova do chat com `tipo: "analise"` (rótulo na tela: "Comparação do AgroAI"); `fontes_status`: SRTM passa a "usado" (declividade na comparação).
- Front (autorizado): tipos em `api/tipos.ts` (+ `"analise"` em `TipoFonte`), `api/estrategias.ts`, `components/estrategias/`, seção "Suas estratégias" no `Dashboard.tsx` no lugar do card provisório, rótulo no `components/chat/Mensagens.tsx`.

## Dados que faltam
- **Catálogo dos EUA:** só `milho` (1 de 12). Construído pelo agente `agroai-dataset-eua`, em lotes. Sem ele, fazenda nos EUA fica sem alternativas.
- PAM (palhada local, regra 6): sem ela, usa o valor típico da régua.
- ZARC janelas: não é necessário no v1 (a janela vem do calendário do produtor).

## Em aberto
- Limites de água (50 % / 80 %) e as fórmulas dos critérios: proposta do coordenador, a validar com o Yury.
- Teste de sensibilidade com Kc mínimo e máximo nas culturas de confiança baixa (regra 7): depois do v1.
