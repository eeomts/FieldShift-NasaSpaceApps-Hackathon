import type { ItemCalendario } from "../api/tipos";
import { cx, MESES } from "../components/ui";

export function mesesDe(i: ItemCalendario): number[] {
  if (i.perene) return MESES.map((_, k) => k + 1);
  if (i.inicio_mes == null || i.fim_mes == null) return [];
  const out: number[] = [];
  let m = i.inicio_mes;
  for (;;) {
    out.push(m);
    if (m === i.fim_mes) break;
    m = (m % 12) + 1;
  }
  return out;
}

export function semCobertura(itens: ItemCalendario[]): number[] {
  if (itens.length === 0) return [];
  const ocupados = new Set(itens.flatMap(mesesDe));
  return MESES.map((_, k) => k + 1).filter((m) => !ocupados.has(m));
}

/** "Seu ano no campo": uma linha por cultura e a linha do campo com os meses descobertos. */
export function Calendario({ itens, vazios, nomes }: { itens: ItemCalendario[]; vazios?: number[]; nomes?: Record<string, string> }) {
  const descobertos = vazios ?? semCobertura(itens);
  return (
    <div className="flex flex-col gap-1.5">
      {itens.map((it, idx) => {
        const ms = new Set(mesesDe(it));
        return (
          <div key={idx} className="flex flex-col gap-1">
            <span className="text-xs font-bold text-suave">
              {(it.cultura_id && nomes?.[it.cultura_id]) || it.texto_original}
              {ms.size === 0 && " · época não informada"}
            </span>
            <div className="grid grid-cols-12 gap-1">
              {MESES.map((_, k) => (
                <div key={k} className={cx("h-3 rounded-full", ms.has(k + 1) ? "bg-folha" : "bg-terra")} />
              ))}
            </div>
          </div>
        );
      })}
      <div className="mt-1 grid grid-cols-12 gap-1" aria-label="Meses do ano">
        {MESES.map((m, k) => {
          const vazio = descobertos.includes(k + 1);
          return (
            <div
              key={m}
              title={vazio ? "Campo sem nada" : "Campo ocupado"}
              className={cx(
                "flex h-11 items-center justify-center rounded-[10px] text-[11px] font-bold capitalize",
                vazio ? "bg-terra text-terra-texto ring-2 ring-sol ring-inset" : "bg-folha text-white",
              )}
            >
              {m.slice(0, 1)}
            </div>
          );
        })}
      </div>
    </div>
  );
}
