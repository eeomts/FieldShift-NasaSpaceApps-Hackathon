// Dashboard no visual v3. Questionário, previsão (Open-Meteo), chuva, umidade (SMAP) e NDVI (MODIS) são reais; cada cartão diz a fonte e a data.
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import { api } from "../api/client";
import { useSessao } from "../api/sessao";
import { obterPrevisao } from "../api/previsao";
import { obterSatelite } from "../api/satelite";
import type { CulturaBase, Fazenda, Ndvi, Previsao, Satelite } from "../api/tipos";
import { Casca, SeletorIdioma } from "../components/Casca";
import { Estrategias } from "../components/estrategias/Estrategias";
import {
  Buscando, CartaoNdvi, CartaoUmidade, CHUVA_FORTE_MM, ChuvaRecente, chuvaTexto, dataCurta, diaSemana, numero, posicaoNoAno, PrevisaoSemana, SemDado, textoAviso, textoFalta,
} from "../components/satelite/Satelite";
import { Brilho, Pino, Sair } from "../components/icones";
import { Aviso, BotaoContorno, Carregando, cx } from "../components/ui";
import { INICIAIS_MESES, MESES_LONGOS, useIdioma } from "../i18n";
import { OPCOES_AREA, OPCOES_PRIORIDADES, unidadePadrao } from "../onboarding/dados";
import { passoNoIdioma } from "../onboarding/passos";

const cartao = "rounded-[28px] bg-white p-5 shadow-cartao";
const icone = { fill: "none", stroke: "currentColor", strokeWidth: 2.2, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true } as const;

const maiuscula = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

function saudacao(t: (pt: string, en: string) => string) {
  const h = new Date().getHours();
  return h < 12 ? t("Bom dia", "Good morning") : h < 18 ? t("Boa tarde", "Good afternoon") : t("Boa noite", "Good evening");
}

/** Faixas seguidas de meses vazios (Dez e Jan viram duas faixas). */
function faixas(vazios: number[]): [number, number][] {
  const out: [number, number][] = [];
  for (let m = 1; m <= 12; m++) {
    if (!vazios.includes(m)) continue;
    const ult = out[out.length - 1];
    if (ult && ult[1] === m - 1) ult[1] = m;
    else out.push([m, m]);
  }
  return out;
}

/** y do gráfico (0 a 78) para um NDVI: 0 embaixo, 0,9 ou mais no alto. */
const yNdvi = (v: number) => 66 - (Math.min(Math.max(v, 0), 0.9) / 0.9) * 54;

