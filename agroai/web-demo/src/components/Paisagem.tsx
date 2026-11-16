import { cx } from "./ui";
import { useIdioma } from "../i18n";
import { Satelite } from "./icones";

/**
 * Ilustração de morros, sol e plantinhas (igual ao protótipo).
 * As medidas são proporcionais, então funciona tanto na faixa do celular quanto no painel grande do computador.
 */
export function Paisagem({ className }: { className?: string }) {
  const { t } = useIdioma();
  return (
    <div className={cx("relative shrink-0 overflow-hidden rounded-b-[44px] bg-folha-clara", className)} aria-hidden="true">
      <div className="absolute top-[13%] right-[10%] aspect-square w-[38%] max-w-[260px] rounded-full bg-sol shadow-[0_0_0_18px_rgba(255,194,61,0.25)] lg:shadow-[0_0_0_32px_rgba(255,194,61,0.22)]" />

      <div className="absolute top-[20%] left-[8%] flex -rotate-4 items-center gap-2 rounded-full bg-white py-2 pr-3.5 pl-2.5 shadow-[0_10px_24px_-10px_rgba(29,43,34,0.35)] lg:top-[14%]">
        <Satelite className="text-folha" />
        <span className="text-[13px] font-bold lg:text-[15px]">{t("Dados da NASA", "NASA data")}</span>
      </div>
      {/* Etiquetas extras só no computador, onde sobra espaço */}
      <div className="absolute top-[30%] left-[16%] hidden rotate-3 rounded-full bg-white px-3.5 py-2 text-[14px] font-bold shadow-[0_10px_24px_-10px_rgba(29,43,34,0.35)] lg:block">
        {t("Umidade do solo · SMAP", "Soil moisture · SMAP")}
      </div>
      <div className="absolute top-[42%] left-[7%] hidden -rotate-2 rounded-full bg-sol-claro px-3.5 py-2 text-[14px] font-bold text-sol-texto shadow-[0_10px_24px_-10px_rgba(29,43,34,0.35)] lg:block">
        {t("Chuva do mês · GPM", "Rain this month · GPM")}
      </div>

      <div className="absolute -bottom-[40%] -left-[15%] h-[77%] w-[85%] rounded-[50%] bg-morro" />
      <div className="absolute -right-[23%] -bottom-[47%] h-[83%] w-[97%] rounded-[50%] bg-folha" />
      <div className="absolute -bottom-[50%] left-[31%] h-[73%] w-[67%] rounded-[50%] bg-[#2C8C59]" />
      <div className="absolute bottom-[16%] left-[38%] flex -rotate-6 items-end gap-2.5 lg:gap-4">
        {[34, 46, 30].map((h, i) => (
          <div key={i} className="w-2.5 rounded-md bg-creme opacity-85 lg:w-4" style={{ height: `calc(${h}px * var(--escala-planta, 1))` }} />
        ))}
      </div>
    </div>
  );
}
