import type { ReactNode } from "react";
import type {
  CulturaBase, CulturaExcluida, EquipamentoBase, ItemCalendario, Laudo, Perda, Prioridade, Respostas, SNS,
} from "../api/tipos";
import { Check, Mais, Xis } from "../components/icones";
import { Cartao, cx, Opcoes, Selo, SIM_NAO_NAOSEI, Texto, Titulo } from "../components/ui";
import { Calendario, semCobertura } from "./Calendario";
import { Mapa } from "./Mapa";
import { SeletorMeses } from "./SeletorMeses";
import { TextoLivre } from "./TextoLivre";

export interface PassoProps {
  r: Respostas;
  set: (parcial: Partial<Respostas>) => void;
  culturas: CulturaBase[];
  equipamentos: EquipamentoBase[];
}

function Bloco({ titulo, texto, children }: { titulo: string; texto?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-4">
      <Titulo>{titulo}</Titulo>
      {texto && <Texto>{texto}</Texto>}
      {children}
    </div>
  );
}

/** No computador, perguntas curtas lado a lado. No celular, uma embaixo da outra. */
function Grade({ children }: { children: ReactNode }) {
  return <div className="grid gap-4 lg:grid-cols-2 lg:items-start">{children}</div>;
}

const nomeCultura = (culturas: CulturaBase[], id: string | null) => culturas.find((c) => c.id === id)?.nome;

/* ---------- Bloco 1: quem é você ---------- */
export function PassoQuem({ r, set }: PassoProps) {
  return (
    <Bloco titulo="Primeiro, quem é você?" texto="São 6 partes rapidinhas. Dá para parar e continuar depois.">
      <Grade>
      <Opcoes pergunta="Quem está respondendo?" colunas={1} valor={r.q1_quem} onChange={(v) => set({ q1_quem: v })}
        opcoes={[{ valor: "produtor", rotulo: "Sou o produtor" }, { valor: "tecnico", rotulo: "Sou técnico ou ajudo um produtor" }]} />
      <Opcoes pergunta="Tamanho aproximado da área" colunas={2} valor={r.q2_area} onChange={(v) => set({ q2_area: v })}
        opcoes={[
          { valor: "ate_2", rotulo: "Até 2 ha" }, { valor: "2_20", rotulo: "2 a 20 ha" },
          { valor: "20_200", rotulo: "20 a 200 ha" }, { valor: "200_1000", rotulo: "200 a 1.000 ha" },
          { valor: "mais_1000", rotulo: "Mais de 1.000 ha" },
        ]} />
      <Opcoes pergunta="Você recebe visita de técnico agrícola?" valor={r.q3_tecnico} onChange={(v) => set({ q3_tecnico: v })}
        opcoes={[{ valor: "sim", rotulo: "Sim" }, { valor: "as_vezes", rotulo: "Às vezes" }, { valor: "nao", rotulo: "Não" }]} />
      <Opcoes pergunta="Tem criação de animais?" valor={r.q4_animais} onChange={(v) => set({ q4_animais: v })}
        opcoes={[{ valor: "sim", rotulo: "Sim" }, { valor: "nao", rotulo: "Não" }]} />
      </Grade>
    </Bloco>
  );
}

/* ---------- Bloco 2: o campo ---------- */
export function PassoLocal({ r, set }: PassoProps) {
  return (
    <Bloco titulo="Onde fica o seu campo?" texto="Toque no mapa. É com esse ponto que buscamos os dados da NASA.">
      <Mapa valor={r.q5_local ?? null} onChange={(p) => set({ q5_local: { ...p, nome: r.q5_local?.nome ?? null } })} />
      {r.q5_local && (
        <label className="flex flex-col gap-1.5 text-[13px] font-bold">
          Nome do lugar (opcional)
          <input
            maxLength={200}
            value={r.q5_local.nome ?? ""}
            onChange={(e) => set({ q5_local: { ...r.q5_local!, nome: e.target.value || null } })}
            placeholder="Ex.: Sítio Boa Vista, Luís Eduardo Magalhães"
            className="h-12 rounded-2xl border-2 border-borda bg-white px-4 text-[15px] font-normal focus:border-folha focus:outline-none"
          />
        </label>
      )}
    </Bloco>
  );
}

