// Balões do chat e a lista "De onde veio" de cada resposta.
import type { Fonte, Mensagem, TipoFonte } from "../../api/tipos";
import { cx } from "../ui";

const ROTULO_FONTE: Record<TipoFonte, string> = {
  clima: "Clima (NASA)",
  conhecimento: "Base de conhecimento",
  cultura: "Dados da cultura",
  fazenda: "Sua fazenda",
  analise: "Comparação do AgroIA",
};

function DeOndeVeio({ fontes }: { fontes: Fonte[] }) {
  return (
    <div className="mt-1 flex max-w-[90%] flex-col gap-1.5 text-[13px] leading-snug text-suave">
      <span className="font-bold">De onde veio</span>
      <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
        {fontes.map((f, i) => (
          <li key={i} className="rounded-xl bg-terra px-3 py-2">
            <span className="font-bold text-terra-texto">{ROTULO_FONTE[f.tipo] ?? f.tipo}</span>
            {" · "}
            {f.titulo}
            {f.detalhe && <span className="block">{f.detalhe}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Balao({ m }: { m: Mensagem }) {
  const meu = m.papel === "produtor";
  return (
    <div className={cx("flex flex-col", meu ? "items-end" : "items-start")}>
      <div
        className={cx(
          "max-w-[88%] rounded-[20px] px-4 py-3 text-base leading-[1.5] whitespace-pre-wrap break-words",
          meu ? "rounded-br-md bg-folha text-white" : "rounded-bl-md bg-creme text-tinta",
        )}
      >
        {m.texto}
      </div>
      {!meu && m.fontes?.length > 0 && <DeOndeVeio fontes={m.fontes} />}
    </div>
  );
}

export function Pensando() {
  return (
    <div role="status" className="flex items-start">
      <div className="rounded-[20px] rounded-bl-md bg-creme px-4 py-3 text-base text-suave">Pensando…</div>
    </div>
  );
}
