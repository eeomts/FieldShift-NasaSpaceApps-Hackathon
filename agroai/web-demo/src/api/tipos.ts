// Espelho de agroai/api/app/onboarding/schemas.py
export type SNS = "sim" | "nao" | "nao_sei";

export interface Usuario {
  id: string;
  nome: string;
  email: string;
  idioma: string; // "pt" | "en" (contas antigas podem ter outro valor)
  onboarding_concluido: boolean;
}

export interface ItemCalendario {
  cultura_id: string | null;
  texto_original: string;
  inicio_mes: number | null;
  fim_mes: number | null;
  perene: boolean;
  consorcio_com: string[];
  ocupa: "todo" | "parte" | null;
  /** Só no front: ids que o produtor precisa escolher (ex.: arroz x arroz irrigado). */
  alternativas?: string[];
}

export type Correcao = "calcario" | "gesso" | "outra" | "nao" | "nao_sei";
export type EventoPerda = "geada" | "chuva_forte" | "calor" | "seca" | "alagamento" | "granizo" | "salinidade";

export interface Local {
  lat: number;
  lon: number;
  nome?: string | null; // até 200
  pais?: string | null; // ISO alfa-2 maiúsculo (ex.: "BR")
  zona_climatica?: string | null; // Köppen, até 4 letras (ex.: "Aw")
}

/** GET /local/buscar */
export interface LugarBusca {
  nome: string;
  pais: string | null;
  pais_codigo: string | null;
  lat: number;
  lon: number;
}

/** GET /local/info */
export interface InfoLocal {
  hemisferio: "N" | "S";
  zona_climatica: string | null;
  lugar: string | null;
  pais: string | null;
  pais_codigo: string | null;
  geada_no_historico: boolean | null;
}

export interface Perda {
  resposta: SNS | null;
  ano: number | null;
}

export interface CulturaExcluida {
  cultura_id: string | null;
  texto_original: string;
  motivo: "mercado" | "costume" | "deu_errado" | "outro" | null;
}

export interface Equipamento {
  equipamento_id: string | null;
  texto_original: string;
}

export type Prioridade = "agua" | "terra" | "erosao" | "renda" | "animais" | "pragas";

export interface Respostas {
  q1_quem?: "produtor" | "tecnico" | null;
  q2_area?: "ate_2" | "2_20" | "20_200" | "200_1000" | "mais_1000" | null;
  q3_tecnico?: "sim" | "as_vezes" | "nao" | null;
  q4_animais?: "sim" | "nao" | null;
  q5_local?: Local | null;
  q6_irrigacao?: "sim" | "parte" | "nao" | null;
  q7_terreno?: "plano" | "leve" | "inclinado" | null;
  q8_texto?: string | null;
  q8_culturas?: ItemCalendario[];
  q9_meses_vazios?: SNS | null;
  q10_pos_colheita?: "parado" | "pasto" | "outra" | "cobertura" | null;
  q11_palha?: SNS | null;
  q12_analise?: SNS | null;
  q12_tem_resultado?: SNS | null;
  q12_ano?: number | null;
  q12_laudo?: Laudo | null;
  q13_textura?: "arenosa" | "media" | "argilosa" | "nao_sei" | null;
  q14_encharca?: SNS | null;
  q15_casca?: SNS | null;
  q16_erosao?: SNS | null;
  q17_dura?: SNS | null;
  q18_minhocas?: SNS | null;
  q19_cor?: "escura" | "marrom" | "vermelha" | "amarela" | "cinza" | "clara" | "nao_sei" | null;
  q19_jeito?: "solta" | "fofa" | "gruda" | "torroes" | "racha" | "pedras" | "nao_sei" | null;
  q20_partes_piores?: SNS | null;
  q21_correcao?: Correcao[];
  q21_correcao_outra?: string | null;
  q22_adubo?: SNS | null;
  q23_chuva_mudou?: SNS | null;
  q24_perdas?: Partial<Record<EventoPerda, Perda>>;
  q25_prioridades?: Prioridade[];
  q26a_texto?: string | null;
  q26a_excluidas?: CulturaExcluida[];
  q26b_texto?: string | null;
  q26b_equipamentos?: Equipamento[];
}

