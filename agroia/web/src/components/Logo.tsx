import { Broto } from "./icones";

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-[34px] w-[34px] items-center justify-center rounded-xl bg-folha text-white">
        <Broto />
      </div>
      <span className="font-titulo text-[22px] font-extrabold tracking-[-0.02em]">AgroIA</span>
    </div>
  );
}
