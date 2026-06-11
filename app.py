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

# dane pacjenta

patient_info = patients_df[
    patients_df["Pacjent"] == pacjent
]

if not patient_info.empty:

    st.subheader("Dane pacjenta")

    st.dataframe(
        patient_info,
        use_container_width=True
    )

# historia PET

patient_pet = (
    pet_df[
        pet_df["Pacjent"] == pacjent
    ]
    .sort_values(
        "Data badania"
    )
)

st.subheader("Historia badań PET")

st.dataframe(
    patient_pet[
        [
            "Nr PET",
            "Data badania",
            "Rozpoznanie",
            "Odpowiedź"
        ]
    ],
    use_container_width=True
)

# raport kliniczny

st.subheader("Raport kliniczny")

for _, row in patient_pet.iterrows():

    with st.expander(
        f"PET {row['Nr PET']} | {row['Data badania'].date()}"
    ):

        st.write(
            f"### Odpowiedź: {row['Odpowiedź']}"
        )

        st.write(
            row["Wnioski"]
        )

# =====================================
# SUROWE DANE
# =====================================

st.divider()

with st.expander(
    "Pokaż pet_master.xlsx"
):
    st.dataframe(
        pet_df,
        use_container_width=True
    )