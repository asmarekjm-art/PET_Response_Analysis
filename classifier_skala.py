from pathlib import Path
import pandas as pd

INPUT_FILE = Path("source/wnioski_pet.xlsx")
OUTPUT_FILE = Path("source/deauville_lugano.xlsx")


def classify(response):

    response = str(response).upper().strip()

    if response == "CR":
        return "DS1", "CMR"

    elif response == "PR":
        return "DS4", "PMR"

    elif response == "SD":
        return "DS4", "SMD"

    elif response == "PD":
        return "DS5", "PMD"

    return "?", "?"


df = pd.read_excel(INPUT_FILE)

results = []

for _, row in df.iterrows():

    ds, lugano = classify(
        row["Odpowiedź"]
    )

    results.append({

        "Pacjent": row["Pacjent"],
        "Nr PET": row["Nr PET"],
        "Deauville_AI": ds,
        "Lugano_AI": lugano

    })

result_df = pd.DataFrame(results)

result_df.to_excel(
    OUTPUT_FILE,
    index=False
)

print(result_df.head())
print(f"\nRekordów: {len(result_df)}")