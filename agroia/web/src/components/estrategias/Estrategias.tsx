// Seção "Suas estratégias" do Dashboard: busca a comparação e mostra os cartões.
import { useCallback, useEffect, useState } from "react";
import { ErroApi } from "../../api/client";
import { obterEstrategias } from "../../api/estrategias";
import type { Analise } from "../../api/tipos";
import { Aviso, BotaoContorno, Cartao, Texto } from "../ui";
import { CartaoEstrategia } from "./CartaoEstrategia";

function Esqueleto() {
  return (
    <div className="flex flex-col gap-4" role="status">
      <Cartao className="bg-sol-claro">
        <span className="text-base font-bold">Comparando rotações com dados da NASA…</span>
        <Texto>A primeira vez pode levar até 30 segundos.</Texto>
      </Cartao>
      {[0, 1].map((i) => (
        <div key={i} className="flex animate-pulse flex-col gap-3 rounded-[22px] bg-white p-4 shadow-cartao">
          <div className="h-6 w-2/3 rounded-full bg-terra" />
          <div className="h-3.5 w-full rounded-full bg-terra" />
          <div className="h-3.5 w-full rounded-full bg-terra" />
          <div className="h-3.5 w-3/4 rounded-full bg-terra" />
        </div>
      ))}
    </div>
  );
}

export function Estrategias() {
  const [analise, setAnalise] = useState<Analise | null>(null);
  const [erro, setErro] = useState<ErroApi | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [verEliminadas, setVerEliminadas] = useState(false);

  const buscar = useCallback(() => {
    setCarregando(true);
    setErro(null);
    obterEstrategias()
      .then(setAnalise)
      .catch((e) => setErro(e instanceof ErroApi ? e : new ErroApi(0, "Algo deu errado. Tente de novo.")))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(buscar, [buscar]);

  return (
    <section aria-labelledby="titulo-estrategias" className="flex flex-col gap-4 lg:mx-auto lg:w-full lg:max-w-[760px]">
      <h2 id="titulo-estrategias" className="m-0 font-titulo text-2xl font-extrabold tracking-[-0.02em]">Suas estratégias</h2>

      {carregando && <Esqueleto />}

      {!carregando && erro && (
        <div className="flex flex-col gap-3">
          <Aviso>{erro.message}</Aviso>
          {/* 422 pede ajuste nas respostas; o resto pode ser tentado de novo. */}
          {erro.status !== 422 && <BotaoContorno onClick={buscar}>Tentar de novo</BotaoContorno>}
        </div>
      )}

      {!carregando && analise && (
        <>
          {analise.atual_e_a_melhor && (
            <div role="status" className="rounded-2xl bg-folha-clara px-4 py-3 text-base font-bold text-folha-escura">
              Sua rotação atual já é a melhor entre as que testamos.
            </div>
          )}

          <h3 className="m-0 text-lg font-extrabold">Sua rotação hoje</h3>
          <CartaoEstrategia r={analise.atual} pesos={analise.pesos} atual />

          {analise.melhores.length > 0 && (
            <>
              <h3 className="m-0 mt-2 text-lg font-extrabold">Alternativas para comparar</h3>
              {analise.melhores.map((r) => <CartaoEstrategia key={r.id} r={r} pesos={analise.pesos} />)}
            </>
          )}

          <div className="flex flex-col gap-2">
            <button type="button" aria-expanded={verEliminadas} onClick={() => setVerEliminadas(!verEliminadas)}
              className="self-start py-2 text-base font-bold text-folha underline">
              {verEliminadas ? "Esconder o que foi descartado" : "Ver o que foi descartado"}
            </button>
            {verEliminadas && (
              analise.eliminadas.length === 0 ? (
                <Texto>Nada foi descartado.</Texto>
              ) : (
                <ul className="m-0 flex list-none flex-col gap-2 p-0">
                  {analise.eliminadas.map((e, i) => (
                    <li key={i} className="rounded-2xl bg-terra px-4 py-3 text-base">
                      <span className="font-bold">{e.nome}</span>
                      <ul className="m-0 mt-1 list-disc pl-5 text-suave">
                        {e.motivos.map((m, j) => <li key={j}>{m}</li>)}
                      </ul>
                    </li>
                  ))}
                </ul>
              )
            )}
          </div>

          {analise.fontes.length > 0 && (
            <p className="m-0 text-[13px] text-suave">Fontes: {analise.fontes.join(" · ")}</p>
          )}
        </>
      )}

      <p className="m-0 rounded-2xl bg-creme px-4 py-3 text-[15px] font-bold text-suave">
        O AgroIA compara. Quem decide é você, com seu técnico e a cooperativa.
      </p>
    </section>
  );
}
