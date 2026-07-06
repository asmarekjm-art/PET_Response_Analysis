import pandas as pd
from pathlib import Path

# ==========================================
# KONFIGURACJA
# ==========================================

PACJENCI_DIR = Path("pacjenci")
OUTPUT_FILE = Path("source/pet_details.xlsx")

# ==========================================
# KOLUMNY DO POBRANIA
# ==========================================

REQUIRED_COLUMNS = [
    "Nr PET",
    "Problem kliniczny",
    "Glikemia",
    "Czas po FDG",
    "SUVmax_global",
    "Głowa i szyja",
    "Klatka piersiowa",
    "Brzuch i miednica",
    "Układ kostny"
]

# ==========================================
# GŁÓWNA PĘTLA
# ==========================================

results = []

pliki = sorted(PACJENCI_DIR.glob("*.xlsx"))

print(f"\nZnaleziono {len(pliki)} plików pacjentów\n")

for plik in pliki:

    try:

        df = pd.read_excel(plik)

        pacjent = plik.stem

        missing = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing:
            print(
                f"Pominięto {plik.name} - brak kolumn: {missing}"
            )
            continue

        for _, row in df.iterrows():

            results.append({
                "Pacjent": pacjent,
                "Nr PET": row.get("Nr PET"),
                "Problem_kliniczny": row.get("Problem kliniczny"),
                "Glikemia": row.get("Glikemia"),
                "Czas_po_FDG": row.get("Czas po FDG"),
                "SUVmax_global": row.get("SUVmax_global"),
                "Glowa_i_szyja": row.get("Głowa i szyja"),
                "Klatka_piersiowa": row.get("Klatka piersiowa"),
                "Brzuch_i_miednica": row.get("Brzuch i miednica"),
                "Uklad_kostny": row.get("Układ kostny")
            })

    except Exception as e:

        print(
            f"Błąd podczas przetwarzania {plik.name}: {e}"
        )

# ==========================================
# ZAPIS
# ==========================================

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
print("PET DETAILS")
print("=" * 60)
print(f"Liczba rekordów: {len(result_df)}")
print(f"Zapisano: {OUTPUT_FILE}")
print("=" * 60)