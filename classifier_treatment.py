import pandas as pd
from pathlib import Path
import re

# ==========================================
# KONFIGURACJA
# ==========================================

PACJENCI_DIR = Path("pacjenci")
OUTPUT_FILE = Path("source/leczenie_pet.xlsx")

# ==========================================
# SŁOWNIK TERAPII
# ==========================================

TREATMENTS = {
    "ABVD": r"\bABVD\b",
    "BEACOPP": r"\bBEACOPP\b",
    "R-CHOP": r"\bR[- ]?CHOP\b",
    "R-DHAP": r"\bR[- ]?DHAP\b",
    "R-ICE": r"\bR[- ]?ICE\b",
    "GDP": r"\bGDP\b",
    "DHAP": r"\bDHAP\b",
    "ICE": r"\bICE\b",

    "Brentuximab": r"\bbrentuximab\b|\bBV\b",
    "Niwolumab": r"\bniwolumab\b|\bnivolumab\b",
    "Pembrolizumab": r"\bpembrolizumab\b",

    "Radioterapia": r"\bradioterap",
    "Auto-HSCT": r"\bauto[- ]?(HSCT|PBSCT|SCT)\b",
    "Allo-HSCT": r"\ballo[- ]?(HSCT|PBSCT|SCT)\b",
}

# ==========================================
# EKSTRAKCJA LECZENIA
# ==========================================

def extract_treatment_info(text):

    if pd.isna(text):
        return "", ""

    text = str(text)

    text_lower = text.lower()

    # ==========================
    # ETAP LECZENIA
    # ==========================

    stage = "OTHER"

    if any(x in text_lower for x in [
        "ocena zaawansowania",
        "pierwotna ocena",
        "staging",
        "rozpoznanie",
        "diagnostyka"
    ]):
        stage = "BASELINE"



    elif any(x in text_lower for x in [

        "ocena remisji",

        "po zakończeniu chth",

        "po zakonczeniu chth",

        "po zakończeniu chemioterapii",

        "po zakonczeniu chemioterapii",

        "po zakończeniu leczenia",

        "po zakonczeniu leczenia"

    ]):

        stage = "END_OF_TREATMENT"



    elif (

            re.search(

                r"po\s+\d+\s*(cykl|cyklach|kurs|kursach)",

                text_lower

            )

            or any(x in text_lower for x in [

        "ocena odpowiedzi",

        "wczesna ocena odpowiedzi"

    ])

    ):

        stage = "INTERIM"

    elif any(x in text_lower for x in [
        "radioterapia",
        "ifrt",
        "isrt"
    ]):
        stage = "POST_RT"

    elif any(x in text_lower for x in [
        "autopbsct",
        "autohsct",
        "auto-hsct",
        "auto hsct",
        "autoprzeszczep"
    ]):
        stage = "POST_ASCT"

    elif any(x in text_lower for x in [
        "wznowa",
        "nawrót",
        "nawrot"
    ]):
        stage = "RELAPSE"


    elif any(x in text_lower for x in [

        "kontrola",

        "badanie kontrolne",

        "follow-up",

        "follow up",

        "obserwacja",

        "stan po",

        "leczenie podtrzymujące",

        "w celu wykluczenia wznowy"

    ]):

        stage = "FOLLOW_UP"

    # ==========================
    # SCHEMAT
    # ==========================

    found = []

    for treatment, pattern in TREATMENTS.items():

        if re.search(pattern, text, re.IGNORECASE):
            found.append(treatment)

    scheme = ", ".join(sorted(set(found)))

    iif stage == "OTHER":
    print("\n" + "=" * 80)
    print("OTHER")
    print(text)

    return stage, scheme
# ==========================================
# GŁÓWNA PĘTLA
# ==========================================

results = []

files = list(PACJENCI_DIR.glob("*.xlsx"))

for plik in files:

    try:

        df = pd.read_excel(plik)

        required = [
            "Nr PET",
            "Problem kliniczny"
        ]

        if not all(col in df.columns for col in required):
            continue

        patient_name = plik.stem

        for _, row in df.iterrows():

            stage, scheme = extract_treatment_info(
                row["Problem kliniczny"]
            )

            if (
                    row["Nr PET"] == 1
                    and stage == "OTHER"
            ):
                stage = "BASELINE"

            results.append({
                "Pacjent": patient_name,
                "Nr PET": row["Nr PET"],
                "Problem kliniczny": row["Problem kliniczny"],
                "Etap_leczenia": stage,
                "Schemat": scheme
            })

    except Exception as e:
        print(f"Błąd: {plik.name} -> {e}")

# ==========================================
# ZAPIS
# ==========================================

result_df = pd.DataFrame(results)

OUTPUT_FILE.parent.mkdir(exist_ok=True)

result_df.to_excel(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 60)
print("Zapisano:")
print(OUTPUT_FILE)
print(f"Liczba rekordów: {len(result_df)}")
print("=" * 60)