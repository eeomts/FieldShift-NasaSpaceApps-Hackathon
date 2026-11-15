// Telas, opções e regras do questionário. Fonte: data/onboarding/perguntas.yaml (versão v3 revisada).
// Textos em português do Brasil e inglês americano simples, como no yaml.
import type { EventoPerda, InfoLocal, Local, Respostas } from "../api/tipos";
import type { Idioma } from "../i18n";
import { semCobertura } from "./Calendario";

export interface Par {
  pt: string;
  en: string;
}
export const txt = (p: Par, i: Idioma) => p[i];

export interface Opcao<V extends string = string> {
  valor: V;
  pt: string;
  en: string;
  dica?: Par;
  ico?: string;
  sub?: Par;
}

/* ---------- Partes e telas ---------- */

export const PARTES: Par[] = [
  { pt: "Quem é você?", en: "Who are you?" },
  { pt: "Sua propriedade", en: "Your farm" },
  { pt: "O que você planta?", en: "What do you grow?" },
  { pt: "Conhecendo seu solo", en: "Getting to know your soil" },
  { pt: "Clima e perdas de safra", en: "Weather and crop losses" },
  { pt: "Suas prioridades", en: "Your priorities" },
];

export type TelaId =
  | "q1_quem" | "q2_area" | "q3_tecnico" | "q4_animais"
  | "q5_local" | "q6_irrigacao" | "q7_terreno"
  | "q8_culturas" | "q9_meses_vazios" | "q10_pos_colheita" | "q11_palha"
  | "q12_analise" | "q13_textura" | "q14_sinais" | "q19_solo" | "q20_partes_piores" | "q21_correcao" | "q22_adubo"
  | "q23_chuva_mudou" | "q24_perdas"
  | "q25_prioridades" | "q26a_excluidas" | "q26b_equipamentos";

export interface TelaDef {
  id: TelaId;
  /** número da pergunta no yaml (1 a 23): é o "k / total" do topo */
  numero: number;
  /** parte (1 a 6) */
  parte: number;
}

export const TOTAL_PERGUNTAS = 23;

export const TELAS: TelaDef[] = [
  { id: "q1_quem", numero: 1, parte: 1 },
  { id: "q2_area", numero: 2, parte: 1 },
  { id: "q3_tecnico", numero: 3, parte: 1 },
  { id: "q4_animais", numero: 4, parte: 1 },
  { id: "q5_local", numero: 5, parte: 2 },
  { id: "q6_irrigacao", numero: 6, parte: 2 },
  { id: "q7_terreno", numero: 7, parte: 2 },
  { id: "q8_culturas", numero: 8, parte: 3 },
  { id: "q9_meses_vazios", numero: 9, parte: 3 },
  { id: "q10_pos_colheita", numero: 10, parte: 3 },
  { id: "q11_palha", numero: 11, parte: 3 },
  { id: "q12_analise", numero: 12, parte: 4 },
  { id: "q13_textura", numero: 13, parte: 4 },
  { id: "q14_sinais", numero: 14, parte: 4 },
  { id: "q19_solo", numero: 15, parte: 4 },
  { id: "q20_partes_piores", numero: 16, parte: 4 },
  { id: "q21_correcao", numero: 17, parte: 4 },
  { id: "q22_adubo", numero: 18, parte: 4 },
  { id: "q23_chuva_mudou", numero: 19, parte: 5 },
  { id: "q24_perdas", numero: 20, parte: 5 },
  { id: "q25_prioridades", numero: 21, parte: 6 },
  { id: "q26a_excluidas", numero: 22, parte: 6 },
  { id: "q26b_equipamentos", numero: 23, parte: 6 },
];

/** `passo_atual` salvo = posição na lista TELAS; o resumo vem depois da última. */
export const PASSO_RESUMO = TELAS.length;

/** mostrar_se do yaml: só o q9 depende de outra resposta (sobra mês sem cultura no calendário). */
export function telaVisivel(id: TelaId, r: Respostas): boolean {
  if (id === "q9_meses_vazios") return semCobertura(r.q8_culturas ?? []).length > 0;
  return true;
}

export const telasVisiveis = (r: Respostas) => TELAS.filter((t) => telaVisivel(t.id, r));

