import { useEffect, useRef, useState, type ComponentType } from "react";
import { useNavigate } from "react-router";
import { api, ErroApi } from "../api/client";
import { useSessao } from "../api/sessao";
import type { CulturaBase, EquipamentoBase, Fazenda, Respostas } from "../api/tipos";
import { Check, Seta, Voltar } from "../components/icones";
import { Logo } from "../components/Logo";
import { Aviso, BotaoPrimario, Cartao, cx, Selo, Texto, Titulo } from "../components/ui";
import { Calendario } from "./Calendario";
import {
  PassoCampo, PassoClima, PassoLocal, PassoPlanta, PassoPosColheita, PassoPrioridades, PassoQuem,
  PassoRestricoes, PassoSolo1, PassoSolo2, type PassoProps,
} from "./Passos";

const PASSOS: { bloco: string; C: ComponentType<PassoProps> }[] = [
  { bloco: "Quem é você", C: PassoQuem },
  { bloco: "O campo", C: PassoLocal },
  { bloco: "O campo", C: PassoCampo },
  { bloco: "O que você planta", C: PassoPlanta },
  { bloco: "O que você planta", C: PassoPosColheita },
  { bloco: "Seu solo", C: PassoSolo1 },
  { bloco: "Seu solo", C: PassoSolo2 },
  { bloco: "O clima", C: PassoClima },
  { bloco: "Prioridades", C: PassoPrioridades },
  { bloco: "Prioridades", C: PassoRestricoes },
];
const RESUMO = PASSOS.length;
const BLOCOS = [...new Set(PASSOS.map((p) => p.bloco))];

const PERFIS: Record<string, { nome: string; texto: string }> = {
  A: { nome: "Experiência", texto: "Vamos usar os dados globais e as suas respostas. Alguns testes simples deixam a análise mais firme." },
  B: { nome: "Observador", texto: "Vamos combinar o que você observa com os dados globais de solo e clima." },
  C: { nome: "Com laudo", texto: "Os valores do seu laudo vão ter prioridade sobre os modelos. É o nível de confiança mais alto." },
  D: { nome: "Técnico", texto: "Mostramos mais detalhe técnico na tela, e o fluxo é o mesmo." },
};

