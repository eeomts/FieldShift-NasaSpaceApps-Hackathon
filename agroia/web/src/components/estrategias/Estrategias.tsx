// Seção "Suas estratégias" do Dashboard: busca a comparação e mostra os cartões.
import { useCallback, useEffect, useState } from "react";
import { ErroApi } from "../../api/client";
import { obterEstrategias } from "../../api/estrategias";
import type { Analise } from "../../api/tipos";
import { useIdioma } from "../../i18n";
import { Aviso, BotaoContorno, Cartao, Texto } from "../ui";
import { CartaoEstrategia } from "./CartaoEstrategia";

/** Mensagens 422 do motor (a API responde em português) no idioma do produtor. */
const ERROS_EN: Record<string, string> = {
  "Marque o local da fazenda para comparar rotações.": "Mark your farm's location to compare rotations.",
  "Ainda só comparamos rotações no Brasil e nos Estados Unidos; o local da fazenda está fora deles.": "We only compare rotations in Brazil and the United States for now; your farm is outside both.",
  "Ainda não temos as culturas desta região na base.": "We don't have this region's crops in our database yet.",
  "Cadastre o que você planta para comparar rotações.": "Tell us what you grow to compare rotations.",
  "Fazenda não encontrada.": "Farm not found.",
  "Não consegui os dados de clima da NASA agora. Tente de novo em alguns minutos.": "Couldn't get NASA climate data right now. Please try again in a few minutes.",
};

function Esqueleto() {
  const { t } = useIdioma();
  return (
    <div className="flex flex-col gap-4" role="status">
      <Cartao className="bg-sol-claro">
        <span className="text-base font-bold">{t("Comparando rotações com dados da NASA…", "Comparing rotations with NASA data…")}</span>
        <Texto>{t("A primeira vez pode levar até 30 segundos.", "The first time can take up to 30 seconds.")}</Texto>
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
  const { t, idioma } = useIdioma();
  const [analise, setAnalise] = useState<Analise | null>(null);
  const [erro, setErro] = useState<ErroApi | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [verEliminadas, setVerEliminadas] = useState(false);

  const buscar = useCallback(() => {
    setCarregando(true);
    setErro(null);
    obterEstrategias()
      .then(setAnalise)
      .catch((e) => setErro(e instanceof ErroApi ? e : new ErroApi(0, "")))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(buscar, [buscar]);

  return (
    <section aria-labelledby="titulo-estrategias" className="flex flex-col gap-4 lg:mx-auto lg:w-full lg:max-w-[760px]">
      <h2 id="titulo-estrategias" className="m-0 font-titulo text-2xl font-extrabold tracking-[-0.02em]">{t("Suas estratégias", "Your strategies")}</h2>

      {carregando && <Esqueleto />}

      {!carregando && erro && (
        <div className="flex flex-col gap-3">
          <Aviso>{(idioma === "en" ? ERROS_EN[erro.message] : erro.message) || t("Algo deu errado. Tente de novo.", "Something went wrong. Please try again.")}</Aviso>
          {/* 422 pede ajuste nas respostas; o resto pode ser tentado de novo. */}
          {erro.status !== 422 && <BotaoContorno onClick={buscar}>{t("Tentar de novo", "Try again")}</BotaoContorno>}
        </div>
      )}

      {!carregando && analise && (
        <>
          {analise.atual_e_a_melhor && (
            <div role="status" className="rounded-2xl bg-folha-clara px-4 py-3 text-base font-bold text-folha-escura">
              {t("Sua rotação atual já é a melhor entre as que testamos.", "Your current rotation is already the best of the ones we tested.")}
            </div>
          )}

          <h3 className="m-0 text-lg font-extrabold">{t("Sua rotação hoje", "Your rotation today")}</h3>
          <CartaoEstrategia r={analise.atual} pesos={analise.pesos} atual />

          {analise.melhores.length > 0 && (
            <>
              <h3 className="m-0 mt-2 text-lg font-extrabold">{t("Alternativas para comparar", "Alternatives to compare")}</h3>
              {analise.melhores.map((r) => <CartaoEstrategia key={r.id} r={r} pesos={analise.pesos} />)}
            </>
          )}

          <div className="flex flex-col gap-2">
            <button type="button" aria-expanded={verEliminadas} onClick={() => setVerEliminadas(!verEliminadas)}
              className="self-start py-2 text-base font-bold text-folha underline">
              {verEliminadas ? t("Esconder o que foi descartado", "Hide what was ruled out") : t("Ver o que foi descartado", "See what was ruled out")}
            </button>
            {verEliminadas && (
              analise.eliminadas.length === 0 ? (
                <Texto>{t("Nada foi descartado.", "Nothing was ruled out.")}</Texto>
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
            <p className="m-0 text-[13px] text-suave">{t("Fontes", "Sources")}: {analise.fontes.join(" · ")}</p>
          )}
        </>
      )}

      <p className="m-0 rounded-2xl bg-creme px-4 py-3 text-[15px] font-bold text-suave">
        {t("O AgroIA compara. Quem decide é você, com seu técnico e a cooperativa.", "AgroIA compares. You decide, with your agronomist and your co-op.")}
      </p>
    </section>
  );
}