export const TITULOS: Record<TelaId, Par> = {
  q1_quem: { pt: "Quem está respondendo?", en: "Who's filling this in?" },
  q2_area: { pt: "Qual o tamanho aproximado da sua propriedade?", en: "Roughly how big is your farm?" },
  q3_tecnico: { pt: "Você recebe visitas de técnicos agrícolas ou agrônomos?", en: "Do extension agents or agronomists visit your farm?" },
  q4_animais: { pt: "Você cria animais?", en: "Do you keep any livestock?" },
  q5_local: { pt: "Onde fica a sua propriedade?", en: "Where is your farm?" },
  q6_irrigacao: { pt: "Você irriga sua lavoura?", en: "Do you irrigate your crops?" },
  q7_terreno: { pt: "Como é o terreno?", en: "Is your land flat or sloping?" },
  q8_culturas: { pt: "Conte do seu jeito o que você planta, e quando.", en: "Tell us in your own words what you plant, and when." },
  q9_meses_vazios: { pt: "Nos períodos sem plantio, a terra fica descoberta?", en: "When nothing is planted, is the soil left bare?" },
  q10_pos_colheita: { pt: "Depois da colheita, o que acontece com a área?", en: "What happens to the field after harvest?" },
  q11_palha: { pt: "Você deixa a palha e os restos da colheita no campo?", en: "Do you leave the stubble and crop residue on the field?" },
  q12_analise: { pt: "Você já fez análise de solo em laboratório?", en: "Have you ever had your soil tested in a lab?" },
  q13_textura: { pt: "Como você descreveria a terra da sua propriedade?", en: "How would you describe the soil on your farm?" },
  q14_sinais: { pt: "Quais destas situações você já percebeu no seu solo?", en: "Which of these have you noticed in your soil?" },
  q19_solo: { pt: "Com qual destas opções você mais identifica a sua terra?", en: "Which of these looks most like your soil?" },
  q20_partes_piores: { pt: "Existem partes da propriedade onde a lavoura sempre produz pior?", en: "Are there parts of the farm where the crop always does worse?" },
  q21_correcao: { pt: "Você já fez alguma correção no solo?", en: "Have you ever treated your soil to correct it?" },
  q22_adubo: { pt: "Você utiliza adubo ou esterco?", en: "Do you use fertilizer or manure?" },
  q23_chuva_mudou: { pt: "Você sente que as chuvas mudaram nos últimos anos?", en: "Do you feel the rains have changed over the last few years?" },
  q24_perdas: { pt: "Quais destes eventos já fizeram você perder uma safra?", en: "Have any of these ever cost you a crop?" },
  q25_prioridades: { pt: "O que é mais importante para você? Escolha até 3.", en: "What matters most to you? Pick up to 3." },
  q26a_excluidas: { pt: "Tem alguma cultura que você não plantaria? Por quê?", en: "Is there any crop you would not grow? Why?" },
  q26b_equipamentos: { pt: "Que máquinas e equipamentos você tem ou consegue utilizar?", en: "What machinery or equipment do you have or can get access to?" },
};

/* ---------- Opções (yaml) ---------- */

export const SIM_NAO_NAO_SEI: Opcao[] = [
  { valor: "sim", pt: "Sim", en: "Yes", ico: "yes" },
  { valor: "nao", pt: "Não", en: "No", ico: "no" },
  { valor: "nao_sei", pt: "Não sei", en: "Not sure", ico: "idk" },
];

export const OPCOES_QUEM: Opcao[] = [
  { valor: "produtor", pt: "Sou o produtor", en: "I'm the farmer", ico: "farmer" },
  { valor: "tecnico", pt: "Sou técnico ou estou ajudando um produtor", en: "I'm an extension agent, or I'm helping a farmer", ico: "helper" },
];

export const OPCOES_TECNICO: Opcao[] = [
  { valor: "sim", pt: "Sim", en: "Yes", ico: "yes" },
  { valor: "as_vezes", pt: "Às vezes", en: "Sometimes", ico: "part" },
  { valor: "nao", pt: "Não", en: "No", ico: "no" },
];

