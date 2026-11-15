// Moldura comum do Dashboard e da aba AgroAI: abas no topo (computador) e embaixo (celular), PT/EN e sair.
import type { ReactNode } from "react";
import { NavLink } from "react-router";
import { useSessao } from "../api/sessao";
import { useIdioma, type Idioma } from "../i18n";
import { Brilho, Painel, Sair } from "./icones";
import { Logo } from "./Logo";
import { cx } from "./ui";

/** Botão PT / EN. */
export function SeletorIdioma({ className }: { className?: string }) {
  const { idioma, setIdioma } = useIdioma();
  return (
    <div role="group" aria-label="Idioma / Language" className={cx("flex rounded-full border-2 border-borda bg-white p-0.5", className)}>
      {(["pt", "en"] as Idioma[]).map((i) => (
        <button
          key={i}
          type="button"
          aria-pressed={idioma === i}
          onClick={() => setIdioma(i)}
          className={cx(
            "h-8 min-w-[38px] rounded-full border-0 px-2 text-xs font-bold uppercase",
            idioma === i ? "bg-folha text-white" : "bg-transparent text-tinta",
          )}
        >
          {i}
        </button>
      ))}
    </div>
  );
}

export function BotaoSair({ className }: { className?: string }) {
  const { sair } = useSessao();
  const { t } = useIdioma();
  return (
    <button type="button" onClick={sair} aria-label={t("Sair", "Log out")} className={cx("flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-bold text-suave hover:bg-terra", className)}>
      <Sair size={18} /> <span className="hidden lg:inline">{t("Sair", "Log out")}</span>
    </button>
  );
}

function Abas({ className }: { className?: string }) {
  const { t } = useIdioma();
  const item = ({ isActive }: { isActive: boolean }) =>
    cx(
      "flex h-[52px] items-center justify-center gap-2 rounded-[18px] px-5 text-[15px] font-bold no-underline lg:h-12",
      isActive ? "bg-tinta text-white" : "bg-transparent text-tinta hover:bg-terra",
    );
  return (
    <nav aria-label={t("Abas", "Tabs")} className={cx("grid grid-cols-2 gap-2", className)}>
      <NavLink to="/dashboard" className={item}>
        <Painel /> Dashboard
      </NavLink>
      <NavLink to="/agroia" className={item}>
        <Brilho /> AgroAI
      </NavLink>
    </nav>
  );
}

export function Casca({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-dvh flex-col bg-creme">
      <header className="z-10 hidden border-b-2 border-linha bg-white/90 backdrop-blur lg:block">
        <div className="mx-auto flex max-w-[1120px] items-center justify-between gap-6 px-10 py-3">
          <Logo />
          <Abas className="w-[360px]" />
          <div className="flex items-center gap-2">
            <SeletorIdioma />
            <BotaoSair />
          </div>
        </div>
      </header>
      <div className="flex min-h-0 flex-1 flex-col">{children}</div>
      <div className="border-t-2 border-linha bg-white lg:hidden">
        <Abas className="mx-auto max-w-[480px] px-5 pt-2.5 pb-5" />
      </div>
    </div>
  );
}
