import { HAZARD_CATEGORIES } from "../config/hazardCategories";

export default function LayerControls({ selectedCategories, onChange }) {
  function toggleCategory(category) {
    const next = new Set(selectedCategories);
    if (next.has(category)) {
      next.delete(category);
    } else {
      next.add(category);
    }
    onChange(next);
  }

  function selectAll() {
    onChange(new Set(Object.keys(HAZARD_CATEGORIES)));
  }

  function deselectAll() {
    onChange(new Set());
  }

  return (
    <div className="layer-controls">
      <div className="layer-controls-actions">
        <button type="button" onClick={selectAll}>
          Zaznacz wszystkie
        </button>
        <button type="button" onClick={deselectAll}>
          Odznacz wszystkie
        </button>
      </div>
      <ul className="layer-controls-list">
        {Object.entries(HAZARD_CATEGORIES).map(([category, { label, color }]) => (
          <li key={category} className="layer-controls-item">
            <label>
              <input
                type="checkbox"
                checked={selectedCategories.has(category)}
                onChange={() => toggleCategory(category)}
              />
              <span
                className="layer-controls-swatch"
                style={{ backgroundColor: color }}
              />
              {label}
            </label>
          </li>
        ))}
      </ul>
    </div>
  );
}
