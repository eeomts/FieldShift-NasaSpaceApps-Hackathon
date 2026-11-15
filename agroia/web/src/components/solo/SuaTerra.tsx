// Card "Sua terra" do Dashboard: síntese do solo (produtor, laudo, mapa global), com consulta repetida enquanto processa.
import { useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import type { AtributoSolo, EvidenciaSolo, Fazenda, FonteSolo, SoloPonto } from "../../api/tipos";
import { Cartao, Selo, Texto } from "../ui";

const ROTULO: Record<AtributoSolo["atributo"], string> = {
  textura: "Tipo de terra",
  materia_organica: "Matéria orgânica",
  acidez: "Acidez",
};

const VALORES: Record<AtributoSolo["atributo"], Record<string, string>> = {
  textura: {
    arenosa: "Arenosa (terra leve, seca rápido)",
    media: "Média (meio termo entre leve e pesada)",
    argilosa: "Argilosa (terra mais pesada, segura água)",
  },
  materia_organica: {
    baixa: "Baixa (terra com pouca palha e restos de planta)",
    media: "Média",
    alta: "Alta (terra rica em restos de planta)",
  },
  acidez: {
    alta: "Ácida (pode precisar de calcário)",
    media: "Pouco ácida",
    adequada: "Boa para a maioria das culturas",
    alcalino: "Alcalina (pouco ácida, comum em solo calcário)",
  },
};

const TEXTURA_MAPA: Record<string, string> = {
  arenosa: "Arenosa", media: "Média", argilosa: "Argilosa", muito_argilosa: "Muito argilosa", siltosa: "Siltosa",
};

function valorSimples(a: AtributoSolo): string {
  if (!a.valor) return "Ainda sem dado";
  const chave = a.valor.toLowerCase().trim().replace(/[\s-]+/g, "_");
  return VALORES[a.atributo][chave] ?? a.valor;
}

const QUEM: Record<FonteSolo, { rotulo: string; tom: "sol" | "folha" | "ceu" }> = {
  laudo: { rotulo: "Laudo", tom: "folha" },
  produtor: { rotulo: "Você", tom: "folha" },
  soilgrids: { rotulo: "Mapa global", tom: "ceu" },
  teste_campo: { rotulo: "Teste no campo", tom: "sol" },
};

const CONFIANCA = {
  alta: { tom: "folha" as const, rotulo: "Confiança alta" },
  media: { tom: "ceu" as const, rotulo: "Confiança média" },
  baixa: { tom: "sol" as const, rotulo: "Confiança baixa" },
};

const pesoFrase = (p: number) => (p >= 0.6 ? "peso maior" : p >= 0.3 ? "peso médio" : p > 0 ? "peso menor" : "sem peso");

function Esqueleto() {
  return (
    <div className="flex animate-pulse flex-col gap-3" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex flex-col gap-2 rounded-2xl bg-creme p-4">
          <div className="h-4 w-1/3 rounded-full bg-terra" />
          <div className="h-5 w-3/4 rounded-full bg-terra" />
        </div>
      ))}
    </div>
  );
}

function Bloco({ a }: { a: AtributoSolo }) {
  const quem = [...new Set(a.evidencias.map((e) => e.fonte))];
  const conf = a.confianca ? CONFIANCA[a.confianca] : null;
  return (
    <li className="flex flex-col gap-2 rounded-2xl bg-creme p-4">
      <span className="text-base font-bold text-suave">{ROTULO[a.atributo]}</span>
      <span className="text-lg leading-snug font-extrabold">{valorSimples(a)}</span>
      <div className="flex flex-wrap gap-1.5">
        {conf && <Selo tom={conf.tom}>{conf.rotulo}</Selo>}
        {quem.map((f) => <Selo key={f} tom={QUEM[f]?.tom ?? "ceu"}>{QUEM[f]?.rotulo ?? f}</Selo>)}
      </div>
      {a.divergencia && (
        <p className="m-0 rounded-xl bg-sol-claro px-3 py-2 text-base leading-[1.4] text-sol-texto">{a.divergencia}</p>
      )}
    </li>
  );
}

const num = (v: number | null, un = "") => (v == null ? null : `${v.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}${un}`);

function NumerosMapa({ s }: { s: SoloPonto }) {
  const linhas: [string, string | null][] = [
    ["Tipo de terra (classe)", s.classe_textural ? (TEXTURA_MAPA[s.classe_textural] ?? s.classe_textural) : null],
    ["Argila", num(s.argila_pct, " %")],
    ["Areia", num(s.areia_pct, " %")],
    ["Silte (terra fina)", num(s.silte_pct, " %")],
    ["Matéria orgânica", num(s.materia_organica_g_kg, " g/kg")],
    ["pH (acidez)", num(s.ph)],
    ["Erodibilidade K", s.k_usle == null ? null : `${num(s.k_usle)} t·ha·h/(ha·MJ·mm)`],
  ];
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-base font-bold">Números do mapa global</span>
      <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
        {linhas.filter(([, v]) => v != null).map(([r, v]) => (
          <li key={r} className="flex justify-between gap-3 rounded-xl bg-terra px-3 py-2 text-[15px]">
            <span>{r}</span><span className="shrink-0 font-bold">{v}</span>
          </li>
        ))}
      </ul>
      {s.k_usle != null && (
        <span className="text-[15px] text-suave">
          K mostra quanto a terra se desmancha com a chuva: {s.k_usle < 0.02 ? "baixo" : s.k_usle < 0.035 ? "médio" : "alto"}.
        </span>
      )}
      <span className="text-sm text-suave">Fonte: {s.fonte} · camada {s.camada}</span>
    </div>
  );
}

