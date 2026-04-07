import streamlit as st
from views.summary import render_summary_view
from views.validation import render_validation_view
from views.typical_models import render_typical_models_view
from views.motor_case import render_motor_case_view

st.set_page_config(page_title="Guimaraes Dashboard", layout="wide")

st.title("Guimaraes Method Dashboard")

# Navigation
tabs = st.tabs(["Summary", "Validation", "Typical Models", "Motor Case"])

with tabs[0]:
    render_summary_view()

with tabs[1]:
    render_validation_view()

with tabs[2]:
    render_typical_models_view()

with tabs[3]:
    render_motor_case_view()
