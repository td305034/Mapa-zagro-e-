import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  GeoJSON,
  ZoomControl,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import { HAZARD_CATEGORIES } from "../config/hazardCategories";
import { createClusterIcon } from "../utils/clusterIcon";
import RiskPopup from "./RiskPopup";
import powiatBoundaryRaw from "../assets/powiat-kedzierzynsko-kozielski.geojson?raw";

const powiatBoundary = JSON.parse(powiatBoundaryRaw);

const KEDZIERZYN_KOZLE_CENTER = [50.32, 18.1];
const DEFAULT_ZOOM = 11;
const MIN_ZOOM = 10;

const POWIAT_BOUNDS = L.geoJSON(powiatBoundary).getBounds();

const boundaryStyle = {
  color: "#2c3e50",
  weight: 2,
  fill: false,
};

const iconCache = {};

function getIconForCategory(hazardCategory, status) {
  const statusModifier = status === "verified" ? "verified" : "unverified";
  const cacheKey = `${hazardCategory}|${statusModifier}`;
  if (iconCache[cacheKey]) {
    return iconCache[cacheKey];
  }

  const color = HAZARD_CATEGORIES[hazardCategory]?.color ?? "#999999";

  const icon = L.divIcon({
    className: "",
    html: `<span class="risk-marker risk-marker--${statusModifier}" style="
      display: block;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: ${color};
      box-shadow: 0 0 2px rgba(0,0,0,0.6);
    "></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  iconCache[cacheKey] = icon;
  return icon;
}

export default function Map({ risks }) {
  return (
    <MapContainer
      center={KEDZIERZYN_KOZLE_CENTER}
      zoom={DEFAULT_ZOOM}
      minZoom={MIN_ZOOM}
      maxBounds={POWIAT_BOUNDS}
      maxBoundsViscosity={1.0}
      zoomControl={false}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ZoomControl position="bottomright" />
      <GeoJSON data={powiatBoundary} style={boundaryStyle} />
      <MarkerClusterGroup
        chunkedLoading
        showCoverageOnHover={false}
        spiderfyOnMaxZoom={true}
        maxClusterRadius={50}
        iconCreateFunction={createClusterIcon}
      >
        {risks.map((risk) => (
          <Marker
            key={risk.id}
            position={[risk.lat, risk.lng]}
            icon={getIconForCategory(risk.hazard_category, risk.status)}
            riskData={{ hazardCategory: risk.hazard_category }}
          >
            <Popup>
              <RiskPopup risk={risk} />
            </Popup>
          </Marker>
        ))}
      </MarkerClusterGroup>
    </MapContainer>
  );
}
