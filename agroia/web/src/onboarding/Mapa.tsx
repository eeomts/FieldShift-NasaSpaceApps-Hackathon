import L from "leaflet";
import { useEffect, useState } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import { Mira, Pino } from "../components/icones";
import { BotaoContorno } from "../components/ui";

const pino = L.divIcon({
  className: "",
  iconSize: [44, 52],
  iconAnchor: [22, 50],
  html: `<div style="width:44px;height:44px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:#1F7A4D;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 20px -6px rgba(21,92,57,.6)"><div style="width:16px;height:16px;border-radius:50%;background:#FFC23D"></div></div>`,
});

type Ponto = { lat: number; lon: number };

function Cliques({ onPick }: { onPick: (p: Ponto) => void }) {
  useMapEvents({ click: (e) => onPick({ lat: e.latlng.lat, lon: e.latlng.lng }) });
  return null;
}

function Voar({ alvo }: { alvo: Ponto | null }) {
  const map = useMap();
  useEffect(() => {
    if (alvo) map.flyTo([alvo.lat, alvo.lon], Math.max(map.getZoom(), 13), { duration: 0.8 });
  }, [alvo, map]);
  return null;
}

const arred = (n: number) => Math.round(n * 1e5) / 1e5;
const fmt = (n: number) => n.toFixed(4).replace(".", ",") + "°";

export function Mapa({ valor, onChange }: { valor: Ponto | null; onChange: (p: Ponto) => void }) {
  const [voarPara, setVoarPara] = useState<Ponto | null>(null);
  const [gps, setGps] = useState<"parado" | "buscando" | "erro">("parado");

  const escolher = (p: Ponto) => onChange({ lat: arred(p.lat), lon: arred(p.lon) });

  function usarGps() {
    if (!navigator.geolocation) return setGps("erro");
    setGps("buscando");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const p = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        escolher(p);
        setVoarPara(p);
        setGps("parado");
      },
      () => setGps("erro"),
      { enableHighAccuracy: true, timeout: 15000 },
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="h-[300px] overflow-hidden rounded-[28px] shadow-[inset_0_0_0_2px_#C7E8D2]">
        <MapContainer
          center={valor ? [valor.lat, valor.lon] : [10, 0]}
          zoom={valor ? 13 : 2}
          worldCopyJump
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Cliques onPick={escolher} />
          <Voar alvo={voarPara} />
          {valor && <Marker position={[valor.lat, valor.lon]} icon={pino} />}
        </MapContainer>
      </div>
      {valor ? (
        <div className="flex items-center gap-3 rounded-[20px] bg-white px-4 py-3.5 shadow-cartao">
          <Pino className="shrink-0 text-folha" />
          <div className="flex flex-col">
            <span className="text-[15px] font-bold">Ponto marcado</span>
            <span className="text-[13px] text-suave">{fmt(valor.lat)} · {fmt(valor.lon)}</span>
          </div>
        </div>
      ) : (
        <span className="text-[13px] font-bold text-suave">Toque no mapa no meio do seu campo, ou use o GPS.</span>
      )}
      <BotaoContorno type="button" onClick={usarGps} disabled={gps === "buscando"}>
        <Mira size={18} /> {gps === "buscando" ? "Procurando…" : "Usar meu GPS"}
      </BotaoContorno>
      {gps === "erro" && <span className="text-[13px] text-[#8C1D18]">Não conseguimos o GPS. Toque no mapa.</span>}
    </div>
  );
}
