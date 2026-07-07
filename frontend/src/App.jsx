import { useState, useEffect, useMemo } from "react";
import "./App.css";
import { getRisks } from "./api/client";
import { HAZARD_CATEGORIES } from "./config/hazardCategories";
import Map from "./components/Map";
import LayerControls from "./components/LayerControls";

function App() {
  const [risks, setRisks] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState(
    () => new Set(Object.keys(HAZARD_CATEGORIES))
  );
  const [error, setError] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  useEffect(() => {
    getRisks()
      .then(setRisks)
      .catch((err) => setError(err.message));
  }, []);

  const filteredRisks = useMemo(
    () => risks.filter((risk) => selectedCategories.has(risk.hazard_category)),
    [risks, selectedCategories]
  );

  return (
    <div className="app-layout">
      <button
        type="button"
        className="hamburger-button"
        onClick={() => setIsPanelOpen((prev) => !prev)}
        aria-label="Przełącz panel kategorii zagrożeń"
      >
        ☰
      </button>
      <div className={`layer-panel ${isPanelOpen ? "layer-panel--open" : ""}`}>
        <LayerControls
          selectedCategories={selectedCategories}
          onChange={setSelectedCategories}
        />
      </div>
      <main className="app-map">
        {error ? (
          <p className="app-error">
            Nie udało się wczytać danych. Spróbuj odświeżyć stronę.
          </p>
        ) : (
          <Map risks={filteredRisks} />
        )}
      </main>
    </div>
  );
}

export default App;
