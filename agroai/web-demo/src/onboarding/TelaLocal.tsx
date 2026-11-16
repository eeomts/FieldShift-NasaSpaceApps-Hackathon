// Pergunta 5: onde fica a propriedade. Busca por nome, mapa, GPS e cartão com País / Zona climática / Hemisfério.
import { useEffect, useRef, useState } from "react";
import { buscarLugar } from "../api/local";
import type { Local, LugarBusca } from "../api/tipos";
import { Lupa, Mira, Pino } from "../components/icones";
import { Aviso, Bolinhas, BotaoContorno, Selo, Texto, Titulo } from "../components/ui";
import { useIdioma } from "../i18n";
import { descricaoZona, TITULOS } from "./dados";
import { Mapa, type Ponto } from "./Mapa";
import type { TelaProps } from "./Telas";

const arred = (n: number) => Math.round(n * 1e5) / 1e5;
const celula = (n: number) => n.toFixed(2);
const fmt = (n: number, idioma: string) => (idioma === "en" ? n.toFixed(4) : n.toFixed(4).replace(".", ",")) + "°";

export function TelaLocal({ r, set, ctx }: TelaProps) {
  const { idioma, t, erro: textoErro } = useIdioma();
  const local = r.q5_local ?? null;
  const [consulta, setConsulta] = useState("");
  const [resultados, setResultados] = useState<LugarBusca[] | null>(null);
  const [buscando, setBuscando] = useState(false);
  const [erroBusca, setErroBusca] = useState<string | null>(null);
  const [voarPara, setVoarPara] = useState<(Ponto & { k: number }) | null>(null);
  const [gps, setGps] = useState<"parado" | "buscando" | "erro">("parado");
  const pedido = useRef(0);

  // Busca com pausa de meio segundo depois de digitar.
  useEffect(() => {
    const q = consulta.trim();
    if (q.length < 2) {
      setResultados(null);
      setBuscando(false);
      return;
    }
    const n = ++pedido.current;
    setBuscando(true);
    const espera = setTimeout(async () => {
      try {
        const lista = await buscarLugar(q, idioma);
        if (n !== pedido.current) return;
        setResultados(lista);
        setErroBusca(null);
      } catch (e) {
        if (n !== pedido.current) return;
        setResultados(null);
        setErroBusca(textoErro(e));
      } finally {
        if (n === pedido.current) setBuscando(false);
      }
    }, 500);
    return () => clearTimeout(espera);
  }, [consulta, idioma]);

  function marcar(p: Ponto, nome: string | null, pais: string | null, manter: boolean) {
    set((a) => {
      const antes = a.q5_local;
      const mesmaCelula = !!antes && celula(antes.lat) === celula(p.lat) && celula(antes.lon) === celula(p.lon);
      const novo: Local = {
        lat: arred(p.lat),
        lon: arred(p.lon),
        nome: nome ?? (manter ? antes?.nome ?? null : null),
        pais: pais ?? (mesmaCelula ? antes?.pais ?? null : null),
        zona_climatica: mesmaCelula ? antes?.zona_climatica ?? null : null,
      };
      return { q5_local: novo };
    });
  }

  function escolherResultado(l: LugarBusca) {
    marcar({ lat: l.lat, lon: l.lon }, l.nome, l.pais_codigo, false);
    setVoarPara({ lat: l.lat, lon: l.lon, k: Date.now() });
    setConsulta("");
    setResultados(null);
  }

  function usarGps() {
    if (!navigator.geolocation) return setGps("erro");
    setGps("buscando");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const p = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        marcar(p, null, null, false);
        setVoarPara({ ...p, k: Date.now() });
        setGps("parado");
      },
      () => setGps("erro"),
      { enableHighAccuracy: true, timeout: 15000 },
    );
  }

  const info = ctx.info;
  const titulo = info?.lugar ? [info.lugar, info.pais].filter(Boolean).join(", ") : local?.nome ?? t("Ponto marcado", "Spot marked");
  const hemisferio = ctx.hemisferio === "S" ? t("Sul", "South") : t("Norte", "North");
  const carregando = ctx.infoEstado === "carregando";
  const zonaDescr = descricaoZona(ctx.zona, idioma);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Selo>{t("Única pergunta obrigatória", "The only required question")}</Selo>
        <Titulo>{TITULOS.q5_local[idioma]}</Titulo>
        <Texto>{t("Procure o nome da cidade ou da região, ou toque no mapa. É com esse ponto que buscamos os dados da NASA.", "Search for your town or area, or tap the map. We use that spot to pull NASA data.")}</Texto>
      </div>

      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] lg:grid-rows-[repeat(5,auto)] lg:content-start lg:gap-x-6">
          <div className="relative lg:col-start-1">
            <label className="flex h-14 items-center gap-2.5 rounded-[20px] border-2 border-borda bg-white px-4 focus-within:border-folha">
              <Lupa className="shrink-0 text-suave" />
              <input
                type="search"
                value={consulta}
                onChange={(e) => setConsulta(e.target.value)}
                aria-label={t("Procurar cidade ou região", "Search town or area")}
                placeholder={t("Ex.: Sorriso, Mato Grosso", "E.g.: Ames, Iowa")}
                className="min-w-0 flex-1 bg-transparent text-[15px] outline-none placeholder:text-suave/60"
              />
              {buscando && <Bolinhas />}
            </label>
            {resultados && resultados.length > 0 && (
              <ul className="m-0 mt-2 flex list-none flex-col overflow-hidden rounded-[18px] border-2 border-borda bg-white p-0 shadow-cartao">
                {resultados.map((l, i) => (
                  <li key={`${l.lat},${l.lon},${i}`} className="border-b border-linha last:border-b-0">
                    <button type="button" onClick={() => escolherResultado(l)} className="flex min-h-12 w-full flex-col items-start px-4 py-2.5 text-left hover:bg-campo-claro">
                      <span className="text-[15px] font-bold">{l.nome}</span>
                      {l.pais && <span className="text-xs text-suave">{l.pais}</span>}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {resultados && resultados.length === 0 && !buscando && (
              <p role="status" className="m-0 mt-2 text-[13px] font-bold text-suave">
                {t("Nenhum lugar encontrado. Toque no mapa ou use o GPS.", "No place found. Tap the map or use GPS.")}
              </p>
            )}
            {erroBusca && <div className="mt-2"><Aviso>{erroBusca}</Aviso></div>}
          </div>

          <BotaoContorno type="button" onClick={usarGps} disabled={gps === "buscando"} className="h-14 rounded-[20px] lg:col-start-1">
            <Mira size={18} /> {gps === "buscando" ? t("Procurando…", "Looking…") : t("Usar meu GPS", "Use my GPS")}
          </BotaoContorno>
          {gps === "erro" && <span className="text-[13px] font-bold text-perigo lg:col-start-1">{t("Não conseguimos o GPS. Toque no mapa.", "We couldn't get your GPS. Tap the map.")}</span>}

          <div className="lg:col-start-2 lg:row-span-5 lg:row-start-1">
            <Mapa valor={local} voarPara={voarPara} onChange={(p) => marcar(p, null, null, true)} />
          </div>

          {local ? (
            <div className="flex flex-col gap-3 rounded-[22px] bg-white p-4 shadow-cartao lg:col-start-1">
              <div className="flex items-start gap-3">
                <Pino className="mt-0.5 shrink-0 text-folha" />
                <div className="flex min-w-0 flex-col">
                  <span className="text-[15px] leading-snug font-bold">{titulo}</span>
                  <span className="text-[13px] text-suave">{fmt(local.lat, idioma)} · {fmt(local.lon, idioma)}</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <Peca rotulo={t("País", "Country")} valor={info?.pais ?? local.pais ?? "—"} />
                <Peca rotulo={t("Zona climática", "Climate zone")} valor={ctx.zona ?? "—"} extra={ctx.zona ? "(Köppen)" : undefined} />
                <Peca rotulo={t("Hemisfério", "Hemisphere")} valor={hemisferio} />
              </div>
              {carregando && (
                <div role="status" className="flex items-center gap-2 text-[13px] font-bold text-folha-escura">
                  <Bolinhas /> {t("Buscando o clima do ponto…", "Looking up the climate here…")}
                </div>
              )}
              {ctx.infoEstado === "erro" && (
                <span className="text-[13px] font-bold text-perigo">{t("Não deu para buscar o clima deste ponto agora. Pode continuar.", "We couldn't look up the climate here right now. You can continue.")}</span>
              )}
              {zonaDescr && !carregando && (
                <span className="text-[13px] leading-snug text-suave">{zonaDescr} {t("Usamos isso para adaptar as próximas perguntas.", "We use this to adapt the next questions.")}</span>
              )}
              <span className="text-[11px] text-suave">
                {t("Fontes: OpenStreetMap (lugar e país) · NASA POWER (zona climática, calculada com o clima mensal; é uma aproximação do Köppen-Geiger).",
                  "Sources: OpenStreetMap (place and country) · NASA POWER (climate zone, calculated from monthly climate; an approximation of Köppen-Geiger).")}
              </span>
            </div>
          ) : (
            <span className="text-[13px] font-bold text-suave lg:col-start-1">{t("Toque no mapa no meio do seu campo, ou use a busca ou o GPS.", "Tap the map in the middle of your field, or use search or GPS.")}</span>
          )}

          {local && (
            <label className="flex flex-col gap-1.5 text-[13px] font-bold lg:col-start-1">
              {t("Nome do lugar (opcional)", "Place name (optional)")}
              <input
                maxLength={200}
                value={local.nome ?? ""}
                onChange={(e) => set((a) => (a.q5_local ? { q5_local: { ...a.q5_local, nome: e.target.value || null } } : {}))}
                placeholder={t("Ex.: Sítio Boa Vista", "E.g.: Green Hill Farm")}
                className="h-12 rounded-2xl border-2 border-borda bg-white px-4 text-[15px] font-normal focus:border-folha focus:outline-none"
              />
            </label>
          )}
      </div>
    </div>
  );
}

function Peca({ rotulo, valor, extra }: { rotulo: string; valor: string; extra?: string }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5 rounded-2xl bg-campo-claro p-2.5">
      <span className="text-[11px] font-bold text-folha-escura">{rotulo}</span>
      <span className="text-[15px] leading-tight font-bold break-words">{valor}</span>
      {extra && <span className="text-[11px] font-bold text-suave">{extra}</span>}
    </div>
  );
}
