// Próximos passos da fazenda em PT/EN. A API grava o texto em português; o id escolhe a tradução aqui.
import type { Idioma } from "../i18n";

const PASSOS: Record<string, { titulo: Record<Idioma, string>; texto: Record<Idioma, string> }> = {
  valores_laudo: {
    titulo: { pt: "Digite os valores do seu laudo", en: "Enter your soil test values" },
    texto: { pt: "Com pelo menos dois valores (como pH e argila), a análise usa o seu laudo no lugar dos mapas globais.", en: "With at least two values (like pH and clay), the analysis uses your soil test instead of the global maps." },
  },
  teste_tato: {
    titulo: { pt: "Teste do tato (2 minutos)", en: "Feel test (2 minutes)" },
    texto: { pt: "Molhe um punhado de terra e aperte. Se esfarela, é arenosa; se molda e gruda, é argilosa.", en: "Wet a handful of soil and squeeze it. If it crumbles, it's sandy; if it holds its shape and sticks, it's clay." },
  },
  analise_solo: {
    titulo: { pt: "Análise de solo", en: "Soil test" },
    texto: { pt: "Uma análise em laboratório deixa a comparação de estratégias bem mais confiável.", en: "A lab soil test makes the strategy comparison much more reliable." },
  },
  buraco_20cm: {
    titulo: { pt: "Olhe a vida no solo", en: "Check the life in your soil" },
    texto: { pt: "Cave um buraco de um palmo depois de uma chuva e conte as minhocas.", en: "Dig a hand-deep hole after a rain and count the earthworms." },
  },
  observar_chuva: {
    titulo: { pt: "Observe depois da próxima chuva", en: "Watch after the next rain" },
    texto: { pt: "Veja se a água fica parada no campo por mais de um dia.", en: "See if water stays standing in the field for more than a day." },
  },
  punhado: {
    titulo: { pt: "Pegue um punhado de terra", en: "Grab a handful of soil" },
    texto: { pt: "Compare a cor e o jeito na mão com as figuras do questionário.", en: "Compare its color and feel with the pictures in the questionnaire." },
  },
};

/** Título e texto no idioma; passo desconhecido fica como a API mandou. */
export function passoNoIdioma(p: { id: string; titulo: string; texto: string }, idioma: Idioma) {
  const tr = PASSOS[p.id];
  return tr ? { titulo: tr.titulo[idioma], texto: tr.texto[idioma] } : { titulo: p.titulo, texto: p.texto };
}
