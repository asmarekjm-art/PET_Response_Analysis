from config import SOURCE_FILE
from src.loader import load_data
from src.cleaner import (
    clean_data,
    normalize_treatment
)
from src.analyzer import (
    analyze_responses,
    response_statistics,
    treatment_statistics
)

def main():

    print("=== HUBA PET PIPELINE ===")

    data = load_data(SOURCE_FILE)

    print("\nPrzed czyszczeniem:")
    print(data.shape)

    clean = clean_data(data)
    clean = normalize_treatment(clean)

    analyzed = analyze_responses(clean)
    stats = response_statistics(analyzed)
    treatment_stats = treatment_statistics(analyzed)

    print("\n=== SKUTECZNOŚĆ LECZENIA ===")
    print(treatment_stats)

    print("\n=== PODSUMOWANIE HUBA ===")

    print(f"Liczba pacjentów: {len(analyzed)}")

    print(stats)

    print("\nPo czyszczeniu:")
    print(clean.shape)

    print("\nKolumny po czyszczeniu:")
    print(clean.columns.tolist())

    print("\nKlasy odpowiedzi:")

    print(
        analyzed["response_class"]
        .value_counts()
    )


if __name__ == "__main__":
    main()