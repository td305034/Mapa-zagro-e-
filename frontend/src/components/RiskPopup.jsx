import { HAZARD_CATEGORIES } from "../config/hazardCategories";
import { RISK_STATUS_LABELS } from "../config/riskStatus";

export default function RiskPopup({ risk }) {
  const hazardCategory = HAZARD_CATEGORIES[risk.hazard_category];
  const status = RISK_STATUS_LABELS[risk.status];

  return (
    <div className="risk-popup">
      <div className="risk-popup-category">
        <span
          className="risk-popup-category-swatch"
          style={{ backgroundColor: hazardCategory?.color ?? "#999999" }}
        />
        {hazardCategory?.label ?? risk.hazard_category}
      </div>
      <p className="risk-popup-type">{risk.risk_type}</p>
      <p className="risk-popup-main-category">{risk.main_category}</p>
      {risk.address && <p className="risk-popup-address">{risk.address}</p>}
      <div className="risk-popup-status">
        <span
          className="risk-popup-status-badge"
          style={{ backgroundColor: status?.color ?? "#999999" }}
        />
        {status?.label ?? risk.status}
      </div>
      {risk.source && <p className="risk-popup-source">Źródło: {risk.source}</p>}
    </div>
  );
}