export const OPCOES_ANIMAIS: Opcao[] = [
  { valor: "sim", pt: "Sim", en: "Yes", ico: "cow" },
  { valor: "nao", pt: "Não", en: "No", ico: "no" },
];

export const OPCOES_IRRIGACAO: Opcao[] = [
  { valor: "sim", pt: "Sim, toda a propriedade", en: "Yes, the whole farm", ico: "yes" },
  { valor: "parte", pt: "Somente uma parte", en: "Only part of it", ico: "part" },
  { valor: "nao", pt: "Não", en: "No", ico: "no" },
];

/** Faixas em hectares (valor gravado); o rótulo muda de unidade. */
export const OPCOES_AREA: { valor: NonNullable<Respostas["q2_area"]>; ha: Par; acre: Par }[] = [
  { valor: "ate_2", ha: { pt: "Até 2 ha", en: "Up to 2 ha" }, acre: { pt: "Até 5 acres", en: "Up to 5 acres" } },
  { valor: "2_20", ha: { pt: "De 2 a 20 ha", en: "2 to 20 ha" }, acre: { pt: "De 5 a 50 acres", en: "5 to 50 acres" } },
  { valor: "20_200", ha: { pt: "De 20 a 200 ha", en: "20 to 200 ha" }, acre: { pt: "De 50 a 500 acres", en: "50 to 500 acres" } },
  { valor: "200_1000", ha: { pt: "De 200 a 1.000 ha", en: "200 to 1,000 ha" }, acre: { pt: "De 500 a 2.500 acres", en: "500 to 2,500 acres" } },
  { valor: "mais_1000", ha: { pt: "Mais de 1.000 ha", en: "More than 1,000 ha" }, acre: { pt: "Mais de 2.500 acres", en: "More than 2,500 acres" } },
];

/** unidade.por_pais.acre do yaml */
export const PAISES_ACRE = ["US", "GB", "IN", "PK", "BD", "MM", "LR"];
export type Unidade = "ha" | "acre";
export const unidadePadrao = (pais: string | null | undefined): Unidade => (pais && PAISES_ACRE.includes(pais.toUpperCase()) ? "acre" : "ha");

export const OPCOES_TERRENO: (Opcao & { inclinacao: number })[] = [
  { valor: "plano", pt: "Plano", en: "Flat", sub: { pt: "Sem subida nem descida", en: "No ups or downs" }, inclinacao: 0 },
  { valor: "leve", pt: "Um pouco inclinado", en: "Gentle slope", sub: { pt: "Uma descida suave", en: "A soft incline" }, inclinacao: 12 },
  { valor: "inclinado", pt: "Bem inclinado (morro)", en: "Steep (hillside)", sub: { pt: "Ladeira forte", en: "A strong slope" }, inclinacao: 30 },
];

export const OPCOES_POS_COLHEITA: Opcao[] = [
  { valor: "parado", pt: "Fica parada", en: "It's left fallow", ico: "pause" },
  { valor: "pasto", pt: "Vira pasto", en: "It's grazed", ico: "cow" },
  { valor: "outra", pt: "Planto outra coisa", en: "I plant another crop", ico: "sprout" },
  { valor: "cobertura", pt: "Planto algo para cobrir o solo", en: "I sow a cover crop", ico: "sprout" },
];

export const OPCOES_TEXTURA: (Opcao & { cor?: string })[] = [
  { valor: "arenosa", pt: "Mais arenosa", en: "Sandy", cor: "#E6D2A6" },
  { valor: "media", pt: "Meio-termo", en: "In between (loam)", cor: "#B98B5A" },
  { valor: "argilosa", pt: "Mais argilosa (barro)", en: "Clay", cor: "#8E4A2C" },
  { valor: "nao_sei", pt: "Não sei", en: "Not sure", ico: "idk" },
];

