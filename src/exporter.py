import os


def export_results(df):

    os.makedirs("Results/tables", exist_ok=True)

    df.to_csv(
        "Results/tables/classified_patients.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nWyniki zapisane.")