import os
import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="AI Platform — Quality & Cost", layout="wide")
st.title("AI Platform — Quality, Latency & Cost")

with psycopg.connect(os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")) as conn:
    df = pd.read_sql("SELECT * FROM llm_calls ORDER BY ts DESC LIMIT 5000", conn)

if df.empty:
    st.info("No calls yet — send a request to /v1/chat.")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calls", len(df))
    c2.metric("Total cost (USD)", f"{df.cost_usd.astype(float).sum():.4f}")
    c3.metric("p95 latency (ms)", int(df.latency_ms.quantile(0.95)))
    c4.metric("Self-hosted share", f"{(df.route == 'self_hosted').mean():.0%}")
    st.subheader("Cost by tenant")
    st.bar_chart(df.groupby("tenant_id").cost_usd.apply(lambda s: s.astype(float).sum()))
    st.subheader("Calls by route / reason")
    st.dataframe(df.groupby(["route", "reason"]).size().rename("calls").reset_index())
    st.subheader("Latency over time")
    st.line_chart(df.set_index("ts").latency_ms)
