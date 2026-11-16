// Cartões do Dashboard com dado real dos satélites da NASA (rota GET /fazenda/satelite).
import type { ReactNode } from "react";
import type { Chuva, CodigoFalta, DiaPrevisao, Ndvi, Previsao, Satelite, Umidade } from "../../api/tipos";
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

/** Fazenda nos EUA: polegadas e °F (o resto do app também usa acre lá). */
export const chuvaTexto = (mm: number, imperial: boolean, idioma: Idioma) =>
  imperial ? `${numero(mm / 25.4, idioma, mm / 25.4 < 10 ? 2 : 1)} in` : `${numero(mm, idioma)} mm`;

const temperatura = (c: number, imperial: boolean) => `${Math.round(imperial ? (c * 9) / 5 + 32 : c)}°`;

type T = (pt: string, en: string) => string;

/** Texto, no idioma do produtor, do motivo de um dado de satélite não ter vindo. */
export function textoFalta(codigo: CodigoFalta, t: T): string {
  switch (codigo) {
    case "sem_token":
      return t("O servidor ainda não tem o acesso aos dados da NASA (Earthdata).", "The server doesn't have access to NASA data (Earthdata) yet.");
    case "sem_permissao":
      return t("A NASA recusou o acesso a este dado.", "NASA refused access to this data.");
    case "sem_dado_ponto":
      return t("O satélite não tem dado para este ponto (água, cidade ou gelo).", "The satellite has no data for this spot (water, city or ice).");
    case "nuvem":
      return t("As imagens do último ano estão cobertas de nuvem neste ponto.", "Last year's images are covered by clouds at this spot.");
    case "sem_arquivo":
      return t("A NASA ainda não publicou imagens recentes para este ponto.", "NASA hasn't published recent images for this spot yet.");
    case "fora_do_ar":
      return t("Não consegui falar com a NASA agora. Tente de novo em alguns minutos.", "Couldn't reach NASA right now. Please try again in a few minutes.");
    default:
      return t("Erro ao ler este dado da NASA.", "Error reading this NASA data.");
  }
}

export function textoAviso(codigo: Satelite["avisos"][number], t: T): string {
  return codigo === "imerg_bloqueado"
    ? t("A conta do Earthdata ainda não autorizou a GES DISC, onde fica o IMERG. Mostrando a chuva do NASA POWER, que também vem da NASA.",
        "The Earthdata account hasn't authorized GES DISC, where IMERG lives, yet. Showing NASA POWER rain, which also comes from NASA.")
    : t("O IMERG não respondeu agora. Mostrando a chuva do NASA POWER, que também vem da NASA.",
        "IMERG didn't respond right now. Showing NASA POWER rain, which also comes from NASA.");
}

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

export function ChuvaRecente({ chuva, imperial = false }: { chuva: Chuva; imperial?: boolean }) {
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
    `Chuva diária nos últimos ${n} dias: ${chuvaTexto(chuva.total_30d, imperial, idioma)} no total, ${chuvaTexto(chuva.total_7d, imperial, idioma)} nos últimos 7 dias.`,
    `Daily rain over the last ${n} days: ${chuvaTexto(chuva.total_30d, imperial, idioma)} in total, ${chuvaTexto(chuva.total_7d, imperial, idioma)} in the last 7 days.`,
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-x-5 gap-y-1">
        <span className="text-sm"><b className="font-titulo text-xl font-extrabold">{chuvaTexto(chuva.total_7d, imperial, idioma)}</b> <span className="text-suave">{t("nos últimos 7 dias", "in the last 7 days")}</span></span>
        <span className="text-sm"><b className="font-titulo text-xl font-extrabold">{chuvaTexto(chuva.total_30d, imperial, idioma)}</b> <span className="text-suave">{t(`em ${n} dias`, `in ${n} days`)}</span></span>
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
              <title>{`${dataCurta(d.data, idioma)}: ${imperial ? chuvaTexto(d.mm, true, idioma) : `${numero(d.mm, idioma, 1)} mm`}`}</title>
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
          {chuvaTexto(chuva.maior!.mm, imperial, idioma)}
        </span>
      )}
      </div>
      <div className="flex justify-between text-[11px] font-bold text-suave" aria-hidden="true">
        <span>{dataCurta(chuva.dias[0].data, idioma)}</span>
        <span>{dataCurta(chuva.dias[n - 1].data, idioma)}</span>
      </div>
      <Fonte>{chuva.fonte} · {chuva.resolucao} · {t("diário", "daily")} · {t("passe o dedo ou o mouse nas barras para ver cada dia", "hover or tap a bar to see each day")}</Fonte>
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
          <Fonte>{ndvi.fonte} · {ndvi.resolucao} · {t("a cada 16 dias", "every 16 days")} · {t("imagem de", "image from")} {dataCurta(ndvi.data, idioma)}</Fonte>
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

