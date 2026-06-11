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

def extract_treatment(text):

    if pd.isna(text):
        return ""

    text = str(text)

    found = []

    for treatment, pattern in TREATMENTS.items():

        if re.search(pattern, text, re.IGNORECASE):
            found.append(treatment)

    return ", ".join(sorted(set(found)))

# ==========================================
# GŁÓWNA PĘTLA
# ==========================================

results = []

files = list(PACJENCI_DIR.glob("*.xlsx"))

for file in files:

    try:

        df = pd.read_excel(file)

        required = ["Nr PET", "Problem kliniczny"]

        if not all(col in df.columns for col in required):
            continue

        patient_name = file.stem

        for _, row in df.iterrows():

            treatment = extract_treatment(
                row["Problem kliniczny"]
            )

            results.append({
                "Pacjent": patient_name,
                "Nr PET": row["Nr PET"],
                "Problem kliniczny": row["Problem kliniczny"],
                "Leczenie": treatment
            })

    except Exception as e:
        print(f"Błąd: {file.name} -> {e}")

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