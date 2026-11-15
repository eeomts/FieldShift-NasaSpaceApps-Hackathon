// Questionário: uma pergunta por tela, salvo (PUT /fazenda) a cada "Continuar". Telas e regras: dados.ts.
import { useEffect, useMemo, useRef, useState, type ComponentType } from "react";
import { useNavigate } from "react-router";
import { api, ErroApi } from "../api/client";
import { infoLocal } from "../api/local";
import { useSessao } from "../api/sessao";
import type { CulturaBase, EquipamentoBase, Fazenda, InfoLocal, Respostas } from "../api/tipos";
import { SeletorIdioma } from "../components/Casca";
import { Check, Seta, Voltar } from "../components/icones";
import { Logo } from "../components/Logo";
import { Aviso, BotaoContorno, BotaoPrimario, Carregando, cx, Selo } from "../components/ui";
import { useIdioma } from "../i18n";
import {
  PARTES, PASSO_RESUMO, telaVisivel, TELAS, TOTAL_PERGUNTAS, unidadePadrao, hemisferioDe, type TelaId, type Unidade,
} from "./dados";
import { Resumo } from "./Resumo";
import { TelaLocal } from "./TelaLocal";
import * as T from "./Telas";

const TELA: Record<TelaId, ComponentType<T.TelaProps>> = {
  q1_quem: T.TelaQuem,
  q2_area: T.TelaArea,
  q3_tecnico: T.TelaTecnico,
  q4_animais: T.TelaAnimais,
  q5_local: TelaLocal,
  q6_irrigacao: T.TelaIrrigacao,
  q7_terreno: T.TelaTerreno,
  q8_culturas: T.TelaCulturas,
  q9_meses_vazios: T.TelaMesesVazios,
  q10_pos_colheita: T.TelaPosColheita,
  q11_palha: T.TelaPalha,
  q12_analise: T.TelaAnalise,
  q13_textura: T.TelaTextura,
  q14_sinais: T.TelaSinais,
  q19_solo: T.TelaSolo,
  q20_partes_piores: T.TelaPartesPiores,
  q21_correcao: T.TelaCorrecao,
  q22_adubo: T.TelaAdubo,
  q23_chuva_mudou: T.TelaChuvaMudou,
  q24_perdas: T.TelaPerdas,
  q25_prioridades: T.TelaPrioridades,
  q26a_excluidas: T.TelaExcluidas,
  q26b_equipamentos: T.TelaEquipamentos,
};

