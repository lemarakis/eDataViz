import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.db import query_df
from data.queries_lookup import LOOKUP_BREEDS
from data.queries import DATA_PRODUCTION, DATA_PRODUCTION_TOTAL


# ------------------------------------------------------
# PAGE: Στατιστικά ανά Παραγωγικό Έτος
# ------------------------------------------------------
st.title("Στατιστικά ανά Παραγωγικό Έτος")


# ------------------------------------------------------
# Load lookup tables
# ------------------------------------------------------
breeds_df = query_df(LOOKUP_BREEDS)

breed_options = {}
for index, row in breeds_df.iterrows():
    key = row["name"]
    value = row["id"]
    breed_options[key] = value


# ------------------------------------------------------
# User Filters
# ------------------------------------------------------
with st.container():
    st.subheader("Φίλτρα")

    col1, col2, col3, col4 = st.columns(4)

    # Φυλή
    with col1:
        selected_breed = st.selectbox(
            "Επιλογή Φυλής",
            list(breed_options.keys())
        )

    # Γαλακτική περίοδος Από
    with col2:
        lact_from = st.selectbox(
            "Γαλ. περίοδος Από",
            list(range(1, 16)),
            index=0
        )

    # Γαλακτική περίοδος Έως
    with col3:
        lact_to = st.selectbox(
            "Γαλ. περίοδος Έως",
            list(range(1, 16)),
            index=14
        )

    # Διάρκεια γαλ/γής ≥ X ημέρες
    with col4:
        min_days = st.number_input(
            "Διάρκεια γαλ/γής ≥ (ημέρες)",
            min_value=0,
            max_value=365,
            value=90
        )

# Έλεγχος εύρους Γαλ. Περιόδου
if lact_from > lact_to:
    st.error("Η τιμή 'Από' πρέπει να είναι μικρότερη ή ίση από την 'Έως'.")
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
    "lact_from": int(lact_from),
    "lact_to": int(lact_to),
    "min_days": int(min_days)
}

df = query_df(DATA_PRODUCTION, params=params)
df = df.round(2)  # 2 decimal places
df_totals = query_df(DATA_PRODUCTION_TOTAL, params=params) # Συγκεντρωτικά
df_totals = df_totals.round(2)  # 2 decimal places

# ------------------------------------------------------
# Display results
# ------------------------------------------------------
if df.empty or df_totals.empty:
    st.warning("Δεν βρέθηκαν δεδομένα για τα συγκεκριμένα φίλτρα.")
    st.stop()


# ------------------------------------------------------
# Summary Table
# ------------------------------------------------------
st.subheader("Συγκεντρωτικά Μεγέθη")

# Παίρνουμε την πρώτη (και μοναδική) γραμμή
row = df_totals.iloc[0]

summary_data = {
    "Σύνολο Γεννήσεων": row["total_births"],
    "Μέση Διάρκεια Γαλ/γής (ημ.).": row["avg_days"],
    "Μέση Γαλ/γή (κιλά)": row["avg_milk"],
    "Τυπ. Απόκλιση Γαλ/γής": row["std_milk"],
    "Τυπ. Απόκλιση Διάρκειας Γαλ/γής": row["std_days"],
    "Τυπ. Απόκλιση Γεννήσεων": row["std_births"],
    "Μέσος όρος Πολυδυμίας": row["avg_poly"],
    "Πλήθος Ετών": row["total_years"]
}

# Μετατροπή σε DataFrame 2 γραμμών (Δείκτης, Τιμή)
summary_df = pd.DataFrame(
    list(summary_data.items()),
    columns=["Δείκτης", "Τιμή"]
)

st.dataframe(summary_df, width="stretch")

st.write("---")

# ------------------------------------------------------
# Γράφημα Plotly Dual-Y (Milk + Days)
# ------------------------------------------------------
st.subheader("Γαλακτοπαραγωγή & Διάρκεια Γαλ/γής ανά Έτος")

