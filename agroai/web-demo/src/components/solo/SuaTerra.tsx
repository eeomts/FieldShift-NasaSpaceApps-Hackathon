// Card "Sua terra" do Dashboard: síntese do solo (produtor, laudo, mapa global), com consulta repetida enquanto processa.
import { useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import type { AtributoSolo, EvidenciaSolo, Fazenda, FonteSolo, SoloPonto } from "../../api/tipos";
import { useIdioma } from "../../i18n";
import { Cartao, Selo, Texto } from "../ui";

type T = (pt: string, en: string) => string;

// Classes do K iguais às da API (motor/parametros.py): Mannigel et al. 2002, Acta Scientiarum 24(5).
const K_LIMITE_BAIXA = 0.015;
const K_LIMITE_MEDIA = 0.03;

const rotulo = (t: T, a: AtributoSolo["atributo"]) =>
  ({ textura: t("Tipo de terra", "Soil type"), materia_organica: t("Matéria orgânica", "Organic matter"), acidez: t("Acidez", "Acidity") })[a];

function valores(t: T): Record<AtributoSolo["atributo"], Record<string, string>> {
  return {
    textura: {
      arenosa: t("Arenosa (terra leve, seca rápido)", "Sandy (light soil, dries fast)"),
      media: t("Média (meio termo entre leve e pesada)", "Medium (between light and heavy)"),
      argilosa: t("Argilosa (terra mais pesada, segura água)", "Clay (heavier soil, holds water)"),
    },
    materia_organica: {
      baixa: t("Baixa (terra com pouca palha e restos de planta)", "Low (little straw and plant residue)"),
      media: t("Média", "Medium"),
      alta: t("Alta (terra rica em restos de planta)", "High (rich in plant residue)"),
    },
    acidez: {
      alta: t("Ácida (pode precisar de calcário)", "Acidic (may need lime)"),
      media: t("Pouco ácida", "Slightly acidic"),
      adequada: t("Boa para a maioria das culturas", "Good for most crops"),
      alcalino: t("Alcalina (pouco ácida, comum em solo calcário)", "Alkaline (not acidic, common in limestone soil)"),
    },
  };
}

function texturaMapa(t: T, c: string): string {
  const m: Record<string, string> = {
    arenosa: t("Arenosa", "Sandy"), media: t("Média", "Medium"), argilosa: t("Argilosa", "Clay"),
    muito_argilosa: t("Muito argilosa", "Very clayey"), siltosa: t("Siltosa", "Silty"),
  };
  return m[c] ?? c;
}

function valorSimples(t: T, a: AtributoSolo): string {
  if (!a.valor) return t("Ainda sem dado", "No data yet");
  const chave = a.valor.toLowerCase().trim().replace(/[s-]+/g, "_");
  return valores(t)[a.atributo][chave] ?? a.valor;
}

function quem(t: T): Record<FonteSolo, { rotulo: string; tom: "sol" | "folha" | "ceu" }> {
  return {
    laudo: { rotulo: t("Laudo", "Lab report"), tom: "folha" },
    produtor: { rotulo: t("Você", "You"), tom: "folha" },
    soilgrids: { rotulo: t("Mapa global", "Global map"), tom: "ceu" },
    teste_campo: { rotulo: t("Teste no campo", "Field test"), tom: "sol" },
  };
}

function confianca(t: T) {
  return {
    alta: { tom: "folha" as const, rotulo: t("Confiança alta", "High confidence") },
    media: { tom: "ceu" as const, rotulo: t("Confiança média", "Medium confidence") },
    baixa: { tom: "sol" as const, rotulo: t("Confiança baixa", "Low confidence") },
  };
}

const pesoFrase = (t: T, p: number) =>
  p >= 0.6 ? t("peso maior", "higher weight") : p >= 0.3 ? t("peso médio", "medium weight") : p > 0 ? t("peso menor", "lower weight") : t("sem peso", "no weight");

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
  const { t } = useIdioma();
  const Q = quem(t);
  const fontes = [...new Set(a.evidencias.map((e) => e.fonte))];
  const conf = a.confianca ? confianca(t)[a.confianca] : null;
  return (
    <li className="flex flex-col gap-2 rounded-2xl bg-creme p-4">
      <span className="text-base font-bold text-suave">{rotulo(t, a.atributo)}</span>
      <span className="text-lg leading-snug font-extrabold">{valorSimples(t, a)}</span>
      <div className="flex flex-wrap gap-1.5">
        {conf && <Selo tom={conf.tom}>{conf.rotulo}</Selo>}
        {fontes.map((f) => <Selo key={f} tom={Q[f]?.tom ?? "ceu"}>{Q[f]?.rotulo ?? f}</Selo>)}
      </div>
      {a.divergencia && (
        <p className="m-0 rounded-xl bg-sol-claro px-3 py-2 text-base leading-[1.4] text-sol-texto">{a.divergencia}</p>
      )}
    </li>
  );
}

