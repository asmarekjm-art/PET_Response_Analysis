
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

    "Węzły chłonne szyjne": [
        "węzły chłonne szyjne",
        "węzły szyjne",
        "szyjne"
    ],

    "Węzły chłonne pachowe": [
        "węzły chłonne pachowe",
        "pachowe"
    ],

    "Węzły chłonne śródpiersia": [
        "śródpiersiu",
        "śródpiersia",
        "przytchawicze",
        "okna aortalno-płucnego",
        "podostrogowe"
    ],

    "Węzły chłonne pachwinowe": [
        "pachwinowe"
    ],

    "Węzły chłonne zaotrzewnowe": [
        "okołoaortal",
        "zaotrzewnow",
        "przyaortal"
    ],

    "Węzły chłonne krezkowe": [
        "krezkowe"
    ],

    "Śledziona": [
        "śledzion"
    ],

    "Wątroba": [
        "wątrob",
        "watrob"
    ],

    "Żołądek": [
        "żołądk",
        "zoladk",
        "wpust",
        "dno żołądka"
    ],

    "Płuca": [
        "płuc",
        "pluc"
    ],

    "Kości": [
        "kostn",
        "kości",
        "kosc"
    ],

    "Szpik": [
        "szpik"
    ],

    "Miednica": [
        "miednic"
    ],

    "Węzły chłonne wnęk": [
        "wnęki",
        "wneki"
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

    if not locations:

        if (
            "bardzo dobrą odpowiedź" in text
            or "bardzo dobra odpowiedź" in text
            or "całkowita odpowiedź" in text
            or "brak aktywnej choroby" in text
            or "nie uwidoczniono" in text
        ):
            return "Brak aktywnej choroby"

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

for _, row in result_df[
    result_df["Lokalizacja_zmian"] == "Nieokreślona"
].head(10).iterrows():
    print("\n" + "=" * 80)
    print(row["Pacjent"])
    print(row["Nr PET"])
