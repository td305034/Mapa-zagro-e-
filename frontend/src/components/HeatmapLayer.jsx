import { useEffect } from "react";
import { useMap } from "react-leaflet";
import "leaflet.heat";
import L from "leaflet";

export default function HeatmapLayer({ risks }) {
  const map = useMap();

  useEffect(() => {
    if (!risks.length) return;

    const points = risks.map((risk) => [risk.lat, risk.lng, risk.weight]);

    const heatLayer = L.heatLayer(points, {
      radius: 30,
      blur: 20,
      maxZoom: 15,
      max: 5,
      gradient: {
        0.1: "#2166ac",
        0.15: "#67a9cf",
        0.2: "#fdae61",
        0.3: "#f46d43",
        0.4: "#d73027",
      },
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [risks, map]);

  return null;
}
