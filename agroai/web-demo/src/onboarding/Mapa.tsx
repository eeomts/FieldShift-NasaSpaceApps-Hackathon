import L from "leaflet";
import { useEffect } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import { useIdioma } from "../i18n";

const pino = L.divIcon({
  className: "",
  iconSize: [44, 52],
  iconAnchor: [22, 50],
  html: `<div style="width:44px;height:44px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:#1F7A4D;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 20px -6px rgba(21,92,57,.6)"><div style="width:16px;height:16px;border-radius:50%;background:#FFC23D"></div></div>`,
});

export type Ponto = { lat: number; lon: number };

function Cliques({ onPick }: { onPick: (p: Ponto) => void }) {
  useMapEvents({ click: (e) => onPick({ lat: e.latlng.lat, lon: e.latlng.lng }) });
  return null;
}

/** `alvo.k` muda a cada pedido, para voar de novo até o mesmo ponto. */
function Voar({ alvo }: { alvo: (Ponto & { k: number }) | null }) {
  const map = useMap();
  useEffect(() => {
    if (alvo) map.flyTo([alvo.lat, alvo.lon], Math.max(map.getZoom(), 13), { duration: 0.8 });
  }, [alvo, map]);
  return null;
}

/** Mapa para marcar a propriedade (toque no mapa). A busca e o GPS ficam na tela do local. */
export function Mapa({ valor, onChange, voarPara }: { valor: Ponto | null; onChange: (p: Ponto) => void; voarPara: (Ponto & { k: number }) | null }) {
  const { t } = useIdioma();
  return (
    <div
      role="group"
      aria-label={t("Mapa: toque para marcar a sua propriedade", "Map: tap to mark your farm")}
      className="h-[260px] overflow-hidden rounded-[28px] shadow-[inset_0_0_0_2px_var(--color-campo)] lg:h-[420px]"
    >
      <MapContainer center={valor ? [valor.lat, valor.lon] : [10, 0]} zoom={valor ? 13 : 2} worldCopyJump style={{ height: "100%", width: "100%" }}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Cliques onPick={onChange} />
        <Voar alvo={voarPara} />
        {valor && <Marker position={[valor.lat, valor.lon]} icon={pino} />}
      </MapContainer>
    </div>
  );
}
