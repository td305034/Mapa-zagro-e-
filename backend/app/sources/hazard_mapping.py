import re

from app.models import HazardCategory

def normalize(text: str) -> str:
    """Usuwa nadmiarowe białe znaki, przycina, ujednolica przed dopasowaniem."""
    return re.sub(r"\s+", " ", text).strip()

RISK_TYPE_TO_HAZARD = {
    "Bezpieczeństwo publiczne": HazardCategory.CRITICAL_SUPPLY,
    "Bezpieczeństwo dostaw paliw": HazardCategory.CRITICAL_SUPPLY,
    "Zagrożenie budowlane": HazardCategory.STRUCTURAL,
    "Grozi zawaleniem": HazardCategory.STRUCTURAL,
    "Grozi zawaleniem, wandalizm": HazardCategory.STRUCTURAL,
    "Grozi zawaleniem (teren ogrodzony)": HazardCategory.STRUCTURAL,
    "Niebezpieczne zachowania na drodze (wyścigi)": HazardCategory.TRAFFIC,
    "Możliwa kolizja": HazardCategory.TRAFFIC,
    "Niski przejazd, utrudnienie w dotarciu służb": HazardCategory.TRAFFIC,
    "Niewłaściwe parkowanie utrudniające dojazd": HazardCategory.TRAFFIC,
    "Zagrożenie w ruchu drogowym": HazardCategory.TRAFFIC,
    "Zagrożenie pożarowe": HazardCategory.FIRE,
    "Możliwość podtopień posesji na ul. 1 Maja": HazardCategory.FLOOD,
    "Możliwość tworzenia się zatoru na rzece": HazardCategory.FLOOD,
    "Brak możliwości sterowania przepływami wody": HazardCategory.FLOOD,
    "Możliwość sterowania poziomem akwenu": HazardCategory.FLOOD,
    "Możliwosć zatoru i podtopień": HazardCategory.FLOOD,
    "Zagrożenie powodziowe": HazardCategory.FLOOD,
    "Możliwość podtopień": HazardCategory.FLOOD,
    "Gromadzenie się młodzieży, wandalizm": HazardCategory.CRIME,
    "Nielegalne wysypywanie śmieci": HazardCategory.ENVIRONMENTAL,
}

def get_hazard_category(risk_type_raw: str) -> HazardCategory | None:
    key = normalize(risk_type_raw)
    hazard = RISK_TYPE_TO_HAZARD.get(key)
    if hazard is None:
        # ważne: nie zgaduj, zaloguj brak dopasowania, żeby świadomie uzupełnić mapowanie
        print(f"UWAGA: brak mapowania hazard_category dla: '{key}'")
    return hazard