from __future__ import annotations

import pandas as pd
import streamlit as st

from data_loader import load_validation_data


METRICS = {
    "current": {
        "catalog": "actual_i_rated_a",
        "predicted": "pred_i_rated_a",
        "error": "err_i_pct",
        "label": "Rated current",
    },
    "torque": {
        "catalog": "actual_t_rated_nm",
        "predicted": "pred_t_rated_nm",
        "error": "err_t_pct",
        "label": "Rated torque",
    },
    "efficiency": {
        "catalog": "actual_eta_rated",
        "predicted": "pred_eta_rated",
        "error": "err_eta_pct",
        "label": "Efficiency",
    },
    "power_factor": {
        "catalog": "actual_pf_rated",
        "predicted": "pred_pf_rated",
        "error": "err_pf_pct",
        "label": "Power factor",
    },
}

def render_motor_case_view():
    st.header("Individual Motor Case")
    df = load_validation_data()
    
    if df.empty:
        st.warning("No data available.")
        return

    # Motor selector
    motor_list = sorted(df["motor_id"].astype(str).unique())
    selected_motor = st.selectbox("Select a motor", motor_list)
    
    motor_data = df[df['motor_id'] == selected_motor].iloc[0]
    
    # Comparison table
    st.subheader("Comparison: Catalog vs. Predicted")
    vars = list(METRICS.keys())
    comp_data = []
    for var in vars:
        metric_cfg = METRICS[var]
        comp_data.append({
            "Variable": metric_cfg["label"],
            "Catalog": motor_data[metric_cfg["catalog"]],
            "Predicted": motor_data[metric_cfg["predicted"]],
            "Error (%)": motor_data[metric_cfg["error"]] * 100,
        })
    
    st.table(pd.DataFrame(comp_data))
    
    # Summary of finding
    st.subheader("Key Findings")
    st.info(f"The model predicts this motor with a nominal MAPE of {motor_data['mape_nominal']:.2%}.")
