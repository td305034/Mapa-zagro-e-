import L from "leaflet";
import { HAZARD_CATEGORIES } from "../config/hazardCategories";

const SIZE = 40;
const RADIUS = 16;
const STROKE_WIDTH = 8;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function createClusterIcon(cluster) {
  const childMarkers = cluster.getAllChildMarkers();
  const total = childMarkers.length;

  const counts = {};
  childMarkers.forEach((marker) => {
    const category = marker.options.riskData?.hazardCategory;
    if (category) {
      counts[category] = (counts[category] || 0) + 1;
    }
  });

  let offset = 0;
  const segments = Object.entries(counts)
    .map(([category, count]) => {
      const fraction = count / total;
      const dashLength = fraction * CIRCUMFERENCE;
      const segment = `
        <circle
          cx="${SIZE / 2}" cy="${SIZE / 2}" r="${RADIUS}"
          fill="none"
          stroke="${HAZARD_CATEGORIES[category]?.color || "#999"}"
          stroke-width="${STROKE_WIDTH}"
          stroke-dasharray="${dashLength} ${CIRCUMFERENCE - dashLength}"
          stroke-dashoffset="${-offset}"
          transform="rotate(-90 ${SIZE / 2} ${SIZE / 2})"
        />
      `;
      offset += dashLength;
      return segment;
    })
    .join("");

  const html = `
    <div style="position: relative; width: ${SIZE}px; height: ${SIZE}px;">
      <svg width="${SIZE}" height="${SIZE}">
        ${segments}
      </svg>
      <div style="
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: bold; color: #333;
      ">${total}</div>
    </div>
  `;

  return L.divIcon({
    html,
    className: "custom-cluster-icon",
    iconSize: L.point(SIZE, SIZE),
  });
}