function Terreno({ inclinacao }: { inclinacao: number }) {
  const y = 44 - inclinacao;
  return (
    <svg viewBox="0 0 80 56" className="h-12 w-full" aria-hidden="true">
      <circle cx="64" cy="14" r="7" fill="#FFC23D" />
      <path d={`M0 44 L80 ${y} L80 56 L0 56 Z`} fill="#3FA36B" />
      <path d={`M0 44 L80 ${y}`} stroke="#1F7A4D" strokeWidth="3" fill="none" />
    </svg>
  );
}

export function PassoCampo({ r, set }: PassoProps) {
  const terrenos = [
    { v: "plano" as const, rotulo: "Plano", inc: 0 },
    { v: "leve" as const, rotulo: "Levemente inclinado", inc: 12 },
    { v: "inclinado" as const, rotulo: "Bem inclinado", inc: 30 },
  ];
  return (
    <Bloco titulo="Como é o seu campo?">
      <Grade>
      <Opcoes pergunta="Tem irrigação?" valor={r.q6_irrigacao} onChange={(v) => set({ q6_irrigacao: v })}
        opcoes={[{ valor: "sim", rotulo: "Sim" }, { valor: "parte", rotulo: "Só em parte" }, { valor: "nao", rotulo: "Não" }]} />
      <fieldset className="m-0 flex flex-col gap-2.5 rounded-[22px] border-0 bg-white p-4 shadow-cartao">
        <legend className="float-left mb-2.5 w-full p-0 text-[15px] font-bold">Como é o terreno?</legend>
        <div className="grid grid-cols-3 gap-2">
          {terrenos.map((t) => {
            const on = r.q7_terreno === t.v;
            return (
              <button key={t.v} type="button" aria-pressed={on} onClick={() => set({ q7_terreno: t.v })}
                className={cx("flex flex-col items-center gap-1.5 rounded-2xl border-2 p-2 text-[13px] leading-tight font-bold",
                  on ? "border-folha bg-folha-clara" : "border-borda bg-white")}>
                <Terreno inclinacao={t.inc} />
                {t.rotulo}
              </button>
            );
          })}
        </div>
      </fieldset>
      </Grade>
    </Bloco>
  );
}

/* ---------- Bloco 3: o que você planta (pergunta 8) ---------- */
function SeletorCultura({ culturas, valor, onChange, rotulo }: {
  culturas: CulturaBase[]; valor: string | null; onChange: (id: string | null) => void; rotulo: string;
}) {
  return (
    <select
      aria-label={rotulo}
      value={valor ?? ""}
      onChange={(e) => onChange(e.target.value || null)}
      className="h-11 rounded-xl border-2 border-borda bg-white px-3 text-[15px] font-bold focus:border-folha focus:outline-none"
    >
      <option value="">Não está na lista</option>
      {[...culturas].sort((a, b) => a.nome.localeCompare(b.nome, "pt")).map((c) => (
        <option key={c.id} value={c.id}>{c.nome}</option>
      ))}
    </select>
  );
}

