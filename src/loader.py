import pandas as pd


def load_data(file_path):

    print(f"Wczytywanie pliku: {file_path}")

    df = pd.read_excel(file_path)

    return df