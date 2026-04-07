from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_validation_data


METRICS = {
    "current": {
        "catalog": "actual_i_rated_a",
        "predicted": "pred_i_rated_a",
        "error": "err_i_pct",
        "label": "Rated current",
        "unit": "A",
    },
    "torque": {
        "catalog": "actual_t_rated_nm",
        "predicted": "pred_t_rated_nm",
        "error": "err_t_pct",
        "label": "Rated torque",
        "unit": "Nm",
    },
    "efficiency": {
        "catalog": "actual_eta_rated",
        "predicted": "pred_eta_rated",
        "error": "err_eta_pct",
        "label": "Efficiency",
        "unit": "pu",
    },
    "power_factor": {
        "catalog": "actual_pf_rated",
        "predicted": "pred_pf_rated",
        "error": "err_pf_pct",
        "label": "Power factor",
        "unit": "pu",
    },
}


def _r2_score(actual: pd.Series, predicted: pd.Series) -> float:
    if actual.empty:
        return math.nan
    mean_actual = actual.mean()
    ss_res = ((actual - predicted) ** 2).sum()
    ss_tot = ((actual - mean_actual) ** 2).sum()
    if ss_tot == 0:
        return math.nan
    return 1.0 - float(ss_res / ss_tot)

def render_validation_view():
    st.header("Model Validation")
    df = load_validation_data()
    
    if df.empty:
        st.warning("No validation data found.")
        return

    current_metrics = METRICS["current"]
    torque_metrics = METRICS["torque"]
    efficiency_metrics = METRICS["efficiency"]
    pf_metrics = METRICS["power_factor"]

    # Metrics
    col1, col2, col3 = st.columns(3)
    global_mape = df[["mape_nominal"]].mean().iloc[0] if "mape_nominal" in df.columns else math.nan
    global_r2_values = []
    for metric in METRICS.values():
        if metric["catalog"] in df.columns and metric["predicted"] in df.columns:
            global_r2_values.append(_r2_score(df[metric["catalog"]], df[metric["predicted"]]))
    global_r2 = sum(global_r2_values) / len(global_r2_values) if global_r2_values else math.nan

    col1.metric("Global R2", f"{global_r2:.3f}" if pd.notna(global_r2) else "N/A")
    col2.metric("Global MAPE", f"{global_mape:.2%}" if pd.notna(global_mape) else "N/A")
    col3.metric("Validated motors", f"{len(df):,}")

    # Predicted vs Actual
    st.subheader("Predicted vs. Actual")
    selected_metric = st.selectbox("Select variable for scatter plot", list(METRICS.keys()))
    metric_cfg = METRICS[selected_metric]
    # (diagnostics removed)
    
    fig = px.scatter(
        df, 
        x=metric_cfg["catalog"], 
        y=metric_cfg["predicted"],
        hover_data=["motor_id"],
        title=f"Catalog vs Predicted: {metric_cfg['label']}"
    )
    fig.add_shape(
        type="line",
        line=dict(dash="dash"),
        x0=df[metric_cfg["catalog"]].min(),
        y0=df[metric_cfg["catalog"]].min(),
        x1=df[metric_cfg["catalog"]].max(),
        y1=df[metric_cfg["catalog"]].max(),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Residuals
    st.subheader("Residual Analysis")
    fig_res = px.box(df, x="power_band", y=metric_cfg["error"], title="Residuals by Power Band")
    st.plotly_chart(fig_res, use_container_width=True)

    # Top high-error
    st.subheader("High Error Motors")
    top_cols = ["motor_id", "mape_nominal", "status", "source_file"]
    available_cols = [column for column in top_cols if column in df.columns]
    st.dataframe(df.nlargest(5, "mape_nominal")[available_cols])
