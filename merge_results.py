from pathlib import Path
import pandas as pd

# =====================================
# PLIKI
# =====================================

PLIK_ROZPOZNANIA = Path(
    "source/rozpoznania_pacjentow.xlsx"
)

PLIK_ODPOWIEDZI = Path(
    "source/wnioski_pet.xlsx"
)

PLIK_DETAILS = Path(
    "source/pet_details.xlsx"
)

PLIK_LECZENIE = Path(
    "source/leczenie_pet.xlsx"
)

PLIK_WYNIK = Path(
    "source/pet_master.xlsx"
)

PLIK_LOCATIONS = Path(
    "source/locations.xlsx"
)

# =====================================
# WCZYTANIE
# =====================================

df_diag = pd.read_excel(
    PLIK_ROZPOZNANIA
)

df_resp = pd.read_excel(
    PLIK_ODPOWIEDZI
)

df_details = pd.read_excel(
    PLIK_DETAILS
)

df_treatment = pd.read_excel(
    PLIK_LECZENIE
)

df_locations = pd.read_excel(
    PLIK_LOCATIONS
)

# =====================================
# ROZPOZNANIA
# =====================================

df_master = df_resp.merge(

    df_diag[[
        "Pacjent",
        "Rozpoznanie",
        "ICD10"
    ]],

    on="Pacjent",
    how="left"
)

# =====================================
# DETAILS
# =====================================

df_master = df_master.merge(

    df_details,

    on=[
        "Pacjent",
        "Nr PET"
    ],

    how="left"
)

# =====================================
# LECZENIE
# =====================================

df_master = df_master.merge(

    df_treatment[[
        "Pacjent",
        "Nr PET",
        "Etap_leczenia",
        "Schemat"
    ]],

    on=[
        "Pacjent",
        "Nr PET"
    ],

    how="left"
)

# =====================================
# LOKALIZACJE
# =====================================

df_master = df_master.merge(

    df_locations,

    on=[
        "Pacjent",
        "Nr PET"
    ],

    how="left"
)
# =====================================
# KOLEJNOŚĆ KOLUMN
# =====================================

df_master = df_master[[

    "Pacjent",

    "Rozpoznanie",
    "ICD10",

    "Nr PET",
    "Data badania",

    "Etap_leczenia",
    "Schemat",

    "Odpowiedź",

    "Glikemia",
    "Czas_po_FDG",
    "SUVmax_global",
    "Lokalizacja_zmian",
    "Problem_kliniczny",

    "Glowa_i_szyja",
    "Klatka_piersiowa",
    "Brzuch_i_miednica",
    "Uklad_kostny",

    "Wnioski"
]]

# =====================================
# SORTOWANIE
# =====================================

df_master["Data badania"] = pd.to_datetime(
    df_master["Data badania"],
    format="%d.%m.%Y",
    errors="coerce"
)

df_master = df_master.sort_values(
    ["Pacjent", "Data badania"]
)

# =====================================
# ZAPIS
# =====================================

df_master.to_excel(
    PLIK_WYNIK,
    index=False
)

print()
print("=" * 60)
print("PET MASTER")
print("=" * 60)
print(f"Zapisano: {PLIK_WYNIK}")
print(f"Liczba badań: {len(df_master)}")
print("=" * 60)