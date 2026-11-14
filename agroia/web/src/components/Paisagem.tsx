import { Satelite } from "./icones";

/** Ilustração do topo da tela de entrada (morros, sol e plantinhas), igual ao protótipo. */
export function Paisagem({ altura = 300 }: { altura?: number }) {
  return (
    <div className="relative shrink-0 overflow-hidden rounded-b-[44px] bg-folha-clara" style={{ height: altura }} aria-hidden="true">
      <div className="absolute top-10 right-10 h-[150px] w-[150px] rounded-full bg-sol shadow-[0_0_0_18px_rgba(255,194,61,0.25)]" />
      <div className="absolute top-16 left-8 flex -rotate-4 items-center gap-2 rounded-full bg-white py-2 pr-3.5 pl-2.5 shadow-[0_10px_24px_-10px_rgba(29,43,34,0.35)]">
        <Satelite className="text-folha" />
        <span className="text-[13px] font-bold">Dados da NASA</span>
      </div>
      <div className="absolute -bottom-[120px] -left-[60px] h-[230px] w-[330px] rounded-[50%] bg-morro" />
      <div className="absolute -right-[90px] -bottom-[140px] h-[250px] w-[380px] rounded-[50%] bg-folha" />
      <div className="absolute -bottom-[150px] left-[120px] h-[220px] w-[260px] rounded-[50%] bg-[#2C8C59]" />
      <div className="absolute bottom-12 left-[150px] flex -rotate-6 gap-2.5">
        {[34, 46, 30].map((h, i) => (
          <div key={i} className="w-2.5 rounded-md bg-creme opacity-85" style={{ height: h }} />
        ))}
      </div>
    </div>
  );
}
