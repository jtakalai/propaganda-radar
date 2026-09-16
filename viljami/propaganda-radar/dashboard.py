"""Review UI: see predictions, correct them by hand.

    streamlit run dashboard.py
"""

from pathlib import Path

import streamlit as st

from classifier import LABELS
from store import CsvStore

DATA_PATH = Path(__file__).resolve().parent / "data" / "feed.csv"

st.set_page_config(page_title="Propaganda Radar", layout="wide")
st.title("Propaganda Radar")

store = CsvStore(DATA_PATH)
df = store.load()

if df.empty:
    st.info("No headlines yet - run feeder.py first.")
else:
    df["label"] = df["label"].where(df["label"] != "", df["predicted_label"])
    edited = st.data_editor(
        df,
        column_config={
            "label": st.column_config.SelectboxColumn("label", options=LABELS),
            "headline": st.column_config.TextColumn("headline", width="large"),
        },
        disabled=["outlet", "date", "headline", "url", "predicted_label", "predicted_confidence"],
        hide_index=True,
        use_container_width=True,
    )
    if st.button("Save corrections"):
        changed = edited[edited["label"] != df["predicted_label"]]
        for _, row in changed.iterrows():
            store.set_label(row["url"], row["label"], labelled_by="ui")
        st.success(f"saved {len(changed)} labels")
