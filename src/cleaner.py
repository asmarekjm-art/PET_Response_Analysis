def clean_data(df):

    # usuń kolumny Unnamed
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # usuń puste rekordy
    df = df.dropna(subset=["LP"])

    return df