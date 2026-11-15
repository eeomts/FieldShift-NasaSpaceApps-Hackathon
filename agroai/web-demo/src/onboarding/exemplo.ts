// Produtor fictício de demonstração (Corn Belt, Iowa), baseado em data/demo/pontos_demo_eua.csv (cornbelt_1).
// Usado para vir com o questionário todo preenchido na apresentação.
import type { Respostas } from "../api/tipos";
import type { Idioma } from "../i18n";

export function respostasExemplo(idioma: Idioma): Respostas {
  const en = idioma === "en";
  const t = (pt: string, ingles: string) => (en ? ingles : pt);
  return {
    q1_quem: "produtor",
    q2_area: "20_200",
    q3_tecnico: "as_vezes",
    q4_animais: "nao",
    q5_local: { lat: 42.07, lon: -93.45, nome: "Story County, Iowa", pais: "US", zona_climatica: "Dfa" },
    q6_irrigacao: "nao",
    q7_terreno: "plano",
    q8_texto: t(
      "Planto milho um ano e soja no outro, de maio a outubro. No inverno o campo fica descoberto.",
      "I grow corn one year and soybean the next, from May to October. In winter the field is left bare.",
    ),
    q8_culturas: [
      { cultura_id: "milho", texto_original: t("milho", "corn"), inicio_mes: 5, fim_mes: 10, perene: false, consorcio_com: [], ocupa: "todo" },
      { cultura_id: "soja", texto_original: t("soja", "soybean"), inicio_mes: 5, fim_mes: 10, perene: false, consorcio_com: [], ocupa: "todo" },
    ],
    q9_meses_vazios: "sim",
    q10_pos_colheita: "parado",
    q11_palha: "nao",
    q12_analise: "nao",
    q13_textura: "media",
    q14_encharca: "nao",
    q15_casca: "nao_sei",
    q16_erosao: "sim",
    q17_dura: "nao",
    q18_minhocas: "sim",
    q19_cor: "escura",
    q19_jeito: "fofa",
    q20_partes_piores: "nao",
    q21_correcao: ["calcario"],
    q22_adubo: "sim",
    q23_chuva_mudou: "sim",
    // Eventos visíveis na zona Dfa; salinidade fica escondida (vazia), como a tela grava.
    q24_perdas: {
      geada: { resposta: "nao", ano: null },
      chuva_forte: { resposta: "sim", ano: null },
      calor: { resposta: "nao", ano: null },
      seca: { resposta: "sim", ano: null },
      alagamento: { resposta: "nao", ano: null },
      granizo: { resposta: "nao", ano: null },
      salinidade: { resposta: null, ano: null },
    },
    q25_prioridades: ["terra", "erosao", "renda"],
    q26a_excluidas: [],
    q26b_equipamentos: [
      { equipamento_id: "trator", texto_original: t("trator", "tractor") },
      { equipamento_id: "plantadeira_graos", texto_original: t("plantadeira de grãos", "grain planter") },
      { equipamento_id: "colhedora", texto_original: t("colhedora", "combine harvester") },
      { equipamento_id: "pulverizador", texto_original: t("pulverizador", "sprayer") },
    ],
  };
}
