from pathlib import Path
import pandas as pd

# =====================================
# KONFIGURACJA
# =====================================

FOLDER_PACJENCI = Path("pacjenci")

PLIK_WYNIK = Path(
    "source/wnioski_pet.xlsx"
)

#wnioski
def classify_response(wnioski):

    if pd.isna(wnioski):
        return "UNCERTAIN"

    text = str(wnioski).lower()

    # =========================
    # CR
    # =========================

    cr_keywords = [

        "bardzo dobrą odpowiedź",
        "bardzo dobra odpowiedź",

        "nie uwidoczniono obecności aktywnej metabolicznie",

        "nie uwidoczniono cech aktywnej metabolicznie",

        "nie uwidoczniono jednoznacznych cech",

        "nie uwidoczniono obecności aktywnego metabolicznie procesu",

        "nie uwidoczniono aktywnego metabolicznie procesu",

        "całkowita remisja",

        "pełna odpowiedź",

        "brak cech aktywnej metabolicznie choroby",

        "brak aktywnej metabolicznie choroby"
    ]

    for keyword in cr_keywords:

        if keyword in text:
            return "CR"

    # =========================
    # PR
    # =========================

    pr_keywords = [

        "częściowa regresja",

        "częściowa regresja metaboliczna",

        "częściowa regresja radiologiczna",

        "regresja metaboliczna",

        "regresja radiologiczna",

        "zmniejszenie aktywności metabolicznej",

        "zmniejszenie liczby zmian",

        "zmniejszenie wielkości zmian",

        "dobra odpowiedź",

        "dobra odpowiedź metaboliczna",

        "dobrą odpowiedź metaboliczną",

        "istotna odpowiedź",

        "korzystna odpowiedź",

        "odpowiedź na leczenie",

        "regresja zmian",
        "częściową regresję metaboliczną",

        "częściową regresję radiologiczną",

        "częściowa regresja procesu chłoniakowego",

        "regresję procesu chłoniakowego",

        "odpowiedź procesu chłoniakowego",

        "odpowiedź choroby chłoniakowej",

        "zmniejszenie aktywności zmian",

        "istotną regresję",

        "wyraźną regresję"

    ]

    for keyword in pr_keywords:

        if keyword in text:
            return "PR"

    # =========================
    # PD
    # =========================

    pd_keywords = [

        "podejrzenie wznowy",

        "wznowy choroby",

        "progresja",

        "aktywna metabolicznie choroba chłoniakowa",

        "aktywny metabolicznie proces chłoniakowy",

        "obecność aktywnej metabolicznie choroby chłoniakowej",

        "obecność aktywnych metabolicznie",

        "obecność aktywnego metabolicznie procesu",

        "obecność aktywnego metabolicznie",

        "aktywnego metabolicznie procesu chłoniakowego",

        "aktywną metabolicznie chorobę chłoniakową",

        "aktywnych metabolicznie węzłów chłonnych",

        "pobudzonych metabolicznie węzłów chłonnych",

        "nadal aktywna metabolicznie",

        "nadal aktywny metabolicznie",

        "nadal aktywnych metabolicznie",

        "nowe ogniska",

        "nowych zmian",

        "rozległy naciek chłoniakowy",
        "obecność nadal aktywnej metabolicznie choroby chłoniakowej",

        "obecność nadal aktywnego metabolicznie",

        "nadal aktywnego metabolicznie obszaru",

        "aktywne metabolicznie węzły chłonne",

        "aktywny metabolicznie węzeł chłonny",

        "aktywny metabolicznie naciek chłoniakowy",

        "aktywne metabolicznie węzły chłonne po obu stronach przepony",

        "aktywne metabolicznie węzły chłonne krezkowe",

        "masywnym zajęciem węzłów chłonnych",

        "zajęciem węzłów chłonnych",

        "naciek procesu chłoniakowego",
        "aktywnego metabolicznie węzła chłonnego",

        "aktywny metabolicznie naciek",

        "nacieku procesu chłoniakowego",

        "wznowa choroby chłoniakowej",

        "wznowa choroby?",

        "aktywne metabolicznie zmiany",

        "dwie aktywne metabolicznie zmiany",

        "pakiety węzłowe"
    ]

    for keyword in pd_keywords:

        if keyword in text:
            return "PD"

    # =========================
    # SD
    # =========================

    sd_keywords = [

        "stabilizacja",

        "choroba stabilna",

        "obraz stabilny",

        "bez istotnych zmian",

        "bez większych zmian",

        "utrzymują się zmiany",

        "porównywalny obraz",

        "bez istotnej dynamiki",

        "bez progresji",

        "bez regresji",
        "jak w badaniu poprzednim",

        "obraz nie uległ zasadniczej zmianie",

        "nie uległ zmianie",

        "utrzymujące się pobudzenie metaboliczne"
    ]

    for keyword in sd_keywords:

        if keyword in text:
            return "SD"

    # =========================
    # NIEJEDNOZNACZNE
    # =========================

    return "UNCERTAIN"

# =====================================
# ZBIERANIE WNIOSKÓW
# =====================================

wyniki = []
unknown = []

for plik in FOLDER_PACJENCI.glob("*.xlsx"):

    print(f"Przetwarzam: {plik.name}")

    try:

        df = pd.read_excel(plik)

        wymagane = [
            "Nr PET",
            "Data badania",
            "Wnioski"
        ]

        if not all(
            col in df.columns
            for col in wymagane
        ):
            continue

        for _, row in df.iterrows():

            odpowiedz = classify_response(
                row["Wnioski"]
            )

            rekord = {

                "Pacjent": plik.stem,
                "Nr PET": row["Nr PET"],
                "Data badania": row["Data badania"],
                "Wnioski": row["Wnioski"],
                "Odpowiedź": odpowiedz

            }

            wyniki.append(rekord)

            if odpowiedz == "UNCERTAIN":

                unknown.append(rekord)

    except Exception as e:

        print(f"Błąd: {e}")

# =====================================
# ZAPIS
# =====================================

pd.DataFrame(wyniki).to_excel(
    PLIK_WYNIK,
    index=False
)

pd.DataFrame(unknown).to_excel(
    "source/uncertain_response.xlsx",
    index=False
)
print("\nPodsumowanie:")

print(
    pd.DataFrame(wyniki)["Odpowiedź"]
    .value_counts()
)
print("\nGotowe.")