from pathlib import Path
import pandas as pd

# =====================================
# KONFIGURACJA
# =====================================

FOLDER_PACJENCI = Path("pacjenci")
PLIK_WYNIK = Path("source/rozpoznania_pacjentow.xlsx")

# =====================================
# SŁOWNIK ROZPOZNAŃ
# =====================================

DIAGNOSIS_MAP = {

    "HL": {
    "icd10": "C81",
    "keywords": [
        "hl.",
        "hl,",
        " hl ",
        "hodgkin",
        "hodgkina",
        "choroba hodgkina",
        "ziarnica",
        "ziarniczy",
        "nlphl",
        "nodular lymphocyte predominant"
        ]
    },

    "PMBCL": {
        "icd10": "C83.3",
        "keywords": [
            "primary mediastinal",
            "chłoniak śródpiersia"
        ]
    },

    "DLBCL": {
        "icd10": "C83.3",
        "keywords": [
            "dlbcl",
            "dlblc",
            "chłoniak nieziarniczy rozlany"
        ]
    },

    "FL": {
        "icd10": "C82",
        "keywords": [
            "grudkowy",
            "guzkowaty",
            "follicular"
        ]
    },

    "MCL": {
        "icd10": "C83.1",
        "keywords": [
            "mantle cell",
            "komórek płaszcza",
            "mcl"
        ]
    },



    "MALT": {
        "icd10": "C88.4",
        "keywords": [
            "malt"
        ]
    },

    "MZL": {
        "icd10": "C85.1",
        "keywords": [
            "marginal zone",
            "marginalny"
        ]
    },
    "PTCL": {
    "icd10": "C84.4",
    "keywords": [
        "obwodowy chłoniak z komórek t",
        "skórny z komórek t",
        "chłoniak obwodowy i skórny z komórek t",
        "chłoniak t-komórkowy",
        "komórek t/nk",
        "t/nk",
        "ptcl"
        ]
    },

    "B_CELL_NOS": {
    "icd10": "C85.1",
    "keywords": [
        "agresywny chłoniak b",
        "chłoniak b-komórkowy",
        "chłoniak z komórek b"
        ]
    }
}

# =====================================
# KLASYFIKACJA
# =====================================
def classify_diagnosis(problem):

    if pd.isna(problem):
        return "UNKNOWN", ""

    text = str(problem).lower()

    for diagnosis, data in DIAGNOSIS_MAP.items():

        for keyword in data["keywords"]:

            if keyword.lower() in text:

                return (
                    diagnosis,
                    data["icd10"]
                )

    return "UNKNOWN", ""


# =====================================
# ZBIERANIE WYNIKÓW
# =====================================

wyniki = []
unknown = []
for plik in FOLDER_PACJENCI.glob("*.xlsx"):

    print(f"Przetwarzam: {plik.name}")

    try:

        df = pd.read_excel(plik)

        if "Problem kliniczny" not in df.columns:

            print("Brak kolumny Problem kliniczny")
            continue

        problemy = df["Problem kliniczny"].dropna()

        if len(problemy) == 0:
            unknown.append({

                "Pacjent": plik.stem,
                "Problem kliniczny": "BRAK DANYCH"

            })

            continue

        problem = " ".join(
            problemy.astype(str)
        )

        rozpoznanie, icd10 = (
            classify_diagnosis(problem)
        )

        if rozpoznanie == "UNKNOWN":
            unknown.append({

                "Pacjent": plik.stem,
                "Problem kliniczny": problem

            })

        wyniki.append({

            "Pacjent": plik.stem,
            "Problem kliniczny": problem,
            "Rozpoznanie": rozpoznanie,
            "ICD10": icd10

        })

    except Exception as e:

        print(f"Błąd: {e}")

# =====================================
# ZAPIS
# =====================================

df_wyniki = pd.DataFrame(wyniki)

df_wyniki.to_excel(
    PLIK_WYNIK,
    index=False
)
pd.DataFrame(unknown).to_excel(
    "source/unknown_diagnosis.xlsx",
    index=False
)
print("\nZapisano:")
print(PLIK_WYNIK)