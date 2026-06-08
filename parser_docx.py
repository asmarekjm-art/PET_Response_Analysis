from docx import Document
import pandas as pd
import re
from pathlib import Path

# folder z opisami DOCX
folder = Path("opisy")

for plik in folder.glob("*.docx"):

    print(f"Przetwarzam: {plik.name}")

    doc = Document(plik)

    tekst = "\n".join(
        paragraf.text
        for paragraf in doc.paragraphs
    )

    # wyszukiwanie dat
    pattern = r"\d{2}[,\.]\d{2}[,\.]\d{4}"

    daty = list(
        re.finditer(pattern, tekst)
    )

    badania = []

    for i, match in enumerate(daty):

        start = match.start()

        if i < len(daty) - 1:
            end = daty[i + 1].start()
        else:
            end = len(tekst)

        fragment = tekst[start:end]

        data = (
            match.group()
            .replace(",", ".")
        )

        # problem kliniczny
        problem = ""

        m = re.search(
            r"Problem kliniczny:(.*?)(Konsultujący|Głowa i szyja)",
            fragment,
            re.S
        )

        if m:
            problem = m.group(1).strip()

        # wnioski
        wnioski = ""

        m = re.search(
            r"Wnioski:(.*)",
            fragment,
            re.S
        )

        if m:
            wnioski = m.group(1).strip()

        badania.append({
            "Data badania": data,
            "Nr PET": f"PET {i+1}",
            "Etap leczenia": problem,
            "Wnioski": wnioski
        })

    df = pd.DataFrame(badania)

    nazwa = plik.stem + ".xlsx"

    zapis = Path("pacjenci") / nazwa

    df.to_excel(
        zapis,
        index=False
    )

    print(f"Zapisano: {zapis}")