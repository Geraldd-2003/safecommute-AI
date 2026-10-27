"""Data: preview of the dataset in use."""

import altair as alt
import streamlit as st

import engine as E
from ui import components as C
from ui import state, style

c = state.ctx()
df = c.df

C.page_header("Data", f"Dataset in use: {c.dataset}.")
k = st.columns(4)
k[0].metric("Commuters", len(df), border=True)
k[1].metric("Starting places", df["Origin_Address"].nunique(), border=True)
k[2].metric("Destinations", df["Destination_Address"].nunique(), border=True)
k[3].metric("Time slots", df["Travel_Time_Slot"].nunique(), border=True)

if c.simulated_gender:
    st.info("Gender and Women_Only are simulated in this dataset (gender guessed from the first name, about 35% "
            "of women opt in). In the real app each user declares them.", icon=":material/science:")
elif (df["Gender"] == "Not declared").all():
    st.info("This file has no Gender / Women_Only columns, so nobody is in women-only mode.",
            icon=":material/info:")

query = st.text_input("Filter rows", placeholder="Search a name, place or slot",
                      help="Keeps the rows where any column contains this text.")
view = df
if query:
    mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)
    view = df[mask]
st.caption(f"{len(view)} of {len(df)} rows")
st.dataframe(view, hide_index=True, width="stretch", height=320)


def count_chart(col: str, color: str) -> alt.Chart:
    counts = df[col].value_counts().rename_axis("Place").reset_index(name="Commuters")
    return alt.Chart(counts).mark_bar(color=color, cornerRadiusEnd=3).encode(
        x=alt.X("Commuters:Q"), y=alt.Y("Place:N", sort="-x", title=None, axis=alt.Axis(labelLimit=280)),
        tooltip=["Place", "Commuters"]).properties(height=max(160, 22 * len(counts)))


a, b = st.columns(2, gap="large")
with a, st.container(border=True):
    st.markdown("**Commuters per starting place**")
    st.altair_chart(count_chart("Origin_Address", style.PRIMARY), width="stretch")
with b, st.container(border=True):
    st.markdown("**Commuters per destination**")
    st.altair_chart(count_chart("Destination_Address", style.ACCENT), width="stretch")

st.markdown("**Columns.** Required: " + ", ".join(f"`{x}`" for x in E.REQUIRED_COLUMNS)
            + ". Optional: `Gender` (F / M), `Women_Only` (True / False).")
