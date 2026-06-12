
import pandas as pd
from pathlib import Path

# =====================================
# KONFIGURACJA
# =====================================

PACJENCI_DIR = Path("pacjenci")
OUTPUT_FILE = Path("source/locations.xlsx")

# =====================================
# SŁOWNIK LOKALIZACJI
# =====================================

LOCATION_RULES = {
    "Śródpiersie": [
        "śródpiersi",
        "srodpiersi"
    ],

    "Płuco": [
        "płuc",
        "pluc"
    ],

    "Węzły": [
        "węzł",
        "wezl"
    ],

    "Śledziona": [
        "śledzion",
        "sledzion"
    ],

    "Wątroba": [
        "wątrob",
        "watrob"
    ],

    "Kości": [
        "kości",
        "kosc",
        "kostn",
        "szpik"
    ],

    "Żołądek": [
        "żołądk",
        "zoladk",
        "wpust",
        "dno żołądka"
    ],

    "Jelita": [
        "jelit"
    ],

    "Miednica": [
        "miednic"
    ],

    "Pachy": [
        "pachow"
    ],

    "Szyja": [
        "szyjn",
        "nadobojczyk"
    ]
}

# =====================================
# DETEKCJA LOKALIZACJI
# =====================================

def classify_locations(wnioski):

    if pd.isna(wnioski):
        return "Brak danych"

    text = str(wnioski).lower()

    locations = []

    for location, keywords in LOCATION_RULES.items():

        if any(word in text for word in keywords):
            locations.append(location)

    # brak aktywnej choroby
    if (
        "bardzo dobrą odpowiedź" in text
        or "bardzo dobra odpowiedź" in text
        or "całkowita odpowiedź" in text
        or "brak aktywnej choroby" in text
        or "nie uwidoczniono" in text
    ):
        return "Brak aktywnej choroby"

    if not locations:
        return "Nieokreślona"

    return ", ".join(sorted(set(locations)))

# =====================================
# GŁÓWNA PĘTLA
# =====================================

results = []

for file in sorted(PACJENCI_DIR.glob("*.xlsx")):

    try:

        df = pd.read_excel(file)

        if "Wnioski" not in df.columns:
            continue

        patient = file.stem

        for _, row in df.iterrows():

            results.append({
                "Pacjent": patient,
                "Nr PET": row["Nr PET"],
                "Lokalizacja_zmian": classify_locations(
                    row["Wnioski"]
                )
            })

    except Exception as e:

        print(f"Błąd {file.name}: {e}")

# =====================================
# ZAPIS
# =====================================

result_df = pd.DataFrame(results)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

result_df.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("LOCATIONS")
print("=" * 60)
print(f"Rekordów: {len(result_df)}")
print(f"Zapisano: {OUTPUT_FILE}")
print("=" * 60)