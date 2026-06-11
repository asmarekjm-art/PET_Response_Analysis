import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# KONFIGURACJA
# =====================================


st.set_page_config(
    page_title="PET Response Analysis",
    page_icon="☢️",
    layout="wide"
)

st.title("☢️ PET Response Analysis")

# =====================================
# ŁADOWANIE DANYCH
# =====================================

@st.cache_data
def load_data():

    patients = pd.read_excel(
        "source/dane pacjentow.xlsx"
    )

    pet = pd.read_excel(
        "source/pet_master.xlsx"
    )

    return patients, pet


patients_df, pet_df = load_data()



patients_df["Pacjent"] = (
    patients_df["IMIE"].astype(str).str.strip().str.upper()
    + " "
    + patients_df["NAZWISKO"].astype(str).str.strip().str.upper()
)
# =====================================
# PRZYGOTOWANIE
# =====================================

pet_df["Data badania"] = pd.to_datetime(
    pet_df["Data badania"],
    errors="coerce"
)

# =====================================
# STATYSTYKI
# =====================================

st.header("📊 Statystyki grupy")

col1, col2, col3, col4 = st.columns(4)

liczba_pacjentow = patients_df["Pacjent"].nunique()

liczba_pet = len(pet_df)

sredni_wiek = round(
    patients_df[
        "Wiek w chwili rozpoczęcia leczenia"
    ].mean(),
    1
)

kobiety = len(
    patients_df[
        patients_df["płeć"].str.lower() == "kobieta"
    ]
)

mezczyzni = len(
    patients_df[
        patients_df["płeć"].str.lower() == "mężczyzna"
    ]
)

with col1:
    st.metric(
        "Pacjenci",
        liczba_pacjentow
    )

with col2:
    st.metric(
        "Badania PET",
        liczba_pet
    )

with col3:
    st.metric(
        "Kobiety / Mężczyźni",
        f"{kobiety}/{mezczyzni}"
    )

with col4:
    st.metric(
        "Średni wiek",
        sredni_wiek
    )

# =====================================
# WYKRESY
# =====================================

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("Rozpoznania")

    diag = (
        pet_df["Rozpoznanie"]
        .value_counts()
        .reset_index()
    )

    diag.columns = [
        "Rozpoznanie",
        "Liczba"
    ]

    fig = px.bar(
        diag,
        x="Rozpoznanie",
        y="Liczba"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("Odpowiedzi")

    resp = (
        pet_df["Odpowiedź"]
        .value_counts()
        .reset_index()
    )

    resp.columns = [
        "Odpowiedź",
        "Liczba"
    ]

    fig = px.bar(
        resp,
        x="Odpowiedź",
        y="Liczba"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# ROZPOZNANIE VS ODPOWIEDŹ
# =====================================

st.divider()

st.header("Rozpoznanie vs Odpowiedź")

cross = pd.crosstab(
    pet_df["Rozpoznanie"],
    pet_df["Odpowiedź"]
)

st.dataframe(
    cross,
    use_container_width=True
)

heatmap = px.imshow(
    cross,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)
# =====================================
# PACJENT
# =====================================

st.divider()

st.header("👤 Pacjent")

pacjent = st.selectbox(
    "Wybierz pacjenta",
    sorted(
        pet_df["Pacjent"]
        .dropna()
        .unique()
    )
)

# =====================================
# DANE PACJENTA
# =====================================

patient_pet = (
    pet_df[
        pet_df["Pacjent"] == pacjent
    ]
    .sort_values("Data badania")
)

patient_info = patients_df[
    patients_df["Pacjent"] == pacjent
]

if not patient_info.empty and not patient_pet.empty:

    patient_row = patient_info.iloc[0]

    liczba_pet_pacjenta = len(patient_pet)

    pierwsza_data = patient_pet["Data badania"].min()
    ostatnia_data = patient_pet["Data badania"].max()

    liczba_dni = (
        ostatnia_data - pierwsza_data
    ).days

    rozpoznanie = patient_pet.iloc[0]["Rozpoznanie"]
    icd10 = patient_pet.iloc[0]["ICD10"]

    ostatnia_odpowiedz = patient_pet.iloc[-1]["Odpowiedź"]

    diagnosis_map = {
        "HL": "Chłoniak Hodgkina",
        "DLBCL": "Rozlany chłoniak z dużych komórek B",
        "FL": "Chłoniak grudkowy",
        "MCL": "Chłoniak z komórek płaszcza",
        "PMBCL": "Pierwotny chłoniak śródpiersia z dużych komórek B",
        "PTCL": "Obwodowy chłoniak T-komórkowy",
        "OTHER_B_CELL": "Inny chłoniak B-komórkowy"
    }

    st.subheader("📋 Podsumowanie pacjenta")

    # Kafelki

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Płeć",
            patient_row["płeć"].capitalize()
        )

    with col2:
        st.metric(
            "Wiek przy rozpoznaniu",
            f"{int(patient_row['Wiek w chwili rozpoczęcia leczenia'])} lat"
        )

    with col3:
        st.metric(
            "PET/CT",
            liczba_pet_pacjenta
        )

    with col4:
        st.metric(
            "ICD10",
            icd10
        )

    # Rozpoznanie

    st.info(
        f"Rozpoznanie: {diagnosis_map.get(rozpoznanie, rozpoznanie)} ({icd10})"
    )
    # Parametry PET

    suv_values = pd.to_numeric(
        patient_pet["SUVmax_global"],
        errors="coerce"
    )

    glucose_values = pd.to_numeric(
        patient_pet["Glikemia"],
        errors="coerce"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Ostatni SUVmax",
            round(suv_values.dropna().iloc[-1], 1)
            if not suv_values.dropna().empty
            else "-"
        )

    with col2:
        st.metric(
            "Maksymalny SUVmax",
            round(suv_values.max(), 1)
            if not suv_values.dropna().empty
            else "-"
        )

    with col3:
        st.metric(
            "Średnia glikemia",
            round(glucose_values.mean(), 1)
            if not glucose_values.dropna().empty
            else "-"
        )
    # Obserwacja

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Okres obserwacji",
            f"{pierwsza_data.strftime('%d.%m.%Y')} – {ostatnia_data.strftime('%d.%m.%Y')}"
        )

    with col2:
        st.metric(
            "Czas obserwacji",
            f"{liczba_dni} dni"
        )

    # Aktualny status

    if ostatnia_odpowiedz == "CR":
        st.success(
            "Aktualny status: całkowita odpowiedź metaboliczna"
        )

    elif ostatnia_odpowiedz == "PR":
        st.info(
            "Aktualny status: częściowa odpowiedź metaboliczna"
        )

    elif ostatnia_odpowiedz == "SD":
        st.warning(
            "Aktualny status: stabilizacja choroby"
        )

    elif ostatnia_odpowiedz == "PD":
        st.error(
            "Aktualny status: progresja choroby"
        )

    else:
        st.warning(
            "Aktualny status: wynik niejednoznaczny"
        )

