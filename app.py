import streamlit as st
import pandas as pd
from pathlib import Path

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Pacjenci",
        master_df["Pacjent"].nunique()
    )

with col2:
    st.metric(
        "Badania PET",
        len(master_df)
    )

with col3:
    st.metric(
        "Średnia PET/pacjenta",
        round(
            len(master_df)
            / master_df["Pacjent"].nunique(),
            1
        )
    )

with col4:
    st.metric(
        "Średni SUVmax",
        round(
            master_df["SUVmax"].mean(),
            1
        )
    )

st.divider()

# =====================================
# RANKING PACJENTÓW
# =====================================

st.subheader("🏆 Skuteczność leczenia")

st.dataframe(
    suv_summary.sort_values(
        "Zmiana_%",
        ascending=True
    ),
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
PACJENT

{pacjent}

PRZEBIEG DIAGNOSTYKI

Liczba badań PET/CT: {len(dane)}

Okres obserwacji:
{pierwsza_data:%d.%m.%Y} - {ostatnia_data:%d.%m.%Y}

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

if "Nr PET" in dane.columns and "Nr badania" not in dane.columns:
    dane["Nr badania"] = (
        dane["Nr PET"]
        .astype(str)
        .str.replace("PET ", "", regex=False)
    )

kolumny = [
    col for col in [
        "Data badania",
        "Nr badania",
        "Etap leczenia",
        "Linia leczenia",
        "SUVmax",
        "Deauville",
        "Ocena odpowiedzi",
        "Wnioski"
    ]
    if col in dane.columns
]
dane_wyswietl = dane.copy()

dane_wyswietl["Data badania"] = (
    pd.to_datetime(
        dane_wyswietl["Data badania"]
    ).dt.strftime("%d.%m.%Y")
)

st.dataframe(
    dane_wyswietl[kolumny],
    width="stretch"
)