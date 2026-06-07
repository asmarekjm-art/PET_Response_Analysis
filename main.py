from config import SOURCE_FILE
from src.loader import load_data
from src.cleaner import clean_data

def main():

    print("=== HUBA PET PIPELINE ===")

    data = load_data(SOURCE_FILE)

    print("\nPrzed czyszczeniem:")
    print(data.shape)

    clean = clean_data(data)

    print("\nPo czyszczeniu:")
    print(clean.shape)

    print("\nKolumny po czyszczeniu:")
    print(clean.columns.tolist())

if __name__ == "__main__":
    main()