/** Principais valores de uma análise de solo (pergunta 12). Tudo opcional. */
export interface Laudo {
  ph_agua?: number | null;
  materia_organica_g_dm3?: number | null;
  fosforo_mg_dm3?: number | null;
  potassio_mg_dm3?: number | null;
  argila_pct?: number | null;
  ctc_cmolc_dm3?: number | null;
  saturacao_bases_pct?: number | null;
}

/** Um item do retrato do solo. `valor` é a categoria que o motor usa; `texto` é o que aparece na tela. */
export interface Indicador {
  atributo: string;
  valor: string;
  texto: string | null;
  fonte: "produtor" | "laudo";
  origem: string;
  confianca: string;
  numero?: number | null;
}

export type FonteSolo = "laudo" | "teste_campo" | "produtor" | "soilgrids";

export interface EvidenciaSolo { fonte: FonteSolo; valor: string; peso: number; texto: string }

export interface AtributoSolo {
  atributo: "textura" | "materia_organica" | "acidez";
  valor: string | null;
  confianca: "alta" | "media" | "baixa" | null;
  evidencias: EvidenciaSolo[];
  divergencia: string | null;
}

export interface SoloPonto {
  argila_pct: number | null; areia_pct: number | null; silte_pct: number | null;
  carbono_g_kg: number | null; materia_organica_g_kg: number | null; ph: number | null;
  ctc_cmol_kg: number | null; densidade_g_cm3: number | null;
  classe_textural: string | null; k_usle: number | null;
  incerteza: Record<string, number | null>;
  camada: "0–30 cm"; fonte: string;
  sem_dado: boolean;
}

export interface Fazenda {
  id: string;
  respostas: Respostas;
  passo_atual: number;
  onboarding_concluido: boolean;
  status_processamento: "pendente" | "processando" | "pronto" | "erro";
  perfil: "A" | "B" | "C" | null;
  papel: "produtor" | "tecnico" | null;
  modificadores: { irrigacao: string | null; animais: boolean | null };
  retrato_solo: {
    fonte?: string;
    sintese?: AtributoSolo[];
    soilgrids?: SoloPonto | null;
    indicadores?: Indicador[];
    figuras?: { cor: string | null; jeito: string | null; leitura: string; confianca: string; atributos: Indicador[] } | null;
  };
  proximos_passos: { id: string; titulo: string; texto: string }[];
  meses_sem_cobertura: number[];
}

export interface ItemInterpretado {
  texto_original: string;
  id: string | null;
  encontrado: boolean;
  confianca: "alta" | "media" | "baixa";
  alternativas?: string[];
  inicio_mes?: number | null;
  fim_mes?: number | null;
  perene?: boolean;
  consorcio_com?: string[];
  motivo?: CulturaExcluida["motivo"];
}

export interface PedidoInterpretar {
  campo: "culturas" | "excluidas" | "equipamentos";
  texto: string;
  hemisferio: "N" | "S";
  idioma: "pt" | "en";
}

export interface Interpretacao {
  fonte: "ia" | "lista";
  itens: ItemInterpretado[];
}

export interface CulturaBase {
  id: string;
  nome: string;
  grupo: string;
  perene: boolean;
  tipos: string[];
}

export interface EquipamentoBase {
  id: string;
  nome: string;
}

// Chat (espelho de agroai/api/app/schemas/chat.py)
export type TipoFonte = "clima" | "conhecimento" | "cultura" | "fazenda" | "analise";

export interface Fonte {
  tipo: TipoFonte;
  titulo: string;
  detalhe: string | null;
}

export interface Mensagem {
  id: number;
  papel: "produtor" | "assistente";
  texto: string;
  fontes: Fonte[];
  ferramentas_usadas: string[];
  criada_em: string; // ISO 8601 UTC
}

