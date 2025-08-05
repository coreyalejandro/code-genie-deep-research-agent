import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "knowledge.db"

st.set_page_config(page_title="Research Dashboard", layout="wide")
st.title("🧠 Deep Research Agent Dashboard")

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM knowledge", conn)
    conn.close()
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
min_depth, max_depth = st.sidebar.slider("Depth", 1, 10, (1, 2))
cluster = st.sidebar.selectbox("Cluster", options=["All"] + sorted(df['cluster_label'].dropna().unique().astype(str).tolist()))

query = st.sidebar.text_input("Search text")

# Filter logic
filtered = df[
    (df["depth"] >= min_depth) & (df["depth"] <= max_depth)
]

if cluster != "All":
    filtered = filtered[filtered["cluster_label"].astype(str) == cluster]

if query:
    filtered = filtered[filtered["summary"].str.contains(query, case=False, na=False)]

# Table view
st.write(f"Showing {len(filtered)} entries")
st.dataframe(filtered, use_container_width=True)

# Export buttons
st.download_button(
    label="⬇️ Export JSON",
    data=filtered.to_json(orient="records", indent=2),
    file_name="filtered_knowledge.json",
    mime="application/json"
)

st.download_button(
    label="⬇️ Export Markdown",
    data="\n".join([f"- {r}" for r in filtered['summary'].tolist()]),
    file_name="filtered_summary.md",
    mime="text/markdown"
)
