import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import sys

# =====================================
# KONFIGURACJA
# =====================================

st.set_page_config(
    page_title="PET Response Analysis",
    page_icon="☢️",
    layout="wide"
)

# =====================================
# NAGŁÓWEK
# =====================================

col1, col2 = st.columns([8, 1])

with col1:
    st.title("☢️ PET Response Analysis")

with col2:

    st.write("")  # lekkie wyrównanie w pionie

    if st.button("🔄 Aktualizuj"):

        with st.spinner("Przetwarzanie danych..."):

            result = subprocess.run(
                [sys.executable, "run_pipeline.py"],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:

            st.success(
                "Baza została zaktualizowana."
            )

            st.cache_data.clear()

            st.rerun()

        else:

            st.error(
                "Wystąpił błąd podczas aktualizacji."
            )

            st.code(result.stderr)

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

import unicodedata

def normalize_patient_name(name):

    if pd.isna(name):
        return ""

    name = str(name).upper().strip()

    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )

    name = " ".join(name.split())

    parts = sorted(name.split())

    return " ".join(parts)


patients_df["Pacjent"] = (
    patients_df["IMIE"].astype(str)
    + " "
    + patients_df["NAZWISKO"].astype(str)
)

patients_df["Pacjent"] = (
    patients_df["Pacjent"]
    .apply(normalize_patient_name)
)

pet_df["Pacjent"] = (
    pet_df["Pacjent"]
    .apply(normalize_patient_name)
)
patients_df = patients_df[
    patients_df["Pacjent"].notna()
]

patients_df = patients_df[
    patients_df["Pacjent"].str.strip() != ""
]


# =====================================
# PRZYGOTOWANIE
# =====================================

pet_df["Data badania"] = pd.to_datetime(
    pet_df["Data badania"],
    errors="coerce"
)

diagnosis_map = {
    "HL": "Chłoniak Hodgkina",
    "DLBCL": "DLBCL",
    "FL": "Chłoniak grudkowy",
    "MCL": "Chłoniak z komórek płaszcza",
    "PMBCL": "Pierwotny chłoniak śródpiersia",
    "PTCL": "Obwodowy chłoniak T-komórkowy",
    "OTHER_B_CELL": "Inny chłoniak B-komórkowy"
}

# =====================================
# STATYSTYKI
# =====================================

st.header("📊 Statystyki grupy")

col1, col2, col3, col4, col5, col6 = st.columns(6)

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
naj_rozpoznanie = (
    pet_df["Rozpoznanie"]
    .value_counts()
    .idxmax()
)

last_pet = (
    pet_df
    .sort_values("Data badania")
    .groupby("Pacjent")
    .tail(1)
)

naj_odpowiedz = (
    last_pet["Odpowiedź"]
    .value_counts()
    .idxmax()
)

followup_years = []

for pacjent in pet_df["Pacjent"].unique():

    tmp = pet_df[
        pet_df["Pacjent"] == pacjent
    ]

    if len(tmp) < 2:
        continue

    dni = (
        tmp["Data badania"].max()
        -
        tmp["Data badania"].min()
    ).days

    followup_years.append(
        dni / 365.25
    )

