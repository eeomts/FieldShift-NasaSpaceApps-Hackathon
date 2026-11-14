import { useState } from "react";
import { api, ErroApi } from "../api/client";
import type { Interpretacao } from "../api/tipos";
import { Brilho } from "../components/icones";
import { Aviso, Selo } from "../components/ui";

/** Componente único das perguntas 8, 26a e 26b: texto livre -> IA -> lista para confirmar. */
export function TextoLivre({
  campo,
  rotulo,
  exemplo,
  texto,
  onTexto,
  onResultado,
}: {
  campo: "culturas" | "excluidas" | "equipamentos";
  rotulo: string;
  exemplo: string;
  texto: string;
  onTexto: (t: string) => void;
  onResultado: (r: Interpretacao) => void;
}) {
  const [estado, setEstado] = useState<"parado" | "lendo">("parado");
  const [fonte, setFonte] = useState<Interpretacao["fonte"] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function separar() {
    setEstado("lendo");
    setErro(null);
    try {
      const r = await api<Interpretacao>("/onboarding/interpretar", { method: "POST", body: { campo, texto } });
      setFonte(r.fonte);
      onResultado(r);
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não deu para ler o texto agora. Escolha pela lista abaixo.");
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
      <button
        type="button"
        onClick={separar}
        disabled={!texto.trim() || estado === "lendo"}
        className="flex h-12 items-center justify-center gap-2 rounded-2xl bg-sol px-4 text-[15px] font-bold text-tinta shadow-degrau-sol transition-transform active:translate-y-[3px] disabled:opacity-50"
      >
        <Brilho size={18} />
        {estado === "lendo" ? "Lendo…" : "Separar com a AgroIA"}
      </button>
      {fonte === "ia" && <Selo tom="folha"><Brilho size={14} /> A AgroIA entendeu. Confere abaixo?</Selo>}
      {fonte === "lista" && <Selo>A IA não está disponível agora. Achamos pelo nome; confira e complete pela lista.</Selo>}
      {erro && <Aviso>{erro}</Aviso>}
    </div>
  );
}
