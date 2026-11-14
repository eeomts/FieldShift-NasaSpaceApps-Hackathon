import { cx, MESES, MESES_LONGOS } from "../components/ui";

/** Régua de 12 meses: o 1º toque marca o início, o 2º marca o fim (pode virar o ano). */
export function SeletorMeses({
  inicio,
  fim,
  onChange,
}: {
  inicio: number | null;
  fim: number | null;
  onChange: (inicio: number | null, fim: number | null) => void;
}) {
  const dentro = (m: number) => {
    if (inicio == null) return false;
    if (fim == null) return m === inicio;
    return inicio <= fim ? m >= inicio && m <= fim : m >= inicio || m <= fim;
  };
  const tocar = (m: number) => {
    if (inicio == null || fim != null) onChange(m, null);
    else onChange(inicio, m);
  };
  const resumo =
    inicio == null ? "Toque no mês em que planta" : fim == null ? "Agora toque no mês em que colhe" : `${MESES_LONGOS[inicio - 1]} → ${MESES_LONGOS[fim - 1]}`;
  return (
    <div className="flex flex-col gap-2">
      <div className="grid grid-cols-6 gap-1.5">
        {MESES.map((nome, k) => {
          const m = k + 1;
          const on = dentro(m);
          return (
            <button
              key={nome}
              type="button"
              aria-pressed={on}
              aria-label={MESES_LONGOS[k]}
              onClick={() => tocar(m)}
              className={cx(
                "h-11 rounded-xl text-[13px] font-bold capitalize transition-colors",
                on ? "bg-folha text-white" : "bg-terra text-terra-texto hover:bg-folha-clara",
                (m === inicio || m === fim) && "ring-2 ring-sol",
              )}
            >
              {nome}
            </button>
          );
        })}
      </div>
      <span className="text-[13px] font-bold text-suave">{resumo}</span>
    </div>
  );
}
