
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

    "Węzły szyjne": [
        "szyjne"
    ],

    "Węzły nadobojczykowe": [
        "nadobojczyk"
    ],

    "Węzły pachowe": [
        "pachowe"
    ],

    "Węzły śródpiersia": [
        "śródpiersi",
        "przytchawicze",
        "podostrogowe",
        "okna aortalno-płucnego"
    ],

    "Węzły wnęk": [
        "wnęki",
        "wnęk"
    ],

    "Węzły zaotrzewnowe": [
        "zaotrzewnow",
        "okołoaortal",
        "przyaortal"
    ],

    "Węzły krezkowe": [
        "krezk"
    ],

    "Węzły pachwinowe": [
        "pachwin"
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
        "zoladk"
    ],

    "Jelita": [
        "jelit",
        "okrężnic",
        "esica"
    ],

    "Trzustka": [
        "trzust"
    ],

    "Nerki": [
        "nerk"
    ],

    "Nadnercza": [
        "nadnercz"
    ],

    "Płuca": [
        "płuc",
        "pluc"
    ],

    "Opłucna": [
        "opłucn"
    ],

    "Kości": [
        "kostn",
        "kości",
        "kosc"
    ],

    "Szpik": [
        "szpik"
    ],

    "Tkanki miękkie": [
        "tkankach miękkich",
        "tkanki miękkie"
    ],

    "Miednica": [
        "miednic"
    ]
}


# =====================================
# DETEKCJA LOKALIZACJI
# =====================================
def classify_locations(wnioski):
    if pd.isna(wnioski):
        return "Brak danych"

    text = str(wnioski).lower()

    # brak aktywnej choroby
    if any(
            x in text
            for x in [
                "całkowita odpowiedź",
                "brak aktywnej choroby",
                "bardzo dobra odpowiedź",
                "nie uwidoczniono aktywnych",
                "bez cech aktywnej choroby"
            ]
    ):
        return "Brak aktywnej choroby"

    if pd.isna(wnioski):
        return "Brak danych"

    text = str(wnioski).lower()

    locations = []

    for location, keywords in LOCATION_RULES.items():

        if any(word in text for word in keywords):
            locations.append(location)


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
            full_text = " ".join([

                str(row.get("Głowa i szyja", "") or ""),
                str(row.get("Klatka piersiowa", "") or ""),
                str(row.get("Brzuch i miednica", "") or ""),
                str(row.get("Układ kostny", "") or ""),
                str(row.get("Wnioski", "") or "")

            ])

            results.append({
                "Pacjent": patient,
                "Nr PET": row["Nr PET"],
                "Lokalizacja_zmian": classify_locations(
                    full_text
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
