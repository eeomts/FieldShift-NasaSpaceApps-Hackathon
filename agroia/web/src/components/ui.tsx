import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";

export function cx(...c: (string | false | null | undefined)[]) {
  return c.filter(Boolean).join(" ");
}

export function BotaoPrimario({ className, children, ...p }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...p}
      className={cx(
        "flex h-14 items-center justify-center gap-2 rounded-[20px] bg-folha px-5 text-[17px] font-bold text-white shadow-degrau",
        "transition-transform active:translate-y-[3px] active:shadow-[0_2px_0_var(--color-folha-escura)]",
        "disabled:opacity-60 disabled:active:translate-y-0",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function BotaoContorno({ className, children, ...p }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...p}
      className={cx(
        "flex h-12 items-center justify-center gap-2 rounded-2xl border-2 border-folha bg-transparent px-4 text-[15px] font-bold text-folha disabled:opacity-60",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Campo({ rotulo, erro, ...p }: InputHTMLAttributes<HTMLInputElement> & { rotulo: string; erro?: string }) {
  return (
    <label className="flex flex-col gap-1.5 text-[13px] font-bold">
      {rotulo}
      <input
        {...p}
        className="h-12 rounded-2xl border-2 border-borda bg-white px-4 text-[15px] font-normal text-tinta placeholder:text-suave/60 focus:border-folha focus:outline-none"
      />
      {erro && <span className="font-normal text-[#B3261E]">{erro}</span>}
    </label>
  );
}

export function Titulo({ children }: { children: ReactNode }) {
  return <h1 className="m-0 font-titulo text-[30px] leading-[1.08] font-extrabold tracking-[-0.03em]">{children}</h1>;
}

export function Texto({ children }: { children: ReactNode }) {
  return <p className="m-0 text-[15px] leading-[1.45] text-suave">{children}</p>;
}

export function Cartao({ className, children }: { className?: string; children: ReactNode }) {
  // Fundo branco só quando quem usa não passou outra cor (as classes do Tailwind não se sobrepõem pela ordem).
  const temFundo = /(^|\s)bg-/.test(className ?? "");
  return <div className={cx("flex flex-col gap-2.5 rounded-[22px] p-4 shadow-cartao", !temFundo && "bg-white", className)}>{children}</div>;
}

export function Selo({ tom = "sol", children }: { tom?: "sol" | "folha" | "ceu"; children: ReactNode }) {
  const tons = {
    sol: "bg-sol-claro text-sol-texto",
    folha: "bg-folha-clara text-folha-escura",
    ceu: "bg-ceu text-ceu-texto",
  };
  return <span className={cx("inline-flex items-center gap-1.5 self-start rounded-full px-2.5 py-1 text-xs font-bold", tons[tom])}>{children}</span>;
}

export function Aviso({ children }: { children: ReactNode }) {
  return (
    <div role="alert" className="rounded-2xl bg-[#FDE7E4] px-4 py-3 text-sm font-medium text-[#8C1D18]">
      {children}
    </div>
  );
}

/** Grupo de opções (Sim / Não / Não sei e afins), no estilo do protótipo. */
export function Opcoes<T extends string>({
  pergunta,
  ajuda,
  opcoes,
  valor,
  onChange,
  colunas,
}: {
  pergunta: string;
  ajuda?: string;
  opcoes: { valor: T; rotulo: string }[];
  valor: T | null | undefined;
  onChange: (v: T) => void;
  colunas?: number;
}) {
  return (
    <fieldset className="m-0 flex flex-col gap-2.5 rounded-[22px] border-0 bg-white p-4 shadow-cartao">
      <legend className="float-left mb-2.5 w-full p-0 text-[15px] leading-[1.35] font-bold">{pergunta}</legend>
      {ajuda && <span className="-mt-1 text-[13px] text-suave">{ajuda}</span>}
      <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${colunas ?? Math.min(opcoes.length, 3)}, minmax(0, 1fr))` }}>
        {opcoes.map((o) => {
          const on = valor === o.valor;
          return (
            <button
              key={o.valor}
              type="button"
              aria-pressed={on}
              onClick={() => onChange(o.valor)}
              className={cx(
                "min-h-11 rounded-[14px] border-2 px-2 py-2 text-sm leading-tight font-bold transition-colors",
                on ? "border-folha bg-folha text-white" : "border-borda bg-white text-tinta hover:border-folha/50",
              )}
            >
              {o.rotulo}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}

export const SIM_NAO_NAOSEI = [
  { valor: "sim" as const, rotulo: "Sim" },
  { valor: "nao" as const, rotulo: "Não" },
  { valor: "nao_sei" as const, rotulo: "Não sei" },
];

export const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
export const MESES_LONGOS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
