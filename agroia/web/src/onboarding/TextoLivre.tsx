import { useState } from "react";
import { api } from "../api/client";
import type { Interpretacao, PedidoInterpretar } from "../api/tipos";
import { Brilho } from "../components/icones";
import { Aviso, Bolinhas, Selo } from "../components/ui";
import { useIdioma } from "../i18n";

/** Componente único das perguntas 8, 22 e 23: texto livre -> IA -> lista para confirmar. */
export function TextoLivre({
  campo,
  rotulo,
  exemplo,
  textoBotao,
  carregandoTexto,
  hemisferio,
  texto,
  onTexto,
  onResultado,
}: {
  campo: PedidoInterpretar["campo"];
  rotulo: string;
  exemplo: string;
  textoBotao: string;
  carregandoTexto: string;
  hemisferio: "N" | "S";
  texto: string;
  onTexto: (t: string) => void;
  onResultado: (r: Interpretacao) => void;
}) {
  const { idioma, t, erro: textoErro } = useIdioma();
  const [estado, setEstado] = useState<"parado" | "lendo">("parado");
  const [fonte, setFonte] = useState<Interpretacao["fonte"] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function separar() {
    setEstado("lendo");
    setErro(null);
    try {
      const body: PedidoInterpretar = { campo, texto, hemisferio, idioma };
      const r = await api<Interpretacao>("/onboarding/interpretar", { method: "POST", body });
      setFonte(r.fonte);
      onResultado(r);
    } catch (e) {
      setErro(textoErro(e) + " " + t("Escolha pela lista abaixo.", "Pick from the list below."));
    } finally {
      setEstado("parado");
    }
  }

  return (
    <div className="flex flex-col gap-2.5">
      <label className="flex flex-col gap-2 text-[13px] font-bold">
        {rotulo}
        <textarea
          rows={3}
          maxLength={1000}
          value={texto}
          onChange={(e) => onTexto(e.target.value)}
          placeholder={exemplo}
          className="resize-none rounded-[18px] border-2 border-borda bg-white px-4 py-3.5 text-[15px] leading-snug font-normal text-tinta placeholder:text-suave/60 focus:border-folha focus:outline-none"
        />
      </label>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={separar}
          disabled={!texto.trim() || estado === "lendo"}
          className="flex h-12 flex-1 items-center justify-center gap-2 rounded-2xl bg-sol px-4 text-[15px] font-bold text-tinta shadow-degrau-sol transition-transform active:translate-y-[3px] disabled:opacity-50"
        >
          <Brilho size={18} />
          {textoBotao}
        </button>
        <button
          type="button"
          onClick={() => onTexto(exemplo)}
          disabled={estado === "lendo"}
          className="h-12 rounded-2xl border-2 border-borda bg-white px-4 text-[15px] font-bold disabled:opacity-50"
        >
          {t("Exemplo", "Example")}
        </button>
      </div>
      {estado === "lendo" && (
        <div role="status" className="flex items-center gap-2 text-[13px] font-bold text-folha-escura">
          <Bolinhas /> {carregandoTexto}
        </div>
      )}
      {fonte === "ia" && estado === "parado" && <Selo tom="folha"><Brilho size={14} /> {t("A AgroIA entendeu. Confere abaixo?", "AgroIA got it. Does this look right?")}</Selo>}
      {fonte === "lista" && estado === "parado" && (
        <Selo>{t("A IA não está disponível agora. Achamos pelo nome; confira e complete pela lista.", "The AI is not available right now. We matched by name; check it and fill in from the list.")}</Selo>
      )}
      {erro && <Aviso>{erro}</Aviso>}
    </div>
  );
}
