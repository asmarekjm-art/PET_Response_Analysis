from docx import Document
import pandas as pd
import re
from pathlib import Path

# =====================================
# FOLDERY
# =====================================

folder_opisy = Path("opisy")
folder_wynik = Path("pacjenci")

folder_wynik.mkdir(exist_ok=True)

# =====================================
# PRZETWARZANIE PLIKÓW
# =====================================

for plik in folder_opisy.glob("*.docx"):

    print(f"\nPrzetwarzam: {plik.name}")

    doc = Document(plik)

    tekst = "\n".join(
        paragraf.text
        for paragraf in doc.paragraphs
    )

    # =====================================
    # WYSZUKIWANIE POCZĄTKÓW BADAŃ PET
    # =====================================

    pattern = r"\d{2}[,\.]\d{2}[,\.]\d{4}\s*\n\s*Zakres badania"

    daty = list(
        re.finditer(pattern, tekst)
    )

    print(f"Znaleziono badań PET: {len(daty)}")

    badania = []

    # =====================================
    # PODZIAŁ NA POSZCZEGÓLNE BADANIA
    # =====================================

    for i, match in enumerate(daty):

        start = match.start()

        if i < len(daty) - 1:
            end = daty[i + 1].start()
        else:
            end = len(tekst)

        fragment = tekst[start:end]

        # =====================================
        # DATA BADANIA
        # =====================================

        m_data = re.search(
            r"\d{2}[,\.]\d{2}[,\.]\d{4}",
            match.group()
        )

        data = ""

        if m_data:
            data = (
                m_data.group()
                .replace(",", ".")
            )

        # =====================================
        # PROBLEM KLINICZNY
        # =====================================

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

        # =====================================
        # ZAKRES BADANIA
        # =====================================

        zakres = ""

        m = re.search(
            r"Zakres badania:(.*?)(Problem kliniczny:)",
            fragment,
            re.S
        )

        if m:

            zakres = (
                m.group(1)
                .replace("\n", " ")
                .strip()
            )

        # =====================================
        # OPIS BADANIA
        # =====================================

        opis = ""

        m = re.search(
            r"Głowa i szyja(.*?)Wnioski:",
            fragment,
            re.S
        )

        if m:

            opis = (
                m.group(1)
                .replace("\n", " ")
                .strip()
            )

        # =====================================
        # WNIOSKI
        # =====================================

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

        # =====================================
        # SUVmax
        # =====================================

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

        # =====================================
        # ZAPIS BADANIA
        # =====================================

        badania.append({

            "Nr badania": i + 1,

            "Data badania": data,

            "Problem kliniczny": problem,

            "Zakres badania": zakres,

            "Opis badania": opis,

            "Wnioski": wnioski,

            "SUVmax": suvmax

        })

    # =====================================
    # EXCEL PACJENTA
    # =====================================

    df = pd.DataFrame(badania)

    zapis = (
        folder_wynik /
        f"{plik.stem}.xlsx"
    )

    df.to_excel(
        zapis,
        index=False
    )

    print(f"Zapisano: {zapis}")

print("\nGotowe.")