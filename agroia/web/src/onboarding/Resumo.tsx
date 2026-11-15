// Resumo no fim do questionário: perfil (calculado pela API), calendário, retrato do solo e próximos passos.
import { passoNoIdioma } from "./passos";
import type { CulturaBase, Fazenda, Indicador } from "../api/tipos";
import { Pino } from "../components/icones";
import { cx, Selo, Titulo } from "../components/ui";
import { useIdioma, type Idioma } from "../i18n";
import { Calendario } from "./Calendario";
import { OPCOES_ANIMAIS, OPCOES_AREA, OPCOES_IRRIGACAO, OPCOES_TECNICO, OPCOES_TERRENO, rotuloDe, unidadePadrao } from "./dados";

const PERFIS: Record<string, { nome: { pt: string; en: string }; texto: { pt: string; en: string } }> = {
  A: {
    nome: { pt: "Experiência", en: "Experience" },
    texto: { pt: "Vamos usar os dados globais e as suas respostas. Alguns testes simples deixam a análise mais firme.", en: "We'll use global data and your answers. A few simple tests make the analysis firmer." },
  },
  B: {
    nome: { pt: "Observador", en: "Observer" },
    texto: { pt: "Vamos combinar o que você observa com os dados globais de solo e clima.", en: "We'll combine what you observe with global soil and weather data." },
  },
  C: {
    nome: { pt: "Com laudo", en: "With lab report" },
    texto: { pt: "Os valores do seu laudo vão ter prioridade sobre os modelos. É o nível de confiança mais alto.", en: "Your lab values come first, ahead of the models. This is the highest confidence level." },
  },
};

const ROTULO_ATRIBUTO: Record<string, { pt: string; en: string }> = {
  textura: { pt: "Textura", en: "Texture" },
  drenagem: { pt: "Água parada", en: "Standing water" },
  encrostamento: { pt: "Casca", en: "Crust" },
  erosao_observada: { pt: "Erosão", en: "Erosion" },
  compactacao: { pt: "Dureza", en: "Hardness" },
  vida_no_solo: { pt: "Vida no solo", en: "Soil life" },
  declividade: { pt: "Terreno", en: "Slope" },
};

function rotuloAtributo(a: string, i: Idioma) {
  const r = ROTULO_ATRIBUTO[a];
  if (r) return r[i];
  const txt = a.replace(/_/g, " ");
  return txt.charAt(0).toUpperCase() + txt.slice(1);
}

function Secao({ n, titulo, children, className }: { n: number; titulo: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={cx("flex flex-col gap-3 rounded-[28px] bg-white p-5 shadow-cartao", className)}>
      <h2 className="m-0 text-[13px] font-bold text-folha">{n} · {titulo}</h2>
      {children}
    </section>
  );
}

