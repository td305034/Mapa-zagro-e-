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
      <aside className="app-sidebar">
        <LayerControls
          selectedCategories={selectedCategories}
          onChange={setSelectedCategories}
        />
      </aside>
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
