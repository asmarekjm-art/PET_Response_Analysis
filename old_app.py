import streamlit as st
import pandas as pd
from pathlib import Path

pacjenci_info = pd.read_excel(
    "source/dane pacjentow.xlsx"
)

pacjenci_info = pacjenci_info.dropna(
    subset=["IMIE", "NAZWISKO"]
)

# =====================================
# KONFIGURACJA
# =====================================

st.set_page_config(
    page_title="PET Response Analysis",
    page_icon="☢️",
    layout="wide"
)

st.title("☢️ PET Response Analysis")
st.subheader("Analysis of Treatment Response in Hodgkin Lymphoma Patients")

# =====================================
# WCZYTYWANIE PLIKÓW
# =====================================

folder = Path("pacjenci")

all_data = []

for file in folder.glob("*.xlsx"):

    df = pd.read_excel(file)

    name = file.stem

    name = (
        name.replace("_PET", "")
        .replace("_standard", "")
        .replace("_uzupelniony", "")
        .replace("_Podsumowanie_DATY", "")
        .replace("_Podsumowanie", "")
    )

    df["Pacjent"] = name.replace("_", " ")

    all_data.append(df)

master_df = pd.concat(all_data, ignore_index=True)

rozpoznania = (
    master_df
    .groupby("Pacjent")["Rozpoznanie"]
    .first()
)
# =====================================
# CZYSZCZENIE DANYCH
# =====================================

