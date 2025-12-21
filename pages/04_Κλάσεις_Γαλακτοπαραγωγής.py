import streamlit as st

from data.db import query_df
from data.queries_lookup import LOOKUP_BREEDS,LOOKUP_YEARS
from data.queries import DATA_CLASSIFICATION


# ------------------------------------------------------
# PAGE: Στατιστικά ανά Κλάση Γαλακτοπαραγωγής
# ------------------------------------------------------
st.title("Στατιστικά ανά Κλάση Γαλακτοπαραγωγής")


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

    # Γαλακτική περίοδος Από
    with col2:
        lact_from = st.selectbox(
            "Γαλ. περίοδος Από",
            list(range(1, 16)),
            index=0
        )

    # Γαλακτική περίοδος Έως
        lact_to = st.selectbox(
            "Γαλ. περίοδος Έως",
            list(range(1, 16)),
            index=14
        )

    # Έτος
    with col3:
        year_from = st.selectbox(
            "Επιλογή Έτους Από",
            list(years_option.keys())
        )

        year_to = st.selectbox(
            "Επιλογή Έτους Έως",
            list(years_option.keys()),
            index=len(years_option) - 1  # -> τελευταία (μέγιστη)
        )

# Έλεγχος εύρους Γαλ. Περιόδου
if lact_from > lact_to:
    st.error("Στο πεδίο Γαλ. περίοδος η τιμή 'Από' πρέπει να είναι μικρότερη ή ίση από την 'Έως'.")
    st.stop()

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
    "lact_from": int(lact_from),
    "lact_to": int(lact_to),
    "year_from": int(year_from),
    "year_to": int(year_to)
}

df = query_df(DATA_CLASSIFICATION, params=params)
df = df.round(2)  # 2 decimal places

# ------------------------------------------------------
# Display results
# ------------------------------------------------------
if df.empty:
    st.warning("Δεν βρέθηκαν δεδομένα για τα συγκεκριμένα φίλτρα.")
    st.stop()

# ------------------------------------------------------
# Bar Chart + Curved Line + Ideal Gaussian Curve
# ------------------------------------------------------
st.subheader("Πλήθος Ζώων ανά Κλάση Γαλακτοπαραγωγής")

import numpy as np
import math
import plotly.graph_objects as go

# Βασικά δεδομένα
class_labels = df["class_range"].astype(str)
counts = df["total_animals"].values


# Υπολογισμός midpoints π.χ. "101 - 150" -> 125
def get_midpoint(r):
    p = r.replace(" ", "").split("-")
    return (int(p[0]) + int(p[1])) / 2


midpoints = df["class_range"].apply(get_midpoint).values

fig = go.Figure()

# ------------------------------------------------------
# 1. Bars
# ------------------------------------------------------
fig.add_trace(go.Bar(
    x=midpoints,
    y=counts,
    name="Ζώα",
    marker=dict(color="#762124")
))

# ------------------------------------------------------
# 2. πραγματική κατανομή
# ------------------------------------------------------
fig.add_trace(go.Scatter(
    x=midpoints,
    y=counts,
    mode="lines+markers",
    name="Πραγματική Κατανομή",
    line=dict(color="blue", width=2, shape="spline")
))

# ------------------------------------------------------
# 3. Ιδανική Gauss
# ------------------------------------------------------
if len(midpoints) > 1 and counts.max() > 0:
    # Midpoint της κλάσης με το max πλήθος
    peak_midpoint = midpoints[np.argmax(counts)]

    # Weighted std
    variance = np.average((midpoints - peak_midpoint) ** 2, weights=counts)
    std_x = math.sqrt(variance)

    # Ομαλό x-range
    x_smooth = np.linspace(midpoints.min(), midpoints.max(), 300)

    # Gauss centered at peak
    gauss_raw = np.exp(-0.5 * ((x_smooth - peak_midpoint) / std_x) ** 2)

    # Scale ώστε peak(Y) = max(counts)
    gauss_scaled = gauss_raw * (counts.max() / gauss_raw.max())

    # Ιδανική καμπύλη Gauss
    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=gauss_scaled,
        mode="lines",
        name="Ιδανική Καμπύλη Gauss",
        hoverinfo="skip",  # no hover
        line=dict(color="green", width=3, shape="spline")
    ))

# ------------------------------------------------------
# Layout
# ------------------------------------------------------
fig.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="Κλάση Γαλακτοπαραγωγής",
        tickmode="array",
        tickvals=midpoints.tolist(),
        ticktext=class_labels.tolist()
    ),
    yaxis_title="Πλήθος Ζώων",
    height=450,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------
# Data Table
# ------------------------------------------------------
st.subheader("Ανάλυση Δεδομένων")
st.dataframe(df, width="stretch")
