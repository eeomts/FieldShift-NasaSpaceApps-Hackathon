// Cartão de uma estratégia: culturas por mês, nota, critérios, motivos e "De onde veio".
import type { Analise, Criterio, ItemEstrategia, Resultado } from "../../api/tipos";
import { Cartao, cx, MESES, Selo } from "../ui";

const ROTULO: Record<Criterio, string> = {
  agua: "Economiza água",
  terra: "Cuida da terra",
  erosao: "Segura a terra (erosão)",
  pragas: "Menos praga",
  renda: "Renda",
  animais: "Comida pros animais",
};

const CONFIANCA = {
  alta: { tom: "folha" as const, rotulo: "Confiança alta", frase: "Há boa medição para estas culturas." },
  media: { tom: "ceu" as const, rotulo: "Confiança média", frase: "Há alguma medição; confirme com seu técnico." },
  baixa: { tom: "sol" as const, rotulo: "Confiança baixa", frase: "Estimativa com pouca medição no Brasil, confirme com seu técnico." },
};

function mesesDe(i: ItemEstrategia): Set<number> {
  if (i.perene) return new Set(MESES.map((_, k) => k + 1));
  const out = new Set<number>();
  if (i.inicio_mes == null || i.fim_mes == null) return out;
  let m = i.inicio_mes;
  for (let n = 0; n < 12; n++) {
    out.add(m);
    if (m === i.fim_mes) break;
    m = (m % 12) + 1;
  }
  return out;
}

function Faixa({ itens }: { itens: ItemEstrategia[] }) {
  return (
    <div className="flex flex-col gap-2">
      {itens.map((it, idx) => {
        const ms = mesesDe(it);
        return (
          <div key={idx} className="flex flex-col gap-1">
            <span className="text-base font-bold">
              {it.nome}
              {ms.size === 0 && <span className="font-normal text-suave"> · época não informada</span>}
            </span>
            <div className="grid grid-cols-12 gap-1">
              {MESES.map((m, k) => (
                <div key={m} title={m} className={cx("h-3.5 rounded-full", ms.has(k + 1) ? "bg-folha" : "bg-terra")} />
              ))}
            </div>
          </div>
        );
      })}
      <div className="grid grid-cols-12 gap-1" aria-hidden="true">
        {MESES.map((m) => (
          <span key={m} className="text-center text-[11px] font-bold text-suave capitalize">{m.slice(0, 1)}</span>
        ))}
      </div>
    </div>
  );
}

function Lista({ titulo, itens }: { titulo: string; itens: string[] }) {
  if (itens.length === 0) return null;
  return (
    <div className="flex flex-col gap-1">
      <span className="text-base font-bold">{titulo}</span>
      <ul className="m-0 flex list-disc flex-col gap-1 pl-5 text-base leading-[1.45] text-suave">
        {itens.map((t, i) => <li key={i}>{t}</li>)}
      </ul>
    </div>
  );
}

function DeOndeVeio({ r }: { r: Resultado }) {
  return (
    <details className="rounded-2xl bg-creme px-4 py-3">
      <summary className="cursor-pointer text-base font-bold text-folha-escura">De onde veio</summary>
      <div className="mt-3 flex flex-col gap-4">
        {r.notas.map((n) => (
          <div key={n.criterio} className="flex flex-col gap-1.5">
            <span className="text-base font-bold">{ROTULO[n.criterio]}</span>
            <p className="m-0 text-base leading-[1.45] text-suave">{n.explicacao}</p>
            {n.evidencias.length > 0 && (
              <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
                {n.evidencias.map((e, i) => (
                  <li key={i} className="rounded-xl bg-terra px-3 py-2 text-[15px] leading-snug">
                    {e.texto}
                    {e.valor != null && <span className="font-bold"> · {e.valor}{e.unidade ? ` ${e.unidade}` : ""}</span>}
                    <span className="block text-sm text-suave">
                      Fonte: {e.fonte}{e.periodo ? ` · ${e.periodo}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}

export function CartaoEstrategia({ r, pesos, atual }: { r: Resultado; pesos: Analise["pesos"]; atual?: boolean }) {
  // Escolhido = peso acima de 0,06; se todos os pesos são iguais (nada escolhido), não destaca nenhum.
  const valores = Object.values(pesos);
  const algumEscolhido = Math.max(...valores) - Math.min(...valores) > 0.02;
  const pontos = r.nota_final == null ? null : Math.round(r.nota_final * 100);
  const conf = CONFIANCA[r.confianca];
  return (
    <Cartao className="gap-4 lg:p-6">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1.5">
          {atual && <Selo tom="ceu">Sua rotação hoje</Selo>}
          <h3 className="m-0 font-titulo text-xl leading-tight font-extrabold">{r.nome}</h3>
        </div>
        <div className="flex shrink-0 flex-col items-end">
          {pontos == null ? (
            <span className="text-base font-bold text-suave">sem nota</span>
          ) : (
            <>
              <span className="font-titulo text-[32px] leading-none font-extrabold text-folha">{pontos}</span>
              <span className="text-sm text-suave">de 100 pontos</span>
            </>
          )}
        </div>
      </div>

      <Faixa itens={r.itens} />

      <div className="flex flex-col gap-2.5">
        {r.notas.map((n) => {
          const prioridade = algumEscolhido && pesos[n.criterio] > 0.06;
          const valor = n.nota == null ? null : Math.round(n.nota * 100);
          return (
            <div key={n.criterio} className="flex flex-col gap-1">
              <div className="flex items-baseline justify-between gap-2 text-base">
                <span className={prioridade ? "font-extrabold" : "font-semibold"}>
                  {ROTULO[n.criterio]}
                  {prioridade && <span className="ml-2 rounded-full bg-sol-claro px-2 py-0.5 text-xs font-bold text-sol-texto">Importante pra você</span>}
                </span>
                <span className="shrink-0 text-suave">{valor == null ? "sem dado" : valor}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-terra" role="img" aria-label={`${ROTULO[n.criterio]}: ${valor == null ? "sem dado" : `${valor} de 100`}`}>
                {valor != null && <div className={cx("h-full rounded-full", prioridade ? "bg-folha" : "bg-morro")} style={{ width: `${valor}%` }} />}
              </div>
            </div>
          );
        })}
      </div>

      <Lista titulo="Por que" itens={r.por_que} />
      <Lista titulo="Onde piora" itens={r.onde_piora} />

      {r.alertas.length > 0 && (
        <ul className="m-0 flex list-none flex-col gap-2 p-0">
          {r.alertas.map((a, i) => (
            <li key={`${a.codigo}-${i}`} className="rounded-2xl bg-sol-claro px-4 py-3 text-base leading-[1.4] text-sol-texto">{a.texto}</li>
          ))}
        </ul>
      )}

      <div className="flex flex-col gap-1">
        <Selo tom={conf.tom}>{conf.rotulo}</Selo>
        <span className="text-[15px] text-suave">{conf.frase}</span>
      </div>
      {r.lacunas.length > 0 && (
        <ul className="m-0 flex list-none flex-col gap-0.5 p-0 text-[13px] text-suave">
          {r.lacunas.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
      )}

      <DeOndeVeio r={r} />
    </Cartao>
  );
}
