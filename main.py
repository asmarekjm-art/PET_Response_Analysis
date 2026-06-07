import pandas as pd
from pathlib import Path

# =========================
# FUNKCJE
# =========================

def lugano(response):

    mapping = {
        "CR": "Complete Response",
        "PR": "Partial Response",
        "SD": "Stable Disease",
        "PD": "Progressive Disease"
    }

    return mapping.get(str(response).strip(), "Unknown")


def deauville(response):

    mapping = {
        "CR": 3,
        "PR": 4,
        "SD": 4,
        "PD": 5
    }

    return mapping.get(str(response).strip(), None)


# =========================
# WCZYTANIE PLIKÓW
# =========================

folder = Path("pacjenci")

all_data = []

for file in folder.glob("*.xlsx"):

    print(f"Wczytuję: {file.name}")

    df = pd.read_excel(file)

    df["Pacjent"] = file.stem

    all_data.append(df)

# =========================
# POŁĄCZENIE DANYCH
# =========================

master_df = pd.concat(all_data, ignore_index=True)

# =========================
# LUGANO I DEAUVILLE
# =========================

master_df["Lugano"] = (
    master_df["Ocena odpowiedzi"]
    .apply(lugano)
)

master_df["Deauville"] = (
    master_df["Ocena odpowiedzi"]
    .apply(deauville)
)

# =========================
# STATYSTYKI
# =========================

liczba_pacjentow = (
    master_df["Pacjent"]
    .nunique()
)

liczba_pet = len(master_df)

print("\n===== PODSUMOWANIE =====")
print(f"Liczba pacjentów: {liczba_pacjentow}")
print(f"Liczba badań PET: {liczba_pet}")

# =========================
# PET NA PACJENTA
# =========================

pet_per_patient = (
    master_df
    .groupby("Pacjent")["Nr PET"]
    .count()
)

print("\n===== PET NA PACJENTA =====")
print(pet_per_patient)

# =========================
# CHARAKTERYSTYKA PACJENTÓW
# =========================

summary = (
    master_df
    .groupby("Pacjent")
    .agg(
        liczba_pet=("Nr PET", "count"),
        pierwsze_badanie=("Data badania", "min"),
        ostatnie_badanie=("Data badania", "max")
    )
)

print("\n===== CHARAKTERYSTYKA =====")
print(summary)

# =========================
# ZAPIS
# =========================

with pd.ExcelWriter("Wyniki_HUBA.xlsx") as writer:

    master_df.to_excel(
        writer,
        sheet_name="Badania",
        index=False
    )

    summary.to_excel(
        writer,
        sheet_name="Pacjenci"
    )

print("\nZapisano: Wyniki_HUBA.xlsx")