export function Onboarding() {
  const navigate = useNavigate();
  const { recarregar } = useSessao();
  const [r, setR] = useState<Respostas>({});
  const [passo, setPasso] = useState(0);
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [culturas, setCulturas] = useState<CulturaBase[]>([]);
  const [equipamentos, setEquipamentos] = useState<EquipamentoBase[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const rolagem = useRef<HTMLDivElement>(null);

  useEffect(() => {
    Promise.all([
      api<Fazenda>("/fazenda").then((f) => {
        setFazenda(f);
        setR(f.respostas);
        setPasso(f.onboarding_concluido ? 0 : Math.min(f.passo_atual, RESUMO));
      }).catch((e) => {
        if (!(e instanceof ErroApi && e.status === 404)) setErro(e.message);
      }),
      api<CulturaBase[]>("/culturas").then(setCulturas),
      api<EquipamentoBase[]>("/equipamentos").then(setEquipamentos),
    ])
      .catch((e) => setErro(e instanceof ErroApi ? e.message : "Não deu para carregar. Recarregue a página."))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    rolagem.current?.scrollTo({ top: 0 });
  }, [passo]);

  const set = (parcial: Partial<Respostas>) => setR((atual) => ({ ...atual, ...parcial }));

  async function salvar(proximo: number, concluir = false) {
    setSalvando(true);
    setErro(null);
    try {
      const f = await api<Fazenda>("/fazenda", { method: "PUT", body: { respostas: r, passo_atual: proximo, concluir } });
      setFazenda(f);
      if (concluir) {
        await recarregar();
        navigate("/dashboard", { replace: true });
      } else {
        setPasso(proximo);
      }
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não deu para salvar. Tente de novo.");
    } finally {
      setSalvando(false);
    }
  }

  if (carregando) return <div className="flex min-h-dvh items-center justify-center text-suave">Carregando…</div>;

  const Atual = passo < RESUMO ? PASSOS[passo].C : null;
  const blocoAtual = passo < RESUMO ? BLOCOS.indexOf(PASSOS[passo].bloco) : BLOCOS.length;
  const precisaLocal = passo === 1 && !r.q5_local;

  return (
    <main className="flex h-dvh flex-col lg:flex-row">
      {/* Computador: barra lateral com as partes do questionário */}
      <aside className="hidden w-[300px] shrink-0 flex-col gap-8 border-r-2 border-linha bg-white/60 px-8 py-9 lg:flex xl:w-[340px]">
        <Logo />
        <div className="flex flex-col gap-1.5">
          <span className="font-titulo text-[22px] leading-tight font-extrabold tracking-[-0.02em]">Conte sobre o seu campo</span>
          <span className="text-sm text-suave">Leva uns 5 minutos. Dá para parar e continuar depois.</span>
        </div>
        <ol className="m-0 flex list-none flex-col gap-1.5 p-0" aria-label="Partes do questionário">
          {[...BLOCOS, "Resumo"].map((b, i) => {
            const feito = i < blocoAtual;
            const atual = i === blocoAtual;
            return (
              <li
                key={b}
                aria-current={atual ? "step" : undefined}
                className={cx(
                  "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-[15px] font-bold transition-colors",
                  atual ? "bg-folha text-white shadow-degrau" : feito ? "text-tinta" : "text-suave/70",
                )}
              >
                <span
                  className={cx(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-sm",
                    atual ? "bg-sol text-tinta" : feito ? "bg-folha-clara text-folha" : "bg-terra text-terra-texto",
                  )}
                >
                  {feito ? <Check size={16} /> : i + 1}
                </span>
                {b}
              </li>
            );
          })}
        </ol>
        <span className="mt-auto self-start rounded-full bg-sol-claro px-3 py-1.5 text-xs font-bold text-sol-texto">
          A AgroIA apoia. Quem decide é você.
        </span>
      </aside>

      <div className="flex min-h-0 flex-1 flex-col">
        {/* Celular: barra de progresso no topo */}
        <header className="mx-auto flex w-full max-w-[480px] flex-col gap-3.5 px-6 pt-6 pb-2 lg:hidden">
          <div className="flex items-center justify-between">
            <span className="text-[13px] font-bold text-suave">
              {passo < RESUMO ? `Parte ${blocoAtual + 1} de ${BLOCOS.length} · ${PASSOS[passo].bloco}` : "Tudo pronto"}
            </span>
            <Selo>Leva uns 5 minutos</Selo>
          </div>
          <div className="grid gap-1.5" style={{ gridTemplateColumns: `repeat(${BLOCOS.length}, minmax(0, 1fr))` }}
            role="progressbar" aria-valuemin={0} aria-valuemax={BLOCOS.length} aria-valuenow={blocoAtual}>
            {BLOCOS.map((b, i) => (
              <div key={b} className={cx("h-2 rounded-full transition-colors", i <= blocoAtual ? "bg-folha" : "bg-borda")} />
            ))}
          </div>
        </header>

        <div ref={rolagem} className="flex-1 overflow-y-auto">
          <div className="mx-auto flex w-full max-w-[480px] flex-col gap-4 px-6 pt-3 pb-4 lg:max-w-[720px] lg:px-10 lg:pt-12 lg:pb-10">
            {passo < RESUMO && (
              <span className="hidden text-[13px] font-bold tracking-wide text-folha uppercase lg:block">
                Parte {blocoAtual + 1} de {BLOCOS.length} · {PASSOS[passo].bloco}
              </span>
            )}
            {Atual ? (
              <Atual r={r} set={set} culturas={culturas} equipamentos={equipamentos} />
            ) : (
              <Resumo fazenda={fazenda} culturas={culturas} />
            )}
            {erro && <Aviso>{erro}</Aviso>}
          </div>
        </div>

        <footer className="border-t-2 border-linha bg-creme">
          <div className="mx-auto flex w-full max-w-[480px] gap-2.5 px-6 pt-3.5 pb-7 lg:max-w-[720px] lg:px-10 lg:py-5">
            {passo > 0 && (
              <button type="button" aria-label="Voltar" onClick={() => setPasso(passo - 1)} disabled={salvando}
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[20px] border-2 border-borda bg-white">
                <Voltar />
              </button>
            )}
            {passo < RESUMO ? (
              <BotaoPrimario className="flex-1 lg:ml-auto lg:max-w-[320px]" disabled={salvando || precisaLocal} onClick={() => salvar(passo + 1)}>
                {salvando ? "Salvando…" : precisaLocal ? "Marque o campo no mapa" : "Continuar"}
              </BotaoPrimario>
            ) : (
              <BotaoPrimario className="flex-1 lg:ml-auto lg:max-w-[320px]" disabled={salvando} onClick={() => salvar(RESUMO, true)}>
                {salvando ? "Salvando…" : "Ver minha fazenda"} {!salvando && <Seta />}
              </BotaoPrimario>
            )}
          </div>
        </footer>
      </div>
    </main>
  );
}

function Resumo({ fazenda, culturas }: { fazenda: Fazenda | null; culturas: CulturaBase[] }) {
  if (!fazenda) return null;
  const perfil = fazenda.perfil ? PERFIS[fazenda.perfil] : null;
  const itens = fazenda.respostas.q8_culturas ?? [];
  const nomes = Object.fromEntries(culturas.map((c) => [c.id, c.nome]));
  const solo = fazenda.retrato_solo;
  return (
    <div className="flex flex-col gap-4">
      <Titulo>Pronto! Veja o que entendemos.</Titulo>
      <Texto>Confira antes de seguir. Dá para voltar e mudar qualquer resposta.</Texto>

      {perfil && (
        <Cartao className="bg-folha text-white shadow-degrau">
          <span className="text-xs font-bold opacity-85">Seu perfil</span>
          <span className="font-titulo text-2xl font-extrabold">{fazenda.perfil} · {perfil.nome}</span>
          <span className="text-sm leading-snug opacity-90">{perfil.texto}</span>
        </Cartao>
      )}

      <div className="grid gap-4 lg:grid-cols-2 lg:items-start">
      {itens.length > 0 && (
        <Cartao>
          <span className="text-[13px] font-bold">Seu ano no campo</span>
          <Calendario itens={itens} vazios={fazenda.meses_sem_cobertura} nomes={nomes} />
          {fazenda.meses_sem_cobertura.length > 0 && (
            <span className="rounded-xl bg-sol-claro px-3 py-2 text-[13px] text-sol-texto">
              {fazenda.meses_sem_cobertura.length} meses com a terra descoberta. Vamos olhar isso com os dados.
            </span>
          )}
        </Cartao>
      )}

      {((solo.indicadores?.length ?? 0) > 0 || solo.figuras) && (
        <Cartao>
          <span className="text-[13px] font-bold">Retrato do seu solo</span>
          <Selo tom="ceu">Informado por você · vamos cruzar com SoilGrids e NASA</Selo>
          {solo.figuras && <span className="text-[15px] font-bold">{solo.figuras.leitura}</span>}
          <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
            {solo.indicadores?.map((i) => (
              <li key={i.atributo} className="text-sm text-suave">• {i.valor}</li>
            ))}
          </ul>
        </Cartao>
      )}

      </div>

      {fazenda.proximos_passos.length > 0 && (
        <div className="grid gap-2.5 lg:grid-cols-3">
          <span className="text-[13px] font-bold lg:col-span-3">Para deixar a análise mais firme</span>
          {fazenda.proximos_passos.map((p) => (
            <Cartao key={p.id} className="gap-1">
              <span className="font-bold">{p.titulo}</span>
              <span className="text-sm leading-snug text-suave">{p.texto}</span>
            </Cartao>
          ))}
        </div>
      )}

      <span className="self-center rounded-full bg-sol-claro px-3 py-1.5 text-xs font-bold text-sol-texto">
        A AgroIA apoia. Quem decide é você.
      </span>
    </div>
  );
}
