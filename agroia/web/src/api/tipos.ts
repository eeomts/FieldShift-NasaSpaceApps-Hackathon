// Espelho de agroia/api/app/onboarding/schemas.py
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

export interface Fazenda {
  id: string;
  respostas: Respostas;
  passo_atual: number;
  onboarding_concluido: boolean;
  status_processamento: string;
  perfil: "A" | "B" | "C" | null;
  papel: "produtor" | "tecnico" | null;
  modificadores: { irrigacao: string | null; animais: boolean | null };
  retrato_solo: {
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

// Chat (espelho de agroia/api/app/schemas/chat.py)
export type TipoFonte = "clima" | "conhecimento" | "cultura" | "fazenda";

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
