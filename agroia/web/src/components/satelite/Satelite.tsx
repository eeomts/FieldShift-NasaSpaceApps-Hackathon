// Cartões do Dashboard com dado real dos satélites da NASA (rota GET /fazenda/satelite).
import type { ReactNode } from "react";
import type { Chuva, Ndvi, Umidade } from "../../api/tipos";
import { useIdioma, type Idioma } from "../../i18n";
import { cx } from "../ui";

const icone = { fill: "none", stroke: "currentColor", strokeWidth: 2.2, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true } as const;

/** "2026-10-16" vira data local (sem o fuso puxar para o dia anterior). */
export const paraData = (s: string) => {
  const [a, m, d] = s.split("-").map(Number);
  return new Date(a, m - 1, d);
};

export const dataCurta = (s: string, idioma: Idioma) =>
  paraData(s).toLocaleDateString(idioma === "en" ? "en-US" : "pt-BR", { day: "numeric", month: "short" }).replace(".", "");

export const numero = (v: number, idioma: Idioma, casas = 0) =>
  v.toLocaleString(idioma === "en" ? "en-US" : "pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

function Fonte({ children }: { children: ReactNode }) {
  return <span className="text-[11px] leading-snug text-suave">{children}</span>;
}

export function SemDado({ texto }: { texto: string }) {
  return <span className="rounded-2xl bg-areia p-3 text-sm leading-snug text-suave">{texto}</span>;
}

export function Buscando() {
  const { t } = useIdioma();
  return <span className="animate-pulse rounded-2xl bg-areia p-3 text-sm text-suave">{t("Buscando nos satélites da NASA…", "Fetching from NASA satellites…")}</span>;
}

/* ---------------- Chuva dos últimos 30 dias ---------------- */

export function ChuvaRecente({ chuva }: { chuva: Chuva }) {
  const { t, idioma } = useIdioma();
  const w = 300;
  const h = 96;
  const topo = 16; // espaço para o rótulo do maior dia
  const base = h - 2;
  const n = chuva.dias.length;
  const passo = w / n;
  const largura = Math.max(passo - 2, 1); // 2px de vão entre as barras
  const maxMm = Math.max(...chuva.dias.map((d) => d.mm), 1);
  const altura = (mm: number) => (mm / maxMm) * (base - topo);
  const raio = Math.min(2, largura / 2);
  const iMaior = chuva.maior ? chuva.dias.findIndex((d) => d.data === chuva.maior!.data) : -1;
  const resumo = t(
    `Chuva diária nos últimos ${n} dias: ${numero(chuva.total_30d, idioma)} mm no total, ${numero(chuva.total_7d, idioma)} mm nos últimos 7 dias.`,
    `Daily rain over the last ${n} days: ${numero(chuva.total_30d, idioma)} mm in total, ${numero(chuva.total_7d, idioma)} mm in the last 7 days.`,
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-x-5 gap-y-1">
        <span className="text-sm"><b className="font-titulo text-xl font-extrabold">{numero(chuva.total_7d, idioma)} mm</b> <span className="text-suave">{t("nos últimos 7 dias", "in the last 7 days")}</span></span>
        <span className="text-sm"><b className="font-titulo text-xl font-extrabold">{numero(chuva.total_30d, idioma)} mm</b> <span className="text-suave">{t(`em ${n} dias`, `in ${n} days`)}</span></span>
      </div>
      <div className="relative h-24">
      {/* Estica na largura (preserveAspectRatio="none"); por isso o rótulo do maior dia fica em HTML, sem deformar. */}
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className="absolute inset-0 h-full w-full" role="img" aria-label={resumo}>
        <line x1="0" x2={w} y1={base} y2={base} stroke="var(--color-borda)" strokeWidth="1" />
        {chuva.dias.map((d, i) => {
          const x = i * passo + 1;
          const a = altura(d.mm);
          const y = base - a;
          return (
            <g key={d.data}>
              <title>{`${dataCurta(d.data, idioma)}: ${numero(d.mm, idioma, 1)} mm`}</title>
              <rect x={i * passo} y={0} width={passo} height={h} fill="transparent" />
              {a > 0.5 && (
                <path
                  vectorEffect="non-scaling-stroke"
                  d={`M${x} ${base} V${y + raio} Q${x} ${y} ${x + raio} ${y} H${x + largura - raio} Q${x + largura} ${y} ${x + largura} ${y + raio} V${base} Z`}
                  fill="var(--color-chuva)"
                  className="transition-opacity hover:opacity-70"
                />
              )}
            </g>
          );
        })}
      </svg>
      {iMaior >= 0 && chuva.maior!.mm > 0 && (
        <span className="pointer-events-none absolute -translate-x-1/2 -translate-y-full text-[10px] font-bold whitespace-nowrap"
          style={{ left: `${Math.min(Math.max(((iMaior + 0.5) / n) * 100, 6), 94)}%`, top: `${base - altura(chuva.maior!.mm) - 2}px` }}>
          {numero(chuva.maior!.mm, idioma)} mm
        </span>
      )}
      </div>
      <div className="flex justify-between text-[11px] font-bold text-suave" aria-hidden="true">
        <span>{dataCurta(chuva.dias[0].data, idioma)}</span>
        <span>{dataCurta(chuva.dias[n - 1].data, idioma)}</span>
      </div>
      <Fonte>{chuva.fonte} · {chuva.resolucao} · {t("passe o dedo ou o mouse nas barras para ver cada dia", "hover or tap a bar to see each day")}</Fonte>
    </div>
  );
}

/* ---------------- Umidade do solo (SMAP) ---------------- */

export function CartaoUmidade({ umidade, falta }: { umidade: Umidade | null; falta?: string | null }) {
  const { t, idioma } = useIdioma();
  const titulo = !umidade
    ? null
    : umidade.situacao === "seco"
      ? t("Mais seco que o normal", "Drier than normal")
      : umidade.situacao === "umido"
        ? t("Mais úmido que o normal", "Wetter than normal")
        : umidade.situacao === "normal"
          ? t("Perto do normal", "About normal")
          : t(`${numero(umidade.raiz * 100, idioma)}% de água no solo`, `${numero(umidade.raiz * 100, idioma)}% water in the soil`);
  return (
    <div className="flex flex-col gap-2.5 rounded-[24px] bg-white p-4 shadow-cartao">
      <div className="flex h-[38px] w-[38px] items-center justify-center rounded-[13px] bg-ceu text-chuva">
        <svg width="20" height="20" viewBox="0 0 24 24" {...icone}><path d="M12 22a7 7 0 0 0 7-7c0-4-7-13-7-13S5 11 5 15a7 7 0 0 0 7 7z" /></svg>
      </div>
      <span className="text-xs font-bold text-suave">{t("Umidade do solo", "Soil moisture")}</span>
      {!umidade ? (
        <SemDado texto={falta ?? t("Sem dado do SMAP agora.", "No SMAP data right now.")} />
      ) : (
        <>
          <span className="font-titulo text-lg leading-tight font-extrabold">{titulo}</span>
          {umidade.posicao !== null && (
            <div className="relative h-2.5 rounded-full bg-[linear-gradient(90deg,#F2B48A,var(--color-areia)_50%,#9CC5EE)]"
              role="img" aria-label={t(`Mais úmido que ${numero(umidade.posicao * 100, idioma)}% dos anos anteriores neste dia`, `Wetter than ${numero(umidade.posicao * 100, idioma)}% of past years on this day`)}>
              <div className="absolute -top-1 h-[18px] w-[18px] -translate-x-1/2 rounded-full border-[3px] border-white bg-tinta" style={{ left: `${Math.min(Math.max(umidade.posicao, 0.04), 0.96) * 100}%` }} />
            </div>
          )}
          <span className="text-xs leading-snug text-suave">
            {t("Raízes", "Root zone")}: {numero(umidade.raiz * 100, idioma)}%
            {umidade.media_historica !== null && <> · {t("normal", "normal")} {numero(umidade.media_historica * 100, idioma)}%</>}
            {umidade.anos_comparados > 0 && <> · {t(`${umidade.anos_comparados} anos`, `${umidade.anos_comparados} years`)}</>}
          </span>
          <Fonte>{umidade.fonte} · {umidade.resolucao} · {dataCurta(umidade.data, idioma)}</Fonte>
        </>
      )}
    </div>
  );
}

/* ---------------- Saúde da lavoura (MODIS NDVI) ---------------- */

export function CartaoNdvi({ ndvi, falta }: { ndvi: Ndvi | null; falta?: string | null }) {
  const { t, idioma } = useIdioma();
  const rotulo = {
    descoberto: t("Pouca planta: terra exposta", "Few plants: bare soil"),
    pouco: t("Pouco verde", "A little green"),
    verde: t("Verde", "Green"),
    muito: t("Bem verde", "Very green"),
  };
  return (
    <div className="flex flex-col gap-2.5 rounded-[24px] bg-white p-4 shadow-cartao">
      <div className="flex h-[38px] w-[38px] items-center justify-center rounded-[13px] bg-campo-claro text-folha">
        <svg width="20" height="20" viewBox="0 0 24 24" {...icone}><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z" /><path d="M2 21c0-3 1.9-5.4 5.2-6.1" /></svg>
      </div>
      <span className="text-xs font-bold text-suave">{t("Saúde da lavoura", "Crop health")}</span>
      {!ndvi ? (
        <SemDado texto={falta ?? t("Sem dado do MODIS agora.", "No MODIS data right now.")} />
      ) : (
        <>
          <span className="font-titulo text-lg leading-tight font-extrabold">{rotulo[ndvi.situacao]}</span>
          <span className={cx("self-start rounded-full px-2.5 py-1 text-xs font-bold", ndvi.situacao === "descoberto" ? "bg-areia text-terra-texto" : "bg-campo-claro text-folha-escura")}>
            NDVI {numero(ndvi.valor, idioma, 2)}
          </span>
          <Fonte>{ndvi.fonte} · {ndvi.resolucao} · {t("imagem de", "image from")} {dataCurta(ndvi.data, idioma)}</Fonte>
        </>
      )}
    </div>
  );
}

/* ---------------- NDVI real ao longo do ano (para sobrepor à curva do calendário) ---------------- */

/** Posição no ano (0 a 1) de uma data, para casar com o eixo Jan–Dez da curva. */
export const posicaoNoAno = (s: string) => {
  const d = paraData(s);
  const inicio = new Date(d.getFullYear(), 0, 1);
  return Math.min((d.getTime() - inicio.getTime()) / (365 * 864e5), 0.999);
};
