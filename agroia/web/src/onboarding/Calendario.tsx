import type { ItemCalendario } from "../api/tipos";
import { INICIAIS_MESES, MESES_CURTOS, useIdioma } from "../i18n";
import { cx } from "../components/ui";

const TODOS = Array.from({ length: 12 }, (_, k) => k + 1);

export function mesesDe(i: ItemCalendario): number[] {
  if (i.perene) return TODOS;
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
  return TODOS.filter((m) => !ocupados.has(m));
}

/** Calendário de 12 meses: P = plantio, C = colheita, verde claro = campo ocupado, ponto = campo sem nada. */
export function Calendario({ itens, vazios, nomes }: { itens: ItemCalendario[]; vazios?: number[]; nomes?: Record<string, string> }) {
  const { idioma, t } = useIdioma();
  const descobertos = vazios ?? semCobertura(itens);
  const nomeDe = (it: ItemCalendario) => (it.cultura_id && nomes?.[it.cultura_id]) || it.texto_original;
  const celula = "flex h-7 items-center justify-center rounded-lg text-[11px] font-bold";
  return (
    <div className="flex flex-col gap-2.5">
      <div className="grid grid-cols-12 gap-1 text-center text-[11px] font-bold text-suave" aria-hidden="true">
        {INICIAIS_MESES.map((l, k) => <span key={k}>{l}</span>)}
      </div>
      {itens.map((it, idx) => {
        const ms = new Set(mesesDe(it));
        return (
          <div key={idx} className="flex flex-col gap-1">
            <span className="text-[13px] font-bold">
              {nomeDe(it)}
              {it.perene && <span className="font-normal text-suave"> {t("(o ano todo)", "(all year)")}</span>}
              {!it.perene && ms.size === 0 && <span className="font-normal text-suave"> {t("· época não informada", "· season not given")}</span>}
            </span>
            <div className="grid grid-cols-12 gap-1" role="img" aria-label={nomeDe(it) + ": " + [...ms].map((m) => MESES_CURTOS[idioma][m - 1]).join(", ")}>
              {TODOS.map((m) => {
                const dentro = ms.has(m);
                const plantio = !it.perene && dentro && m === it.inicio_mes;
                const colheita = !it.perene && dentro && m === it.fim_mes;
                return (
                  <div
                    key={m}
                    className={cx(
                      celula,
                      colheita ? "bg-sol text-tinta" : plantio ? "bg-folha text-white" : dentro ? "bg-campo" : "bg-areia",
                    )}
                  >
                    {colheita ? t("C", "H") : plantio ? "P" : ""}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
      <div className="flex flex-col gap-1">
        <span className="text-[13px] font-bold">{t("Campo sem nada", "Bare field")}</span>
        <div className="grid grid-cols-12 gap-1" role="img" aria-label={descobertos.map((m) => MESES_CURTOS[idioma][m - 1]).join(", ") || t("nenhum mês", "no months")}>
          {TODOS.map((m) => (
            <div key={m} className={cx(celula, descobertos.includes(m) ? "bg-sol-claro text-sol-texto ring-2 ring-sol ring-inset" : "bg-transparent")}>
              {descobertos.includes(m) ? "•" : ""}
            </div>
          ))}
        </div>
      </div>
      <ul className="m-0 flex list-none flex-wrap gap-x-3 gap-y-1 p-0 text-[11px] font-bold text-suave">
        <li className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm bg-folha" /> {t("P · Plantio", "P · Planting")}</li>
        <li className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm bg-sol" /> {t("C · Colheita", "H · Harvest")}</li>
        <li className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm bg-campo" /> {t("No campo", "In the field")}</li>
        <li className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm bg-areia ring-1 ring-borda" /> {t("Vazio", "Empty")}</li>
      </ul>
    </div>
  );
}
