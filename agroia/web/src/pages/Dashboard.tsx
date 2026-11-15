import { useEffect, useState } from "react";
import { Link } from "react-router";
import { api } from "../api/client";
import { useSessao } from "../api/sessao";
import type { CulturaBase, Fazenda } from "../api/tipos";
import { Logo } from "../components/Logo";
import { Calendario } from "../onboarding/Calendario";
import { Brilho, Painel, Sair } from "../components/icones";
import { Cartao, cx, Selo, Texto, Titulo } from "../components/ui";

function Abas({ className }: { className?: string }) {
  return (
    <nav aria-label="Abas" className={cx("grid grid-cols-2 gap-2", className)}>
      <span aria-current="page" className="flex h-[52px] items-center justify-center gap-2 rounded-[18px] bg-tinta px-5 text-[15px] font-bold text-white lg:h-12">
        <Painel /> Dashboard
      </span>
      <span className="flex h-[52px] items-center justify-center gap-2 rounded-[18px] px-5 text-[15px] font-bold text-suave/60 lg:h-12" title="Na próxima parte">
        <Brilho /> AgroIA
      </span>
    </nav>
  );
}

/** Provisório: o Dashboard de verdade (dados NASA) é a parte 3. */
export function Dashboard() {
  const { usuario, sair } = useSessao();
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [nomes, setNomes] = useState<Record<string, string>>({});

  useEffect(() => {
    api<Fazenda>("/fazenda").then(setFazenda).catch(() => setFazenda(null));
    api<CulturaBase[]>("/culturas").then((cs) => setNomes(Object.fromEntries(cs.map((c) => [c.id, c.nome])))).catch(() => {});
  }, []);

  const temCalendario = !!fazenda?.respostas.q8_culturas?.length;

  return (
    <div className="flex min-h-dvh flex-col">
      {/* Computador: barra no topo com logo, abas e sair */}
      <header className="sticky top-0 z-10 hidden border-b-2 border-linha bg-white/90 backdrop-blur lg:block">
        <div className="mx-auto flex max-w-[1120px] items-center justify-between gap-6 px-10 py-3.5">
          <Logo />
          <Abas className="w-[360px]" />
          <button type="button" onClick={sair} className="flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-bold text-suave hover:bg-terra">
            <Sair size={18} /> Sair
          </button>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-[480px] flex-1 flex-col gap-4 px-5 pt-6 pb-6 lg:max-w-[1120px] lg:gap-6 lg:px-10 lg:pt-10">
        <div className="flex items-center justify-between">
          <Selo tom="folha">Perfil {fazenda?.perfil ?? "…"}</Selo>
          <button type="button" onClick={sair} className="flex items-center gap-1.5 rounded-xl px-2 py-1 text-sm font-bold text-suave lg:hidden">
            <Sair size={18} /> Sair
          </button>
        </div>
        <Titulo>Olá, {usuario?.nome.split(" ")[0]}!</Titulo>

        <div className={cx("grid gap-4 lg:gap-6", temCalendario && "lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] lg:items-start")}>
          <div className="flex flex-col gap-4">
            <Cartao className="bg-sol-claro lg:p-6">
              <span className="font-bold lg:text-lg">Preparando os dados da sua fazenda…</span>
              <Texto>
                Seu questionário está salvo. A busca dos dados da NASA para o seu ponto entra na próxima parte do projeto.
              </Texto>
            </Cartao>
            <Link to="/chat" className="flex h-14 items-center justify-center gap-2 rounded-[20px] bg-folha px-5 text-[17px] font-bold text-white shadow-degrau">
              <Brilho /> Conversar com o assistente
            </Link>
            <Link to="/onboarding" className="text-center text-sm font-bold text-folha lg:text-left">Revisar minhas respostas</Link>
          </div>
          {temCalendario && fazenda && (
            <Cartao className="lg:p-6">
              <span className="text-[13px] font-bold">Seu ano no campo</span>
              <Calendario itens={fazenda.respostas.q8_culturas!} vazios={fazenda.meses_sem_cobertura} nomes={nomes} />
            </Cartao>
          )}
        </div>
      </main>

      {/* Celular: abas embaixo */}
      <div className="sticky bottom-0 border-t-2 border-linha bg-white lg:hidden">
        <Abas className="mx-auto max-w-[480px] px-5 pt-2.5 pb-6" />
      </div>
    </div>
  );
}
