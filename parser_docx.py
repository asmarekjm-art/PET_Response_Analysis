from docx import Document
import pandas as pd
import re
from pathlib import Path


# =====================================
# FOLDER Z OPISAMI
# =====================================

folder = Path("opisy")

# =====================================
# PRZETWARZANIE PLIKÓW
# =====================================

for plik in folder.glob("*.docx"):

    print(f"\nPrzetwarzam: {plik.name}")

    doc = Document(plik)

    tekst = "\n".join(
        paragraf.text
        for paragraf in doc.paragraphs
    )

    # =========================
    # WYSZUKIWANIE DAT
    # =========================

    pattern = r"\d{2}[,\.]\d{2}[,\.]\d{4}\s*\n\s*Zakres badania"

    daty = list(
        re.finditer(pattern, tekst)
    )

    print(f"Znaleziono badań PET: {len(daty)}")

    badania = []


    def get_lugano(response):

        mapping = {

            "Baseline":
                "Badanie wyjściowe",

            "CR":
                "Complete Response (CR) - całkowita odpowiedź na leczenie",

            "PR":
                "Partial Response (PR) - częściowa odpowiedź na leczenie",

            "SD":
                "Stable Disease (SD) - stabilizacja choroby",

            "PD":
                "Progressive Disease (PD) - progresja choroby"

        }

        return mapping.get(response, "Unknown")


    def get_response_description(response):

        mapping = {
            "Baseline": "Badanie wyjściowe przed rozpoczęciem leczenia",
            "CR": "Całkowita odpowiedź metaboliczna",
            "PR": "Częściowa odpowiedź metaboliczna",
            "SD": "Stabilizacja choroby",
            "PD": "Progresja choroby"
        }

        return mapping.get(response, "")


    def get_deauville(response):

        mapping = {

            "Baseline":
                "Nie dotyczy",

            "CR":
                "3 - wychwyt nie większy niż wątroba",

            "PR":
                "4 - wychwyt umiarkowanie większy od wątroby",

            "SD":
                "4 - utrzymujący się wychwyt patologiczny",

            "PD":
                "5 - znacznie zwiększony wychwyt lub nowe zmiany"

        }

        return mapping.get(response, "")

    # =========================
    # PODZIAŁ NA BADANIA
    # =========================

    for i, match in enumerate(daty):

        start = match.start()

        if i < len(daty) - 1:
            end = daty[i + 1].start()
        else:
            end = len(tekst)

        fragment = tekst[start:end]

        # =========================
        # DATA
        # =========================

        data = re.search(
            r"\d{2}[,\.]\d{2}[,\.]\d{4}",
            match.group()
        ).group().replace(",", ".")

        # =========================
        # ETAP LECZENIA
        # =========================

        problem = ""

        m = re.search(
            r"Problem kliniczny:(.*?)(Konsultujący|Głowa i szyja)",
            fragment,
            re.S
        )

        if m:
            problem = (
                m.group(1)
                .replace("\n", " ")
                .strip()
            )
            print("=" * 80)
            print(problem)

        problem = re.sub(
            r"^.*?(Ocena)",
            "Ocena",
            problem,
            flags=re.IGNORECASE
        )
        rozpoznanie = ""

        p = problem.lower()

        if "marginal zone lymphoma" in p:
            rozpoznanie = "MZL"

        elif "marginal zone" in p:
            rozpoznanie = "MZL"

        elif "malt" in p:
            rozpoznanie = "MALT"

        elif "mantle cell" in p or "komórek płaszcza" in p:
            rozpoznanie = "MCL"

        elif "dlbcl" in p:
            rozpoznanie = "DLBCL"

        elif "pmbcl" in p:
            rozpoznanie = "PMBCL"

        elif "follicular" in p:
            rozpoznanie = "FL"

        elif "hodgkin" in p or "ziarnica" in p:
            rozpoznanie = "HL"

        else:
            rozpoznanie = "Inne"
        # =========================
        # WNIOSKI
        # =========================

        wnioski = ""

        m = re.search(
            r"Wnioski:(.*)",
            fragment,
            re.S
        )

        if m:
            wnioski = (
                m.group(1)
                .replace("\n", " ")
                .strip()
            )

        # =========================
        # SUVMAX
        # =========================

        suvy = re.findall(
            r"SUV\s*max\s*(?:do)?\s*(\d+[,.]\d+)",
            fragment,
            flags=re.IGNORECASE
        )

        suvy = [
            float(
                x.replace(",", ".")
            )
            for x in suvy
        ]

        suvmax = max(suvy) if suvy else None

        # =========================
        # WYNIK PET
        # =========================

        txt = wnioski.lower()

        if (
                "nie uwidoczniono" in txt
                and "procesu chłoniakowego" in txt
        ):
            wynik_pet = "Brak aktywnej choroby"

        elif (
                "aktywnego metabolicznie procesu chłoniakowego" in txt
                or "aktywny metabolicznie proces chłoniakowy" in txt
                or "obecność aktywnej metabolicznie choroby" in txt
        ):
            wynik_pet = "Aktywna choroba"

        else:
            wynik_pet = "Do oceny"

            print("\nDATA:", data)
            print("WNIOSKI:")
            print(wnioski[:500])
            print("----------------")

        # =========================
        # OCENA ODPOWIEDZI
        # =========================

        if i == 0:

            odpowiedz = "Baseline"

        else:

            if wynik_pet == "Brak aktywnej choroby":
                odpowiedz = "CR"


            elif (

                    "progres" in txt

                    or "zwiększenie" in txt

                    or "więcej niż w badaniu poprzednim" in txt

                    or "nowe ogniska" in txt

            ):

                odpowiedz = "PD"


            elif (

                    "częściowa regresja" in txt

                    or "regresja metaboliczna" in txt

                    or "regresja radiologiczna" in txt

            ):

                odpowiedz = "PR"

            else:
                odpowiedz = "SD"
        opis_odpowiedzi = get_response_description(
            odpowiedz
        )

        lugano = get_lugano(
            odpowiedz
        )

        deauville = get_deauville(
            odpowiedz
        )
        # =========================
        # DODANIE WIERSZA
        # =========================
        summary = ""

        if odpowiedz == "Baseline":
            summary = (
                "Aktywna metabolicznie choroba przed rozpoczęciem leczenia. "
                "Badanie wyjściowe stanowiące punkt odniesienia."
            )

        elif odpowiedz == "CR":
            summary = (
                f"Nie stwierdza się aktywnej metabolicznie choroby. "
                f"Klasyfikacja Lugano: {lugano}. "
                f"Deauville: {deauville}."
            )

        elif odpowiedz == "PR":
            summary = (
                f"Częściowa odpowiedź metaboliczna na leczenie. "
                f"Klasyfikacja Lugano: {lugano}. "
                f"Deauville: {deauville}."
            )

        elif odpowiedz == "PD":
            summary = (
                f"Progresja choroby. "
                f"Klasyfikacja Lugano: {lugano}. "
                f"Deauville: {deauville}."
            )

        else:
            summary = (
                f"Stabilizacja choroby. "
                f"Klasyfikacja Lugano: {lugano}. "
                f"Deauville: {deauville}."
            )

        badania.append({

            "Data badania": data,
            "Etap leczenia": problem,
            "Rozpoznanie": rozpoznanie,
            "SUVmax": suvmax,
            "Ocena odpowiedzi": odpowiedz,
            "Lugano": lugano,
            "Deauville": deauville,
            "Wnioski": wnioski,
            "Podsumowanie": summary
        })

    # =========================
    # ZAPIS EXCEL
    # =========================

    df = pd.DataFrame(badania)

    nazwa = plik.stem + ".xlsx"

    zapis = Path("pacjenci") / nazwa

    df.to_excel(
        zapis,
        index=False
    )

    print(f"Zapisano: {zapis}")

print("\nGotowe.")