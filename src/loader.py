import pandas as pd

def load_data(file_path):
    xls = pd.ExcelFile(file_path, engine="odf")

    print("Dostępne arkusze:")
    print(xls.sheet_names)

    df = pd.read_excel(
        file_path,
        sheet_name="Arkusz1",
        engine="odf"
    )

    print(df.shape)
    print(df.head())

    return df