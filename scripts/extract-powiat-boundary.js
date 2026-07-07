// Jednorazowy skrypt: wyciąga granice powiatu kędzierzyńsko-kozielskiego
// z pełnego pliku powiaty.json (Geoportal, public domain) i zapisuje jako
// osobny, mały plik GeoJSON używany przez frontend.
//
// Użycie: node scripts/extract-powiat-boundary.js <ścieżka-do-powiaty.json>

const fs = require("fs");
const path = require("path");

const sourcePath = process.argv[2];
if (!sourcePath) {
  console.error("Podaj ścieżkę do pliku powiaty.json jako argument.");
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(sourcePath, "utf8"));

const feature = data.features.find((f) =>
  (f.properties.JPT_NAZWA_ || "").toLowerCase().includes("kędzierzyńsko-kozielski")
);

if (!feature) {
  console.error("Nie znaleziono powiatu kędzierzyńsko-kozielskiego w pliku źródłowym.");
  process.exit(1);
}

const output = {
  type: "FeatureCollection",
  features: [feature],
};

const outputPath = path.join(
  __dirname,
  "..",
  "frontend",
  "src",
  "assets",
  "powiat-kedzierzynsko-kozielski.geojson"
);

fs.writeFileSync(outputPath, JSON.stringify(output));
console.log(`Zapisano ${outputPath}`);
console.log("Właściwości:", feature.properties);
