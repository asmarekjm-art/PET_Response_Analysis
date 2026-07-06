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
# WYODRĘBNIANIE SEKCJI
# =====================================
def extract_section(text, start, ends):
    pattern = (
            start +
            r"(.*?)" +
            "(" + "|".join(ends) + ")"
    )

    m = re.search(
        pattern,
        text,
        re.S | re.I
    )

    if m:
        return (
            m.group(1)
            .replace("\n", " ")
            .strip()
        )

    return ""

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
            r"Problem kliniczny:(.*?)(Głowa i szyja:|Konsultujący)",
            fragment,
            re.S | re.I
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
            r"Zakres badania:\s*(.*?)\s*Akwizycję",
            fragment,
            re.S
        )

        if m:
            zakres = m.group(1).strip()

#glikemia
        glikemia = ""

        m = re.search(
            r"Glikemia:\s*(\d+)",
            fragment,
            re.I
        )

        if m:
            glikemia = m.group(1)

# czas po podaniu FDG
        czas_po_fdg = ""

        m = re.search(
            r"po\s*(\d+)\s*min\s*od\s*podania",
            fragment,
            re.I
        )

        if m:
            czas_po_fdg = m.group(1)



        glowa_szyja = extract_section(
            fragment,
            r"Głowa i szyja:",
            [
                r"Klatka piersiowa i śródpiersie:"
            ]
        )

        klatka_piersiowa = extract_section(
            fragment,
            r"Klatka piersiowa i śródpiersie:",
            [
                r"Brzuch i miednica:"
            ]
        )

        brzuch_miednica = extract_section(
            fragment,
            r"Brzuch i miednica:",
            [
                r"Układ kostny:"
            ]
        )

        uklad_kostny = extract_section(
            fragment,
            r"Układ kostny:",
            [
                r"Wartości referencyjne:",
                r"Wnioski:"
            ]
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

            "Nr PET": i + 1,
            "Data badania": data,

            "Problem kliniczny": problem,

            "Zakres badania": zakres,
            "Glikemia": glikemia,
            "Czas po FDG": czas_po_fdg,

            "Głowa i szyja": glowa_szyja,
            "Klatka piersiowa": klatka_piersiowa,
            "Brzuch i miednica": brzuch_miednica,
            "Układ kostny": uklad_kostny,

            "Wnioski": wnioski,

            "SUVmax_global": suvmax
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