fig = go.Figure()

# Γραμμή 1 - Μέση Γαλακτοπαραγωγή (αριστερός άξονας)
fig.add_trace(
    go.Scatter(
        x=df["p_year"],
        y=df["avg_milk"],
        mode="lines+markers",
        name="Μέση Γαλ/γή (κιλά)",
        line=dict(color="blue", width=3),
        hovertemplate=(
            "<b>Έτος</b>: %{x}<br>"
            "<b>Μέση Γαλ/γή</b>: %{y} κιλά<extra></extra>"
        ),
        yaxis="y"
    )
)

# Γραμμή 2 - Μέση Διάρκεια Γαλ/γής (δεξιός άξονας)
fig.add_trace(
    go.Scatter(
        x=df["p_year"],
        y=df["avg_days"],
        mode="lines+markers",
        name="Μέση Διάρκεια Γαλ/γής (ημέρες)",
        line=dict(color="orange", width=3),
        hovertemplate=(
            "<b>Έτος</b>: %{x}<br>"
            "<b>Μέση Διάρκεια</b>: %{y} ημέρες<extra></extra>"
        ),
        yaxis="y2"
    )
)

# Ρυθμίσεις layout με δύο άξονες Y
fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis=dict(
        title="Έτος"
    ),
    yaxis=dict(
        title="Μέση Γαλ/γή (κιλά)",
        side="left"
    ),
    yaxis2=dict(
        title="Μέση Διάρκεια Γαλ/γής (ημέρες)",
        side="right",
        overlaying="y"
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5,
        title_text=""
    )
)

st.plotly_chart(fig, width="stretch")

st.write("---")

# ------------------------------------------------------
# Mini STD Charts (per year)
# ------------------------------------------------------
st.subheader("Τυπικές Αποκλίσεις ανά Έτος (STD)")

col_std1, col_std2, col_std3 = st.columns(3)

# --- STD Milk ---
fig_std_milk = go.Figure()
fig_std_milk.add_trace(
    go.Scatter(
        x=df["p_year"],
        y=df["std_milk"],
        mode="lines+markers",
        name="STD Γάλακτος",
        line=dict(color="blue", width=2),
        hovertemplate=
        "<b>Έτος</b>: %{x}<br>" +
        "<b>STD Γάλακτος</b>: %{y}<extra></extra>"
    )
)
fig_std_milk.update_layout(
    height=250,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Έτος",
    yaxis_title="STD Γάλακτος"
)
col_std1.plotly_chart(fig_std_milk, width="stretch")

# --- STD Days ---
fig_std_days = go.Figure()
fig_std_days.add_trace(
    go.Scatter(
        x=df["p_year"],
        y=df["std_days"],
        mode="lines+markers",
        name="STD Ημερών",
        line=dict(color="orange", width=2),
        hovertemplate=
        "<b>Έτος</b>: %{x}<br>" +
        "<b>STD Ημερών</b>: %{y}<extra></extra>"
    )
)
fig_std_days.update_layout(
    height=250,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Έτος",
    yaxis_title="STD Ημερών"
)
col_std2.plotly_chart(fig_std_days, width="stretch")

# --- STD Births ---
fig_std_births = go.Figure()
fig_std_births.add_trace(
    go.Scatter(
        x=df["p_year"],
        y=df["std_births"],
        mode="lines+markers",
        name="STD Γεννήσεων",
        line=dict(color="green", width=2),
        hovertemplate=
        "<b>Έτος</b>: %{x}<br>" +
        "<b>STD Γεννήσεων</b>: %{y}<extra></extra>"
    )
)
fig_std_births.update_layout(
    height=250,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Έτος",
    yaxis_title="STD Γεννήσεων"
)
col_std3.plotly_chart(fig_std_births, width="stretch")

st.write("---")

# ------------------------------------------------------
# Data Table
# ------------------------------------------------------
st.subheader("Ανάλυση Δεδομένων")
st.dataframe(df, width="stretch")
