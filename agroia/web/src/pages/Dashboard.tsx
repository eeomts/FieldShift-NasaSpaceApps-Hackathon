// Dashboard no visual v3. O que vem do questionário é real; previsão, umidade e NDVI são EXEMPLO e a tela diz isso.
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import { api } from "../api/client";
import { useSessao } from "../api/sessao";
import type { CulturaBase, Fazenda } from "../api/tipos";
import { Casca, SeletorIdioma } from "../components/Casca";
import { Brilho, Pino, Sair } from "../components/icones";
import { Aviso, BotaoContorno, Carregando, cx } from "../components/ui";
import { INICIAIS_MESES, MESES_LONGOS, useIdioma, type Idioma } from "../i18n";
import { OPCOES_AREA, OPCOES_PRIORIDADES, unidadePadrao } from "../onboarding/dados";

const cartao = "rounded-[28px] bg-white p-5 shadow-cartao";
const icone = { fill: "none", stroke: "currentColor", strokeWidth: 2.2, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true } as const;

/** Exemplo de 7 dias: máxima, mínima e chuva em mm (valores do protótipo). */
const PREVISAO_EXEMPLO: [number, number, number][] = [[33, 21, 2], [34, 22, 0], [31, 21, 8], [27, 20, 62], [28, 20, 15], [30, 21, 4], [32, 21, 0]];

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

function CurvaVerde({ vazios }: { vazios: number[] }) {
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
  const lista = vazios.map((m) => MESES_LONGOS[idioma][m - 1]).join(", ");
  return (
    <div className="relative h-24">
      {faixas(vazios).map(([a, b]) => (
        <div key={a} className="absolute top-0 bottom-[18px] rounded-xl bg-[repeating-linear-gradient(135deg,var(--color-areia)_0_8px,var(--color-creme)_8px_16px)]"
          style={{ left: `${((a - 1) / 12) * 100}%`, width: `${((b - a + 1) / 12) * 100}%` }}>
          <span className="block px-1 pt-2 text-center text-xs font-bold text-terra-texto">{b - a >= 2 ? t("Terra descoberta", "Bare soil") : ""}</span>
        </div>
      ))}
      <svg viewBox={`0 0 ${w} 78`} preserveAspectRatio="none" role="img" aria-label={vazios.length ? t(`Campo verde, menos em: ${lista}`, `Field green, except in: ${lista}`) : t("Campo verde o ano todo", "Field green all year")}
        className="absolute top-0 left-0 h-[78px] w-full">
        <path d={d} fill="none" stroke="#1F7A4D" strokeWidth="4" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="absolute right-0 bottom-0 left-0 grid grid-cols-12 text-center text-[11px] font-bold text-suave" aria-hidden="true">
        {INICIAIS_MESES.map((l, i) => <span key={i}>{l}</span>)}
      </div>
    </div>
  );
}

function diaSemana(offset: number, idioma: Idioma) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return maiuscula(d.toLocaleDateString(idioma === "en" ? "en-US" : "pt-BR", { weekday: "short" }).replace(".", ""));
}

