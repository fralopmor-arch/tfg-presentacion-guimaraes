from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_parameter_data, load_typical_model_table, load_typical_models

def render_typical_models_view():
    st.header("Typical Models by Group")
    
    typical_models = load_typical_models()
    params_df = load_parameter_data()
    group_df = load_typical_model_table()
    
    if not typical_models:
        st.warning("No typical models data found.")
        return

    # Group selector
    def _group_label(model: dict) -> str:
        return " | ".join(
            [
                str(model.get("efficiency_class", "all")) or "all",
                str(model.get("starting_torque_category", "all")) or "all",
                str(model.get("manufacturer", "all")) or "all",
                f"{model.get('poles', 'all')}P",
                str(model.get("power_band", "all")) or "all",
                f"n={model.get('n_samples', 0)}",
            ]
        )

    model_labels = [_group_label(model) for model in typical_models]
    selected_label = st.selectbox("Select Group", model_labels)
    selected_index = model_labels.index(selected_label)
    selected_model = typical_models[selected_index]
    
    # Parameters Table
    st.subheader(f"Parameters for {selected_label}")
    params_table = pd.DataFrame(
        [
            {
                "Parameter": param,
                "a": values.get("a"),
                "b": values.get("b"),
                "R2": values.get("r2"),
                "Median pu": values.get("median_pu"),
                "MAD pu": values.get("mad_pu"),
            }
            for param, values in selected_model.get("params", {}).items()
        ]
    )
    st.dataframe(params_table, use_container_width=True)

    # Scatter plot
    st.subheader("Parameter Trend (Power vs Parameter)")
    param_to_plot = st.selectbox(
        "Select Parameter to Visualize",
        ["r1", "x1", "r2_rated", "r20", "x2_rated", "x20", "r_m", "x_m"],
    )

    filtered_df = params_df.copy()
    for column in ["efficiency_class", "starting_torque_category", "manufacturer", "poles", "power_band"]:
        model_value = selected_model.get(column, "")
        if column in filtered_df.columns and model_value not in (None, ""):
            filtered_df = filtered_df[filtered_df[column].astype(str) == str(model_value)]

    if param_to_plot in filtered_df.columns and not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="rated_power_w",
            y=param_to_plot,
            hover_data=["motor_id"],
            log_x=True,
            title=f"{param_to_plot} vs Rated Power",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Parameter data not available for plotting in this group.")

    if not group_df.empty:
        st.subheader("Group-level fit row")
        group_row = group_df.copy()
        for column in ["efficiency_class", "starting_torque_category", "manufacturer", "poles", "power_band"]:
            model_value = selected_model.get(column, "")
            if column in group_row.columns and model_value not in (None, ""):
                group_row = group_row[group_row[column].astype(str) == str(model_value)]
        if not group_row.empty:
            st.dataframe(group_row.iloc[[0]], use_container_width=True)
        else:
            st.info("No matching row found in typical_params_by_group.csv for this group.")
