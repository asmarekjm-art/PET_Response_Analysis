def clean_data(df):

    # usuń kolumny Unnamed
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # usuń puste rekordy
    df = df.dropna(subset=["LP"])

def normalize_treatment(df):
        df["RODZAJ LECZENIA"] = (
            df["RODZAJ LECZENIA"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


    return df