export function Dashboard() {
  const { usuario, sair } = useSessao();
  const { idioma, t, erro: textoErro } = useIdioma();
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [nomes, setNomes] = useState<Record<string, string>>({});
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

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
    const area = OPCOES_AREA.find((o) => o.valor === r.q2_area)?.[un][idioma];
    const lugar = r.q5_local?.nome ?? null;
    const nomeCultura = (it: (typeof itens)[number]) => (it.cultura_id && nomes[it.cultura_id]) || it.texto_original;
    const primeira = itens[0] ? nomeCultura(itens[0]) : null;
    const comDescida = r.q7_terreno === "leve" || r.q7_terreno === "inclinado";
    const alerta =
      comDescida && vazios.length
        ? t("Seu campo tem descida e fica sem cobertura parte do ano. Chuva forte pode levar terra.", "Your field has a slope and is bare part of the year. Heavy rain can wash soil away.")
        : vazios.length
          ? t("Seu campo fica sem cobertura parte do ano. Chuva forte pode levar terra.", "Your field is bare part of the year. Heavy rain can wash soil away.")
          : t("Chuva forte pode encharcar o campo e levar terra. Vale ficar de olho.", "Heavy rain can flood the field and wash soil away. Worth keeping an eye on it.");
    const prioridades = (r.q25_prioridades ?? []).map((p) => OPCOES_PRIORIDADES.find((o) => o.valor === p)?.[idioma]).filter(Boolean) as string[];
    const passo1 = fazenda.proximos_passos[0];
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
          <span className="rounded-full bg-areia px-3 py-1.5 text-[13px] font-bold text-terra-texto">{t("Clima e satélite: dados de exemplo", "Weather and satellite: sample data")}</span>
        </div>

        {/* Alerta (exemplo) */}
        <div className="flex flex-col gap-3 rounded-[28px] bg-sol p-5 shadow-degrau-sol lg:col-span-5" style={{ boxShadow: "0 6px 0 var(--color-sol-escuro)" }}>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-tinta text-sol">
              <svg width="22" height="22" viewBox="0 0 24 24" {...icone}><path d="M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3" /><path d="M8 19v2M8 13v2M16 19v2M16 13v2M12 21v2M12 15v2" /></svg>
            </div>
            <div className="flex min-w-0 flex-1 flex-col">
              <span className="text-xs font-bold tracking-wider uppercase">{t("Fique de olho", "Heads up")} · {diaSemana(3, idioma)}</span>
              <span className="font-titulo text-xl font-extrabold tracking-[-0.02em]">{t("Chuva forte: 62 mm", "Heavy rain: 62 mm")}</span>
            </div>
            <span className="self-start rounded-full bg-white/60 px-2 py-0.5 text-[11px] font-bold">{t("Exemplo", "Example")}</span>
          </div>
          <p className="m-0 text-sm leading-snug">{alerta}</p>
          <Link to={perguntar(t("O que fazer com a chuva forte no meu campo?", "What should I do about heavy rain on my field?"))}
            className="inline-flex h-11 items-center gap-2 self-start rounded-[14px] bg-tinta px-4 text-sm font-bold text-white no-underline">
            <Brilho size={16} /> {t("Perguntar à AgroIA", "Ask AgroIA")}
          </Link>
        </div>

        {/* Próximos 7 dias (exemplo) */}
        <div className={cx(cartao, "flex flex-col gap-3.5 lg:col-span-7")}>
          <div className="flex items-baseline justify-between gap-2">
            <h2 className="m-0 font-titulo text-lg font-extrabold">{t("Próximos 7 dias", "Next 7 days")}</h2>
            <span className="text-[13px] font-bold text-chuva">{t("91 mm de chuva", "91 mm of rain")}</span>
          </div>
          <div className="grid grid-cols-7 gap-1">
            {PREVISAO_EXEMPLO.map(([max, min, mm], i) => (
              <div key={i} className={cx("flex flex-col items-center gap-1.5 rounded-2xl py-2.5", mm >= 50 ? "bg-sol-claro" : "bg-creme")}>
                <span className="text-xs font-bold">{diaSemana(i, idioma)}</span>
                {mm >= 5 ? (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563A8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3" /><path d="M8 17v3M12 19v3M16 17v3" /></svg>
                ) : (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#C98500" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
                )}
                <span className="text-[13px] font-bold">{max}°</span>
                <span className="text-xs text-suave">{min}°</span>
                <span className="text-[11px] font-bold text-chuva">{mm} mm</span>
              </div>
            ))}
          </div>
          <span className="text-xs text-suave">{t("Exemplo. A previsão real para o seu ponto entra na próxima etapa.", "Example. The real forecast for your spot comes in the next step.")}</span>
        </div>

        {/* Umidade e NDVI (exemplo) */}
        <div className="grid grid-cols-2 gap-3 lg:col-span-5">
          <div className="flex flex-col gap-2.5 rounded-[24px] bg-white p-4 shadow-cartao">
            <div className="flex h-[38px] w-[38px] items-center justify-center rounded-[13px] bg-ceu text-chuva">
              <svg width="20" height="20" viewBox="0 0 24 24" {...icone}><path d="M12 22a7 7 0 0 0 7-7c0-4-7-13-7-13S5 11 5 15a7 7 0 0 0 7 7z" /></svg>
            </div>
            <span className="text-xs font-bold text-suave">{t("Umidade do solo", "Soil moisture")}</span>
            <span className="font-titulo text-lg leading-tight font-extrabold">{t("Mais seco que o normal", "Drier than normal")}</span>
            <div className="relative h-2.5 rounded-full bg-[linear-gradient(90deg,#F2B48A,var(--color-areia)_50%,#9CC5EE)]" aria-hidden="true">
              <div className="absolute -top-1 left-[28%] h-[18px] w-[18px] -translate-x-1/2 rounded-full border-[3px] border-white bg-tinta" />
            </div>
            <span className="text-[11px] text-suave">{t("NASA SMAP L4 · ~9 km · exemplo", "NASA SMAP L4 · ~9 km · example")}</span>
          </div>
          <div className="flex flex-col gap-2.5 rounded-[24px] bg-white p-4 shadow-cartao">
            <div className="flex h-[38px] w-[38px] items-center justify-center rounded-[13px] bg-campo-claro text-folha">
              <svg width="20" height="20" viewBox="0 0 24 24" {...icone}><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z" /><path d="M2 21c0-3 1.9-5.4 5.2-6.1" /></svg>
            </div>
            <span className="text-xs font-bold text-suave">{t("Saúde da lavoura", "Crop health")}</span>
            <span className="font-titulo text-lg leading-tight font-extrabold">{t("Campo sem cobertura", "Bare field")}</span>
            <span className="self-start rounded-full bg-areia px-2.5 py-1 text-xs font-bold text-terra-texto">NDVI {idioma === "en" ? "0.18" : "0,18"}</span>
            <span className="text-[11px] text-suave">{t("NASA MODIS · 250 m · exemplo", "NASA MODIS · 250 m · example")}</span>
          </div>
        </div>

        {/* O verde do campo no ano (do calendário) */}
        <div className={cx(cartao, "flex flex-col gap-3 lg:col-span-7")}>
          <div className="flex flex-col gap-0.5">
            <h2 className="m-0 font-titulo text-lg font-extrabold">{t("O verde do seu campo no ano", "How green your field is over the year")}</h2>
            <span className="text-[13px] text-suave">{t("Desenhado a partir do seu calendário", "Drawn from your own calendar")}</span>
          </div>
          {itens.length ? (
            <CurvaVerde vazios={vazios} />
          ) : (
            <span className="rounded-2xl bg-areia p-3 text-sm text-suave">{t("Conte o que você planta e quando para desenhar esta curva.", "Tell us what you grow and when to draw this curve.")}</span>
          )}
          <span className="text-[11px] text-suave">{t("Em breve: NASA MODIS NDVI (MOD13Q1) · 250 m · a cada 16 dias", "Coming soon: NASA MODIS NDVI (MOD13Q1) · 250 m · every 16 days")}</span>
        </div>

        {/* Estratégias (exemplo) */}
        <div className="flex flex-col gap-3.5 rounded-[28px] bg-folha p-5 text-white shadow-degrau lg:col-span-8">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-bold tracking-wider text-[#CFEBD9] uppercase">{t("Estratégias de rotação", "Rotation strategies")}</span>
            <span className="rounded-full bg-white/20 px-2 py-0.5 text-[11px] font-bold">{t("Exemplo", "Example")}</span>
          </div>
          <span className="font-titulo text-2xl leading-tight font-extrabold tracking-[-0.02em]">
            {primeira ? t(`3 caminhos para depois da colheita de ${primeira}`, `3 options for after the ${primeira} harvest`) : t("3 caminhos para depois da colheita", "3 options for after harvest")}
          </span>
          <div className="flex flex-col gap-2">
            {[
              { n: t("Campo vazio", "Bare field"), tag: t("Hoje", "Today"), bg: "#F5EEDF" },
              { n: t("Planta de cobertura", "Cover crop"), tag: t("Combina com você", "Good fit for you"), bg: "#FFC23D" },
              { n: t("Segunda cultura curta", "Short second crop"), tag: t("Mais renda", "More income"), bg: "#CFEBD9" },
            ].map((s) => (
              <div key={s.n} className="flex items-center justify-between gap-2 rounded-[14px] bg-white/15 px-3 py-2.5">
                <span className="text-sm font-bold">{primeira ? `${primeira} → ${s.n}` : s.n}</span>
                <span className="rounded-full px-2.5 py-1 text-xs font-bold text-tinta" style={{ background: s.bg }}>{s.tag}</span>
              </div>
            ))}
          </div>
          <span className="text-xs opacity-90">{t("A comparação de verdade, com dados da NASA, entra na próxima etapa.", "The real comparison, with NASA data, comes in the next step.")}</span>
          <Link to={perguntar(primeira ? t(`O que plantar depois da colheita de ${primeira}?`, `What should I plant after the ${primeira} harvest?`) : t("O que plantar depois da colheita?", "What should I plant after harvest?"))}
            className="inline-flex items-center gap-1.5 self-start text-[15px] font-bold text-white no-underline">
            {t("Perguntar à AgroIA", "Ask AgroIA")} <Brilho size={16} />
          </Link>
        </div>

        {/* Sua fazenda (real, do questionário) */}
        <div className={cx(cartao, "flex flex-col gap-3 lg:col-span-4")}>
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
          {t("A AgroIA apoia. Quem decide é você.", "AgroIA helps. You decide.")}{" "}
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