export function Onboarding() {
  const navigate = useNavigate();
  const { recarregar } = useSessao();
  const { idioma, t, erro: textoErro } = useIdioma();
  const [r, setR] = useState<Respostas>({});
  const [passo, setPasso] = useState(0); // posição em TELAS; PASSO_RESUMO = resumo
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [culturas, setCulturas] = useState<CulturaBase[]>([]);
  const [equipamentos, setEquipamentos] = useState<EquipamentoBase[]>([]);
  const [info, setInfo] = useState<InfoLocal | null>(null);
  const [infoEstado, setInfoEstado] = useState<"ocioso" | "carregando" | "ok" | "erro">("ocioso");
  const [unidadeEscolhida, setUnidadeEscolhida] = useState<Unidade | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [falhaInicial, setFalhaInicial] = useState<string | null>(null);
  const [tentativa, setTentativa] = useState(0);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const rolagem = useRef<HTMLDivElement>(null);

  // Fazenda salva (retoma de onde parou).
  useEffect(() => {
    let vivo = true;
    setCarregando(true);
    setFalhaInicial(null);
    api<Fazenda>("/fazenda")
      .then((f) => {
        if (!vivo) return;
        setFazenda(f);
        setR(f.respostas);
        let p = f.onboarding_concluido ? 0 : Math.min(f.passo_atual, PASSO_RESUMO);
        while (p < PASSO_RESUMO && !telaVisivel(TELAS[p].id, f.respostas)) p++;
        setPasso(p);
      })
      .catch((e) => {
        if (!vivo) return;
        if (!(e instanceof ErroApi && e.status === 404)) setFalhaInicial(textoErro(e));
      })
      .finally(() => vivo && setCarregando(false));
    return () => {
      vivo = false;
    };
    // só na abertura (ou ao tentar de novo)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tentativa]);

  // Listas no idioma da tela.
  useEffect(() => {
    let vivo = true;
    api<CulturaBase[]>(`/culturas?idioma=${idioma}`).then((l) => vivo && setCulturas(l)).catch(() => {});
    api<EquipamentoBase[]>(`/equipamentos?idioma=${idioma}`).then((l) => vivo && setEquipamentos(l)).catch(() => {});
    return () => {
      vivo = false;
    };
  }, [idioma]);

  // País, zona climática, hemisfério e geada do ponto (GET /local/info), a cada ponto novo (~1 km).
  const lat = r.q5_local?.lat;
  const lon = r.q5_local?.lon;
  const chaveLocal = lat == null || lon == null ? null : `${lat.toFixed(2)},${lon.toFixed(2)},${idioma}`;
  useEffect(() => {
    if (chaveLocal === null || lat == null || lon == null) {
      setInfo(null);
      setInfoEstado("ocioso");
      return;
    }
    let vivo = true;
    setInfoEstado("carregando");
    infoLocal(Number(lat.toFixed(2)), Number(lon.toFixed(2)), idioma)
      .then((i) => {
        if (!vivo) return;
        setInfo(i);
        setInfoEstado("ok");
        setR((a) =>
          a.q5_local
            ? { ...a, q5_local: { ...a.q5_local, pais: i.pais_codigo ?? a.q5_local.pais ?? null, zona_climatica: i.zona_climatica ?? a.q5_local.zona_climatica ?? null, nome: a.q5_local.nome ?? i.lugar ?? null } }
            : a,
        );
      })
      .catch(() => vivo && setInfoEstado("erro"));
    return () => {
      vivo = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chaveLocal]);

  useEffect(() => {
    rolagem.current?.scrollTo({ top: 0 });
  }, [passo]);

  const set = (p: T.Atualizar) => setR((a) => ({ ...a, ...(typeof p === "function" ? p(a) : p) }));

  const emResumo = passo >= PASSO_RESUMO;
  const tela = emResumo ? null : TELAS[passo];
  const parteAtual = tela ? tela.parte : PARTES.length;

  const proximo = useMemo(() => {
    let p = passo + 1;
    while (p < PASSO_RESUMO && !telaVisivel(TELAS[p].id, r)) p++;
    return p;
  }, [passo, r]);
  const anterior = useMemo(() => {
    let p = passo - 1;
    while (p >= 0 && !telaVisivel(TELAS[p].id, r)) p--;
    return p;
  }, [passo, r]);

  async function salvar(destino: number, concluir = false) {
    setSalvando(true);
    setErro(null);
    try {
      const f = await api<Fazenda>("/fazenda", { method: "PUT", body: { respostas: r, passo_atual: destino, concluir } });
      setFazenda(f);
      if (concluir) {
        await recarregar();
        navigate("/dashboard", { replace: true });
      } else {
        setPasso(destino);
      }
    } catch (e) {
      setErro(textoErro(e));
    } finally {
      setSalvando(false);
    }
  }

  if (carregando) return <div className="flex min-h-dvh flex-col"><Carregando texto={t("Carregando…", "Loading…")} /></div>;
  if (falhaInicial)
    return (
      <div className="mx-auto flex min-h-dvh max-w-[480px] flex-col justify-center gap-4 px-6">
        <Aviso>{falhaInicial}</Aviso>
        <BotaoContorno type="button" onClick={() => setTentativa((n) => n + 1)}>{t("Tentar de novo", "Try again")}</BotaoContorno>
      </div>
    );

  // Barras: uma por parte; a parte atual enche conforme as perguntas visíveis dela.
  const visiveisDaParte = TELAS.filter((x) => x.parte === parteAtual && telaVisivel(x.id, r));
  const posNaParte = tela ? visiveisDaParte.findIndex((x) => x.id === tela.id) + 1 : 0;
  const preenchimento = (parte: number) => (parte < parteAtual ? 100 : parte === parteAtual && tela ? Math.max(8, (posNaParte / Math.max(1, visiveisDaParte.length)) * 100) : emResumo ? 100 : 0);

  const local = r.q5_local ?? null;
  const ctx: T.ContextoTelas = {
    culturas,
    equipamentos,
    info,
    infoEstado,
    zona: local?.zona_climatica ?? info?.zona_climatica ?? null,
    pais: local?.pais ?? info?.pais_codigo ?? null,
    hemisferio: hemisferioDe(local, info),
    unidade: unidadeEscolhida ?? unidadePadrao(local?.pais ?? info?.pais_codigo),
    setUnidade: setUnidadeEscolhida,
  };

  const Atual = tela ? TELA[tela.id] : null;
  const precisaLocal = tela?.id === "q5_local" && !r.q5_local;
  const ultima = !emResumo && proximo >= PASSO_RESUMO;
  const nomeParte = (i: number) => PARTES[i][idioma];

  return (
    <main className="flex h-dvh flex-col lg:flex-row">
      {/* Computador: barra lateral com as partes do questionário */}
      <aside className="hidden w-[300px] shrink-0 flex-col gap-8 border-r-2 border-linha bg-white/60 px-8 py-9 lg:flex xl:w-[340px]">
        <div className="flex items-center justify-between gap-3">
          <Logo />
          <SeletorIdioma />
        </div>
        <div className="flex flex-col gap-1.5">
          <span className="font-titulo text-[22px] leading-tight font-extrabold tracking-[-0.02em]">{t("Conte sobre a sua fazenda", "Tell us about your farm")}</span>
          <span className="text-sm text-suave">{t("Leva uns 5 minutos. Dá para parar e continuar depois.", "It takes about 5 minutes. You can stop and pick up later.")}</span>
        </div>
        <ol className="m-0 flex list-none flex-col gap-1.5 p-0" aria-label={t("Partes do questionário", "Questionnaire parts")}>
          {[...PARTES.map((p) => p[idioma]), t("Resumo", "Summary")].map((nome, i) => {
            const feito = i + 1 < parteAtual;
            const atual = i + 1 === parteAtual;
            return (
              <li key={nome} aria-current={atual ? "step" : undefined}
                className={cx("flex items-center gap-3 rounded-2xl px-3 py-2.5 text-[15px] font-bold transition-colors", atual ? "bg-folha text-white shadow-degrau" : feito ? "text-tinta" : "text-suave/70")}>
                <span className={cx("flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-sm", atual ? "bg-sol text-tinta" : feito ? "bg-campo-claro text-folha" : "bg-areia text-terra-texto")}>
                  {feito ? <Check size={16} /> : i + 1}
                </span>
                {nome}
              </li>
            );
          })}
        </ol>
        <span className="mt-auto self-start rounded-full bg-sol-claro px-3 py-1.5 text-xs font-bold text-sol-texto">{t("A AgroAI apoia. Quem decide é você.", "AgroAI helps. You decide.")}</span>
      </aside>

      <div className="flex min-h-0 flex-1 flex-col">
        <header className="mx-auto flex w-full max-w-[480px] flex-col gap-3.5 px-6 pt-5 pb-2 lg:max-w-[760px] lg:px-10 lg:pt-9">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[13px] leading-tight font-bold text-suave">
              {tela ? t(`Parte ${parteAtual} de ${PARTES.length} · ${nomeParte(parteAtual - 1)}`, `Part ${parteAtual} of ${PARTES.length} · ${nomeParte(parteAtual - 1)}`) : t("Pronto!", "All set!")}
            </span>
            <div className="flex shrink-0 items-center gap-2">
              {tela ? <Selo>{tela.numero} / {TOTAL_PERGUNTAS}</Selo> : <Selo>{t("Tudo respondido", "All answered")}</Selo>}
              <SeletorIdioma className="lg:hidden" />
            </div>
          </div>
          <div className="grid grid-cols-6 gap-1.5" role="progressbar" aria-valuemin={0} aria-valuemax={PARTES.length} aria-valuenow={Math.min(parteAtual, PARTES.length)}
            aria-label={t("Progresso do questionário", "Questionnaire progress")}>
            {PARTES.map((_, i) => (
              <div key={i} className="h-2 overflow-hidden rounded-full bg-borda">
                <div className="h-full rounded-full bg-folha transition-all" style={{ width: `${preenchimento(i + 1)}%` }} />
              </div>
            ))}
          </div>
        </header>

        <div ref={rolagem} className="flex-1 overflow-y-auto">
          <div className="mx-auto flex w-full max-w-[480px] flex-col gap-4 px-6 pt-4 pb-6 lg:max-w-[760px] lg:px-10 lg:pt-8 lg:pb-10">
            {Atual ? <Atual key={tela!.id} r={r} set={set} ctx={ctx} /> : <Resumo fazenda={fazenda} culturas={culturas} />}
            {erro && <Aviso>{erro}</Aviso>}
          </div>
        </div>

        <footer className="border-t-2 border-linha bg-creme">
          <div className="mx-auto flex w-full max-w-[480px] gap-2.5 px-6 pt-3.5 pb-7 lg:max-w-[760px] lg:px-10 lg:py-5">
            {(emResumo || anterior >= 0) && (
              <button type="button" aria-label={t("Voltar", "Back")} disabled={salvando}
                onClick={() => setPasso(emResumo ? (anterior >= 0 ? anterior : 0) : anterior)}
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[20px] border-2 border-borda bg-white">
                <Voltar />
              </button>
            )}
            {!emResumo ? (
              <BotaoPrimario className="flex-1 lg:ml-auto lg:max-w-[320px]" disabled={salvando || precisaLocal} onClick={() => salvar(proximo)}>
                {salvando ? t("Salvando…", "Saving…") : precisaLocal ? t("Marque o campo no mapa", "Mark your farm on the map") : ultima ? t("Ver meu resumo", "See my summary") : t("Continuar", "Continue")}
                {!salvando && !precisaLocal && <Seta />}
              </BotaoPrimario>
            ) : (
              <BotaoPrimario className="flex-1 lg:ml-auto lg:max-w-[320px]" disabled={salvando} onClick={() => salvar(PASSO_RESUMO, true)}>
                {salvando ? t("Salvando…", "Saving…") : t("Ver minha fazenda", "See my farm")} {!salvando && <Seta />}
              </BotaoPrimario>
            )}
          </div>
        </footer>
      </div>
    </main>
  );
}
