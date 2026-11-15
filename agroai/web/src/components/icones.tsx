// Ícones de traço, como no protótipo (sem emoji).
type P = { size?: number; className?: string };
const base = (size = 20) => ({
  width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor",
  strokeWidth: 2.2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true,
});

export const Seta = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></svg>);
export const Voltar = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M19 12H5" /><path d="m11 18-6-6 6-6" /></svg>);
export const Brilho = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" /><path d="M19 17l.8 2.2L22 20l-2.2.8L19 23l-.8-2.2L16 20l2.2-.8z" /></svg>);
export const Pino = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" /></svg>);
export const Mira = ({ size, className }: P) => (<svg {...base(size)} className={className}><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M2 12h3M19 12h3" /></svg>);
export const Check = ({ size, className }: P) => (<svg {...base(size)} className={className} strokeWidth={2.6}><path d="M20 6 9 17l-5-5" /></svg>);
export const Xis = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M18 6 6 18M6 6l12 12" /></svg>);
export const Mais = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M12 5v14M5 12h14" /></svg>);
export const Satelite = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M13 7 9 3 5 7l4 4" /><path d="m17 11 4 4-4 4-4-4" /><path d="m8 12 4 4 6-6-4-4Z" /><path d="m16 8 3-3" /><path d="M9 21a6 6 0 0 0-6-6" /></svg>);
export const Broto = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M7 20h10" /><path d="M10 20c5.5-2.5.8-6.4 3-10" /><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z" /><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z" /></svg>);
export const Painel = ({ size, className }: P) => (<svg {...base(size)} className={className}><rect x="3" y="3" width="7" height="9" rx="2" /><rect x="14" y="3" width="7" height="5" rx="2" /><rect x="14" y="12" width="7" height="9" rx="2" /><rect x="3" y="16" width="7" height="5" rx="2" /></svg>);
export const Sair = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="m16 17 5-5-5-5" /><path d="M21 12H9" /></svg>);

/** Ícones das opções do questionário (traço simples, sem emoji). */
const CAMINHOS: Record<string, string> = {
  yes: "M20 6 9 17l-5-5",
  no: "M18 6 6 18M6 6l12 12",
  idk: "M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01",
  farmer: "M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM4.5 21a7.5 7.5 0 0 1 15 0M6 6.5h12",
  helper: "M9 2h6v4H9zM16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 14l2 2 4-4",
  part: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 3v18M12 3a9 9 0 0 1 0 18",
  cow: "M4 6c0 2 1 3 3 3M20 6c0 2-1 3-3 3M7 9h10v6a5 5 0 0 1-10 0zM10 13h.01M14 13h.01M10 17h4",
  pause: "M8 5v14M16 5v14",
  sprout: "M7 20h10M12 20v-8M12 12c0-3-2-5-6-5 0 3 2 5 6 5zM12 14c0-3 2-5 6-5 0 3-2 5-6 5z",
  flask: "M10 2v7.5L4.5 19a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9.5V2M8.5 2h7M7 16h10",
  snow: "M12 2v20M4.9 7l14.2 10M19.1 7 4.9 17",
  rain: "M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3M8 19v2M8 13v2M16 19v2M16 13v2M12 21v2M12 15v2",
  flood: "M2 8c2-2 4-2 6 0s4 2 6 0 4-2 6 0M2 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0M2 20c2-2 4-2 6 0s4 2 6 0 4-2 6 0",
  hail: "M20 14.6A5 5 0 0 0 18 5h-1.3A8 8 0 1 0 4 13.3M8 18h.01M12 20h.01M16 18h.01M10 16h.01M14 16h.01",
  sun: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  dry: "M12 22a7 7 0 0 0 7-7c0-4-7-13-7-13S5 11 5 15a7 7 0 0 0 7 7zM3 3l18 18",
  salt: "M8 21h8V10H8zM9 10V6h6v4M10 3h4v3h-4zM11 14h2M11 17h2",
  worm: "M3 15c3-6 6 2 9-4s6 2 9-4M20 5h.01",
  crack: "M13 2 9 9l5 3-4 6 3 4",
  area: "M3 3h18v18H3zM3 12h18M12 3v18",
};

export function IconeOpcao({ nome, size = 22, className }: { nome: string; size?: number; className?: string }) {
  return (
    <svg {...base(size)} className={className}>
      <path d={CAMINHOS[nome] ?? CAMINHOS.idk} />
    </svg>
  );
}

export const Lupa = ({ size, className }: P) => (<svg {...base(size)} className={className}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>);
export const Enviar = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="m22 2-7 20-4-9-9-4z" /><path d="M22 2 11 13" /></svg>);
export const Lixeira = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v6M14 11v6" /></svg>);
export const Trocar = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="m17 3 4 4-4 4" /><path d="M3 7h18" /><path d="m7 21-4-4 4-4" /><path d="M21 17H3" /></svg>);
export const Globo = ({ size, className }: P) => (<svg {...base(size)} className={className}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" /></svg>);
export const Conversas = ({ size, className }: P) => (<svg {...base(size)} className={className}><path d="M21 12a8 8 0 0 1-11.6 7.1L3 21l1.9-5.4A8 8 0 1 1 21 12z" /></svg>);
