import streamlit as st
import plotly.graph_objects as go

from data.db import query_df
from data.queries_lookup import LOOKUP_BREEDS, LOOKUP_YEARS
from data.queries import DATA_PRODUCTION_LACT

# ------------------------------------------------------
# PAGE TITLE
# ------------------------------------------------------
st.title("Διασπορά Γαλακτοπαραγωγής & Διάρκειας Ανά Γ.Π.")


# ------------------------------------------------------
# Load lookup tables
# ------------------------------------------------------
breeds_df = query_df(LOOKUP_BREEDS)
breed_options = {}
for index, row in breeds_df.iterrows():
    key = row["name"]
    value = row["id"]
    breed_options[key] = value

years_df = query_df(LOOKUP_YEARS)
years_option = {}
for index, row in years_df.iterrows():
    key = row["p_year"]
    value = row["p_year"]
    years_option[key] = value


# ------------------------------------------------------
# User Filters
# ------------------------------------------------------
with st.container():
    st.subheader("Φίλτρα")

    col1, col2, col3 = st.columns(3)

    # Φυλή
    with col1:
        selected_breed = st.selectbox(
            "Επιλογή Φυλής",
            list(breed_options.keys())
        )

    # Έτος
    with col2:
        year_from = st.selectbox(
            "Επιλογή Έτους Από",
            list(years_option.keys())
        )

        year_to = st.selectbox(
            "Επιλογή Έτους Έως",
            list(years_option.keys()),
            index=len(years_option) - 1  # -> τελευταία (μέγιστη)
        )

    # Διάρκεια γαλ/γής ≥ X ημέρες
    with col3:
        min_days = st.number_input(
            "Διάρκεια γαλ/γής ≥ (ημέρες)",
            min_value=0,
            max_value=365,
            value=90
        )

# Έλεγχος εύρους Έτους
if year_from > year_to:
    st.error("Στο πεδίο Παραγωγικό Έτος η τιμή 'Από' πρέπει να είναι μικρότερη ή ίση από την 'Έως'.")
    st.stop()

selected_breed_id = breed_options[selected_breed]

# Αν η φυλή είναι Άγνωστη -> exit
if selected_breed_id == 1:
    st.warning("Παρακαλώ επιλέξτε έγκυρη φυλή.")
    st.stop()

st.write("---")


# ------------------------------------------------------
# Execute SQL queries
# ------------------------------------------------------
params = {
    "breed": int(selected_breed_id),
    "year_from": int(year_from),
    "year_to": int(year_to),
    "min_days": int(min_days)
}

df = query_df(DATA_PRODUCTION_LACT, params)
df = df.round(2)  # 2 decimal places

if df.empty:
    st.warning("Δεν βρέθηκαν δεδομένα για τα συγκεκριμένα φίλτρα.")
    st.stop()


# ------------------------------------------------------
# Plotly Μέση Γαλακτοπαραγωγή (kg)
# ------------------------------------------------------
st.subheader("Μέση Γαλακτοπαραγωγή (kg) + Τυπική Απόκλιση ανά Γ.Π.")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["p_lact"],
        y=df["avg_milk"],
        mode="markers",
        name="Avg Milk (kg)",
        error_y=dict(
            type="data",
            array=df["std_milk"],
            visible=True
        ),
        marker=dict(
            size=10,
            symbol="circle",
            color="#4DA6FF"
        )
    )
)

fig.update_layout(
    xaxis_title="Γαλακτική Περίοδος",
    yaxis_title="Μ.Ο. Γαλ/γής (kg)",
    showlegend=False,
    height=500,
    margin=dict(l=70, r=40, t=40, b=60)
)
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, width="stretch")


# ------------------------------------------------------
# Plotly: Μέση Διάρκεια Γαλ/γής
# ------------------------------------------------------
st.subheader("Μέση Διάρκεια Γαλακτοπαραγωγής (ημέρες) + Τυπική Απόκλιση ανά Γ.Π.")

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=df["p_lact"],
        y=df["avg_days"],
        mode="markers",
        name="Avg Duration (days)",
        error_y=dict(
            type="data",
            array=df["std_days"],
            visible=True
        ),
        marker=dict(
            size=10,
            symbol="circle",
            color="#FFB347"
        )
    )
)

fig2.update_layout(
    xaxis_title="Γαλακτική Περίοδος",
    yaxis_title="Μ.Ο. Διάρκεια (ημέρες)",
    showlegend=False,
    height=500,
    margin=dict(l=70, r=40, t=40, b=60)
)

fig2.update_xaxes(dtick=1)
st.plotly_chart(fig2, width="stretch")




# ------------------------------------------------------
# Data Table
# ------------------------------------------------------
st.subheader("Πίνακας Δεδομένων")
st.dataframe(df, width="stretch")