# =====================================
# HISTORIA PET
# =====================================

response_map = {
    "CR": "Całkowita odpowiedź metaboliczna",
    "PR": "Częściowa odpowiedź metaboliczna",
    "SD": "Stabilizacja choroby",
    "PD": "Progresja choroby",
    "UNCERTAIN": "Wynik niejednoznaczny"
}



st.subheader("Historia badań PET/CT")

historia_df = patient_pet.copy()

historia_df["Odpowiedź"] = (
    historia_df["Odpowiedź"]
    .map(response_map)
    .fillna(historia_df["Odpowiedź"])
)

historia_df = patient_pet.copy()

historia_df["Data badania"] = (
    historia_df["Data badania"]
    .dt.strftime("%d.%m.%Y")
)

response_short = {
    "CR": "🟢 Całkowita odpowiedź",
    "PR": "🔵 Częściowa odpowiedź",
    "SD": "🟡 Stabilizacja choroby",
    "PD": "🔴 Progresja choroby",
    "UNCERTAIN": "⚪ Wynik niejednoznaczny"
}

historia_df["Odpowiedź na leczenie"] = (
    historia_df["Odpowiedź"]
    .map(response_short)
)

st.dataframe(
    historia_df[
        [
            "Data badania",
            "Nr PET",
            "Etap_leczenia",
            "Schemat",
            "SUVmax_global",
            "Odpowiedź na leczenie"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# =====================================
# RAPORT KLINICZNY
# =====================================

st.subheader("Raport kliniczny")

for _, row in patient_pet.iterrows():

    with st.expander(
        f"PET {row['Nr PET']} | {row['Data badania'].strftime('%d.%m.%Y')}"
    ):

        odpowiedz = response_map.get(
            row["Odpowiedź"],
            row["Odpowiedź"]
        )

        st.write(
            f"**Odpowiedź:** {odpowiedz}"
        )
        st.write(
            f"**Etap leczenia:** {row.get('Etap_leczenia', '-')}"
        )

        st.write(
            f"**Schemat:** {row.get('Schemat', '-')}"
        )

        st.write(
            f"**SUVmax:** {row.get('SUVmax_global', '-')}"
        )

        st.write(
            f"**Glikemia:** {row.get('Glikemia', '-')}"
        )

        st.write(
            f"**Czas po FDG:** {row.get('Czas_po_FDG', '-')}"
        )

        wnioski = str(row["Wnioski"])

        frazy_do_usuniecia = [
            "Poza tym jak w opisie powyżej.",
            "Poza tym jak w opisie powyzej.",
            "Poza tym jak w opisie powyżej",
            "Poza tym jak w opisie powyzej",
            "Poza tym, jak w opisie powyżej.",
            "Poza tym, jak w opisie powyzej.",
            "Poza tym, jak w opisie powyżej",
            "Poza tym, jak w opisie powyzej"
        ]

        for fraza in frazy_do_usuniecia:
            wnioski = wnioski.replace(fraza, "")

        wnioski = wnioski.strip()

        st.write(wnioski)