/** Grade da pergunta 14 (cada linha grava o seu campo). */
export const LINHAS_SINAIS: { id: "q14_encharca" | "q15_casca" | "q16_erosao" | "q17_dura" | "q18_minhocas"; pt: string; en: string; bom?: boolean; ico: string }[] = [
  { id: "q14_encharca", pt: "A água fica empoçada por mais de um dia depois de chuva forte", en: "Water stands for more than a day after heavy rain", ico: "flood" },
  { id: "q15_casca", pt: "A terra forma uma casca dura quando seca", en: "The soil forms a hard crust when it dries", ico: "crack" },
  { id: "q16_erosao", pt: "A chuva leva terra embora (erosão, valetas ou água barrenta)", en: "Rain washes soil away (erosion, gullies or muddy runoff)", ico: "rain" },
  { id: "q17_dura", pt: "A terra fica muito dura para cavar ou arar", en: "The soil gets too hard to dig or plow", ico: "area" },
  { id: "q18_minhocas", pt: "Encontro minhocas quando cavo", en: "I find earthworms when I dig", bom: true, ico: "worm" },
];

export const FOTOS = "/fotos-solo/";
export const OPCOES_COR: (Opcao & { imagem?: string })[] = [
  { valor: "escura", imagem: "cor_escura.jpg", pt: "Preta ou marrom bem escura", en: "Black or very dark brown" },
  { valor: "marrom", imagem: "cor_marrom.jpg", pt: "Marrom", en: "Brown" },
  { valor: "vermelha", imagem: "cor_vermelha.jpg", pt: "Vermelha", en: "Red" },
  { valor: "amarela", imagem: "cor_amarela.jpg", pt: "Amarelada", en: "Yellowish" },
  { valor: "cinza", imagem: "cor_cinza.jpg", pt: "Cinza ou com manchas cinza", en: "Gray, or gray-mottled" },
  { valor: "clara", imagem: "cor_clara.jpg", pt: "Clara ou esbranquiçada", en: "Pale or whitish" },
  { valor: "nao_sei", pt: "Não sei", en: "Not sure" },
];
export const OPCOES_JEITO: (Opcao & { imagem?: string })[] = [
  { valor: "solta", imagem: "jeito_solta.jpg", pt: "Solta, escorre entre os dedos", en: "Loose — runs through your fingers" },
  { valor: "fofa", imagem: "jeito_fofa.jpg", pt: "Fofa, em pequenos grumos", en: "Crumbly, in small lumps" },
  { valor: "gruda", imagem: "jeito_gruda.jpg", pt: "Gruda e dá para moldar quando molhada", en: "Sticky — you can mold it when wet" },
  { valor: "torroes", imagem: "jeito_torroes.jpg", pt: "Torrões duros que não se desfazem", en: "Hard clods that won't break up" },
  { valor: "racha", imagem: "jeito_racha.jpg", pt: "Racha quando seca", en: "Cracks open when dry" },
  { valor: "pedras", imagem: "jeito_pedras.jpg", pt: "Pedregosa, com muito cascalho", en: "Stony, with lots of gravel" },
  { valor: "nao_sei", pt: "Não sei", en: "Not sure" },
];

export const CAMPOS_LAUDO: { id: keyof NonNullable<Respostas["q12_laudo"]>; pt: string; en: string; unidade: string }[] = [
  { id: "ph_agua", pt: "pH em água", en: "pH (water)", unidade: "" },
  { id: "argila_pct", pt: "Argila", en: "Clay", unidade: "%" },
  { id: "materia_organica_g_dm3", pt: "Matéria orgânica", en: "Organic matter", unidade: "g/dm³" },
  { id: "fosforo_mg_dm3", pt: "Fósforo (P)", en: "Phosphorus (P)", unidade: "mg/dm³" },
  { id: "potassio_mg_dm3", pt: "Potássio (K)", en: "Potassium (K)", unidade: "mg/dm³" },
  { id: "ctc_cmolc_dm3", pt: "CTC", en: "CEC", unidade: "cmolc/dm³" },
  { id: "saturacao_bases_pct", pt: "Saturação por bases (V%)", en: "Base saturation (V%)", unidade: "%" },
];

/** Correções do solo (pergunta 17). A ordem muda com o local (gesso primeiro em clima seco). */
const CALCARIO: Opcao = { valor: "calcario", pt: "Calcário", en: "Lime", dica: { pt: "para terra ácida", en: "for acid soil" }, ico: "flask" };
const GESSO: Opcao = { valor: "gesso", pt: "Gesso agrícola", en: "Gypsum", dica: { pt: "para terra com sal", en: "for salty soil" }, ico: "flask" };
const OUTRA: Opcao = { valor: "outra", pt: "Outra correção", en: "Something else", ico: "sprout" };
const NUNCA: Opcao = { valor: "nao", pt: "Nunca fiz", en: "Never", ico: "no" };
const NAOSEI: Opcao = { valor: "nao_sei", pt: "Não sei", en: "Not sure", ico: "idk" };

