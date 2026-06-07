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
def detect_response(opis):
    return "CR"

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

#LUGANO
# Automatyczna ocena odpowiedzi z opisu PET

master_df["Ocena odpowiedzi"] = (
    master_df["Opis"]
    .apply(detect_response)
)

master_df["Lugano"] = (
    master_df["Ocena odpowiedzi"]
    .apply(lugano)
)

master_df["Deauville"] = (
    master_df["Ocena odpowiedzi"]
    .apply(deauville)
)
def detect_response(opis):

    opis = str(opis).lower()

    if any(x in opis for x in [
        "brak aktywnej metabolicznie choroby",
        "brak aktywnego procesu chłoniakowego",
        "brak aktywnych zmian",
        "całkowita remisja"
    ]):
        return "CR"

    if any(x in opis for x in [
        "częściowa regresja",
        "znaczna regresja",
        "bardzo dobra odpowiedź",
        "dobra odpowiedź",
        "regresja zmian"
    ]):
        return "PR"

    if any(x in opis for x in [
        "stabilizacja",
        "bez istotnej zmiany",
        "utrzymują się zmiany"
    ]):
        return "SD"

    if any(x in opis for x in [
        "progresja",
        "wznowa",
        "nowe zmiany",
        "nawrót"
    ]):
        return "PD"

    return "Nieokreślone"
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

patient_status = (
    master_df
    .sort_values("Data badania")
    .groupby("Pacjent")
    .tail(1)
)

patient_status = patient_status[
    ["Pacjent", "Ocena odpowiedzi", "Lugano", "Deauville"]
]

print("\n===== OSTATNI WYNIK PACJENTA =====")
print(patient_status)
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
patient_status.to_excel(
    writer,
    sheet_name="Ostatni_wynik",
    index=False
)

print("\nZapisano: Wyniki_HUBA.xlsx")