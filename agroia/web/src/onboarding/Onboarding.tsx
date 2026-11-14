import { useEffect, useRef, useState, type ComponentType } from "react";
import { useNavigate } from "react-router";
import { api, ErroApi } from "../api/client";
import { useSessao } from "../api/sessao";
import type { CulturaBase, EquipamentoBase, Fazenda, Respostas } from "../api/tipos";
import { Seta, Voltar } from "../components/icones";
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
    <main className="mx-auto flex h-dvh max-w-[480px] flex-col">
      <header className="flex flex-col gap-3.5 px-6 pt-6 pb-2">
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

      <div ref={rolagem} className="flex flex-1 flex-col gap-4 overflow-y-auto px-6 pt-3 pb-4">
        {Atual ? (
          <Atual r={r} set={set} culturas={culturas} equipamentos={equipamentos} />
        ) : (
          <Resumo fazenda={fazenda} culturas={culturas} />
        )}
        {erro && <Aviso>{erro}</Aviso>}
      </div>

      <footer className="flex gap-2.5 border-t-2 border-linha bg-creme px-6 pt-3.5 pb-7">
        {passo > 0 && (
          <button type="button" aria-label="Voltar" onClick={() => setPasso(passo - 1)} disabled={salvando}
            className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[20px] border-2 border-borda bg-white">
            <Voltar />
          </button>
        )}
        {passo < RESUMO ? (
          <BotaoPrimario className="flex-1" disabled={salvando || precisaLocal} onClick={() => salvar(passo + 1)}>
            {salvando ? "Salvando…" : precisaLocal ? "Marque o campo no mapa" : "Continuar"}
          </BotaoPrimario>
        ) : (
          <BotaoPrimario className="flex-1" disabled={salvando} onClick={() => salvar(RESUMO, true)}>
            {salvando ? "Salvando…" : "Ver minha fazenda"} {!salvando && <Seta />}
          </BotaoPrimario>
        )}
      </footer>
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

      {fazenda.proximos_passos.length > 0 && (
        <div className="flex flex-col gap-2.5">
          <span className="text-[13px] font-bold">Para deixar a análise mais firme</span>
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
