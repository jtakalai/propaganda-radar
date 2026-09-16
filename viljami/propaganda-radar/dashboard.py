"""Review UI: browse latest headlines, click one to see the prediction, relabel it.

    streamlit run dashboard.py
"""

import json

import streamlit as st

from classifier import LABELS
from store import DEFAULT_DATA_PATH, CsvStore

LIST_COLUMNS = ["outlet", "date", "headline", "predicted_label", "label", "match"]

st.set_page_config(page_title="Propaganda Radar", layout="wide")
st.title("Propaganda Radar")

store = CsvStore(DEFAULT_DATA_PATH)
df = store.load()

if df.empty:
    st.info("No headlines yet - run feeder.py first.")
    st.stop()

labelled = df[df["label"] != ""]
with st.sidebar:
    st.metric("Total headlines", len(df))
    st.metric("Labelled", f"{len(labelled)} ({len(labelled) / len(df):.0%})")
    st.caption("By label:")
    st.dataframe(labelled["label"].value_counts(), use_container_width=True)

# blank until labelled, then an instant right/wrong check against the model -
# also the filter for "give me the training set": df[df["label"] != ""]
df["match"] = df.apply(
    lambda r: "" if r["label"] == "" else ("✓" if r["label"] == r["predicted_label"] else "✗"),
    axis=1,
)

selection = st.dataframe(
    df[LIST_COLUMNS],
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
    key="table",
)

selected_rows = selection.selection.rows
if not selected_rows:
    st.caption("Click a row to see the article and relabel it.")
    st.stop()

row = df.iloc[selected_rows[0]]

st.divider()
left, right = st.columns([3, 2])

with left:
    st.subheader(row["headline"])
    st.caption(f"{row['outlet']} · {row['date']}")
    st.link_button("Open original article", row["url"])
    if row["summary"]:
        st.write(row["summary"])

with right:
    st.metric("Predicted label", row["predicted_label"])

    st.markdown("**Correct label**")
    current = row["label"] or row["predicted_label"]
    corrected = st.selectbox("label", LABELS, index=LABELS.index(current), key=f"label-{row['url']}", label_visibility="collapsed")

    st.markdown("**Comment** - why is this right/wrong?")
    comment = st.text_area("comment", value=row["comment"], key=f"comment-{row['url']}", label_visibility="collapsed")

    if st.button("Save"):
        store.set_label(row["url"], corrected, labelled_by="ui", comment=comment)
        st.success("saved")
        st.rerun()

    with st.expander("Debug: model output"):
        st.caption(f"model: {row['model_version']}  ·  confidence: {row['predicted_confidence']}")
        probs = json.loads(row["predicted_probs"] or "{}")
        st.bar_chart(probs)
