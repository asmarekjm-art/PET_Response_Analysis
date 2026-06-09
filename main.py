import pandas as pd
from pathlib import Path

# =========================
# FUNKCJE
# =========================

def detect_response(opis):

    opis = str(opis).lower()

    if any(x in opis for x in [
        "pełna odpowiedź metaboliczna",
        "całkowita odpowiedź metaboliczna",
        "complete response",
        "remisja metaboliczna",
        "brak patologicznego wychwytu fdg",
        "brak ognisk patologicznego wychwytu fdg",
        "nie uwidoczniono aktywnej choroby",
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

import re

def detect_deauville(opis):

    opis = str(opis).lower()

    patterns = [
        r"deauville\s*1",
        r"deauville\s*2",
        r"deauville\s*3",
        r"deauville\s*4",
        r"deauville\s*5"
    ]

    for pattern in patterns:
        match = re.search(pattern, opis)

        if match:
            return int(match.group()[-1])

    return None

def generate_summary(response, deauville_score):

    if response == "CR":
        return (
            f"Nie stwierdza się aktywnej metabolicznie choroby. "
            f"Uzyskano całkowitą odpowiedź metaboliczną na leczenie. "
            f"Klasyfikacja Lugano: Complete Response (CR), Deauville {deauville_score}."
        )

    elif response == "PR":
        return (
            f"Widoczna regresja zmian w porównaniu z poprzednim badaniem. "
            f"Nadal obecne są resztkowe ogniska aktywności metabolicznej. "
            f"Klasyfikacja Lugano: Partial Response (PR), Deauville {deauville_score}."
        )

    elif response == "SD":
        return (
            f"Obraz pozostaje stabilny względem poprzedniego badania. "
            f"Brak jednoznacznych cech regresji lub progresji. "
            f"Klasyfikacja Lugano: Stable Disease (SD), Deauville {deauville_score}."
        )

    elif response == "PD":
        return (
            f"Stwierdza się progresję choroby z nowymi lub bardziej aktywnymi zmianami. "
            f"Klasyfikacja Lugano: Progressive Disease (PD), Deauville {deauville_score}."
        )

    return (
        "Nie udało się jednoznacznie określić odpowiedzi na leczenie "
        "na podstawie dostępnego opisu PET."
    )


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

master_df["Nr badania"] = master_df["Nr PET"]

# =========================
# DATY
# =========================

master_df["Data badania"] = pd.to_datetime(
    master_df["Data badania"],
    dayfirst=True,
    errors="coerce"
)

# =========================
# SUVmax
# =========================

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
    master_df["Opis"]
    .apply(detect_deauville)
)

master_df["Deauville"] = master_df.apply(
    lambda row:
        row["Deauville"]
        if pd.notna(row["Deauville"])
        else deauville(row["Ocena odpowiedzi"]),
    axis=1
)

master_df["Wnioski"] = master_df.apply(
    lambda row: generate_summary(
        row["Ocena odpowiedzi"],
        row["Deauville"]
    ),
    axis=1
)

# =========================
# ANALIZY
# =========================

liczba_pacjentow = master_df["Pacjent"].nunique()
liczba_pet = len(master_df)

print("\n===== PODSUMOWANIE =====")
print(f"Liczba pacjentów: {liczba_pacjentow}")
print(f"Liczba badań PET: {liczba_pet}")

pet_per_patient = (
    master_df
    .groupby("Pacjent")["Nr PET"]
    .count()
)

summary = (
    master_df
    .groupby("Pacjent")
    .agg(
        liczba_pet=("Nr PET", "count"),
        pierwsze_badanie=("Data badania", "min"),
        ostatnie_badanie=("Data badania", "max")
    )
)

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

patient_status = (
    master_df
    .sort_values(["Pacjent", "Data badania"])
    .groupby("Pacjent")
    .tail(1)
)

# =========================
# FORMAT DAT DO EXCELA
# =========================

master_df["Data badania"] = (
    master_df["Data badania"]
    .dt.strftime("%d.%m.%Y")
)

# =========================
# TABELA GŁÓWNA
# =========================

badania_export = master_df[
    [
        "Data badania",
        "Nr badania",
        "Etap leczenia",
        "Linia leczenia",
        "Linia leczenia",
        "SUVmax",
        "Deauville",
        "Ocena odpowiedzi",
        "Wnioski"
    ]
]

# =========================
# ZAPIS EXCEL
# =========================

with pd.ExcelWriter("Wyniki.xlsx") as writer:

    badania_export.to_excel(
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

print("\nZapisano: Wyniki.xlsx")