export interface ConversaResumo {
  id: number;
  titulo: string | null;
  criada_em: string;
  atualizada_em: string;
}

export interface EnviarMensagem {
  mensagem: string;
  idioma: "pt" | "en" | null;
}

export interface Conversa extends ConversaResumo {
  mensagens: Mensagem[];
}

// Motor de rotação (espelho de agroai/api/app/schemas/estrategias.py)
export type Criterio = "agua" | "terra" | "erosao" | "pragas" | "renda" | "animais";

export interface Evidencia {
  texto: string;
  valor: number | string | null;
  unidade: string | null;
  fonte: string;
  periodo: string | null;
}

export interface ItemEstrategia {
  cultura_id: string | null;
  nome: string;
  inicio_mes: number | null;
  fim_mes: number | null;
  perene: boolean;
}

export interface NotaCriterio {
  criterio: Criterio;
  nota: number | null;
  explicacao: string;
  evidencias: Evidencia[];
}

export interface Resultado {
  id: string;
  nome: string;
  origem: "atual" | "janela" | "tolerante_seca" | "leguminosa";
  itens: ItemEstrategia[];
  nota_final: number | null; // 0 a 1 (a tela mostra 0 a 100 pontos)
  notas: NotaCriterio[];
  por_que: string[];
  onde_piora: string[];
  alertas: { codigo: string; texto: string }[];
  confianca: "alta" | "media" | "baixa";
  lacunas: string[];
}

export interface Analise {
  pais: "BR" | "US";
  atual_e_a_melhor: boolean;
  pesos: Record<Criterio, number>;
  atual: Resultado;
  melhores: Resultado[];
  eliminadas: { nome: string; motivos: string[] }[];
  fontes: string[];
  gerado_em: string; // ISO 8601 UTC
}

// Satélite da fazenda (rota GET /fazenda/satelite). Datas em "AAAA-MM-DD".
export interface Umidade {
  fonte: string;
  resolucao: string;
  data: string;
  superficie: number; // m³/m³, 0-5 cm
  raiz: number; // m³/m³, zona das raízes
  situacao: "seco" | "normal" | "umido" | null;
  posicao: number | null; // 0 a 1 entre os mesmos dias dos anos anteriores
  media_historica: number | null;
  anos_comparados: number;
}

export interface Ndvi {
  fonte: string;
  resolucao: string;
  data: string;
  valor: number;
  situacao: "descoberto" | "pouco" | "verde" | "muito";
  serie: { data: string; valor: number }[];
}

export interface DiaChuva {
  data: string;
  mm: number;
}

export interface Chuva {
  fonte: string;
  resolucao: string;
  dias: DiaChuva[];
  total_7d: number;
  total_30d: number;
  maior: DiaChuva | null;
}

export interface Satelite {
  lat: number;
  lon: number;
  umidade: Umidade | null;
  ndvi: Ndvi | null;
  chuva: Chuva | null;
  faltas: Partial<Record<"umidade" | "ndvi" | "chuva", CodigoFalta>>;
  avisos: ("imerg_bloqueado" | "imerg_indisponivel")[];
  gerado_em: string;
}

/** Por que um dado de satélite não veio (o texto, em PT ou EN, fica no front). */
export type CodigoFalta = "sem_token" | "sem_permissao" | "sem_dado_ponto" | "nuvem" | "sem_arquivo" | "fora_do_ar" | "erro";

// Previsão dos próximos 7 dias (rota GET /fazenda/previsao, Open-Meteo).
export interface DiaPrevisao {
  data: string;
  tmax: number | null; // °C
  tmin: number | null; // °C
  chuva_mm: number | null;
  chance_chuva: number | null; // %
  codigo_tempo: number | null; // WMO
}

export interface Previsao {
  fonte: string;
  licenca: string;
  dias: DiaPrevisao[];
  gerado_em: string;
}
