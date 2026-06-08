import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="PET Response Analysis",
    page_icon="☢️",
    layout="wide"
)

st.title("☢️ PET Response Analysis")
st.subheader("Analysis of Treatment Response in Hodgkin Lymphoma Patients")

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

# SUVmax
master_df["SUVmax"] = (
    master_df["SUVmax"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

master_df["SUVmax"] = pd.to_numeric(
    master_df["SUVmax"],
    errors="coerce"
)

# Daty
master_df["Data badania"] = pd.to_datetime(
    master_df["Data badania"],
    dayfirst=True,
    errors="coerce"
)

# =====================
# DASHBOARD GŁÓWNY
# =====================

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

# =====================
# WYBÓR PACJENTA
# =====================

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

# =====================
# KARTA PACJENTA
# =====================

st.subheader(f"👤 {pacjent}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Liczba PET",
        len(dane)
    )

with col2:

    suv = dane["SUVmax"].dropna()

    if len(suv):
        st.metric(
            "SUVmax początkowy",
            round(suv.iloc[0], 2)
        )

with col3:

    suv = dane["SUVmax"].dropna()

    if len(suv):
        st.metric(
            "SUVmax końcowy",
            round(suv.iloc[-1], 2)
        )

# =====================
# ANALIZA SUVMAX
# =====================

if len(suv) >= 2:

    zmiana = (
        (suv.iloc[-1] - suv.iloc[0])
        / suv.iloc[0]
    ) * 100

    st.metric(
        "Zmiana SUVmax (%)",
        round(zmiana, 1)
    )

# =====================
# WYKRES
# =====================

st.subheader("📈 Trend SUVmax")

wykres = dane.dropna(subset=["SUVmax"])

if len(wykres):

    st.line_chart(
        wykres.set_index("Nr PET")["SUVmax"]
    )

# =====================
# TABELA
# =====================

st.subheader("📋 Historia badań PET")

st.dataframe(
    dane,
    use_container_width=True
)