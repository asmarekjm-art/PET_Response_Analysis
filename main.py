from config import SOURCE_FILE
from src.loader import load_data
from src.cleaner import clean_data
from src.analyzer import analyze_responses


def main():

    print("=== HUBA PET PIPELINE ===")

    data = load_data(SOURCE_FILE)

    print("\nPrzed czyszczeniem:")
    print(data.shape)

    clean = clean_data(data)

    analyzed = analyze_responses(clean)

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