# Plano do solo v1 (SoilGrids)

> 15/11/2026. Base: `data/arquitetura-tratamento/...base única.md` (seção "3. SoilGrids"), `docs/.../tools/SOILGRIDS.md`, `MOTOR-DE-ANALISE.md` (cálculo 2: fusão de evidências).

## Decisões do usuário (15/11)
- Card "Sua terra" no Dashboard (front autorizado).
- Erodibilidade K (Williams/EPIC) entra agora, também no critério de erosão do motor. Água disponível (pedotransferência) fica para quando a equipe escolher a função (a do ZARC).

## API
- **Cliente** `app/services/integracao/soilgrids.py`: `GET https://rest.isric.org/soilgrids/v2.0/properties/query`, propriedades `clay, sand, silt, soc, phh2o, bdod, cec, nitrogen, cfvo`, profundidades 0–5, 5–15, 15–30, 30–60, 60–100 cm, valores `mean, Q0.05, Q0.5, Q0.95`. Fatores de conversão da tabela do documento (argila/areia/silte ÷10 → %; soc ÷10 → g/kg; phh2o ÷10; bdod ÷100 → g/cm³; cec ÷10 → cmol(c)/kg; nitrogen ÷100 → g/kg; cfvo ÷10 → %). Argila+areia+silte renormalizado se ≠ 100 ± 2. Médias ponderadas pela espessura: superficial 0–30 cm e raízes 0–100 cm. Incerteza relativa (Q0,95 − Q0,05) ÷ Q0,50. Área urbana/água (valores nulos): sem dado, marcado. API lenta e com limite: timeout longo, poucas tentativas, cache.
- **Derivados**: classe textural (grupamentos da Embrapa: arenosa, média, argilosa, muito argilosa, siltosa), matéria orgânica = carbono × 1,724, acidez pelo pH (mesmas faixas do laudo em `perfil.py`), K USLE pelo método de Williams (EPIC).
- **Cache** (migration `0007`): tabela `solo_ponto` (chave = lat/lon arredondados a 3 casas; camada `superficial`|`raizes`; números convertidos; `classe_textural`; `k_usle`; `incerteza` JSONB; `fonte`; `atualizado_em`). Sem dado também é guardado (para não chamar de novo).
- **Em segundo plano**: ao salvar a fazenda com local novo, `status_processamento` = `processando` e uma tarefa (BackgroundTasks) busca o SoilGrids, refaz o retrato e grava `pronto` (ou `erro`, com o retrato só do produtor). Sem local: `pendente`.
- **Fusão** (cálculo 2) para textura, matéria orgânica e acidez: cada evidência vota com o peso da fonte (laudo 0,9; teste de campo 0,7; observação do produtor 0,5; SoilGrids 0,4; "não sei" 0). Vence o valor com mais votos; confiança pelo total e pela concordância. Quando o SoilGrids discorda do produtor: frase "O mapa global sugere X, mas você observou Y. No seu campo vale o que você vê."
- **Motor**: o critério de erosão passa a usar também o K (fator por classe de K, proposta em `parametros.py`).
- `fontes_status`: SoilGrids passa a "usado".

## Contrato (acréscimos em `GET /fazenda`, nada removido)
```ts
type FonteSolo = "laudo" | "teste_campo" | "produtor" | "soilgrids";
interface EvidenciaSolo { fonte: FonteSolo; valor: string; peso: number; texto: string }
interface AtributoSolo {
  atributo: "textura" | "materia_organica" | "acidez";
  valor: string | null;                 // ex. "argilosa", "media", "alta"
  confianca: "alta" | "media" | "baixa" | null;
  evidencias: EvidenciaSolo[];
  divergencia: string | null;           // a frase quando o mapa discorda do produtor
}
interface SoloPonto {
  argila_pct: number | null; areia_pct: number | null; silte_pct: number | null;
  carbono_g_kg: number | null; materia_organica_g_kg: number | null; ph: number | null;
  ctc_cmol_kg: number | null; densidade_g_cm3: number | null;
  classe_textural: string | null; k_usle: number | null;
  incerteza: Record<string, number | null>;
  camada: "0–30 cm"; fonte: string;     // "SoilGrids 2.0 (ISRIC), 250 m"
  sem_dado: boolean;                    // área urbana ou água
}
// RetratoSolo (já existe) ganha:
//   sintese: AtributoSolo[];
//   soilgrids: SoloPonto | null;
// Fazenda.status_processamento: "pendente" | "processando" | "pronto" | "erro"
```

## Front (autorizado)
- `api/tipos.ts`: os tipos acima; `status_processamento` com o literal.
- `components/solo/SuaTerra.tsx` (novo) + card "Sua terra" no `Dashboard.tsx`: cada atributo da síntese com valor em linguagem simples, selo de confiança, de onde veio (selos "Você", "Laudo", "Mapa global") e a frase de divergência; os números do SoilGrids em "De onde veio". Enquanto `processando`: "Buscando o mapa de solo da sua região… pode levar até 1 minuto" e nova consulta ao `GET /fazenda` a cada 5 s (até 2 min). `erro`: o retrato do produtor e a frase "Não consegui o mapa de solo agora; mostramos o que você contou." `sem_dado`: "O mapa global não cobre este ponto (área urbana ou água)."
