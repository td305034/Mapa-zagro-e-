import { MapContainer, TileLayer, Marker } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { HAZARD_CATEGORIES } from "../config/hazardCategories";

const KEDZIERZYN_KOZLE_CENTER = [50.32, 18.1];
const DEFAULT_ZOOM = 11;

const iconCache = {};

function getIconForCategory(hazardCategory) {
  if (iconCache[hazardCategory]) {
    return iconCache[hazardCategory];
  }

  const color = HAZARD_CATEGORIES[hazardCategory]?.color ?? "#999999";

  const icon = L.divIcon({
    className: "",
    html: `<span style="
      display: block;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: ${color};
      border: 2px solid #ffffff;
      box-shadow: 0 0 2px rgba(0,0,0,0.6);
    "></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  iconCache[hazardCategory] = icon;
  return icon;
}

export default function Map({ risks }) {
  return (
    <MapContainer
      center={KEDZIERZYN_KOZLE_CENTER}
      zoom={DEFAULT_ZOOM}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {risks.map((risk) => (
        <Marker
          key={risk.id}
          position={[risk.lat, risk.lng]}
          icon={getIconForCategory(risk.hazard_category)}
        />
      ))}
    </MapContainer>
  );
}
