import { useEffect, useState } from "react";
import { Link } from "react-router";
import { api } from "../api/client";
import { useSessao } from "../api/sessao";
import type { CulturaBase, Fazenda } from "../api/tipos";
import { Calendario } from "../onboarding/Calendario";
import { Brilho, Painel, Sair } from "../components/icones";
import { Cartao, Selo, Texto, Titulo } from "../components/ui";

/** Provisório: o Dashboard de verdade (dados NASA) é a parte 3. */
export function Dashboard() {
  const { usuario, sair } = useSessao();
  const [fazenda, setFazenda] = useState<Fazenda | null>(null);
  const [nomes, setNomes] = useState<Record<string, string>>({});

  useEffect(() => {
    api<Fazenda>("/fazenda").then(setFazenda).catch(() => setFazenda(null));
    api<CulturaBase[]>("/culturas").then((cs) => setNomes(Object.fromEntries(cs.map((c) => [c.id, c.nome])))).catch(() => {});
  }, []);

  return (
    <main className="mx-auto flex min-h-dvh max-w-[480px] flex-col">
      <div className="flex flex-1 flex-col gap-4 px-5 pt-6 pb-6">
        <div className="flex items-center justify-between">
          <Selo tom="folha">Perfil {fazenda?.perfil ?? "…"}</Selo>
          <button type="button" onClick={sair} className="flex items-center gap-1.5 rounded-xl px-2 py-1 text-sm font-bold text-suave">
            <Sair size={18} /> Sair
          </button>
        </div>
        <Titulo>Olá, {usuario?.nome.split(" ")[0]}!</Titulo>
        <Cartao className="bg-sol-claro">
          <span className="font-bold">Preparando os dados da sua fazenda…</span>
          <Texto>
            Seu questionário está salvo. A busca dos dados da NASA para o seu ponto entra na próxima parte do projeto.
          </Texto>
        </Cartao>
        {fazenda && fazenda.respostas.q8_culturas && fazenda.respostas.q8_culturas.length > 0 && (
          <Cartao>
            <span className="text-[13px] font-bold">Seu ano no campo</span>
            <Calendario itens={fazenda.respostas.q8_culturas} vazios={fazenda.meses_sem_cobertura} nomes={nomes} />
          </Cartao>
        )}
        <Link to="/onboarding" className="text-center text-sm font-bold text-folha">Revisar minhas respostas</Link>
      </div>
      <nav aria-label="Abas" className="sticky bottom-0 grid grid-cols-2 gap-2 border-t-2 border-linha bg-white px-5 pt-2.5 pb-6">
        <span aria-current="page" className="flex h-[52px] items-center justify-center gap-2 rounded-[18px] bg-tinta text-[15px] font-bold text-white">
          <Painel /> Dashboard
        </span>
        <span className="flex h-[52px] items-center justify-center gap-2 rounded-[18px] text-[15px] font-bold text-suave/60" title="Na próxima parte">
          <Brilho /> AgroIA
        </span>
      </nav>
    </main>
  );
}