function CurvaVerde({ vazios, calendario, ndvi }: { vazios: number[]; calendario: boolean; ndvi: Ndvi | null }) {
  const { t, idioma } = useIdioma();
  const w = 350;
  const pts = Array.from({ length: 12 }, (_, i) => ({ x: ((i + 0.5) * w) / 12, y: vazios.includes(i + 1) ? 62 : 16 }));
  let d = `M0 ${pts[0].y}`;
  let ant = { x: 0, y: pts[0].y };
  for (const p of [...pts, { x: w, y: pts[11].y }]) {
    const meio = (ant.x + p.x) / 2;
    d += ` C ${meio} ${ant.y}, ${meio} ${p.y}, ${p.x} ${p.y}`;
    ant = p;
  }
  const real = (ndvi?.serie ?? []).map((p) => ({ ...p, x: posicaoNoAno(p.data) * w, y: yNdvi(p.valor) })).sort((p, q) => p.x - q.x);
  const linhaReal = real.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
  const lista = vazios.map((m) => MESES_LONGOS[idioma][m - 1]).join(", ");
  const rotulo = [
    calendario ? (vazios.length ? t(`Pelo seu calendário, o campo fica verde menos em: ${lista}.`, `From your calendar, the field is green except in: ${lista}.`) : t("Pelo seu calendário, o campo fica verde o ano todo.", "From your calendar, the field is green all year.")) : "",
    real.length ? t(`Satélite: NDVI de ${numero(Math.min(...real.map((p) => p.valor)), idioma, 2)} a ${numero(Math.max(...real.map((p) => p.valor)), idioma, 2)} no último ano.`, `Satellite: NDVI from ${numero(Math.min(...real.map((p) => p.valor)), idioma, 2)} to ${numero(Math.max(...real.map((p) => p.valor)), idioma, 2)} over the last year.`) : "",
  ].filter(Boolean).join(" ");
  return (
    <div className="flex flex-col gap-2">
      {calendario && real.length > 0 && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[12px] font-bold text-suave">
          <span className="inline-flex items-center gap-1.5"><svg width="22" height="8" aria-hidden="true"><line x1="1" x2="21" y1="4" y2="4" stroke="#1F7A4D" strokeWidth="2.5" strokeLinecap="round" /><circle cx="11" cy="4" r="3.5" fill="#1F7A4D" stroke="#fff" strokeWidth="1.5" /></svg>{t("Satélite (NDVI real)", "Satellite (real NDVI)")}</span>
          <span className="inline-flex items-center gap-1.5"><svg width="22" height="8" aria-hidden="true"><line x1="1" x2="21" y1="4" y2="4" stroke="#8FB9A0" strokeWidth="2.5" strokeDasharray="4 4" strokeLinecap="round" /></svg>{t("Pelo seu calendário", "From your calendar")}</span>
        </div>
      )}
      <div className="relative h-24">
        {calendario && faixas(vazios).map(([a, b]) => (
          <div key={a} className="absolute top-0 bottom-[18px] rounded-xl bg-[repeating-linear-gradient(135deg,var(--color-areia)_0_8px,var(--color-creme)_8px_16px)]"
            style={{ left: `${((a - 1) / 12) * 100}%`, width: `${((b - a + 1) / 12) * 100}%` }}>
            <span className="block px-1 pt-2 text-center text-xs font-bold text-terra-texto">{b - a >= 2 ? t("Terra descoberta", "Bare soil") : ""}</span>
          </div>
        ))}
        <svg viewBox={`0 0 ${w} 78`} preserveAspectRatio="none" role="img" aria-label={rotulo} className="absolute top-0 left-0 h-[78px] w-full">
          {calendario && (
            <path d={d} fill="none" stroke={real.length ? "#8FB9A0" : "#1F7A4D"} strokeWidth={real.length ? 2.5 : 4} strokeDasharray={real.length ? "6 6" : undefined}
              strokeLinecap="round" vectorEffect="non-scaling-stroke" />
          )}
          {real.length > 0 && <path d={linhaReal} fill="none" stroke="#1F7A4D" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />}
        </svg>
        {/* Pontos em HTML para ficarem redondos mesmo com o SVG esticado; o title mostra a data e o valor. */}
        {real.map((p) => (
          <span key={p.data} title={`${dataCurta(p.data, idioma)}: NDVI ${numero(p.valor, idioma, 2)}`}
            className="group absolute flex h-5 w-5 -translate-x-1/2 -translate-y-1/2 items-center justify-center"
            style={{ left: `${(p.x / w) * 100}%`, top: `${p.y}px` }}>
            <span className="h-2.5 w-2.5 rounded-full border-2 border-white bg-folha transition-transform group-hover:scale-150" />
          </span>
        ))}
        <div className="absolute right-0 bottom-0 left-0 grid grid-cols-12 text-center text-[11px] font-bold text-suave" aria-hidden="true">
          {INICIAIS_MESES.map((l, i) => <span key={i}>{l}</span>)}
        </div>
      </div>
    </div>
  );
}