function NumerosMapa({ s }: { s: SoloPonto }) {
  const { t, idioma } = useIdioma();
  const num = (v: number | null, un = "") => (v == null ? null : `${v.toLocaleString(idioma === "en" ? "en-US" : "pt-BR", { maximumFractionDigits: 2 })}${un}`);
  const linhas: [string, string | null][] = [
    [t("Tipo de terra (classe)", "Soil type (class)"), s.classe_textural ? texturaMapa(t, s.classe_textural) : null],
    [t("Argila", "Clay"), num(s.argila_pct, " %")],
    [t("Areia", "Sand"), num(s.areia_pct, " %")],
    [t("Silte (terra fina)", "Silt (fine soil)"), num(s.silte_pct, " %")],
    [t("Matéria orgânica", "Organic matter"), num(s.materia_organica_g_kg, " g/kg")],
    [t("pH (acidez)", "pH (acidity)"), num(s.ph)],
    [t("Erodibilidade K", "Erodibility K"), s.k_usle == null ? null : `${num(s.k_usle)} t·ha·h/(ha·MJ·mm)`],
  ];
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-base font-bold">{t("Números do mapa global", "Global map numbers")}</span>
      <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
        {linhas.filter(([, v]) => v != null).map(([r, v]) => (
          <li key={r} className="flex justify-between gap-3 rounded-xl bg-terra px-3 py-2 text-[15px]">
            <span>{r}</span><span className="shrink-0 font-bold">{v}</span>
          </li>
        ))}
      </ul>
      {s.k_usle != null && (
        <span className="text-[15px] text-suave">
          {t("K mostra quanto a terra se desmancha com a chuva", "K shows how much the soil washes away in the rain")}:{" "}
          {s.k_usle < K_LIMITE_BAIXA ? t("baixo", "low") : s.k_usle < K_LIMITE_MEDIA ? t("médio", "medium") : t("alto", "high")}.
        </span>
      )}
      <span className="text-sm text-suave">{t("Fonte", "Source")}: {s.fonte} · {t("camada", "layer")} {s.camada}</span>
    </div>
  );
}

function Evidencia({ e }: { e: EvidenciaSolo }) {
  const { t } = useIdioma();
  return (
    <li className="rounded-xl bg-terra px-3 py-2 text-[15px] leading-snug">
      {e.texto} <span className="font-bold">· {e.valor}</span>
      <span className="block text-sm text-suave">{t("Fonte", "Source")}: {quem(t)[e.fonte]?.rotulo ?? e.fonte} · {pesoFrase(t, e.peso)}</span>
    </li>
  );
}

function DeOndeVeio({ sintese, solo }: { sintese: AtributoSolo[]; solo: SoloPonto | null | undefined }) {
  const { t } = useIdioma();
  const mapa = solo && !solo.sem_dado ? solo : null;
  return (
    <details className="rounded-2xl bg-creme px-4 py-3">
      <summary className="cursor-pointer text-base font-bold text-folha-escura">{t("De onde veio", "Where this came from")}</summary>
      <div className="mt-3 flex flex-col gap-4">
        {sintese.map((a) => (
          <div key={a.atributo} className="flex flex-col gap-1.5">
            <span className="text-base font-bold">{rotulo(t, a.atributo)}</span>
            {a.evidencias.length === 0 ? (
              <span className="text-[15px] text-suave">{t("Sem informação até agora.", "No information yet.")}</span>
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
  const { t } = useIdioma();
  const itens = fazenda.retrato_solo.indicadores?.filter((i) => i.texto) ?? [];
  if (itens.length === 0 && !fazenda.retrato_solo.figuras) return <Texto>{t("Conte mais sobre a sua terra para ver o retrato aqui.", "Tell us more about your land to see its portrait here.")}</Texto>;
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
  const { t } = useIdioma();
  const [fazenda, setFazenda] = useState<Fazenda>(inicial);
  const [desisti, setDesisti] = useState(false);
  const processando = fazenda.status_processamento === "processando";
  const inicio = useRef(Date.now());

  useEffect(() => {
    if (!processando) return;
    const timer = setInterval(() => {
      if (Date.now() - inicio.current > LIMITE) {
        clearInterval(timer);
        setDesisti(true);
        return;
      }
      api<Fazenda>("/fazenda").then(setFazenda).catch(() => {});
    }, A_CADA);
    return () => clearInterval(timer);
  }, [processando]);

  const solo = fazenda.retrato_solo;
  const sintese = solo.sintese ?? [];
  const status = fazenda.status_processamento;
  const semLocal = status === "pendente" && !fazenda.respostas.q5_local;
  const aviso = "m-0 rounded-2xl bg-sol-claro px-4 py-3 text-base font-bold text-sol-texto";

  return (
    <section aria-labelledby="titulo-terra" className="flex flex-col gap-4 lg:mx-auto lg:w-full lg:max-w-[760px]">
      <h2 id="titulo-terra" className="m-0 font-titulo text-2xl font-extrabold tracking-[-0.02em]">{t("Sua terra", "Your land")}</h2>
      <Cartao className="gap-4 lg:p-6">
        {processando && !desisti && (
          <div role="status" className="flex flex-col gap-3">
            <p className={aviso}>
              {t("Buscando o mapa de solo da sua região… é um serviço lento e pode levar alguns minutos. Você pode continuar usando o app.",
                "Fetching the soil map for your region… this service is slow and can take a few minutes. You can keep using the app.")}
            </p>
            <Esqueleto />
          </div>
        )}
        {processando && desisti && (
          <p role="status" className={aviso}>{t("Ainda processando; volte daqui a pouco.", "Still processing; come back in a little while.")}</p>
        )}
        {status === "erro" && (
          <p role="status" className={aviso}>
            {t("Não consegui o mapa de solo agora; mostramos o que você contou.", "We couldn't get the soil map right now; we're showing what you told us.")}
          </p>
        )}
        {semLocal && <Texto>{t("Diga onde fica a sua terra para buscarmos o mapa de solo da região.", "Tell us where your land is so we can fetch the soil map for the area.")}</Texto>}
        {solo.soilgrids?.sem_dado && (
          <p className="m-0 rounded-2xl bg-ceu px-4 py-3 text-base text-ceu-texto">{t("O mapa global não cobre este ponto (área urbana ou água).", "The global map doesn't cover this spot (urban area or water).")}</p>
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
