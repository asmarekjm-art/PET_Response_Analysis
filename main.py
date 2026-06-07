from config import SOURCE_FILE
from src.loader import load_data


def main():

    print("=== HUBA PET PIPELINE ===")

    data = load_data(SOURCE_FILE)

    print("\nWymiary danych:")
    print(data.shape)

    print("\nKolumny:")
    print(data.columns.tolist())


if __name__ == "__main__":
    main()