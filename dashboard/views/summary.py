from __future__ import annotations

from pathlib import Path

import streamlit as st

from data_loader import load_dashboard_summary, load_parameter_data, load_validation_data, load_typical_model_table

def render_summary_view():
    st.subheader("General Summary")

    summary = load_dashboard_summary()
    validation_df = load_validation_data()
    params_df = load_parameter_data()
    groups_df = load_typical_model_table()

    if summary:
        st.subheader("Runtime data policy")
        st.info(summary.get("runtime_data_policy", {}).get("rule", "The dashboard reads from outputs/ only."))

        cols = st.columns(4)
        cols[0].metric("Validated motors", f"{len(validation_df):,}")
        cols[1].metric("Solved motors", f"{len(params_df):,}")
        cols[2].metric("Typical groups", f"{len(groups_df):,}")
        
    else:
        st.info("dashboard_summary.json not found in outputs/.")

    summary_path = Path("outputs") / "run_evaluation.md"
    if summary_path.exists():
        st.subheader("Evaluation summary")
        st.markdown(summary_path.read_text(encoding="utf-8"))
