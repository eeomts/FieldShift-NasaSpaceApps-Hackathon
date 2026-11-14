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