mean_followup = round(
    sum(followup_years) / len(followup_years),
    1
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

with col5:
    st.metric(
        "Najczęstsza odpowiedź"
        " na leczenie",
        naj_odpowiedz
    )

with col6:
    st.metric(
        "Follow-up",
        f"{mean_followup} lat"
    )
# =====================================
# Aktualny status pacjentów
# =====================================

st.divider()

st.subheader("📈 Aktualny status pacjentów")

last_pet = (
    pet_df
    .sort_values("Data badania")
    .groupby("Pacjent")
    .tail(1)
)

response_counts = (
    last_pet["Odpowiedź"]
    .value_counts(normalize=True)
    * 100
).round(1)

cr = response_counts.get("CR", 0)
pr = response_counts.get("PR", 0)
sd = response_counts.get("SD", 0)
pd_resp = response_counts.get("PD", 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "CR",
        f"{cr}%"
    )

with col2:
    st.metric(
        "PR",
        f"{pr}%"
    )

with col3:
    st.metric(
        "SD",
        f"{sd}%"
    )
with col4:
    st.metric(
        "PD",
        f"{pd_resp}%"
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

    diag["Rozpoznanie"] = diag["Rozpoznanie"].replace({
        "OTHER_B_CELL": "B-CELL NOS"
    })

    fig_diag = px.bar(
        diag.sort_values("Liczba"),
        x="Liczba",
        y="Rozpoznanie",
        orientation="h",
        text="Liczba"
    )

    fig_diag.update_traces(
        textposition="outside"
    )

    fig_diag.update_layout(
        height=450,
        showlegend=False,
        margin=dict(
            l=50,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_diag,
        width="stretch"
    )

with right:

    st.subheader("Aktualny status pacjentów")

    last_pet = (
        pet_df
        .sort_values("Data badania")
        .groupby("Pacjent")
        .tail(1)
    )

    resp = (
        last_pet["Odpowiedź"]
        .value_counts()
        .reset_index()
    )

    resp.columns = [
        "Odpowiedź",
        "Liczba"
    ]

    fig_resp = px.bar(
        resp.sort_values("Liczba"),
        x="Liczba",
        y="Odpowiedź",
        orientation="h",
        text="Liczba"
    )

    fig_resp.update_traces(
        textposition="outside"
    )

    fig_resp.update_layout(
        height=450,
        showlegend=False
    )

    st.plotly_chart(
        fig_resp,
        width="stretch"
    )

# =====================================
# ODPOWIEDŹ NA LECZENIE WG ROZPOZNANIA
# =====================================

st.divider()

st.header("📊 Odpowiedź na leczenie wg rozpoznania")

cross_percent = (
    pd.crosstab(
        pet_df["Rozpoznanie"],
        pet_df["Odpowiedź"],
        normalize="index"
    ) * 100
).round(1)

# zamiana skrótów na pełne nazwy
cross_percent.index = [
    diagnosis_map.get(x, x)
    for x in cross_percent.index
]

heatmap = px.imshow(
    cross_percent,
    text_auto=True,
    aspect="auto"
)

heatmap.update_layout(
    xaxis_title="Odpowiedź",
    yaxis_title="Rozpoznanie",
    height=500
)

tab1, tab2 = st.tabs([
    "📋 Procenty",
    "🔥 Heatmapa"
])

with tab1:

    st.caption(
        "Procent odpowiedzi w obrębie każdego rozpoznania"
    )

    percent_display = (
        cross_percent
        .astype(str)
        .add("%")
    )

    st.dataframe(
        percent_display,
        width="stretch"
    )

with tab2:

    st.caption(
        "Im jaśniejszy kolor, tym częstsza odpowiedź w danym rozpoznaniu"
    )

    st.plotly_chart(
        heatmap,
        width="stretch"
    )
# =====================================
# PACJENT
# =====================================

pacjenci = sorted(
    pet_df["Pacjent"]
    .dropna()
    .unique()
)

st.divider()

st.markdown("# 👤 Pacjent")


col1, col2 = st.columns([4, 1])

with col1:
    pacjent = st.selectbox(
        "Pacjent",
        pacjenci,
        label_visibility="collapsed"
    )

with col2:
    st.metric(
        "Pacjenci",
        len(pacjenci)
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

    liczba_lat = round(
        liczba_dni / 365.25,
        1
    )

    rozpoznanie = patient_pet.iloc[0]["Rozpoznanie"]
    icd10 = patient_pet.iloc[0]["ICD10"]

    ostatnia_odpowiedz = patient_pet.iloc[-1]["Odpowiedź"]



    st.header("📋 Podsumowanie pacjenta")

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



#


    # =====================================
    # ROZPOZNANIE I LECZENIE
    # =====================================

    leczenie = ""

    if "Leczenie" in patient_row.index:
        leczenie = str(
            patient_row["Leczenie"]
        ).strip()

    # Kolory rozpoznań

    diagnosis_colors = {
        "HL": "#00B894",
        "DLBCL": "#E74C3C",
        "FL": "#3498DB",
        "MCL": "#9B59B6",
        "PMBCL": "#F39C12",
        "PTCL": "#E91E63",
        "OTHER_B_CELL": "#95A5A6"
    }

    diag_color = diagnosis_colors.get(
        rozpoznanie,
        "#4DA3FF"
    )

    # Kolory leczenia

    treatment_colors = {
        "ABVD": "#00B894",
        "BEACOPP": "#E74C3C",
        "R-CHOP": "#3498DB",
        "R-DHAP": "#9B59B6",
        "R-ICE": "#F39C12",
        "ASCT": "#E91E63"
    }

    leczenie_color = "#4DA3FF"

    for treatment, color in treatment_colors.items():

        if treatment in leczenie.upper():
            leczenie_color = color
            break


    # Kafle

    col1, col2 = st.columns(2)

    with col1:

        diagnosis_name = diagnosis_map.get(
            rozpoznanie,
            rozpoznanie
        )

        st.markdown(
            f"""
    <div style="
    background-color:#16324F;
    padding:15px;
    border-radius:10px;
    border-left:5px solid {diag_color};
    margin-bottom:10px;
    color:white;
    ">
    <b>Rozpoznanie</b><br><br>
    {diagnosis_name}
    </div>
    """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
    <div style="
    background-color:#16324F;
    padding:15px;
    border-radius:10px;
    border-left:5px solid {leczenie_color};
    margin-bottom:10px;
    color:white;
    ">
    <b>Leczenie</b><br><br>
    {leczenie}
    </div>
    """,
            unsafe_allow_html=True
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

        if liczba_lat < 1:
            followup = f"{liczba_dni} dni"
        else:
            followup = f"{liczba_lat} roku"

        st.metric(
            "Follow-up",
            followup
        )


    # Aktualny status

    status_labels = {
        "CR": "Całkowita odpowiedź metaboliczna",
        "PR": "Częściowa odpowiedź metaboliczna",
        "SD": "Stabilizacja choroby",
        "PD": "Progresja choroby",
        "UNCERTAIN": "Wynik niejednoznaczny"
    }

    status_colors = {
        "CR": "#198754",
        "PR": "#0dcaf0",
        "SD": "#ffc107",
        "PD": "#dc3545",
        "UNCERTAIN": "#6c757d"
    }

    status = ostatnia_odpowiedz or "UNCERTAIN"

    st.markdown(
        f"""
        <div style="
            background-color:#16324F;
            padding:15px;
            border-radius:10px;
            border-left:5px solid {status_colors.get(status, '#6c757d')};
            margin-bottom:10px;">
            <div style="font-size:14px;color:#B8D4F0;">
                Aktualny status
            </div>
            <div style="font-size:20px;font-weight:bold;">
                {status}
            </div>
            <div style="font-size:14px;">
                {status_labels.get(status, status)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
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

response_short = {
    "CR": "🟢 CR",
    "PR": "🔵 PR",
    "SD": "🟡 SD",
    "PD": "🔴 PD",
    "UNCERTAIN": "⚪ NIEJEDNOZNACZNY"
}

stage_map = {
    "BASELINE": "Ocena zaawansowania",
    "INTERIM": "Ocena śródleczeniowa",
    "END_OF_TREATMENT": "Po zakończeniu leczenia",
    "POST_RT": "Po radioterapii",
    "POST_ASCT": "Po autoprzeszczepieniu",
    "RELAPSE": "Podejrzenie wznowy",
    "FOLLOW_UP": "Kontrola",
    "OTHER": "-"
}

st.subheader("Historia badań PET/CT")

historia_df = patient_pet.copy()

# pełne nazwy odpowiedzi
historia_df["Odpowiedź pełna"] = (
    historia_df["Odpowiedź"]
    .map(response_map)
    .fillna(historia_df["Odpowiedź"])
)

# skrócone odpowiedzi z ikonami
historia_df["Odpowiedź na leczenie"] = (
    historia_df["Odpowiedź"]
    .map(response_short)
    .fillna(historia_df["Odpowiedź"])
)

# tłumaczenie etapu leczenia — KLUCZOWE, musi być przed tabelą
historia_df["Etap"] = (
    historia_df["Etap_leczenia"]
    .map(stage_map)
    .fillna("-")
)

# format daty
historia_df["Data badania"] = (
    historia_df["Data badania"]
    .dt.strftime("%d.%m.%Y")
)
historia_df = historia_df.rename(
    columns={
        "SUVmax_global": "SUVmax",
        "Czas_po_FDG": "Czas FDG [min]"
    }
)
# tabela
st.dataframe(
    historia_df[
        [
            "Nr PET",
            "Data badania",
            "Etap",
            "Odpowiedź na leczenie",
            "Lokalizacja_zmian",
            "SUVmax",
            "Glikemia",
            "Czas FDG [min]"
        ]
    ],
    width="stretch",
    hide_index=True
)

# =====================================
# RAPORT KLINICZNY
# =====================================
def short_text(text, max_sentences=4):


    if pd.isna(text):
        return "-"

    text = str(text).strip()
    if text.lower() in ["nan", ""]:
        return "-"

    import re
    zdania = re.split(r'(?<=[.!?])\s+', text)

    # frazy klinicznie istotne
    kluczowe = [
        "fdg", "ognisk", "aktyw", "progres", "odpowied", "stabiliz",
        "brak cech", "brak aktyw", "nacie", "zwiększ", "zmniejsz",
        "metabolicz", "chorob", "zlokaliz", "węzł", "śródpiers",
        "płuc", "kośc", "wątro", "śledzion", "naciekanie"
    ]

    # frazy do odrzucenia
    smieci = [
        "poza tym", "jak wyżej", "jak powyżej",
        "do kontroli", "kontrolnie", "badanie wykonano",
        "w porównaniu", "technika badania"
    ]

    def istotne(z):
        z_low = z.lower()
        if any(s in z_low for s in smieci):
            return False
        return any(k in z_low for k in kluczowe)

    # --- ZAWSZE definiujemy czyste ---
    czyste = []
    for z in zdania:
        z = z.strip()
        if len(z) < 5:
            continue
        if any(s in z.lower() for s in smieci):
            continue
        czyste.append(z)

    if not czyste:
        return "-"

    # wybór zdań istotnych
    istotne_zdania = [z for z in czyste if istotne(z)]

    # jeśli brak zdań istotnych -> bierzemy pierwsze sensowne
    if not istotne_zdania:
        wynik = " ".join(czyste[:max_sentences])
    else:
        wynik = " ".join(istotne_zdania[:max_sentences])

    # --- NORMALIZACJA WIELOKROPKÓW ---
    wynik = re.sub(r'\.{3,}', '...', wynik)      # zamień 3+ kropek na '...'
    wynik = re.sub(r'\.\s*\.\s*\.', '...', wynik)  # usuń '... ...'
    wynik = wynik.rstrip('.')                    # usuń kropkę na końcu

    # dodaj końcowe "..." tylko jeśli tekst był dłuższy
    if len(istotne_zdania) > max_sentences:
        wynik += "..."

    return wynik


st.subheader("Raport kliniczny")

for _, row in patient_pet.iterrows():

    with st.expander(
            f"PET {row['Nr PET']} | {row['Data badania'].strftime('%d.%m.%Y')}"
    ):

        odpowiedz = response_map.get(
            row["Odpowiedź"],
            row["Odpowiedź"]
        )

        st.write(f"**Odpowiedź:** {odpowiedz}")

        # --- OPISY ANATOMICZNE ---
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🧠 Głowa i szyja")
            st.write(
                short_text(
                    row.get("Glowa_i_szyja", "")
                )
            )

            st.markdown("#### 🫀 Brzuch i miednica")
            st.write(
                short_text(
                    row.get("Brzuch_i_miednica", "")
                )
            )

        with col2:
            st.markdown("#### 🫁 Klatka piersiowa")
            st.write(
                short_text(
                    row.get("Klatka_piersiowa", "")
                )
            )

            st.markdown("#### 🦴 Układ kostny")
            st.write(
                short_text(
                    row.get("Uklad_kostny", "")
                )
            )

        # --- WNIOSKI ---
        wnioski = str(row.get("Wnioski", ""))

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

        st.markdown("### 📝 Wnioski")
        st.write(wnioski.strip())
