def classify_response(text):

    if not isinstance(text, str):
        return "BRAK_DANYCH"

    text = text.lower()

    if "bardzo dobra" in text:
        return "BARDZO_DOBRA"

    elif "dobra odpowied" in text:
        return "DOBRA"

    elif "częściowa" in text or "czesciowa" in text:
        return "CZESCIOWA"

    elif "stabilizacja" in text:
        return "STABILIZACJA"

    elif "progres" in text:
        return "PROGRESJA"

    elif "wznow" in text:
        return "WZNOWA"

    return "INNE"