/* ---------------- Previsão dos próximos 7 dias (Open-Meteo) ---------------- */

/** Dia "forte" de chuva para o alerta: 30 mm ou mais previstos. */
export const CHUVA_FORTE_MM = 30;

export const diaSemana = (s: string, idioma: Idioma) => {
  const d = paraData(s).toLocaleDateString(idioma === "en" ? "en-US" : "pt-BR", { weekday: "short" }).replace(".", "");
  return d.charAt(0).toUpperCase() + d.slice(1);
};

function IconeTempo({ dia }: { dia: DiaPrevisao }) {
  const chuva = (dia.chuva_mm ?? 0) >= 1 || (dia.codigo_tempo ?? 0) >= 51;
  if (chuva)
    return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563A8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3" /><path d="M8 17v3M12 19v3M16 17v3" /></svg>;
  if ((dia.codigo_tempo ?? 0) >= 2)
    return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4F5F54" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M17.5 19H9a7 7 0 1 1 6.7-9h1.8a4.5 4.5 0 1 1 0 9Z" /></svg>;
  return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#C98500" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>;
}

export function PrevisaoSemana({ previsao, imperial = false }: { previsao: Previsao; imperial?: boolean }) {
  const { t, idioma } = useIdioma();
  const total = previsao.dias.reduce((s, d) => s + (d.chuva_mm ?? 0), 0);
  return (
    <div className="flex flex-col gap-3.5">
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="m-0 font-titulo text-lg font-extrabold">{t("Próximos 7 dias", "Next 7 days")}</h2>
        <span className="text-[13px] font-bold text-chuva">{t(`${chuvaTexto(total, imperial, idioma)} de chuva`, `${chuvaTexto(total, imperial, idioma)} of rain`)}</span>
      </div>
      <ul className="m-0 grid list-none grid-cols-7 gap-1 p-0">
        {previsao.dias.map((d) => {
          const forte = (d.chuva_mm ?? 0) >= CHUVA_FORTE_MM;
          const rotulo = [
            diaSemana(d.data, idioma),
            d.tmax != null && t(`máxima ${temperatura(d.tmax, imperial)}`, `high ${temperatura(d.tmax, imperial)}`),
            d.tmin != null && t(`mínima ${temperatura(d.tmin, imperial)}`, `low ${temperatura(d.tmin, imperial)}`),
            d.chuva_mm != null && t(`${chuvaTexto(d.chuva_mm, imperial, idioma)} de chuva`, `${chuvaTexto(d.chuva_mm, imperial, idioma)} of rain`),
            d.chance_chuva != null && t(`${d.chance_chuva}% de chance`, `${d.chance_chuva}% chance`),
          ].filter(Boolean).join(", ");
          return (
            <li key={d.data} title={rotulo} aria-label={rotulo} className={cx("flex flex-col items-center gap-1 rounded-2xl py-2.5", forte ? "bg-sol-claro" : "bg-creme")}>
              <span className="text-xs font-bold">{diaSemana(d.data, idioma)}</span>
              <IconeTempo dia={d} />
              <span className="text-[13px] font-bold">{d.tmax == null ? "–" : temperatura(d.tmax, imperial)}</span>
              <span className="text-xs text-suave">{d.tmin == null ? "–" : temperatura(d.tmin, imperial)}</span>
              <span className="text-[11px] font-bold text-chuva">{d.chuva_mm == null ? "–" : imperial ? chuvaTexto(d.chuva_mm, true, idioma) : `${numero(d.chuva_mm, idioma)} mm`}</span>
            </li>
          );
        })}
      </ul>
      <Fonte>
        {t("Previsão", "Forecast")}:{" "}
        <a href="https://open-meteo.com/" target="_blank" rel="noreferrer" className="font-bold text-suave underline">Open-Meteo</a> ({previsao.licenca})
      </Fonte>
    </div>
  );
}