export function Resumo({ fazenda, culturas }: { fazenda: Fazenda | null; culturas: CulturaBase[] }) {
  const { idioma, t } = useIdioma();
  if (!fazenda) return null;
  const r = fazenda.respostas;
  const perfil = fazenda.perfil ? PERFIS[fazenda.perfil] : null;
  const itens = r.q8_culturas ?? [];
  const nomes = Object.fromEntries(culturas.map((c) => [c.id, c.nome]));
  const solo = fazenda.retrato_solo;
  const un = unidadePadrao(r.q5_local?.pais);
  const area = OPCOES_AREA.find((o) => o.valor === r.q2_area)?.[un][idioma];
  const chips = [
    area ?? t("Área não informada", "Size not given"),
    t("Irrigação: ", "Irrigation: ") + (rotuloDe(OPCOES_IRRIGACAO, r.q6_irrigacao, idioma) ?? "—"),
    t("Técnico: ", "Agronomist: ") + (rotuloDe(OPCOES_TECNICO, r.q3_tecnico, idioma) ?? "—"),
    t("Animais: ", "Livestock: ") + (rotuloDe(OPCOES_ANIMAIS, r.q4_animais, idioma) ?? "—"),
    t("Terreno: ", "Land: ") + (rotuloDe(OPCOES_TERRENO, r.q7_terreno, idioma) ?? "—"),
  ];
  const lugar = [r.q5_local?.nome, r.q5_local?.pais, r.q5_local?.zona_climatica].filter(Boolean).join(" · ");
  const indicadores = (solo.indicadores ?? []).filter((i: Indicador) => i.texto);
  const temSolo = indicadores.length > 0 || !!solo.figuras;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Titulo>{t("Resumo da sua fazenda", "Your farm summary")}</Titulo>
        {lugar && (
          <span className="flex items-center gap-2 text-sm text-suave"><Pino size={16} className="shrink-0" /> {lugar}</span>
        )}
        <span className="text-sm text-suave">{t("Confira antes de seguir. Dá para voltar e mudar qualquer resposta.", "Check it before you go on. You can go back and change any answer.")}</span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2 lg:items-start">
        <section className="flex flex-col gap-3.5 rounded-[28px] bg-folha p-5 text-white shadow-degrau">
          <h2 className="m-0 text-[13px] font-bold opacity-90">1 · {t("Perfil da propriedade", "Farm profile")}</h2>
          {perfil && fazenda.perfil ? (
            <>
              <div className="flex items-center gap-4">
                <div aria-hidden="true" className="flex h-[72px] w-[72px] shrink-0 items-center justify-center rounded-[22px] bg-sol font-titulo text-[44px] font-extrabold text-tinta shadow-degrau-sol">
                  {fazenda.perfil}
                </div>
                <div className="flex flex-col gap-1">
                  <span className="font-titulo text-2xl leading-tight font-extrabold">{perfil.nome[idioma]}</span>
                  <span className="text-sm leading-snug opacity-90">{perfil.texto[idioma]}</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2" aria-hidden="true">
                {["A", "B", "C"].map((l) => (
                  <span key={l} className={cx("flex h-9 items-center justify-center rounded-xl text-sm font-bold", l === fazenda.perfil ? "bg-sol text-tinta" : "bg-white/15")}>{l}</span>
                ))}
              </div>
            </>
          ) : (
            <span className="text-sm opacity-90">{t("O perfil aparece depois que você terminar.", "Your profile shows up once you finish.")}</span>
          )}
          <div className="flex flex-wrap gap-2">
            {chips.map((c) => <span key={c} className="rounded-full bg-white/15 px-3 py-1.5 text-xs font-bold">{c}</span>)}
          </div>
          {fazenda.papel === "tecnico" && (
            <span className="text-xs font-bold opacity-90">{t("Preenchido por técnico · mostramos mais detalhe técnico", "Filled in by an agent · we show more technical detail")}</span>
          )}
        </section>

        <Secao n={2} titulo={t("Calendário anual de culturas", "Yearly crop calendar")}>
          {itens.length > 0 ? (
            <>
              <Calendario itens={itens} vazios={fazenda.meses_sem_cobertura} nomes={nomes} />
              {fazenda.meses_sem_cobertura.length > 0 && (
                <span className="rounded-xl bg-sol-claro px-3 py-2 text-[13px] text-sol-texto">
                  {t(`${fazenda.meses_sem_cobertura.length} meses com o campo sem nada. Vamos olhar isso com os dados.`, `${fazenda.meses_sem_cobertura.length} months with nothing on the field. We'll look into that with the data.`)}
                </span>
              )}
            </>
          ) : (
            <span className="text-sm text-suave">{t("Você não contou o que planta. Dá para voltar e contar.", "You didn't say what you grow. You can go back and add it.")}</span>
          )}
        </Secao>

        <Secao n={3} titulo={t("Retrato do solo", "Soil snapshot")}>
          <Selo tom="ceu">{t("Informado por você · vamos cruzar com SoilGrids e NASA", "Told by you · we'll cross-check with SoilGrids and NASA")}</Selo>
          {temSolo ? (
            <div className="grid grid-cols-2 gap-2.5">
              {solo.figuras && (
                <div className="col-span-2 flex flex-col gap-0.5 rounded-2xl bg-campo-claro p-3">
                  <span className="text-[11px] font-bold text-folha-escura">{t("Cor e jeito", "Color and feel")}</span>
                  <span className="text-[15px] leading-snug font-bold">{solo.figuras.leitura}</span>
                </div>
              )}
              {indicadores.map((i) => (
                <div key={i.origem + i.atributo} className="flex flex-col gap-0.5 rounded-2xl bg-campo-claro p-3">
                  <span className="text-[11px] font-bold text-folha-escura">{rotuloAtributo(i.atributo, idioma)}</span>
                  <span className="text-[15px] leading-snug font-bold">{i.texto}</span>
                </div>
              ))}
            </div>
          ) : (
            <span className="text-sm text-suave">{t("Você não sabia ou não respondeu sobre o solo. Tudo bem: usamos os mapas globais.", "You weren't sure or skipped the soil questions. That's fine: we use the global maps.")}</span>
          )}
        </Secao>

        <Secao n={4} titulo={t("Próximos passos recomendados", "Suggested next steps")}>
          {fazenda.proximos_passos.length > 0 ? (
            <ol className="m-0 flex list-none flex-col gap-2.5 p-0">
              {fazenda.proximos_passos.slice(0, 3).map((original, i) => {
                const p = { id: original.id, ...passoNoIdioma(original, idioma) };
                return (
                <li key={p.id} className="flex gap-3 rounded-2xl bg-areia p-3">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sol text-sm font-extrabold">{i + 1}</span>
                  <span className="flex flex-col gap-0.5">
                    <span className="text-base font-bold">{p.titulo}</span>
                    <span className="text-sm leading-snug text-suave">{p.texto}</span>
                  </span>
                </li>
                );
              })}
            </ol>
          ) : (
            <span className="text-sm text-suave">{t("Nada pendente por agora.", "Nothing pending for now.")}</span>
          )}
        </Secao>
      </div>

      <span className="self-center rounded-full bg-sol-claro px-3 py-1.5 text-xs font-bold text-sol-texto">{t("A AgroAI apoia. Quem decide é você.", "AgroAI helps. You decide.")}</span>
    </div>
  );
}
