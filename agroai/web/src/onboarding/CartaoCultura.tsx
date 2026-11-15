// Cartão de uma cultura achada na pergunta 8: confirmar, trocar, época (plantio e colheita), consórcio e área.
import { useState } from "react";
import type { CulturaBase, ItemCalendario } from "../api/tipos";
import { Lixeira, Trocar } from "../components/icones";
import { Cartao, cx, Selo } from "../components/ui";
import { MESES_CURTOS, MESES_LONGOS, useIdioma } from "../i18n";
import { mesesDe } from "./Calendario";

export const novoItem = (c: CulturaBase): ItemCalendario => ({
  cultura_id: c.id, texto_original: c.nome, inicio_mes: null, fim_mes: null, perene: c.perene, consorcio_com: [], ocupa: null,
});

function Escolha2({ a, b, valor, onChange }: { a: { v: string; rotulo: string }; b: { v: string; rotulo: string }; valor: string | null; onChange: (v: string) => void }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {[a, b].map((o) => (
        <button key={o.v} type="button" aria-pressed={valor === o.v} onClick={() => onChange(o.v)}
          className={cx("min-h-12 rounded-2xl border-2 px-2 text-[15px] font-bold", valor === o.v ? "border-folha bg-folha text-white" : "border-borda bg-white")}>
          {o.rotulo}
        </button>
      ))}
    </div>
  );
}

