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

PLIK_WYNIK = Path(
    "source/pet_master.xlsx"
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

# =====================================
# ŁĄCZENIE
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
# KOLEJNOŚĆ KOLUMN
# =====================================

df_master = df_master[[
    "Pacjent",
    "Nr PET",
    "Rozpoznanie",
    "ICD10",
    "Data badania",
    "Odpowiedź",
    "Wnioski"
]]

# =====================================
# ZAPIS
# =====================================

df_master.to_excel(
    PLIK_WYNIK,
    index=False
)

print(
    f"\nZapisano: {PLIK_WYNIK}"
)

print(
    f"Liczba badań: {len(df_master)}"
)