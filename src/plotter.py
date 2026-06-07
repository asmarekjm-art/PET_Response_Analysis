import os
import matplotlib.pyplot as plt


def plot_response_distribution(df):

    os.makedirs("Results/plots", exist_ok=True)

    counts = df["response_class"].value_counts()

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar")

    plt.title("Odpowiedź na leczenie")
    plt.xlabel("Klasa odpowiedzi")
    plt.ylabel("Liczba pacjentów")

    plt.tight_layout()

    plt.savefig(
        "Results/plots/response_distribution.png"
    )

    plt.close()

    print("Wykres zapisany.")