// Balões do chat e as fontes de cada resposta.
import type { Fonte, Mensagem, TipoFonte } from "../../api/tipos";
import { useIdioma } from "../../i18n";
import { Bolinhas, cx } from "../ui";
import { Globo } from "../icones";

const ROTULO_FONTE: Record<TipoFonte, { pt: string; en: string }> = {
  clima: { pt: "Clima (NASA)", en: "Weather (NASA)" },
  conhecimento: { pt: "Base de conhecimento", en: "Knowledge base" },
  cultura: { pt: "Dados da cultura", en: "Crop data" },
  fazenda: { pt: "Suas respostas no questionário", en: "Your questionnaire answers" },
  analise: { pt: "Comparação do AgroIA", en: "AgroIA comparison" },
};

function Fontes({ fontes }: { fontes: Fonte[] }) {
  const { idioma, t } = useIdioma();
  return (
    <div className="mt-1 flex max-w-[92%] flex-col gap-1.5">
      <span className="sr-only">{t("De onde veio", "Where it came from")}</span>
      <ul className="m-0 flex list-none flex-wrap gap-1.5 p-0">
        {fontes.map((f, i) => (
          <li key={i} className="inline-flex max-w-full items-start gap-1.5 rounded-2xl bg-ceu px-2.5 py-1.5 text-xs leading-snug text-ceu-texto">
            <Globo size={14} className="mt-px shrink-0" />
            <span>
              <b>{ROTULO_FONTE[f.tipo]?.[idioma] ?? f.tipo}</b> · {f.titulo}
              {f.detalhe && <span className="block">{f.detalhe}</span>}
            </span>
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
          "max-w-[88%] rounded-[22px] px-4 py-3 text-base leading-[1.5] break-words whitespace-pre-wrap",
          meu ? "rounded-br-md bg-folha text-white" : "rounded-bl-md bg-white text-tinta shadow-cartao",
        )}
      >
        {m.texto}
      </div>
      {!meu && m.fontes?.length > 0 && <Fontes fontes={m.fontes} />}
    </div>
  );
}

/** Mensagem da AgroIA que só existe na tela (saudação), sem fonte. */
export function BalaoLocal({ texto }: { texto: string }) {
  return <div className="max-w-[88%] self-start rounded-[22px] rounded-bl-md bg-white px-4 py-3 text-base leading-[1.5] shadow-cartao">{texto}</div>;
}

export function Pensando() {
  const { t } = useIdioma();
  return (
    <div role="status" className="flex items-start">
      <div className="flex items-center gap-2 rounded-[22px] rounded-bl-md bg-white px-4 py-3.5 shadow-cartao">
        <Bolinhas />
        <span className="sr-only">{t("Pensando…", "Thinking…")}</span>
      </div>
    </div>
  );
}
