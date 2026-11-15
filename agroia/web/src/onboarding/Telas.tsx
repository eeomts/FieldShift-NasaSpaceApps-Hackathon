// Telas do questionário (uma pergunta por tela). Textos, opções e regras: dados.ts (yaml).
import type { ReactNode } from "react";
import type {
  Correcao, CulturaBase, EquipamentoBase, EventoPerda, InfoLocal, ItemCalendario, Perda, Prioridade, Respostas, SNS,
} from "../api/tipos";
import { Check, IconeOpcao, Mais, Xis } from "../components/icones";
import { Cartao, cx, Selo, Texto, Titulo } from "../components/ui";
import { MESES_LONGOS, useIdioma } from "../i18n";
import { CartaoCultura, novoItem } from "./CartaoCultura";
import { Calendario, semCobertura } from "./Calendario";
import {
  AJUDA_NEVE, CAMPOS_LAUDO, comecaCom, eventosVisiveis, exemploCulturas, FOTOS, LINHAS_SINAIS, MOTIVOS, OPCOES_AREA, OPCOES_ANIMAIS,
  OPCOES_COR, OPCOES_IRRIGACAO, OPCOES_JEITO, OPCOES_POS_COLHEITA, OPCOES_PRIORIDADES, OPCOES_QUEM, OPCOES_TECNICO, OPCOES_TERRENO,
  OPCOES_TEXTURA, opcoesCorrecao, SIM_NAO_NAO_SEI, TITULOS, type Opcao, type TelaId, type Unidade,
} from "./dados";
import { TextoLivre } from "./TextoLivre";

export interface ContextoTelas {
  culturas: CulturaBase[];
  equipamentos: EquipamentoBase[];
  info: InfoLocal | null;
  infoEstado: "ocioso" | "carregando" | "ok" | "erro";
  zona: string | null;
  pais: string | null;
  hemisferio: "N" | "S";
  unidade: Unidade;
  setUnidade: (u: Unidade) => void;
}

export type Atualizar = Partial<Respostas> | ((r: Respostas) => Partial<Respostas>);

export interface TelaProps {
  r: Respostas;
  set: (p: Atualizar) => void;
  ctx: ContextoTelas;
}

/* ---------- Peças comuns ---------- */

function Pergunta({ id, ajuda, extra, children }: { id: TelaId; ajuda?: string; extra?: ReactNode; children: ReactNode }) {
  const { idioma } = useIdioma();
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <Titulo>{TITULOS[id][idioma]}</Titulo>
        {extra}
      </div>
      {ajuda && <Texto>{ajuda}</Texto>}
      {children}
    </div>
  );
}