export const comecaCom = (zona: string | null | undefined, letra: string) => !!zona && zona.toUpperCase().startsWith(letra);

/** ordem_por_local.gesso_primeiro_se: zona B, ou Csa/Csb. */
export const gessoPrimeiro = (zona: string | null | undefined) => comecaCom(zona, "B") || zona === "Csa" || zona === "Csb";

export function opcoesCorrecao(zona: string | null | undefined): Opcao[] {
  return [...(gessoPrimeiro(zona) ? [GESSO, CALCARIO] : [CALCARIO, GESSO]), OUTRA, NUNCA, NAOSEI];
}

export const OPCOES_PRIORIDADES: { valor: NonNullable<Respostas["q25_prioridades"]>[number]; pt: string; en: string; tag: Par }[] = [
  { valor: "agua", pt: "Economizar água", en: "Save water", tag: { pt: "Água", en: "Water" } },
  { valor: "terra", pt: "Melhorar a terra", en: "Build up the soil", tag: { pt: "Solo", en: "Soil" } },
  { valor: "erosao", pt: "Evitar erosão", en: "Stop erosion", tag: { pt: "Proteção", en: "Protection" } },
  { valor: "renda", pt: "Ganhar uma renda extra", en: "Earn extra income", tag: { pt: "Dinheiro", en: "Money" } },
  { valor: "animais", pt: "Produzir comida para os animais", en: "Grow feed for my animals", tag: { pt: "Animais", en: "Animals" } },
  { valor: "pragas", pt: "Ter menos pragas", en: "Have fewer pests", tag: { pt: "Lavoura", en: "Crops" } },
];

export const MOTIVOS: { valor: "mercado" | "costume" | "deu_errado" | "outro"; pt: string; en: string }[] = [
  { valor: "mercado", pt: "Mercado", en: "Market" },
  { valor: "costume", pt: "Costume", en: "Habit" },
  { valor: "deu_errado", pt: "Já deu errado", en: "It failed before" },
  { valor: "outro", pt: "Outro", en: "Other" },
];

/* ---------- Regras adaptativas ---------- */

/** exemplo_por_zona da pergunta 8: grupo Köppen (1ª letra; Aw/As e Af/Am têm exemplo próprio). */
export const EXEMPLOS_CULTURAS: Record<string, Par> = {
  Af_Am: { pt: "planto mandioca e milho juntos e tenho um pedaço de capim para o gado", en: "I grow cassava and corn together and have a patch of grass for the cattle" },
  Aw_As: { pt: "planto milho e feijão juntos na estação chuvosa e, depois da colheita, o campo fica parado na seca", en: "I plant corn and beans together in the rainy season and leave the field idle in the dry season" },
  B: { pt: "planto sorgo e feijão-caupi quando chegam as chuvas; o resto do ano o campo fica parado", en: "I plant sorghum and cowpea when the rains come; the rest of the year the field is idle" },
  C: { pt: "planto soja no verão e trigo no inverno", en: "I grow soybean in summer and wheat in winter" },
  D: { pt: "planto trigo na primavera e colho no fim do verão; no inverno o campo fica parado", en: "I sow wheat in spring and harvest at the end of summer; in winter the field is idle" },
  padrao: { pt: "planto milho na estação das chuvas e, depois da colheita, deixo o campo parado", en: "I plant corn in the rainy season and leave the field idle after harvest" },
};

export function exemploCulturas(zona: string | null | undefined): Par {
  const z = (zona ?? "").trim();
  if (/^A[fm]/i.test(z)) return EXEMPLOS_CULTURAS.Af_Am;
  if (/^A[ws]/i.test(z)) return EXEMPLOS_CULTURAS.Aw_As;
  if (/^A/i.test(z)) return EXEMPLOS_CULTURAS.Aw_As;
  const g = z.charAt(0).toUpperCase();
  if (g === "B" || g === "C" || g === "D") return EXEMPLOS_CULTURAS[g];
  return EXEMPLOS_CULTURAS.padrao;
}