function CartaoCultura({ item, culturas, onChange, onRemover }: {
  item: ItemCalendario; culturas: CulturaBase[]; onChange: (i: ItemCalendario) => void; onRemover: () => void;
}) {
  const nome = nomeCultura(culturas, item.cultura_id) ?? item.texto_original;
  const consorcio = item.consorcio_com.map((id) => nomeCultura(culturas, id) ?? id).join(" e ");
  return (
    <Cartao>
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <span className="text-[15px] font-bold">Você planta {nome.toLowerCase()}?</span>
          {item.texto_original && item.texto_original.toLowerCase() !== nome.toLowerCase() && (
            <span className="text-xs text-suave">Você escreveu: "{item.texto_original}"</span>
          )}
          {!item.cultura_id && <Selo>Fora da nossa base: entra no calendário, mas não na comparação</Selo>}
        </div>
        <button type="button" onClick={onRemover} aria-label={`Remover ${nome}`}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[14px] bg-terra text-terra-texto">
          <Xis size={18} />
        </button>
      </div>
      <SeletorCultura rotulo="Trocar cultura" culturas={culturas} valor={item.cultura_id}
        onChange={(id) => {
          const c = culturas.find((x) => x.id === id);
          onChange({ ...item, cultura_id: id, perene: c ? c.perene : item.perene });
        }} />
      <label className="flex items-center gap-2 text-sm font-bold">
        <input type="checkbox" className="h-5 w-5 accent-[#1F7A4D]" checked={item.perene}
          onChange={(e) => onChange({ ...item, perene: e.target.checked })} />
        Ocupa o campo o ano todo (perene)
      </label>
      {!item.perene && (
        <>
          <span className="text-[13px] font-bold">De que mês a que mês?</span>
          <SeletorMeses inicio={item.inicio_mes} fim={item.fim_mes}
            onChange={(inicio_mes, fim_mes) => onChange({ ...item, inicio_mes, fim_mes })} />
        </>
      )}
      {item.consorcio_com.length > 0 && (
        <Opcoes pergunta={`É plantado junto com ${consorcio}?`} valor="sim"
          onChange={(v) => v === "nao" && onChange({ ...item, consorcio_com: [] })}
          opcoes={[{ valor: "sim", rotulo: "Sim" }, { valor: "nao", rotulo: "Não" }]} />
      )}
      <div className="grid grid-cols-2 gap-2">
        {(["todo", "parte"] as const).map((o) => (
          <button key={o} type="button" aria-pressed={item.ocupa === o} onClick={() => onChange({ ...item, ocupa: o })}
            className={cx("h-11 rounded-[14px] border-2 text-sm font-bold",
              item.ocupa === o ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
            {o === "todo" ? "Campo todo" : "Uma parte"}
          </button>
        ))}
      </div>
    </Cartao>
  );
}

export function PassoPlanta({ r, set, culturas }: PassoProps) {
  const itens = r.q8_culturas ?? [];
  const nomes = Object.fromEntries(culturas.map((c) => [c.id, c.nome]));
  const vazios = semCobertura(itens);
  const atualizar = (idx: number, novo: ItemCalendario) => set({ q8_culturas: itens.map((x, i) => (i === idx ? novo : x)) });
  return (
    <Bloco titulo="O que você planta, e quando?">
      <TextoLivre
        campo="culturas"
        rotulo="Conte do seu jeito"
        exemplo="Ex.: planto milho e feijão juntos na época das águas, depois mandioca, e tem um pedaço de capim pras vacas"
        texto={r.q8_texto ?? ""}
        onTexto={(t) => set({ q8_texto: t })}
        onResultado={(res) =>
          set({
            q8_culturas: res.itens.map((i) => ({
              cultura_id: i.id, texto_original: i.texto_original, inicio_mes: i.inicio_mes ?? null,
              fim_mes: i.fim_mes ?? null, perene: !!i.perene, consorcio_com: i.consorcio_com ?? [], ocupa: null,
            })),
          })
        }
      />
      <Grade>
      {itens.map((it, idx) => (
        <CartaoCultura key={idx} item={it} culturas={culturas} onChange={(n) => atualizar(idx, n)}
          onRemover={() => set({ q8_culturas: itens.filter((_, i) => i !== idx) })} />
      ))}
      </Grade>
      <AdicionarDaLista
        rotulo="Adicionar cultura pela lista"
        opcoes={culturas.map((c) => ({ id: c.id, nome: c.nome }))}
        onAdicionar={(id) => {
          const c = culturas.find((x) => x.id === id)!;
          set({ q8_culturas: [...itens, { cultura_id: c.id, texto_original: c.nome, inicio_mes: null, fim_mes: null, perene: c.perene, consorcio_com: [], ocupa: null }] });
        }}
      />
      {itens.length > 0 && (
        <Cartao>
          <span className="text-[13px] font-bold">Seu ano no campo</span>
          <Calendario itens={itens} nomes={nomes} />
          {vazios.length > 0 && (
            <>
              <span className="rounded-xl bg-sol-claro px-3 py-2 text-[13px] text-sol-texto">
                {vazios.length} {vazios.length === 1 ? "mês aparece" : "meses aparecem"} sem nada no campo (contorno amarelo).
              </span>
              <Opcoes pergunta="Nesses meses o campo fica sem nada?" valor={r.q9_meses_vazios}
                onChange={(v) => set({ q9_meses_vazios: v })} opcoes={SIM_NAO_NAOSEI} />
            </>
          )}
        </Cartao>
      )}
    </Bloco>
  );
}

function AdicionarDaLista({ rotulo, opcoes, onAdicionar }: { rotulo: string; opcoes: { id: string; nome: string }[]; onAdicionar: (id: string) => void }) {
  return (
    <label className="flex items-center gap-2 rounded-2xl border-2 border-dashed border-borda bg-white/60 px-3 py-2 text-sm font-bold text-folha">
      <Mais size={18} />
      <span className="sr-only">{rotulo}</span>
      <select
        value=""
        onChange={(e) => e.target.value && onAdicionar(e.target.value)}
        className="h-10 flex-1 bg-transparent font-bold focus:outline-none"
      >
        <option value="">{rotulo}</option>
        {[...opcoes].sort((a, b) => a.nome.localeCompare(b.nome, "pt")).map((o) => (
          <option key={o.id} value={o.id}>{o.nome}</option>
        ))}
      </select>
    </label>
  );
}

export function PassoPosColheita({ r, set }: PassoProps) {
  return (
    <Bloco titulo="E depois da colheita?">
      <Grade>
      <Opcoes pergunta="Depois da colheita, o que acontece com o campo?" colunas={2} valor={r.q10_pos_colheita}
        onChange={(v) => set({ q10_pos_colheita: v })}
        opcoes={[
          { valor: "parado", rotulo: "Fica parado" }, { valor: "pasto", rotulo: "Vira pasto" },
          { valor: "outra", rotulo: "Planto outra coisa" }, { valor: "cobertura", rotulo: "Planto algo pra cobrir o solo" },
        ]} />
      <Opcoes pergunta="Deixa a palha ou o resto da cultura no campo?" valor={r.q11_palha}
        onChange={(v) => set({ q11_palha: v })} opcoes={SIM_NAO_NAOSEI} />
      </Grade>
    </Bloco>
  );
}

/* ---------- Bloco 4: solo ---------- */
const PERGUNTAS_SOLO: { k: keyof Respostas; p: string }[] = [
  { k: "q14_encharca", p: "Depois de chuva forte, a água fica empoçada mais de um dia?" },
  { k: "q15_casca", p: "Quando seca, a terra forma uma casca na superfície?" },
  { k: "q16_erosao", p: "Já viu a chuva levando terra (valetas, água barrenta saindo do campo)?" },
  { k: "q17_dura", p: "A terra fica muito dura pra cavar ou arar?" },
  { k: "q18_minhocas", p: "Encontra minhocas quando cava?" },
];

const CAMPOS_LAUDO: { k: keyof Laudo; rotulo: string; unidade: string }[] = [
  { k: "ph_agua", rotulo: "pH em água", unidade: "" },
  { k: "argila_pct", rotulo: "Argila", unidade: "%" },
  { k: "materia_organica_g_dm3", rotulo: "Matéria orgânica", unidade: "g/dm³" },
  { k: "fosforo_mg_dm3", rotulo: "Fósforo (P)", unidade: "mg/dm³" },
  { k: "potassio_mg_dm3", rotulo: "Potássio (K)", unidade: "mg/dm³" },
  { k: "ctc_cmolc_dm3", rotulo: "CTC", unidade: "cmolc/dm³" },
  { k: "saturacao_bases_pct", rotulo: "Saturação por bases (V%)", unidade: "%" },
];

function CamposLaudo({ laudo, onChange }: { laudo: Laudo; onChange: (l: Laudo) => void }) {
  return (
    <div className="flex flex-col gap-2 px-1">
      <span className="text-[13px] font-bold">Valores do laudo (preencha os que tiver)</span>
      <span className="text-xs text-suave">
        Com pelo menos dois valores, a análise usa o seu laudo no lugar dos mapas globais.
        Se a matéria orgânica vier em %, multiplique por 10.
      </span>
      <div className="grid grid-cols-2 gap-2">
        {CAMPOS_LAUDO.map(({ k, rotulo, unidade }) => (
          <label key={k} className="flex flex-col gap-1 text-xs font-bold">
            {rotulo}{unidade && <span className="font-normal text-suave"> ({unidade})</span>}
            <input type="number" inputMode="decimal" step="any" min={0} value={laudo[k] ?? ""}
              onChange={(e) => onChange({ ...laudo, [k]: e.target.value === "" ? null : Number(e.target.value) })}
              className="h-11 rounded-xl border-2 border-borda bg-white px-3 text-[15px] font-bold" />
          </label>
        ))}
      </div>
    </div>
  );
}

export function PassoSolo1({ r, set }: PassoProps) {
  const anoAtual = new Date().getFullYear();
  return (
    <Bloco titulo="O que você sabe do seu solo?" texto={`"Não sei" também ajuda: mostra onde precisamos ter mais cuidado.`}>
      <Grade>
      <div className="flex flex-col gap-4">
      <Opcoes pergunta="Já fez análise de solo em laboratório?" valor={r.q12_analise}
        onChange={(v) => set({ q12_analise: v, ...(v !== "sim" && { q12_tem_resultado: null, q12_ano: null, q12_laudo: null }) })} opcoes={SIM_NAO_NAOSEI} />
      {r.q12_analise === "sim" && (
        <Cartao>
          <Opcoes pergunta="Tem o resultado em mãos?" valor={r.q12_tem_resultado}
            onChange={(v) => set({ q12_tem_resultado: v, ...(v !== "sim" && { q12_laudo: null }) })} opcoes={SIM_NAO_NAOSEI} />
          {r.q12_tem_resultado === "sim" && (
            <CamposLaudo laudo={r.q12_laudo ?? {}} onChange={(l) => set({ q12_laudo: l })} />
          )}
          <label className="flex flex-col gap-1.5 px-1 text-[13px] font-bold">
            De que ano?
            <select value={r.q12_ano ?? ""} onChange={(e) => set({ q12_ano: e.target.value ? Number(e.target.value) : null })}
              className="h-11 rounded-xl border-2 border-borda bg-white px-3 text-[15px] font-bold">
              <option value="">Não lembro</option>
              {Array.from({ length: 20 }, (_, i) => anoAtual - i).map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </label>
        </Cartao>
      )}
      </div>
      <Opcoes pergunta="A terra é mais arenosa, argilosa ou meio-termo?" colunas={2} valor={r.q13_textura}
        onChange={(v) => set({ q13_textura: v })}
        opcoes={[
          { valor: "arenosa", rotulo: "Mais arenosa" }, { valor: "media", rotulo: "Meio-termo" },
          { valor: "argilosa", rotulo: "Mais argilosa" }, { valor: "nao_sei", rotulo: "Não sei" },
        ]} />
      {PERGUNTAS_SOLO.map(({ k, p }) => (
        <Opcoes key={k} pergunta={p} valor={r[k] as SNS | null} onChange={(v) => set({ [k]: v })} opcoes={SIM_NAO_NAOSEI} />
      ))}
      </Grade>
    </Bloco>
  );
}

const CORES = [
  { v: "escura", rotulo: "Preta", desc: "Preta ou marrom bem escura", fundo: "#3B2A20" },
  { v: "marrom", rotulo: "Marrom", desc: "Marrom", fundo: "#7A5230" },
  { v: "vermelha", rotulo: "Vermelha", desc: "Vermelha", fundo: "#9E3B26" },
  { v: "amarela", rotulo: "Amarela", desc: "Amarelada", fundo: "#C9A24A" },
  { v: "cinza", rotulo: "Cinza", desc: "Cinza ou com manchas cinza", fundo: "repeating-radial-gradient(circle at 30% 40%, #8C8C84 0 6px, #A9A79C 6px 12px)" },
  { v: "clara", rotulo: "Clara", desc: "Clara ou esbranquiçada", fundo: "#E6D9BE" },
] as const;

const JEITOS = [
  { v: "solta", rotulo: "Solta", desc: "Escorre entre os dedos" },
  { v: "fofa", rotulo: "Fofa", desc: "Em grumos pequenos" },
  { v: "gruda", rotulo: "Gruda", desc: "Molda quando molhada" },
  { v: "torroes", rotulo: "Torrões duros", desc: "Não se desfazem" },
  { v: "racha", rotulo: "Racha", desc: "Abre fendas quando seca" },
  { v: "pedras", rotulo: "Pedregosa", desc: "Muita pedra ou cascalho" },
] as const;

function BotaoNaoSei({ on, onClick }: { on: boolean; onClick: () => void }) {
  return (
    <button type="button" aria-pressed={on} onClick={onClick}
      className={cx("h-11 rounded-[14px] border-2 text-sm font-bold", on ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
      Não sei
    </button>
  );
}

export function PassoSolo2({ r, set }: PassoProps) {
  return (
    <Bloco titulo="Pegue um punhado de terra" texto="Cor e jeito na mão são pistas, não análise. A gente cruza com os dados de solo depois.">
      <fieldset className="m-0 flex flex-col gap-2.5 rounded-[22px] border-0 bg-white p-4 shadow-cartao">
        <legend className="float-left mb-2.5 w-full p-0 text-[15px] font-bold">Com qual cor a sua terra mais se parece?</legend>
        <div className="grid grid-cols-3 gap-2 lg:grid-cols-6">
          {CORES.map((c) => {
            const on = r.q19_cor === c.v;
            return (
              <button key={c.v} type="button" aria-pressed={on} title={c.desc} aria-label={c.desc} onClick={() => set({ q19_cor: c.v })}
                className={cx("flex min-w-0 flex-col items-stretch gap-1.5 rounded-2xl border-2 p-1.5 text-xs leading-tight font-bold",
                  on ? "border-folha bg-folha-clara" : "border-borda bg-white")}>
                <span className="h-12 rounded-xl" style={{ background: c.fundo }} />
                {c.rotulo}
              </button>
            );
          })}
        </div>
        <BotaoNaoSei on={r.q19_cor === "nao_sei"} onClick={() => set({ q19_cor: "nao_sei" })} />
        <span className="text-xs text-suave">Cores de referência. As fotos reais de solo ainda vão entrar aqui.</span>
      </fieldset>
      <fieldset className="m-0 flex flex-col gap-2.5 rounded-[22px] border-0 bg-white p-4 shadow-cartao">
        <legend className="float-left mb-2.5 w-full p-0 text-[15px] font-bold">E na mão, ela parece mais com qual?</legend>
        <div className="grid grid-cols-2 gap-2 lg:grid-cols-3">
          {JEITOS.map((j) => {
            const on = r.q19_jeito === j.v;
            return (
              <button key={j.v} type="button" aria-pressed={on} onClick={() => set({ q19_jeito: j.v })}
                className={cx("flex flex-col items-start rounded-2xl border-2 px-3 py-2.5 text-left",
                  on ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
                <span className="text-sm font-bold">{j.rotulo}</span>
                <span className={cx("text-xs", on ? "text-white/85" : "text-suave")}>{j.desc}</span>
              </button>
            );
          })}
        </div>
        <BotaoNaoSei on={r.q19_jeito === "nao_sei"} onClick={() => set({ q19_jeito: "nao_sei" })} />
      </fieldset>
      <Grade>
      <Opcoes pergunta="Tem partes do campo onde a lavoura sempre vai pior?" valor={r.q20_partes_piores}
        onChange={(v) => set({ q20_partes_piores: v })} opcoes={SIM_NAO_NAOSEI} />
      <Opcoes pergunta="Já usou calcário?" valor={r.q21_calcario} onChange={(v) => set({ q21_calcario: v })} opcoes={SIM_NAO_NAOSEI} />
      <Opcoes pergunta="Usa adubo ou esterco?" valor={r.q22_adubo} onChange={(v) => set({ q22_adubo: v })} opcoes={SIM_NAO_NAOSEI} />
      </Grade>
    </Bloco>
  );
}

/* ---------- Bloco 5: clima ---------- */
const PERDAS: { k: "geada" | "chuva_forte" | "calor" | "seca"; p: string }[] = [
  { k: "geada", p: "Já perdeu safra por geada?" },
  { k: "chuva_forte", p: "Já perdeu safra por chuva forte?" },
  { k: "calor", p: "Já perdeu safra por calor intenso?" },
  { k: "seca", p: "Já perdeu safra por falta de chuva?" },
];

export function PassoClima({ r, set }: PassoProps) {
  const perdas = r.q24_perdas ?? {};
  const anoAtual = new Date().getFullYear();
  const setPerda = (k: (typeof PERDAS)[number]["k"], p: Perda) => set({ q24_perdas: { ...perdas, [k]: p } });
  return (
    <Bloco titulo="O que você tem sentido no clima?" texto="Com o ano, procuramos o evento nos dados da NASA para o seu ponto.">
      <Opcoes pergunta="Sente que a chuva mudou nos últimos anos?" valor={r.q23_chuva_mudou}
        onChange={(v) => set({ q23_chuva_mudou: v })} opcoes={SIM_NAO_NAOSEI} />
      <Grade>
      {PERDAS.map(({ k, p }) => {
        const atual = perdas[k] ?? { resposta: null, ano: null };
        return (
          <div key={k} className="flex flex-col gap-2">
            <Opcoes pergunta={p} valor={atual.resposta}
              onChange={(v) => setPerda(k, { resposta: v, ano: v === "sim" ? atual.ano : null })} opcoes={SIM_NAO_NAOSEI} />
            {atual.resposta === "sim" && (
              <label className="mx-2 flex items-center justify-between gap-3 text-[13px] font-bold">
                Lembra mais ou menos o ano?
                <select value={atual.ano ?? ""} onChange={(e) => setPerda(k, { ...atual, ano: e.target.value ? Number(e.target.value) : null })}
                  className="h-11 rounded-xl border-2 border-borda bg-white px-3 text-[15px] font-bold">
                  <option value="">Não lembro</option>
                  {Array.from({ length: anoAtual - 1979 }, (_, i) => anoAtual - i).map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
              </label>
            )}
          </div>
        );
      })}
      </Grade>
    </Bloco>
  );
}

/* ---------- Bloco 6: prioridades ---------- */
const PRIORIDADES: { v: Prioridade; rotulo: string; tag: string }[] = [
  { v: "agua", rotulo: "Economizar água", tag: "Água" },
  { v: "terra", rotulo: "Melhorar a terra", tag: "Solo" },
  { v: "erosao", rotulo: "Evitar erosão", tag: "Proteção" },
  { v: "renda", rotulo: "Renda extra", tag: "Dinheiro" },
  { v: "animais", rotulo: "Comida pros animais", tag: "Forragem" },
  { v: "pragas", rotulo: "Menos praga", tag: "Pragas" },
];

const MOTIVOS: { v: NonNullable<CulturaExcluida["motivo"]>; rotulo: string }[] = [
  { v: "mercado", rotulo: "Mercado" }, { v: "costume", rotulo: "Costume" },
  { v: "deu_errado", rotulo: "Já deu errado" }, { v: "outro", rotulo: "Outro" },
];

export function PassoPrioridades({ r, set }: PassoProps) {
  const escolhidas = r.q25_prioridades ?? [];
  const alternar = (v: Prioridade) =>
    set({ q25_prioridades: escolhidas.includes(v) ? escolhidas.filter((x) => x !== v) : escolhidas.length < 3 ? [...escolhidas, v] : escolhidas });
  return (
    <Bloco titulo="O que é mais importante pra você?" texto="Escolha até 3. Isso muda a ordem das sugestões.">
      <div className="grid grid-cols-2 gap-2.5 lg:grid-cols-3">
        {PRIORIDADES.map((p) => {
          const on = escolhidas.includes(p.v);
          const cheio = !on && escolhidas.length >= 3;
          return (
            <button key={p.v} type="button" aria-pressed={on} disabled={cheio} onClick={() => alternar(p.v)}
              className={cx("flex min-h-[76px] flex-col justify-between gap-1.5 rounded-[22px] border-2 p-3.5 text-left text-[15px] font-bold transition-transform",
                on ? "border-folha bg-folha text-white shadow-degrau" : "border-borda bg-white", cheio && "opacity-50")}>
              <span className="flex items-center justify-between text-xs opacity-85">{p.tag}{on && <Check size={16} />}</span>
              {p.rotulo}
            </button>
          );
        })}
      </div>
      <span className="text-[13px] font-bold text-suave">{escolhidas.length} de 3 escolhidas</span>
    </Bloco>
  );
}

export function PassoRestricoes({ r, set, culturas, equipamentos }: PassoProps) {
  const excluidas = r.q26a_excluidas ?? [];
  const equips = r.q26b_equipamentos ?? [];
  const nomeEquip = (id: string | null) => equipamentos.find((e) => e.id === id)?.nome;
  return (
    <Bloco titulo="Seus limites" texto="Assim não sugerimos o que não serve pra você.">
      <TextoLivre campo="excluidas" rotulo="Tem alguma cultura que você não plantaria? Por quê?"
        exemplo="Ex.: não planto soja, não tenho onde vender" texto={r.q26a_texto ?? ""}
        onTexto={(t) => set({ q26a_texto: t })}
        onResultado={(res) => set({ q26a_excluidas: res.itens.map((i) => ({ cultura_id: i.id, texto_original: i.texto_original, motivo: i.motivo ?? null })) })} />
      <Grade>
      {excluidas.map((ex, idx) => (
        <Cartao key={idx}>
          <div className="flex items-center justify-between gap-2">
            <span className="text-[15px] font-bold">Não plantaria: {nomeCultura(culturas, ex.cultura_id) ?? ex.texto_original}</span>
            <button type="button" aria-label="Remover" onClick={() => set({ q26a_excluidas: excluidas.filter((_, i) => i !== idx) })}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[14px] bg-terra text-terra-texto"><Xis size={18} /></button>
          </div>
          {!ex.cultura_id && <Selo>Fora da nossa base: guardamos como texto</Selo>}
          <Opcoes pergunta="Motivo" colunas={2} valor={ex.motivo}
            onChange={(v) => set({ q26a_excluidas: excluidas.map((x, i) => (i === idx ? { ...x, motivo: v } : x)) })} opcoes={MOTIVOS.map((m) => ({ valor: m.v, rotulo: m.rotulo }))} />
        </Cartao>
      ))}
      </Grade>
      <AdicionarDaLista rotulo="Adicionar cultura que não plantaria" opcoes={culturas.map((c) => ({ id: c.id, nome: c.nome }))}
        onAdicionar={(id) => set({ q26a_excluidas: [...excluidas, { cultura_id: id, texto_original: nomeCultura(culturas, id) ?? id, motivo: null }] })} />

      <div className="mt-2" />
      <TextoLivre campo="equipamentos" rotulo="Que máquinas e equipamentos você tem ou consegue usar?"
        exemplo="Ex.: tenho trator pequeno e plantadeira, colheita é na mão" texto={r.q26b_texto ?? ""}
        onTexto={(t) => set({ q26b_texto: t })}
        onResultado={(res) => set({ q26b_equipamentos: res.itens.map((i) => ({ equipamento_id: i.id, texto_original: i.texto_original })) })} />
      {equips.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {equips.map((e, idx) => (
            <span key={idx} className={cx("inline-flex items-center gap-1 rounded-full py-1.5 pr-1.5 pl-3.5 text-sm font-bold",
              e.equipamento_id ? "bg-folha-clara text-folha-escura" : "bg-sol-claro text-sol-texto")}>
              {nomeEquip(e.equipamento_id) ?? `${e.texto_original} (fora da lista)`}
              <button type="button" aria-label="Remover" onClick={() => set({ q26b_equipamentos: equips.filter((_, i) => i !== idx) })}
                className="flex h-8 w-8 items-center justify-center rounded-full"><Xis size={14} /></button>
            </span>
          ))}
        </div>
      )}
      <AdicionarDaLista rotulo="Adicionar equipamento" opcoes={equipamentos.filter((e) => !equips.some((x) => x.equipamento_id === e.id))}
        onAdicionar={(id) => set({ q26b_equipamentos: [...equips, { equipamento_id: id, texto_original: nomeEquip(id) ?? id }] })} />
    </Bloco>
  );
}