export function Dashboard() {
  const { usuario, sair } = useSessao();
  const { idioma, t, erro: textoErro } = useIdioma();
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [nomes, setNomes] = useState<Record<string, string>>({});
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [sat, setSat] = useState<Satelite | null>(null);
  const [satErro, setSatErro] = useState<string | null>(null);
  const [prev, setPrev] = useState<Previsao | null>(null);
  const [prevErro, setPrevErro] = useState<string | null>(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setFazenda(await api<Fazenda>("/fazenda"));
    } catch (e) {
      setErro(textoErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  // Satélite só depois que a fazenda tem ponto no mapa (a 1ª consulta na região leva alguns segundos).
  const temPonto = Boolean(fazenda?.respostas.q5_local);
  useEffect(() => {
    if (!temPonto) return;
    setSat(null);
    setSatErro(null);
    setPrev(null);
    setPrevErro(null);
    obterSatelite().then(setSat).catch((e) => setSatErro(textoErro(e)));
    obterPrevisao().then(setPrev).catch((e) => setPrevErro(textoErro(e)));
  }, [temPonto]);

  useEffect(() => {
    api<CulturaBase[]>(`/culturas?idioma=${idioma}`).then((cs) => setNomes(Object.fromEntries(cs.map((c) => [c.id, c.nome])))).catch(() => {});
  }, [idioma]);

  const primeiroNome = usuario?.nome.split(" ")[0] ?? "";
  const hoje = maiuscula(new Date().toLocaleDateString(idioma === "en" ? "en-US" : "pt-BR", { weekday: "long", day: "numeric", month: "long" }));

  let corpo;
  if (carregando) corpo = <Carregando texto={t("Carregando a sua fazenda…", "Loading your farm…")} />;
  else if (erro || !fazenda)
    corpo = (
      <div className="flex flex-col gap-3 py-6">
        <Aviso>{erro ?? t("Algo deu errado. Tente de novo.", "Something went wrong. Please try again.")}</Aviso>
        <BotaoContorno type="button" onClick={() => void carregar()}>{t("Tentar de novo", "Try again")}</BotaoContorno>
      </div>
    );
  else {
    const r = fazenda.respostas;
    const itens = r.q8_culturas ?? [];
    const vazios = itens.length ? fazenda.meses_sem_cobertura : [];
    const un = unidadePadrao(r.q5_local?.pais);
    const imperial = un === "acre";
    const falta = (parte: "umidade" | "ndvi" | "chuva") => (sat?.faltas[parte] ? textoFalta(sat.faltas[parte]!, t) : satErro);
    const diaForte = prev?.dias.find((d) => (d.chuva_mm ?? 0) >= CHUVA_FORTE_MM) ?? null;
    const area = OPCOES_AREA.find((o) => o.valor === r.q2_area)?.[un][idioma];
    const lugar = r.q5_local?.nome ?? null;
    const nomeCultura = (it: (typeof itens)[number]) => (it.cultura_id && nomes[it.cultura_id]) || it.texto_original;
    const comDescida = r.q7_terreno === "leve" || r.q7_terreno === "inclinado";
    const alerta =
      comDescida && vazios.length
        ? t("Seu campo tem descida e fica sem cobertura parte do ano. Chuva forte pode levar terra.", "Your field has a slope and is bare part of the year. Heavy rain can wash soil away.")
        : vazios.length
          ? t("Seu campo fica sem cobertura parte do ano. Chuva forte pode levar terra.", "Your field is bare part of the year. Heavy rain can wash soil away.")
          : t("Chuva forte pode encharcar o campo e levar terra. Vale ficar de olho.", "Heavy rain can flood the field and wash soil away. Worth keeping an eye on it.");
    const prioridades = (r.q25_prioridades ?? []).map((p) => OPCOES_PRIORIDADES.find((o) => o.valor === p)?.[idioma]).filter(Boolean) as string[];
    const passo1 = fazenda.proximos_passos[0] ? passoNoIdioma(fazenda.proximos_passos[0], idioma) : null;
    const perguntar = (q: string) => `/agroia?q=${encodeURIComponent(q)}`;

    corpo = (
      <div className="grid gap-4 lg:grid-cols-12 lg:gap-6">
        <div className="flex flex-wrap items-center gap-2 lg:col-span-12">
          {(lugar || area) && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-campo-claro px-3 py-1.5 text-[13px] font-bold text-folha-escura">
              <Pino size={14} /> {[lugar, area].filter(Boolean).join(" · ")}
            </span>
          )}
          {fazenda.perfil && <span className="rounded-full bg-white px-3 py-1.5 text-[13px] font-bold shadow-cartao">{t("Perfil", "Profile")} {fazenda.perfil}</span>}
          {sat && (
            <span className="rounded-full bg-ceu px-3 py-1.5 text-[13px] font-bold text-ceu-texto">{t("Dados de satélite da NASA", "NASA satellite data")}</span>
          )}
        </div>

        {sat && sat.avisos.length > 0 && (
          <p className="m-0 rounded-2xl bg-sol-claro px-4 py-2.5 text-[13px] leading-snug text-sol-texto lg:col-span-12">{sat.avisos.map((a) => textoAviso(a, t)).join(" ")}</p>
        )}

        {/* Alerta: chuva forte prevista (Open-Meteo) ou, sem ela, a maior chuva medida no mês; o texto vem do questionário */}
        <div className="flex flex-col gap-3 rounded-[28px] bg-sol p-5 shadow-degrau-sol lg:col-span-5" style={{ boxShadow: "0 6px 0 var(--color-sol-escuro)" }}>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-tinta text-sol">
              <svg width="22" height="22" viewBox="0 0 24 24" {...icone}><path d="M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3" /><path d="M8 19v2M8 13v2M16 19v2M16 13v2M12 21v2M12 15v2" /></svg>
            </div>
            <div className="flex min-w-0 flex-1 flex-col">
              <span className="text-xs font-bold tracking-wider uppercase">{t("Fique de olho", "Heads up")}</span>
              <span className="font-titulo text-xl font-extrabold tracking-[-0.02em]">
                {diaForte
                  ? t(`Chuva forte ${diaSemana(diaForte.data, idioma).toLowerCase()}: ${chuvaTexto(diaForte.chuva_mm!, imperial, idioma)}`, `Heavy rain ${diaSemana(diaForte.data, idioma)}: ${chuvaTexto(diaForte.chuva_mm!, imperial, idioma)}`)
                  : sat?.chuva?.maior && sat.chuva.maior.mm > 0
                    ? t(`Maior chuva do mês: ${chuvaTexto(sat.chuva.maior.mm, imperial, idioma)} em ${dataCurta(sat.chuva.maior.data, idioma)}`, `Biggest rain this month: ${chuvaTexto(sat.chuva.maior.mm, imperial, idioma)} on ${dataCurta(sat.chuva.maior.data, idioma)}`)
                    : t("Chuva forte e erosão", "Heavy rain and erosion")}
              </span>
            </div>
          </div>
          <p className="m-0 text-sm leading-snug">{alerta}</p>
          <Link to={perguntar(t("O que fazer com a chuva forte no meu campo?", "What should I do about heavy rain on my field?"))}
            className="inline-flex h-11 items-center gap-2 self-start rounded-[14px] bg-tinta px-4 text-sm font-bold text-white no-underline">
            <Brilho size={16} /> {t("Perguntar à AgroAI", "Ask AgroAI")}
          </Link>
        </div>

        {/* Previsão dos próximos 7 dias (Open-Meteo, D-014) */}
        <div className={cx(cartao, "flex flex-col gap-3.5 lg:col-span-7")}>
          {!temPonto ? (
            <SemDado texto={t("Marque no mapa onde fica o campo para ver a previsão.", "Mark your field on the map to see the forecast.")} />
          ) : prev ? (
            <PrevisaoSemana previsao={prev} imperial={imperial} />
          ) : prevErro ? (
            <SemDado texto={prevErro} />
          ) : (
            <span className="animate-pulse rounded-2xl bg-areia p-3 text-sm text-suave">{t("Buscando a previsão…", "Fetching the forecast…")}</span>
          )}
        </div>

        {/* Chuva dos últimos 30 dias (IMERG ou NASA POWER) */}
        <div className={cx(cartao, "flex flex-col gap-3.5 lg:col-span-7")}>
          <h2 className="m-0 font-titulo text-lg font-extrabold">{t("Chuva no seu campo", "Rain on your field")}</h2>
          {!temPonto ? (
            <SemDado texto={t("Marque no mapa onde fica o campo para ver a chuva.", "Mark your field on the map to see the rain.")} />
          ) : sat?.chuva ? (
            <ChuvaRecente chuva={sat.chuva} imperial={imperial} />
          ) : sat || satErro ? (
            <SemDado texto={falta("chuva") ?? ""} />
          ) : (
            <Buscando />
          )}
        </div>

        {/* Umidade (SMAP) e NDVI (MODIS) */}
        <div className="grid grid-cols-2 gap-3 lg:col-span-5">
          {temPonto && !sat && !satErro ? (
            <div className="col-span-2 flex flex-col"><Buscando /></div>
          ) : (
            <>
              <CartaoUmidade umidade={sat?.umidade ?? null} falta={falta("umidade")} />
              <CartaoNdvi ndvi={sat?.ndvi ?? null} falta={falta("ndvi")} />
            </>
          )}
        </div>

        {/* O verde do campo no ano: calendário do produtor x NDVI real do MODIS */}
        <div className={cx(cartao, "flex flex-col gap-3 lg:col-span-12")}>
          <div className="flex flex-col gap-0.5">
            <h2 className="m-0 font-titulo text-lg font-extrabold">{t("O verde do seu campo no ano", "How green your field is over the year")}</h2>
            <span className="text-[13px] text-suave">
              {sat?.ndvi ? t("O que o satélite viu no último ano, comparado com o seu calendário", "What the satellite saw over the last year, next to your calendar") : t("Desenhado a partir do seu calendário", "Drawn from your own calendar")}
            </span>
          </div>
          {itens.length || sat?.ndvi ? (
            <CurvaVerde vazios={vazios} calendario={itens.length > 0} ndvi={sat?.ndvi ?? null} />
          ) : (
            <span className="rounded-2xl bg-areia p-3 text-sm text-suave">{t("Conte o que você planta e quando para desenhar esta curva.", "Tell us what you grow and when to draw this curve.")}</span>
          )}
          <span className="text-[11px] text-suave">
            {sat?.ndvi
              ? `${sat.ndvi.fonte} · ${sat.ndvi.resolucao} · ${t("a cada 16 dias", "every 16 days")} · ${t(`${sat.ndvi.serie.length} imagens sem nuvem`, `${sat.ndvi.serie.length} cloud-free images`)}`
              : t("NASA MODIS NDVI (MOD13Q1) · 250 m · a cada 16 dias", "NASA MODIS NDVI (MOD13Q1) · 250 m · every 16 days")}
          </span>
        </div>

        {/* Estratégias: comparação real de rotações (GET /fazenda/estrategias) */}
        <div className="lg:col-span-8">
          <Estrategias />
        </div>

        {/* Sua fazenda (real, do questionário) */}
        <div className={cx(cartao, "flex flex-col gap-3 lg:col-span-4 lg:self-start")}>
          <h2 className="m-0 text-[13px] font-bold text-folha">{t("Sua fazenda", "Your farm")}</h2>
          <span className="text-[11px] text-suave">{t("Fonte: suas respostas no questionário", "Source: your answers in the questionnaire")}</span>
          {itens.length > 0 && (
            <p className="m-0 text-sm leading-snug">{t("Você planta: ", "You grow: ")}<b>{itens.map(nomeCultura).join(", ")}</b>.</p>
          )}
          {vazios.length > 0 && (
            <p className="m-0 text-sm leading-snug">{t("O campo fica sem nada em ", "The field is bare in ")}{vazios.map((m) => MESES_LONGOS[idioma][m - 1]).join(", ")}.</p>
          )}
          {prioridades.length > 0 && (
            <p className="m-0 text-sm leading-snug">{t("O que importa para você: ", "What matters to you: ")}{prioridades.join(", ")}.</p>
          )}
          {passo1 && (
            <p className="m-0 rounded-2xl bg-areia p-3 text-sm leading-snug"><b>{passo1.titulo}</b><br />{passo1.texto}</p>
          )}
          <Link to="/onboarding" className="text-sm font-bold text-folha">{t("Revisar minhas respostas", "Review my answers")}</Link>
        </div>

        <p className="m-0 px-2 text-center text-xs leading-snug text-suave lg:col-span-12">
          {t("A AgroAI apoia. Quem decide é você.", "AgroAI helps. You decide.")}{" "}
          {t("Informações para apoiar sua decisão. Confirme com um técnico agrícola e com a sua experiência.", "Information to support your decision. Check with an agronomist and your own experience.")}
        </p>
      </div>
    );
  }

  return (
    <Casca>
      <div className="flex-1 overflow-y-auto">
        <main className="mx-auto flex w-full max-w-[480px] flex-col gap-4 px-5 pt-6 pb-8 lg:max-w-[1120px] lg:gap-6 lg:px-10 lg:pt-10">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 flex-col gap-1">
              <span className="text-[13px] text-suave">{hoje}</span>
              <h1 className="m-0 font-titulo text-[30px] leading-none font-extrabold tracking-[-0.03em] lg:text-[40px]">{saudacao(t)}, {primeiroNome}</h1>
            </div>
            <div className="flex shrink-0 items-center gap-2 lg:hidden">
              <SeletorIdioma />
              <button type="button" onClick={sair} aria-label={t("Sair", "Log out")}
                className="flex h-12 w-12 items-center justify-center rounded-[18px] bg-sol text-tinta shadow-degrau-sol"><Sair size={20} /></button>
            </div>
          </div>
          {corpo}
        </main>
      </div>
    </Casca>
  );
}