/** Ajuda da pergunta 9 em clima de neve (zona D). */
export const AJUDA_NEVE: Par = {
  pt: "Se nesses meses o campo fica coberto de neve ou de palhada, conte como coberto (responda \"não\").",
  en: "If the field is under snow or crop residue in these months, count it as covered (answer \"no\").",
};

export interface EventoDef {
  valor: EventoPerda;
  pt: string;
  en: string;
  dica?: Par;
  ico: string;
}

const EVENTOS: EventoDef[] = [
  { valor: "geada", pt: "Geada", en: "Frost", ico: "snow" },
  { valor: "chuva_forte", pt: "Chuva forte ou temporal", en: "Heavy rain or storms", ico: "rain" },
  { valor: "alagamento", pt: "Alagamento ou encharcamento", en: "Flooding or waterlogging", ico: "flood" },
  { valor: "granizo", pt: "Chuva de granizo", en: "Hail", ico: "hail" },
  { valor: "calor", pt: "Calor intenso", en: "Extreme heat", ico: "sun" },
  { valor: "seca", pt: "Seca ou falta de chuva", en: "Drought", ico: "dry" },
  { valor: "salinidade", pt: "Salinidade do solo", en: "Salty soil", dica: { pt: "manchas brancas, planta queimando", en: "white crust, scorched plants" }, ico: "salt" },
];
export const TODOS_EVENTOS = EVENTOS.map((e) => e.valor);

/** Geada: aparece se o histórico do ponto tem frio de geada; sem esse dado, some só em clima tropical (zona A). */
export function geadaAparece(info: InfoLocal | null, zona: string | null | undefined): boolean {
  if (info && info.geada_no_historico !== null && info.geada_no_historico !== undefined) return info.geada_no_historico;
  return !comecaCom(zona, "A");
}

/** Salinidade: clima seco (zona B), ou irrigação em clima mediterrâneo (Csa/Csb). */
export function salinidadeAparece(zona: string | null | undefined, irrigacao: Respostas["q6_irrigacao"]): boolean {
  if (comecaCom(zona, "B")) return true;
  return (zona === "Csa" || zona === "Csb") && (irrigacao === "sim" || irrigacao === "parte");
}

export function eventosVisiveis(info: InfoLocal | null, zona: string | null | undefined, irrigacao: Respostas["q6_irrigacao"]): EventoDef[] {
  return EVENTOS.filter((e) => {
    if (e.valor === "geada") return geadaAparece(info, zona);
    if (e.valor === "salinidade") return salinidadeAparece(zona, irrigacao);
    return true;
  });
}

export const hemisferioDe = (local: Local | null | undefined, info: InfoLocal | null): "N" | "S" =>
  info?.hemisferio ?? (local && local.lat >= 0 ? "N" : "S");

/** Descrição curta da zona Köppen (grupo pela 1ª letra). */
export function descricaoZona(zona: string | null | undefined, i: Idioma): string {
  const g = (zona ?? "").charAt(0).toUpperCase();
  const d: Record<string, Par> = {
    A: { pt: "Clima tropical, quente o ano todo.", en: "Tropical climate, warm all year." },
    B: { pt: "Clima seco, com pouca chuva.", en: "Dry climate, with little rain." },
    C: { pt: "Clima temperado, com estações bem marcadas.", en: "Mild climate, with clear seasons." },
    D: { pt: "Clima de inverno frio, às vezes com neve.", en: "Cold-winter climate, sometimes with snow." },
    E: { pt: "Clima muito frio.", en: "Very cold climate." },
  };
  const base = d[g];
  if (!base) return "";
  const aw = /^A[ws]/i.test(zona ?? "") ? { pt: "Clima tropical com estação seca.", en: "Tropical climate with a dry season." } : base;
  return aw[i];
}

/** Rótulo de uma opção já gravada (para o resumo). */
export function rotuloDe(lista: { valor: string; pt: string; en: string }[], valor: string | null | undefined, i: Idioma): string | null {
  if (!valor) return null;
  const o = lista.find((x) => x.valor === valor);
  return o ? o[i] : null;
}