export function CartaoCultura({ item, culturas, onChange, onRemover }: {
  item: ItemCalendario; culturas: CulturaBase[]; onChange: (i: ItemCalendario) => void; onRemover: () => void;
}) {
  const { idioma, t } = useIdioma();
  const [trocando, setTrocando] = useState(false);
  const [modo, setModo] = useState<"plantio" | "colheita">("plantio");
  const nomeDe = (id: string | null) => culturas.find((c) => c.id === id)?.nome;
  const nome = nomeDe(item.cultura_id) ?? item.texto_original;
  const outras = item.consorcio_com.map((id) => nomeDe(id) ?? id).join(` ${t("e", "and")} `);
  const meses = new Set(mesesDe(item));

  function tocarMes(m: number) {
    if (modo === "plantio") {
      onChange({ ...item, inicio_mes: m });
      setModo("colheita");
    } else {
      onChange({ ...item, fim_mes: m });
    }
  }

  const resumo =
    item.inicio_mes != null && item.fim_mes != null
      ? t(`Plantio em ${MESES_LONGOS.pt[item.inicio_mes - 1]} · colheita em ${MESES_LONGOS.pt[item.fim_mes - 1]}.`, `Planting in ${MESES_LONGOS.en[item.inicio_mes - 1]} · harvest in ${MESES_LONGOS.en[item.fim_mes - 1]}.`)
      : t("Toque no mês do plantio e no mês da colheita.", "Tap the planting month and the harvest month.");

  return (
    <Cartao className="gap-3.5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <span className="font-titulo text-xl leading-tight font-extrabold">{t(`Você planta ${nome}?`, `Do you grow ${nome}?`)}</span>
          {item.texto_original && item.texto_original.toLowerCase() !== nome.toLowerCase() && (
            <span className="text-xs text-suave">{t("Você escreveu: ", "You wrote: ")}“{item.texto_original}”</span>
          )}
          {!item.cultura_id && <Selo>{t("Fora da nossa base: entra no calendário, mas não na comparação", "Not in our list: it goes in the calendar, but not in the comparison")}</Selo>}
        </div>
        <button type="button" onClick={onRemover} aria-label={t(`Remover ${nome}`, `Remove ${nome}`)}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[14px] border-2 border-borda bg-white text-perigo">
          <Lixeira size={18} />
        </button>
      </div>

      <button type="button" onClick={() => setTrocando((v) => !v)} aria-expanded={trocando}
        className="flex h-11 items-center gap-2 self-start rounded-[14px] border-2 border-borda bg-white px-3 text-sm font-bold">
        <Trocar size={16} /> {t("Não é essa? Trocar", "Not this one? Change")}
      </button>
      {trocando && (
        <select aria-label={t("Trocar cultura", "Change crop")} value={item.cultura_id ?? ""}
          onChange={(e) => {
            const c = culturas.find((x) => x.id === e.target.value);
            onChange({ ...item, cultura_id: c ? c.id : null, perene: c ? c.perene : item.perene });
            setTrocando(false);
          }}
          className="h-12 rounded-2xl border-2 border-borda bg-white px-3 text-[15px] font-bold focus:border-folha focus:outline-none">
          <option value="">{t("Não está na lista", "Not in the list")}</option>
          {[...culturas].sort((a, b) => a.nome.localeCompare(b.nome, idioma)).map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
      )}

      <label className="flex items-start gap-3 rounded-2xl bg-campo-claro p-3 text-[15px] font-bold">
        <input type="checkbox" className="mt-0.5 h-6 w-6 shrink-0 accent-[#1F7A4D]" checked={item.perene} onChange={(e) => onChange({ ...item, perene: e.target.checked })} />
        {t("Ocupa o campo o ano todo (perene)?", "Takes up the field all year (perennial)?")}
      </label>

      {!item.perene && (
        <div className="flex flex-col gap-2.5">
          <span className="text-[15px] font-bold">{t("De que mês a que mês? Toque para marcar:", "From which month to which month? Tap to mark:")}</span>
          <div className="grid grid-cols-2 gap-2" role="group" aria-label={t("O que você está marcando", "What you are marking")}>
            <button type="button" aria-pressed={modo === "plantio"} onClick={() => setModo("plantio")}
              className={cx("flex min-h-12 items-center justify-center gap-2 rounded-2xl border-2 text-[15px] font-bold", modo === "plantio" ? "border-folha bg-campo-claro" : "border-borda bg-white")}>
              <span className="h-3 w-3 rounded-sm bg-folha" /> {t("Mês de plantio", "Planting month")}
            </button>
            <button type="button" aria-pressed={modo === "colheita"} onClick={() => setModo("colheita")}
              className={cx("flex min-h-12 items-center justify-center gap-2 rounded-2xl border-2 text-[15px] font-bold", modo === "colheita" ? "border-sol-escuro bg-sol-claro" : "border-borda bg-white")}>
              <span className="h-3 w-3 rounded-sm bg-sol" /> {t("Mês de colheita", "Harvest month")}
            </button>
          </div>
          <div className="grid grid-cols-6 gap-1.5">
            {MESES_CURTOS[idioma].map((nomeMes, k) => {
              const m = k + 1;
              const ini = m === item.inicio_mes;
              const fim = m === item.fim_mes;
              return (
                <button key={m} type="button" aria-label={MESES_LONGOS[idioma][k]} aria-pressed={ini || fim} onClick={() => tocarMes(m)}
                  className={cx("flex h-14 flex-col items-center justify-center rounded-xl text-[13px] font-bold transition-colors",
                    fim ? "bg-sol text-tinta" : ini ? "bg-folha text-white" : meses.has(m) ? "bg-campo text-folha-escura" : "bg-areia text-terra-texto")}>
                  {nomeMes}
                  {(ini || fim) && <span className="text-[9px] tracking-wide uppercase">{fim ? t("Colheita", "Harvest") : t("Plantio", "Planting")}</span>}
                </button>
              );
            })}
          </div>
          <span className="rounded-xl bg-campo-claro px-3 py-2 text-[13px] font-bold text-folha-escura">{resumo}</span>
        </div>
      )}

      {item.consorcio_com.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="text-[15px] font-bold">{t(`É plantado junto com ${outras}?`, `Is it planted together with ${outras}?`)}</span>
          <Escolha2 a={{ v: "sim", rotulo: t("Sim", "Yes") }} b={{ v: "nao", rotulo: t("Não", "No") }} valor="sim"
            onChange={(v) => v === "nao" && onChange({ ...item, consorcio_com: [] })} />
        </div>
      )}

      <div className="flex flex-col gap-2">
        <span className="text-[15px] font-bold">{t("Ocupa o campo todo ou uma parte?", "Does it take up the whole field or part of it?")}</span>
        <Escolha2 a={{ v: "todo", rotulo: t("Campo todo", "Whole field") }} b={{ v: "parte", rotulo: t("Uma parte", "Part of it") }} valor={item.ocupa}
          onChange={(v) => onChange({ ...item, ocupa: v as ItemCalendario["ocupa"] })} />
      </div>
    </Cartao>
  );
}
