import pandas as pd
from pathlib import Path

# =========================
# FUNKCJE
# =========================

def detect_response(opis):

    opis = str(opis).lower()

    if any(x in opis for x in [
        "brak aktywnej metabolicznie choroby",
        "brak aktywnych zmian",
        "brak aktywnego procesu chłoniakowego",
        "całkowita remisja",
        "brak cech aktywnego procesu"
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


def lugano(response):

    mapping = {
        "CR": "Complete Response",
        "PR": "Partial Response",
        "SD": "Stable Disease",
        "PD": "Progressive Disease"
    }

    return mapping.get(response, "Unknown")


def deauville(response):

    mapping = {
        "CR": 3,
        "PR": 4,
        "SD": 4,
        "PD": 5
    }

    return mapping.get(response, None)


# =========================
# WCZYTANIE PLIKÓW
# =========================

folder = Path("pacjenci")

all_data = []

for file in folder.glob("*.xlsx"):

    print(f"Wczytuję: {file.name}")

    df = pd.read_excel(file)

    name = file.stem

    name = (
        name.replace("_PET", "")
        .replace("_standard", "")
        .replace("_uzupelniony", "")
        .replace("_Podsumowanie_DATY", "")
        .replace("_Podsumowanie", "")
    )

    df["Pacjent"] = name.replace("_", " ")

    all_data.append(df)

if not all_data:
    raise ValueError("Brak plików Excel w folderze pacjenci")

# =========================
# ŁĄCZENIE DANYCH
# =========================

master_df = pd.concat(all_data, ignore_index=True)

# =========================
# DATY
# =========================

master_df["Data badania"] = pd.to_datetime(
    master_df["Data badania"],
    dayfirst=True,
    errors="coerce"
)
# Czyszczenie SUVmax

master_df["SUVmax"] = (
    master_df["SUVmax"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

master_df["SUVmax"] = pd.to_numeric(
    master_df["SUVmax"],
    errors="coerce"
)
# =========================
# OCENA ODPOWIEDZI
# =========================

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

# =========================
# PODSUMOWANIE
# =========================

liczba_pacjentow = master_df["Pacjent"].nunique()
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
# CHARAKTERYSTYKA
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
# ANALIZA SUVMAX
# =========================

suv_summary = (
    master_df
    .sort_values(["Pacjent", "Data badania"])
    .groupby("Pacjent")
    .agg(
        SUVmax_pierwszy=("SUVmax", "first"),
        SUVmax_ostatni=("SUVmax", "last")
    )
)

suv_summary["Zmiana_%"] = (
    (
        suv_summary["SUVmax_ostatni"]
        - suv_summary["SUVmax_pierwszy"]
    )
    / suv_summary["SUVmax_pierwszy"]
) * 100

suv_summary["Trend"] = suv_summary["Zmiana_%"].apply(
    lambda x: "Progresja" if x > 0 else "Poprawa"
)

print("\n===== ANALIZA SUVMAX =====")
print(suv_summary.round(2))
# =========================
# OSTATNI PET PACJENTA
# =========================

patient_status = (
    master_df
    .sort_values(["Pacjent", "Data badania"])
    .groupby("Pacjent")
    .tail(1)
)

print("\n===== ROZKŁAD ODPOWIEDZI =====")
print(master_df["Ocena odpowiedzi"].value_counts())

print("\n===== OSTATNI WYNIK PACJENTA =====")
print(
    patient_status[
        ["Pacjent", "Ocena odpowiedzi", "Lugano", "Deauville"]
    ].to_string(index=False)
)
print("\n===== SUVMAX =====")
print(
    master_df[
        ["Pacjent", "Nr PET", "SUVmax"]
    ].head(50)
)
# =========================
# ZAPIS EXCEL
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
    suv_summary.to_excel(
        writer,
        sheet_name="SUVmax"
    )

    patient_status.to_excel(
        writer,
        sheet_name="Ostatni_wynik",
        index=False
    )

print("\nZapisano: Wyniki_HUBA.xlsx")