function Evidencia({ e }: { e: EvidenciaSolo }) {
  return (
    <li className="rounded-xl bg-terra px-3 py-2 text-[15px] leading-snug">
      {e.texto} <span className="font-bold">· {e.valor}</span>
      <span className="block text-sm text-suave">Fonte: {QUEM[e.fonte]?.rotulo ?? e.fonte} · {pesoFrase(e.peso)}</span>
    </li>
  );
}

function DeOndeVeio({ sintese, solo }: { sintese: AtributoSolo[]; solo: SoloPonto | null | undefined }) {
  const mapa = solo && !solo.sem_dado ? solo : null;
  return (
    <details className="rounded-2xl bg-creme px-4 py-3">
      <summary className="cursor-pointer text-base font-bold text-folha-escura">De onde veio</summary>
      <div className="mt-3 flex flex-col gap-4">
        {sintese.map((a) => (
          <div key={a.atributo} className="flex flex-col gap-1.5">
            <span className="text-base font-bold">{ROTULO[a.atributo]}</span>
            {a.evidencias.length === 0 ? (
              <span className="text-[15px] text-suave">Sem informação até agora.</span>
            ) : (
              <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
                {a.evidencias.map((e, i) => <Evidencia key={i} e={e} />)}
              </ul>
            )}
          </div>
        ))}
        {mapa && <NumerosMapa s={mapa} />}
      </div>
    </details>
  );
}

/** Fazenda antiga (sem síntese): o retrato de antes. */
function RetratoAntigo({ fazenda }: { fazenda: Fazenda }) {
  const itens = fazenda.retrato_solo.indicadores?.filter((i) => i.texto) ?? [];
  if (itens.length === 0 && !fazenda.retrato_solo.figuras) return <Texto>Conte mais sobre a sua terra para ver o retrato aqui.</Texto>;
  return (
    <>
      {fazenda.retrato_solo.figuras && <span className="text-base font-bold">{fazenda.retrato_solo.figuras.leitura}</span>}
      <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
        {itens.map((i) => <li key={i.origem} className="text-base text-suave">• {i.texto}</li>)}
      </ul>
    </>
  );
}

const A_CADA = 10000;
const LIMITE = 6 * 60 * 1000;

export function SuaTerra({ inicial }: { inicial: Fazenda }) {
  const [fazenda, setFazenda] = useState<Fazenda>(inicial);
  const [desisti, setDesisti] = useState(false);
  const processando = fazenda.status_processamento === "processando";
  const inicio = useRef(Date.now());

  useEffect(() => {
    if (!processando) return;
    const t = setInterval(() => {
      if (Date.now() - inicio.current > LIMITE) {
        clearInterval(t);
        setDesisti(true);
        return;
      }
      api<Fazenda>("/fazenda").then(setFazenda).catch(() => {});
    }, A_CADA);
    return () => clearInterval(t);
  }, [processando]);

  const solo = fazenda.retrato_solo;
  const sintese = solo.sintese ?? [];
  const status = fazenda.status_processamento;
  const semLocal = status === "pendente" && !fazenda.respostas.q5_local;

  return (
    <section aria-labelledby="titulo-terra" className="flex flex-col gap-4 lg:mx-auto lg:w-full lg:max-w-[760px]">
      <h2 id="titulo-terra" className="m-0 font-titulo text-2xl font-extrabold tracking-[-0.02em]">Sua terra</h2>
      <Cartao className="gap-4 lg:p-6">
        {processando && !desisti && (
          <div role="status" className="flex flex-col gap-3">
            <div className="rounded-2xl bg-sol-claro px-4 py-3">
              <span className="text-base font-bold text-sol-texto">Buscando o mapa de solo da sua região… é um serviço lento e pode levar alguns minutos. Você pode continuar usando o app.</span>
            </div>
            <Esqueleto />
          </div>
        )}
        {processando && desisti && (
          <p role="status" className="m-0 rounded-2xl bg-sol-claro px-4 py-3 text-base font-bold text-sol-texto">Ainda processando; volte daqui a pouco.</p>
        )}
        {status === "erro" && (
          <p role="status" className="m-0 rounded-2xl bg-sol-claro px-4 py-3 text-base font-bold text-sol-texto">
            Não consegui o mapa de solo agora; mostramos o que você contou.
          </p>
        )}
        {semLocal && <Texto>Diga onde fica a sua terra para buscarmos o mapa de solo da região.</Texto>}
        {solo.soilgrids?.sem_dado && (
          <p className="m-0 rounded-2xl bg-ceu px-4 py-3 text-base text-ceu-texto">O mapa global não cobre este ponto (área urbana ou água).</p>
        )}

        {sintese.length > 0 ? (
          <>
            <ul className="m-0 flex list-none flex-col gap-3 p-0">
              {sintese.map((a) => <Bloco key={a.atributo} a={a} />)}
            </ul>
            <DeOndeVeio sintese={sintese} solo={solo.soilgrids} />
          </>
        ) : (
          !processando && <RetratoAntigo fazenda={fazenda} />
        )}
      </Cartao>
    </section>
  );
}