master_df["SUVmax"] = (
    master_df["SUVmax"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

master_df["SUVmax"] = pd.to_numeric(
    master_df["SUVmax"],
    errors="coerce"
)

master_df["Data badania"] = pd.to_datetime(
    master_df["Data badania"],
    dayfirst=True,
    errors="coerce"
)
master_df["Data badania"] = pd.to_datetime(
    master_df["Data badania"],
    dayfirst=True,
    errors="coerce"
)
# =====================================
# ANALIZA SUVMAX DLA CAŁEJ GRUPY
# =====================================

suv_summary = []

for pac in master_df["Pacjent"].unique():

    temp = (
        master_df[
            master_df["Pacjent"] == pac
        ]
        .sort_values("Data badania")
    )

    suv = temp["SUVmax"].dropna()

    if len(suv) >= 2:

        zmiana = (
            (suv.iloc[-1] - suv.iloc[0])
            / suv.iloc[0]
        ) * 100

        suv_summary.append(
            {
                "Pacjent": pac,
                "SUVmax_pierwszy": round(suv.iloc[0], 2),
                "SUVmax_ostatni": round(suv.iloc[-1], 2),
                "Zmiana_%": round(zmiana, 2)
            }
        )

suv_summary = pd.DataFrame(suv_summary)

# =====================================
# DASHBOARD GŁÓWNY
# =====================================

liczba_pacjentow = (
    pacjenci_info[
        ["IMIE", "NAZWISKO"]
    ]
    .drop_duplicates()
    .shape[0]
)

plec = (
    pacjenci_info["płeć"]
    .astype(str)
    .str.strip()
    .str.lower()
)

kobiety = (
    (plec == "kobieta") |
    (plec == "kobiety")
).sum()

mezczyzni = (
    (plec == "mężczyzna") |
    (plec == "mezczyzna")
).sum()

brak_danych = (
    liczba_pacjentow
    - kobiety
    - mezczyzni
)

sredni_wiek = round(
    pacjenci_info[
        "Wiek w chwili rozpoczęcia leczenia"
    ].mean(),
    1
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Pacjenci",
        liczba_pacjentow
    )

with col2:
    st.metric(
        "Kobiety",
        kobiety
    )

with col3:
    st.metric(
        "Mężczyźni",
        mezczyzni
    )

with col4:
    st.metric(
        "Brak danych",
        brak_danych
    )

with col5:
    st.metric(
        "Średni wiek",
        sredni_wiek
    )

st.divider()

st.subheader("📊 Rozpoznania")

rozpoznania_df = (
    rozpoznania
    .value_counts()
    .reset_index()
)

rozpoznania_df.columns = [
    "Rozpoznanie",
    "Liczba pacjentów"
]

st.dataframe(
    rozpoznania_df,
    hide_index=True,
    width="stretch"
)
st.subheader("📊 Charakterystyka grupy")

choroby = (
    pacjenci_info["CHOROBA"]
    .value_counts()
    .reset_index()
)

choroby.columns = [
    "Rozpoznanie",
    "Liczba pacjentów"
]

st.dataframe(
    choroby,
    hide_index=True,
    width="stretch"
)
# =====================================
# WYBÓR PACJENTA
# =====================================

pacjent = st.selectbox(
    "Wybierz pacjenta",
    sorted(master_df["Pacjent"].unique())
)

dane = (
    master_df[
        master_df["Pacjent"] == pacjent
    ]
    .sort_values("Data badania")
)

dane = dane.reset_index(drop=True)

dane["Nr badania"] = range(
    1,
    len(dane) + 1
)

# =====================================
# KARTA PACJENTA
# =====================================

st.subheader(f"👤 {pacjent}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Liczba PET",
        len(dane)
    )

suv = dane["SUVmax"].dropna()

with col2:
    if len(suv):
        st.metric(
            "SUVmax początkowy",
            round(suv.iloc[0], 2)
        )

with col3:
    if len(suv):
        st.metric(
            "SUVmax końcowy",
            round(suv.iloc[-1], 2)
        )

# =====================================
# ZMIANA SUVMAX
# =====================================
zmiana = 0

if len(suv) >= 2:
    zmiana = (
        (suv.iloc[-1] - suv.iloc[0])
        / suv.iloc[0]
    ) * 100

ostatni = dane.iloc[-1]

if ostatni["Ocena odpowiedzi"] == "CR":
    st.success("Całkowita odpowiedź metaboliczna")

elif ostatni["Ocena odpowiedzi"] == "PR":
    st.info("Częściowa odpowiedź metaboliczna")

elif ostatni["Ocena odpowiedzi"] == "SD":
    st.warning("Stabilizacja choroby")

elif ostatni["Ocena odpowiedzi"] == "PD":
    st.error("Progresja choroby")

# =====================================
# WYKRES SUVMAX
# =====================================

st.subheader("📈 SUVmax w czasie")

wykres = dane.dropna(subset=["SUVmax"])

if len(wykres) > 0:
    st.line_chart(
        wykres.set_index("Nr badania")["SUVmax"]
    )

st.subheader("📄 Automatyczny raport")

if len(suv) >= 1:

    pierwsza_data = dane["Data badania"].min()
    ostatnia_data = dane["Data badania"].max()

    etapy = " → ".join(
        dane["Etap leczenia"]
        .dropna()
        .astype(str)
        .unique()
    )

    ostatni = (
        dane
        .sort_values("Data badania")
        .iloc[-1]
    )

    raport = f"""
PACJENT: {pacjent}

PRZEBIEG DIAGNOSTYKI

Liczba badań PET/CT: {len(dane)}

Okres obserwacji: {pierwsza_data:%d.%m.%Y} - {ostatnia_data:%d.%m.%Y}

PRZEBIEG LECZENIA

{etapy}

OCENA ODPOWIEDZI

{ostatni['Ocena odpowiedzi']}

SKALA DEAUVILLE

{ostatni['Deauville']}

WNIOSEK

{ostatni['Wnioski']}
"""

    etapy = " → ".join(
        dane["Etap leczenia"]
        .dropna()
        .astype(str)
        .unique()
    )

    ostatni = (
        dane
        .sort_values("Data badania")
        .iloc[-1]
    )

    raport = f"""
    PACJENT

    {pacjent}

    PRZEBIEG DIAGNOSTYKI

    Liczba badań PET/CT: {len(dane)}

    Okres obserwacji:
    {pierwsza_data.strftime('%d.%m.%Y')} - {ostatnia_data.strftime('%d.%m.%Y')}

    PRZEBIEG LECZENIA

    {etapy}

    OCENA AKTYWNOŚCI METABOLICZNEJ

    SUVmax początkowy: {suv.iloc[0]:.1f}

    SUVmax końcowy: {suv.iloc[-1]:.1f}

    Zmiana SUVmax:
    {zmiana:.1f}%

    OCENA ODPOWIEDZI

    {ostatni['Ocena odpowiedzi']}

    SKALA DEAUVILLE

    {ostatni['Deauville']}

    WNIOSEK

    {ostatni['Wnioski']}

    """
with st.expander("📄 Raport kliniczny", expanded=True):
    st.text(raport)

# =====================================
# HISTORIA BADAŃ
# =====================================

st.subheader("📋 Historia badań PET")

kolumny = [
    col for col in [
        "Nr badania",
        "Data badania",
        "Etap leczenia",
        "SUVmax",
        "Lugano",
        "Deauville",
        "Ocena odpowiedzi",
        "Podsumowanie"
    ]
    if col in dane.columns
]

dane_wyswietl = dane[kolumny].copy()

dane_wyswietl["Data badania"] = (
    pd.to_datetime(
        dane_wyswietl["Data badania"]
    ).dt.strftime("%d.%m.%Y")
)

st.dataframe(
    dane_wyswietl.reset_index(drop=True),
    hide_index=True,
    width="stretch"
)