function CartaoOpcao({
  ico, rotulo, dica, sub, on, multi, onClick, cor, children,
}: {
  ico?: string; rotulo: string; dica?: string; sub?: string; on: boolean; multi?: boolean; onClick: () => void; cor?: string; children?: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={onClick}
      className={cx(
        "flex min-h-[64px] w-full items-center gap-3.5 rounded-[22px] border-2 p-3.5 text-left transition-all",
        on ? "border-folha bg-campo-claro shadow-[0_4px_0_var(--color-folha-escura)]" : "border-borda bg-white shadow-cartao hover:border-folha/50",
      )}
    >
      <span className={cx("flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-[14px]", on ? "bg-folha text-white" : "bg-areia text-folha")}
        style={cor ? { background: cor } : undefined}>
        {ico && !cor && (ico === "idk" ? <span className="text-lg font-extrabold">?</span> : <IconeOpcao nome={ico} />)}
      </span>
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="text-base leading-snug font-bold">{rotulo}</span>
        {dica && <span className="text-[13px] text-suave">{dica}</span>}
        {sub && <span className="text-[13px] text-suave">{sub}</span>}
        {children}
      </span>
      <span className={cx("flex h-7 w-7 shrink-0 items-center justify-center border-2", multi ? "rounded-lg" : "rounded-full", on ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
        {on && <Check size={16} />}
      </span>
    </button>
  );
}

function ListaOpcoes({ opcoes, valor, onChange }: { opcoes: (Opcao & { cor?: string })[]; valor: string | null | undefined; onChange: (v: string) => void }) {
  const { idioma } = useIdioma();
  return (
    <div className={cx("grid gap-3", opcoes.length >= 5 && "lg:grid-cols-2")}>
      {opcoes.map((o) => (
        <CartaoOpcao key={o.valor} ico={o.ico} cor={o.cor} rotulo={o[idioma]} dica={o.dica?.[idioma]} sub={o.sub?.[idioma]} on={valor === o.valor} onClick={() => onChange(o.valor)} />
      ))}
    </div>
  );
}

function SimNaoNaoSei({ id, valor, onChange, ajuda }: { id: TelaId; valor: SNS | null | undefined; onChange: (v: SNS) => void; ajuda?: string }) {
  return (
    <Pergunta id={id} ajuda={ajuda}>
      <ListaOpcoes opcoes={SIM_NAO_NAO_SEI} valor={valor} onChange={(v) => onChange(v as SNS)} />
    </Pergunta>
  );
}

function Selecao({ rotulo, valor, onChange, children }: { rotulo: string; valor: string; onChange: (v: string) => void; children: ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5 text-[13px] font-bold">
      {rotulo}
      <select value={valor} onChange={(e) => onChange(e.target.value)} className="h-12 rounded-2xl border-2 border-borda bg-white px-3 text-[15px] font-bold focus:border-folha focus:outline-none">
        {children}
      </select>
    </label>
  );
}

const anosDesde = (inicio: number, n?: number) => {
  const atual = new Date().getFullYear();
  return Array.from({ length: n ?? atual - inicio + 1 }, (_, i) => atual - i);
};

/* ---------- Parte 1 ---------- */

export const TelaQuem = ({ r, set }: TelaProps) => (
  <Pergunta id="q1_quem"><ListaOpcoes opcoes={OPCOES_QUEM} valor={r.q1_quem} onChange={(v) => set({ q1_quem: v as Respostas["q1_quem"] })} /></Pergunta>
);

export function TelaArea({ r, set, ctx }: TelaProps) {
  const { t } = useIdioma();
  const un = ctx.unidade;
  const seletor = (
    <div role="group" aria-label={t("Unidade de área", "Area unit")} className="flex shrink-0 rounded-full border-2 border-borda bg-white p-0.5">
      {(["ha", "acre"] as Unidade[]).map((u) => (
        <button key={u} type="button" aria-pressed={un === u} onClick={() => ctx.setUnidade(u)}
          className={cx("h-8 min-w-[44px] rounded-full px-2.5 text-xs font-bold", un === u ? "bg-folha text-white" : "text-tinta")}>
          {u}
        </button>
      ))}
    </div>
  );
  const ajuda = un === "acre"
    ? t("Mostrando em acres. Toque em “ha” para trocar.", "Showing acres. Tap “ha” to switch.")
    : t("1 hectare é mais ou menos um campo de futebol.", "1 hectare is roughly a football pitch.");
  return (
    <Pergunta id="q2_area" ajuda={ajuda} extra={seletor}>
      <ListaOpcoes
        opcoes={OPCOES_AREA.map((o) => ({ valor: o.valor, pt: o[un].pt, en: o[un].en }))}
        valor={r.q2_area}
        onChange={(v) => set({ q2_area: v as Respostas["q2_area"] })}
      />
    </Pergunta>
  );
}

export const TelaTecnico = ({ r, set }: TelaProps) => (
  <Pergunta id="q3_tecnico"><ListaOpcoes opcoes={OPCOES_TECNICO} valor={r.q3_tecnico} onChange={(v) => set({ q3_tecnico: v as Respostas["q3_tecnico"] })} /></Pergunta>
);

export const TelaAnimais = ({ r, set }: TelaProps) => (
  <Pergunta id="q4_animais"><ListaOpcoes opcoes={OPCOES_ANIMAIS} valor={r.q4_animais} onChange={(v) => set({ q4_animais: v as Respostas["q4_animais"] })} /></Pergunta>
);

/* ---------- Parte 2 ---------- */

export const TelaIrrigacao = ({ r, set }: TelaProps) => (
  <Pergunta id="q6_irrigacao"><ListaOpcoes opcoes={OPCOES_IRRIGACAO} valor={r.q6_irrigacao} onChange={(v) => set({ q6_irrigacao: v as Respostas["q6_irrigacao"] })} /></Pergunta>
);

function Encosta({ inclinacao }: { inclinacao: number }) {
  const y = 44 - inclinacao;
  return (
    <svg viewBox="0 0 120 64" className="h-16 w-[120px] shrink-0 rounded-2xl bg-campo-claro" aria-hidden="true">
      <path d={`M0 46 L120 ${y + 2} L120 64 L0 64 Z`} fill="#C9A878" />
      <path d={`M0 46 L120 ${y + 2}`} stroke="#1F7A4D" strokeWidth="3" fill="none" />
      {[20, 58, 96].map((x) => {
        const base = 46 - ((46 - (y + 2)) * x) / 120;
        return <path key={x} d={`M${x} ${base} v-9 M${x} ${base - 6} l-4 -4 M${x} ${base - 8} l4 -4`} stroke="#1F7A4D" strokeWidth="2" fill="none" strokeLinecap="round" />;
      })}
    </svg>
  );
}

export function TelaTerreno({ r, set }: TelaProps) {
  const { idioma, t } = useIdioma();
  return (
    <Pergunta id="q7_terreno" ajuda={t("Escolha o desenho mais parecido com o seu campo.", "Pick the drawing that looks most like your field.")}>
      <div className="flex flex-col gap-3">
        {OPCOES_TERRENO.map((o) => {
          const on = r.q7_terreno === o.valor;
          return (
            <button key={o.valor} type="button" aria-pressed={on} onClick={() => set({ q7_terreno: o.valor as Respostas["q7_terreno"] })}
              className={cx("flex items-center gap-4 rounded-[22px] border-2 p-3 text-left transition-all",
                on ? "border-folha bg-campo-claro shadow-[0_4px_0_var(--color-folha-escura)]" : "border-borda bg-white shadow-cartao hover:border-folha/50")}>
              <Encosta inclinacao={o.inclinacao} />
              <span className="flex flex-col">
                <span className="text-base font-bold">{o[idioma]}</span>
                <span className="text-[13px] text-suave">{o.sub?.[idioma]}</span>
              </span>
            </button>
          );
        })}
      </div>
    </Pergunta>
  );
}

/* ---------- Parte 3: pergunta 8 e seguintes ---------- */

export function TelaCulturas({ r, set, ctx }: TelaProps) {
  const { idioma, t } = useIdioma();
  const itens = r.q8_culturas ?? [];
  const nomes = Object.fromEntries(ctx.culturas.map((c) => [c.id, c.nome]));
  const exemplo = exemploCulturas(ctx.zona)[idioma];
  const atualizar = (idx: number, novo: ItemCalendario) => set((a) => ({ q8_culturas: (a.q8_culturas ?? []).map((x, i) => (i === idx ? novo : x)) }));
  return (
    <Pergunta id="q8_culturas">
      <TextoLivre
        campo="culturas"
        rotulo={t("Conte do seu jeito", "In your own words")}
        exemplo={exemplo}
        textoBotao={t("Separar com a AgroIA", "Sort it with AgroIA")}
        carregandoTexto={t("A AgroIA está separando as culturas…", "AgroIA is sorting your crops…")}
        hemisferio={ctx.hemisferio}
        texto={r.q8_texto ?? ""}
        onTexto={(x) => set({ q8_texto: x })}
        onResultado={(res) =>
          set({
            q8_culturas: res.itens.map((i) => ({
              cultura_id: i.id, texto_original: i.texto_original, inicio_mes: i.inicio_mes ?? null,
              fim_mes: i.fim_mes ?? null, perene: !!i.perene, consorcio_com: i.consorcio_com ?? [], ocupa: null,
            })),
          })
        }
      />
      <div className="grid gap-4 lg:grid-cols-2 lg:items-start">
        {itens.map((it, idx) => (
          <CartaoCultura key={idx} item={it} culturas={ctx.culturas} onChange={(n) => atualizar(idx, n)}
            onRemover={() => set((a) => ({ q8_culturas: (a.q8_culturas ?? []).filter((_, i) => i !== idx) }))} />
        ))}
      </div>
      <AdicionarDaLista
        rotulo={t("Adicionar cultura", "Add a crop")}
        opcoes={ctx.culturas.map((c) => ({ id: c.id, nome: c.nome }))}
        onAdicionar={(id) => {
          const c = ctx.culturas.find((x) => x.id === id);
          if (c) set((a) => ({ q8_culturas: [...(a.q8_culturas ?? []), novoItem(c)] }));
        }}
      />
      {itens.length > 0 && (
        <Cartao>
          <span className="text-[13px] font-bold">{t("Seu ano no campo", "Your year in the field")}</span>
          <Calendario itens={itens} nomes={nomes} />
        </Cartao>
      )}
    </Pergunta>
  );
}

export function AdicionarDaLista({ rotulo, opcoes, onAdicionar }: { rotulo: string; opcoes: { id: string; nome: string }[]; onAdicionar: (id: string) => void }) {
  const { idioma } = useIdioma();
  return (
    <label className="flex items-center gap-2 rounded-2xl border-2 border-dashed border-folha/60 bg-white/60 px-3 py-2 text-sm font-bold text-folha">
      <Mais size={18} />
      <span className="sr-only">{rotulo}</span>
      <select value="" onChange={(e) => e.target.value && onAdicionar(e.target.value)} className="h-10 min-w-0 flex-1 bg-transparent font-bold focus:outline-none">
        <option value="">{rotulo}</option>
        {[...opcoes].sort((a, b) => a.nome.localeCompare(b.nome, idioma)).map((o) => (
          <option key={o.id} value={o.id}>{o.nome}</option>
        ))}
      </select>
    </label>
  );
}

export function TelaMesesVazios({ r, set, ctx }: TelaProps) {
  const { idioma, t } = useIdioma();
  const itens = r.q8_culturas ?? [];
  const vazios = semCobertura(itens);
  const nomes = Object.fromEntries(ctx.culturas.map((c) => [c.id, c.nome]));
  const neve = comecaCom(ctx.zona, "D");
  return (
    <Pergunta id="q9_meses_vazios" ajuda={neve ? AJUDA_NEVE[idioma] : undefined}>
      <div className="flex flex-col gap-2">
        <Texto>{t("Pelo que você contou, nenhuma cultura ocupa o campo em:", "From what you told us, no crop is on the field in:")}</Texto>
        <div className="flex flex-wrap gap-2">
          {vazios.map((m) => (
            <span key={m} className="rounded-full bg-areia px-3 py-1.5 text-[13px] font-bold text-terra-texto">{MESES_LONGOS[idioma][m - 1]}</span>
          ))}
        </div>
      </div>
      <Cartao>
        <Calendario itens={itens} nomes={nomes} />
      </Cartao>
      <ListaOpcoes opcoes={SIM_NAO_NAO_SEI} valor={r.q9_meses_vazios} onChange={(v) => set({ q9_meses_vazios: v as SNS })} />
    </Pergunta>
  );
}

export const TelaPosColheita = ({ r, set }: TelaProps) => (
  <Pergunta id="q10_pos_colheita"><ListaOpcoes opcoes={OPCOES_POS_COLHEITA} valor={r.q10_pos_colheita} onChange={(v) => set({ q10_pos_colheita: v as Respostas["q10_pos_colheita"] })} /></Pergunta>
);

export const TelaPalha = ({ r, set }: TelaProps) => <SimNaoNaoSei id="q11_palha" valor={r.q11_palha} onChange={(v) => set({ q11_palha: v })} />;

/* ---------- Parte 4 ---------- */

export function TelaAnalise({ r, set }: TelaProps) {
  const { idioma, t } = useIdioma();
  const laudo = r.q12_laudo ?? {};
  return (
    <Pergunta id="q12_analise">
      <ListaOpcoes opcoes={SIM_NAO_NAO_SEI} valor={r.q12_analise}
        onChange={(v) => set({ q12_analise: v as SNS, ...(v !== "sim" && { q12_tem_resultado: null, q12_ano: null, q12_laudo: null }) })} />
      {r.q12_analise === "sim" && (
        <Cartao className="gap-4 bg-sol-claro">
          <span className="text-[15px] font-bold">{t("Sobre a sua análise", "About your soil test")}</span>
          <fieldset className="m-0 flex flex-col gap-2 border-0 p-0">
            <legend className="mb-2 p-0 text-[15px] font-bold">{t("Ainda tem o resultado?", "Do you still have the results?")}</legend>
            <div className="grid grid-cols-3 gap-2">
              {SIM_NAO_NAO_SEI.map((o) => (
                <button key={o.valor} type="button" aria-pressed={r.q12_tem_resultado === o.valor}
                  onClick={() => set({ q12_tem_resultado: o.valor as SNS, ...(o.valor !== "sim" && { q12_laudo: null }) })}
                  className={cx("min-h-12 rounded-2xl border-2 px-2 text-sm font-bold", r.q12_tem_resultado === o.valor ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
                  {o[idioma]}
                </button>
              ))}
            </div>
          </fieldset>
          {r.q12_tem_resultado === "sim" && (
            <div className="flex flex-col gap-2">
              <span className="text-[15px] font-bold">{t("Valores do laudo (preencha os que tiver)", "Lab report values (fill in the ones you have)")}</span>
              <span className="text-[13px] text-suave">
                {t("Com pelo menos dois valores, a análise usa o seu laudo no lugar dos mapas globais. Se a matéria orgânica vier em %, multiplique por 10.",
                  "With at least two values, the analysis uses your lab report instead of the global maps. If organic matter is in %, multiply by 10.")}
              </span>
              <div className="grid grid-cols-2 gap-2.5">
                {CAMPOS_LAUDO.map((c) => (
                  <label key={c.id} className="flex flex-col gap-1 text-xs font-bold">
                    {c[idioma]}{c.unidade && <span className="font-normal text-suave"> ({c.unidade})</span>}
                    <input type="number" inputMode="decimal" step="any" min={0} value={laudo[c.id] ?? ""}
                      onChange={(e) => set({ q12_laudo: { ...laudo, [c.id]: e.target.value === "" ? null : Number(e.target.value) } })}
                      className="h-12 rounded-xl border-2 border-borda bg-white px-3 text-[15px] font-bold focus:border-folha focus:outline-none" />
                  </label>
                ))}
              </div>
            </div>
          )}
          <Selecao rotulo={t("De que ano é?", "What year was it?")} valor={r.q12_ano?.toString() ?? ""} onChange={(v) => set({ q12_ano: v ? Number(v) : null })}>
            <option value="">{t("Não lembro", "I don't remember")}</option>
            {anosDesde(0, 20).map((a) => <option key={a} value={a}>{a}</option>)}
          </Selecao>
        </Cartao>
      )}
    </Pergunta>
  );
}

export const TelaTextura = ({ r, set }: TelaProps) => {
  const { t } = useIdioma();
  return (
    <Pergunta id="q13_textura" ajuda={t("Molhe um pouco de terra e aperte entre os dedos.", "Wet a little soil and squeeze it between your fingers.")}>
      <ListaOpcoes opcoes={OPCOES_TEXTURA} valor={r.q13_textura} onChange={(v) => set({ q13_textura: v as Respostas["q13_textura"] })} />
    </Pergunta>
  );
};

/** Perguntas 14 a 18: cinco sinais do solo numa grade Sim / Não / Não sei. */
export function TelaSinais({ r, set }: TelaProps) {
  const { idioma, t } = useIdioma();
  return (
    <Pergunta id="q14_sinais" ajuda={t("Responda cada linha com Sim, Não ou Não sei.", "Answer each line with Yes, No or Not sure.")}>
      <div className="flex flex-col gap-3">
        {LINHAS_SINAIS.map((l) => (
          <div key={l.id} className={cx("flex flex-col gap-2.5 rounded-[22px] border-2 p-3.5", l.bom ? "border-campo bg-campo-claro" : "border-transparent bg-white shadow-cartao")}>
            <span id={`lin-${l.id}`} className="flex items-start gap-2.5 text-[15px] leading-snug font-bold">
              <span className={cx("mt-px flex h-8 w-8 shrink-0 items-center justify-center rounded-xl", l.bom ? "bg-folha text-white" : "bg-areia text-folha")}><IconeOpcao nome={l.ico} size={18} /></span>
              {l[idioma]}
            </span>
            <div role="group" aria-labelledby={`lin-${l.id}`} className="grid grid-cols-3 gap-2">
              {SIM_NAO_NAO_SEI.map((o) => {
                const on = r[l.id] === o.valor;
                return (
                  <button key={o.valor} type="button" aria-pressed={on} onClick={() => set({ [l.id]: o.valor as SNS })}
                    className={cx("min-h-11 rounded-[14px] border-2 px-1 text-sm font-bold", on ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
                    {o[idioma]}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
        <button type="button" onClick={() => set(Object.fromEntries(LINHAS_SINAIS.map((l) => [l.id, "nao_sei"])) as Partial<Respostas>)}
          className="min-h-12 self-start rounded-2xl border-2 border-folha px-4 text-[15px] font-bold text-folha">
          {t("Não sei responder nenhuma", "I'm not sure about any of these")}
        </button>
      </div>
    </Pergunta>
  );
}

function GrupoFotos({ titulo, opcoes, valor, onChange }: {
  titulo: string; opcoes: (Opcao & { imagem?: string })[]; valor: string | null | undefined; onChange: (v: string) => void;
}) {
  const { idioma } = useIdioma();
  return (
    <fieldset className="m-0 flex flex-col gap-3 rounded-[22px] border-0 bg-white p-4 shadow-cartao">
      <legend className="float-left mb-3 w-full p-0 text-[15px] font-bold">{titulo}</legend>
      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
        {opcoes.map((o) => {
          const on = valor === o.valor;
          return (
            <button key={o.valor} type="button" aria-pressed={on} onClick={() => onChange(o.valor)}
              className={cx("flex min-w-0 flex-col overflow-hidden rounded-2xl border-2 text-left transition-colors", on ? "border-folha bg-campo-claro" : "border-borda bg-white hover:border-folha/50")}>
              {o.imagem ? (
                <img src={FOTOS + o.imagem} alt="" loading="lazy" className="aspect-[4/3] w-full object-cover" />
              ) : (
                <span className="flex aspect-[4/3] w-full items-center justify-center bg-areia text-2xl font-extrabold text-folha">?</span>
              )}
              <span className="flex items-start justify-between gap-1.5 p-2.5 text-[13px] leading-snug font-bold">
                {o[idioma]}
                {on && <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-folha text-white"><Check size={13} /></span>}
              </span>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}

export function TelaSolo({ r, set }: TelaProps) {
  const { t } = useIdioma();
  return (
    <Pergunta id="q19_solo">
      <GrupoFotos titulo={t("Cor:", "Color:")} opcoes={OPCOES_COR} valor={r.q19_cor} onChange={(v) => set({ q19_cor: v as Respostas["q19_cor"] })} />
      <GrupoFotos titulo={t("Aparência ao toque:", "How it feels in your hand:")} opcoes={OPCOES_JEITO} valor={r.q19_jeito} onChange={(v) => set({ q19_jeito: v as Respostas["q19_jeito"] })} />
      <span className="text-xs text-suave">
        {t("Fotos: Wikimedia Commons, vários autores (CC BY, CC BY-SA e domínio público). As fotos de cor foram recortadas.",
          "Photos: Wikimedia Commons, various authors (CC BY, CC BY-SA and public domain). The color photos were cropped.")}
      </span>
    </Pergunta>
  );
}

export const TelaPartesPiores = ({ r, set }: TelaProps) => <SimNaoNaoSei id="q20_partes_piores" valor={r.q20_partes_piores} onChange={(v) => set({ q20_partes_piores: v })} />;

/** Pergunta 17: múltipla; "Nunca fiz" e "Não sei" são exclusivas; gesso vem primeiro em clima seco. */
export function TelaCorrecao({ r, set, ctx }: TelaProps) {
  const { idioma, t } = useIdioma();
  const sel = r.q21_correcao ?? [];
  const alternar = (v: Correcao) => {
    let novo: Correcao[];
    if (v === "nao" || v === "nao_sei") novo = sel.includes(v) ? [] : [v];
    else novo = sel.includes(v) ? sel.filter((x) => x !== v) : [...sel.filter((x) => x !== "nao" && x !== "nao_sei"), v];
    set({ q21_correcao: novo, ...(!novo.includes("outra") && { q21_correcao_outra: null }) });
  };
  return (
    <Pergunta id="q21_correcao" ajuda={t("Pode marcar mais de uma.", "You can pick more than one.")}>
      <div className="grid gap-3">
        {opcoesCorrecao(ctx.zona).map((o) => (
          <CartaoOpcao key={o.valor} multi ico={o.ico} rotulo={o[idioma]} dica={o.dica?.[idioma]} on={sel.includes(o.valor as Correcao)} onClick={() => alternar(o.valor as Correcao)} />
        ))}
      </div>
      {sel.includes("outra") && (
        <label className="flex flex-col gap-1.5 text-[13px] font-bold">
          {t("Qual?", "What was it?")}
          <input maxLength={200} value={r.q21_correcao_outra ?? ""} onChange={(e) => set({ q21_correcao_outra: e.target.value || null })}
            placeholder={t("Qual?", "What was it?")}
            className="h-12 rounded-2xl border-2 border-borda bg-white px-4 text-[15px] font-normal focus:border-folha focus:outline-none" />
        </label>
      )}
    </Pergunta>
  );
}

export const TelaAdubo = ({ r, set }: TelaProps) => <SimNaoNaoSei id="q22_adubo" valor={r.q22_adubo} onChange={(v) => set({ q22_adubo: v })} />;

/* ---------- Parte 5 ---------- */

export const TelaChuvaMudou = ({ r, set }: TelaProps) => <SimNaoNaoSei id="q23_chuva_mudou" valor={r.q23_chuva_mudou} onChange={(v) => set({ q23_chuva_mudou: v })} />;

type Marcacao = Partial<Record<EventoPerda, number | null>> | "nunca" | "nao_sei" | null;

/**
 * Como a tela vira os campos (yaml, "grava"): marcado = sim + ano; não marcado (com outros marcados) = nao;
 * "nunca" = todos nao; "não sei" = todos nao_sei; evento escondido pela regra = vazio (null).
 */
export function gravarPerdas(visiveis: EventoPerda[], todos: EventoPerda[], marcacao: Marcacao): Partial<Record<EventoPerda, Perda>> {
  const out: Partial<Record<EventoPerda, Perda>> = {};
  for (const e of todos) {
    if (!visiveis.includes(e) || marcacao === null) out[e] = { resposta: null, ano: null };
    else if (marcacao === "nunca") out[e] = { resposta: "nao", ano: null };
    else if (marcacao === "nao_sei") out[e] = { resposta: "nao_sei", ano: null };
    else if (e in marcacao) out[e] = { resposta: "sim", ano: marcacao[e] ?? null };
    else out[e] = { resposta: "nao", ano: null };
  }
  return out;
}

export function TelaPerdas({ r, set, ctx }: TelaProps) {
  const { idioma, t } = useIdioma();
  const eventos = eventosVisiveis(ctx.info, ctx.zona, r.q6_irrigacao);
  const vis = eventos.map((e) => e.valor);
  const todos: EventoPerda[] = ["geada", "chuva_forte", "calor", "seca", "alagamento", "granizo", "salinidade"];
  const perdas = r.q24_perdas ?? {};
  const marcados: Partial<Record<EventoPerda, number | null>> = {};
  for (const e of vis) if (perdas[e]?.resposta === "sim") marcados[e] = perdas[e]?.ano ?? null;
  const nenhumMarcado = Object.keys(marcados).length === 0;
  const todosSao = (v: SNS) => vis.length > 0 && vis.every((e) => perdas[e]?.resposta === v);
  const nunca = nenhumMarcado && todosSao("nao");
  const naoSei = nenhumMarcado && todosSao("nao_sei");
  const grava = (m: Marcacao) => set({ q24_perdas: gravarPerdas(vis, todos, m) });

  function alternar(e: EventoPerda) {
    const novo = { ...marcados };
    if (e in novo) delete novo[e];
    else novo[e] = null;
    grava(Object.keys(novo).length ? novo : null);
  }

  return (
    <Pergunta id="q24_perdas" ajuda={t("Pode marcar mais de um. Em cada um, diga mais ou menos o ano.", "You can pick more than one. For each, give the rough year.")}>
      <div className="grid gap-3">
        {eventos.map((e) => {
          const on = e.valor in marcados;
          return (
            <div key={e.valor} className="flex flex-col gap-2">
              <CartaoOpcao multi ico={e.ico} rotulo={e[idioma]} dica={e.dica?.[idioma]} on={on} onClick={() => alternar(e.valor)} />
              {on && (
                <div className="ml-3 rounded-2xl bg-sol-claro p-3">
                  <Selecao rotulo={t("Lembra mais ou menos em que ano aconteceu?", "Roughly what year was it?")} valor={marcados[e.valor]?.toString() ?? ""}
                    onChange={(v) => grava({ ...marcados, [e.valor]: v ? Number(v) : null })}>
                    <option value="">{t("Não lembro", "I don't remember")}</option>
                    {anosDesde(1980).map((a) => <option key={a} value={a}>{a}</option>)}
                  </Selecao>
                </div>
              )}
            </div>
          );
        })}
        <CartaoOpcao multi ico="no" rotulo={t("Nunca perdi uma safra por esses motivos", "I've never lost a crop to any of these")} on={nunca} onClick={() => grava(nunca ? null : "nunca")} />
        <CartaoOpcao multi ico="idk" rotulo={t("Não sei", "Not sure")} on={naoSei} onClick={() => grava(naoSei ? null : "nao_sei")} />
      </div>
    </Pergunta>
  );
}

/* ---------- Parte 6 ---------- */

export function TelaPrioridades({ r, set }: TelaProps) {
  const { idioma, t } = useIdioma();
  const sel = r.q25_prioridades ?? [];
  const alternar = (v: Prioridade) =>
    set({ q25_prioridades: sel.includes(v) ? sel.filter((x) => x !== v) : sel.length < 3 ? [...sel, v] : sel });
  return (
    <Pergunta id="q25_prioridades" ajuda={t("Escolha até 3 alternativas. Isso muda a ordem das sugestões.", "Pick up to 3. This changes the order of the tips.")}>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {OPCOES_PRIORIDADES.map((p) => {
          const pos = sel.indexOf(p.valor);
          const on = pos >= 0;
          const cheio = !on && sel.length >= 3;
          return (
            <button key={p.valor} type="button" aria-pressed={on} disabled={cheio} onClick={() => alternar(p.valor)}
              className={cx("flex min-h-[96px] flex-col justify-between gap-2 rounded-[22px] border-2 p-3.5 text-left text-base font-bold transition-all",
                on ? "border-sol-escuro bg-sol shadow-degrau-sol" : "border-borda bg-white", cheio && "opacity-50")}>
              <span className="flex items-center justify-between text-xs font-bold opacity-80">
                {p.tag[idioma]}
                {on && <span className="flex h-6 w-6 items-center justify-center rounded-full bg-tinta text-white">{pos + 1}</span>}
              </span>
              {p[idioma]}
            </button>
          );
        })}
      </div>
      <span className="text-[13px] font-bold text-suave">{t(`${sel.length} de 3 escolhidas`, `${sel.length} of 3 picked`)}</span>
    </Pergunta>
  );
}

const nomeDe = (culturas: CulturaBase[], id: string | null) => culturas.find((c) => c.id === id)?.nome;

export function TelaExcluidas({ r, set, ctx }: TelaProps) {
  const { idioma, t } = useIdioma();
  const excluidas = r.q26a_excluidas ?? [];
  const exemplo = t("não planto soja, não tenho onde vender", "I don't grow soy, I have nowhere to sell it");
  return (
    <Pergunta id="q26a_excluidas">
      <TextoLivre campo="excluidas" rotulo={t("Conte do seu jeito", "In your own words")} exemplo={exemplo}
        textoBotao={t("Separar com a AgroIA", "Sort it with AgroIA")} carregandoTexto={t("A AgroIA está lendo…", "AgroIA is reading…")}
        hemisferio={ctx.hemisferio} texto={r.q26a_texto ?? ""} onTexto={(x) => set({ q26a_texto: x })}
        onResultado={(res) => set({ q26a_excluidas: res.itens.map((i) => ({ cultura_id: i.id, texto_original: i.texto_original, motivo: i.motivo ?? null })) })} />
      <div className="grid gap-3 lg:grid-cols-2 lg:items-start">
        {excluidas.map((ex, idx) => (
          <Cartao key={idx}>
            <div className="flex items-center justify-between gap-2">
              <span className="text-[15px] font-bold">{t("Não plantaria: ", "Would not grow: ")}{nomeDe(ctx.culturas, ex.cultura_id) ?? ex.texto_original}</span>
              <button type="button" aria-label={t("Remover", "Remove")} onClick={() => set((a) => ({ q26a_excluidas: (a.q26a_excluidas ?? []).filter((_, i) => i !== idx) }))}
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[14px] bg-areia text-terra-texto"><Xis size={18} /></button>
            </div>
            {!ex.cultura_id && <Selo>{t("Fora da nossa base: guardamos como texto", "Not in our list: we keep it as text")}</Selo>}
            <span className="text-[13px] font-bold">{t("Motivo", "Reason")}</span>
            <div className="grid grid-cols-2 gap-2">
              {MOTIVOS.map((m) => (
                <button key={m.valor} type="button" aria-pressed={ex.motivo === m.valor}
                  onClick={() => set((a) => ({ q26a_excluidas: (a.q26a_excluidas ?? []).map((x, i) => (i === idx ? { ...x, motivo: m.valor } : x)) }))}
                  className={cx("min-h-11 rounded-[14px] border-2 px-2 text-sm font-bold", ex.motivo === m.valor ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
                  {m[idioma]}
                </button>
              ))}
            </div>
          </Cartao>
        ))}
      </div>
      <AdicionarDaLista rotulo={t("Adicionar cultura", "Add a crop")} opcoes={ctx.culturas.map((c) => ({ id: c.id, nome: c.nome }))}
        onAdicionar={(id) => set((a) => ({ q26a_excluidas: [...(a.q26a_excluidas ?? []), { cultura_id: id, texto_original: nomeDe(ctx.culturas, id) ?? id, motivo: null }] }))} />
    </Pergunta>
  );
}

export function TelaEquipamentos({ r, set, ctx }: TelaProps) {
  const { t } = useIdioma();
  const equips = r.q26b_equipamentos ?? [];
  const nome = (id: string | null) => ctx.equipamentos.find((e) => e.id === id)?.nome;
  const exemplo = t("tenho um trator pequeno e uma plantadeira; a colheita é na mão", "I have a small tractor and a planter; we harvest by hand");
  return (
    <Pergunta id="q26b_equipamentos">
      <TextoLivre campo="equipamentos" rotulo={t("Conte do seu jeito", "In your own words")} exemplo={exemplo}
        textoBotao={t("Separar com a AgroIA", "Sort it with AgroIA")} carregandoTexto={t("A AgroIA está separando os equipamentos…", "AgroIA is sorting your equipment…")}
        hemisferio={ctx.hemisferio} texto={r.q26b_texto ?? ""} onTexto={(x) => set({ q26b_texto: x })}
        onResultado={(res) => set({ q26b_equipamentos: res.itens.map((i) => ({ equipamento_id: i.id, texto_original: i.texto_original })) })} />
      {equips.length > 0 && (
        <Cartao className="bg-white">
          <span className="text-[13px] font-bold text-folha-escura">{t("Equipamentos que a AgroIA encontrou. Toque para remover:", "Equipment AgroIA found. Tap to remove:")}</span>
          <div className="flex flex-wrap gap-2">
            {equips.map((e, idx) => (
              <button key={idx} type="button" onClick={() => set((a) => ({ q26b_equipamentos: (a.q26b_equipamentos ?? []).filter((_, i) => i !== idx) }))}
                aria-label={t("Remover ", "Remove ") + (nome(e.equipamento_id) ?? e.texto_original)}
                className={cx("inline-flex min-h-11 items-center gap-2 rounded-full border-2 py-1.5 pr-2 pl-4 text-[15px] font-bold",
                  e.equipamento_id ? "border-folha bg-campo-claro text-folha-escura" : "border-sol-escuro bg-sol-claro text-sol-texto")}>
                {nome(e.equipamento_id) ?? `${e.texto_original} ${t("(fora da lista)", "(not in list)")}`}
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-folha text-white"><Xis size={13} /></span>
              </button>
            ))}
          </div>
        </Cartao>
      )}
      <AdicionarDaLista rotulo={t("Adicionar equipamento", "Add equipment")} opcoes={ctx.equipamentos.filter((e) => !equips.some((x) => x.equipamento_id === e.id))}
        onAdicionar={(id) => set((a) => ({ q26b_equipamentos: [...(a.q26b_equipamentos ?? []), { equipamento_id: id, texto_original: nome(id) ?? id }] }))} />
    </Pergunta>
  );
}
