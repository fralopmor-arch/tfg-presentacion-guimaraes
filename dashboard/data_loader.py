from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"


def _power_band(power_w: float) -> str:
    if power_w < 1000:
        return "<1kW"
    if power_w <= 10000:
        return "1-10kW"
    if power_w <= 100000:
        return "10-100kW"
    return ">100kW"


def _add_common_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "rated_power_w" in out.columns and "power_band" not in out.columns:
        out["power_band"] = out["rated_power_w"].apply(lambda value: _power_band(float(value)) if pd.notna(value) else "")
    return out


def _read_csv_files(file_names: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for file_name in file_names:
        path = OUTPUTS_DIR / file_name
        if path.exists():
            frame = pd.read_csv(path)
            frame["source_file"] = file_name
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return _add_common_columns(pd.concat(frames, ignore_index=True))


@st.cache_data
def load_validation_data() -> pd.DataFrame:
    """Load and merge validation CSVs from outputs/."""
    return _read_csv_files(["w22_ie2_validation.csv", "w22_ie5_validation.csv"])


@st.cache_data
def load_parameter_data() -> pd.DataFrame:
    """Load and merge per-motor parameter CSVs from outputs/."""
    return _read_csv_files(["w22_ie2_params.csv", "w22_ie5_params.csv"])


@st.cache_data
def load_typical_models() -> list[dict]:
    """Load the grouped typical-model JSON from outputs/."""
    path = OUTPUTS_DIR / "typical_models_by_group.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return []


@st.cache_data
def load_typical_model_table() -> pd.DataFrame:
    """Load the grouped typical-model CSV from outputs/."""
    path = OUTPUTS_DIR / "typical_params_by_group.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data
def load_dashboard_summary() -> dict:
    """Load the dashboard summary JSON from outputs/."""
    path = OUTPUTS_DIR / "dashboard_summary.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def get_filter_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """Return unique filter options for common dashboard selectors."""
    options: dict[str, list[str]] = {}
    for column, label in [
        ("efficiency_class", "IE"),
        ("poles", "Poles"),
        ("manufacturer", "Manufacturer"),
        ("starting_torque_category", "Starting Category"),
        ("power_band", "Power Band"),
    ]:
        if column in df.columns:
            values = [str(value) for value in df[column].dropna().unique()]
            options[label] = sorted(values)
        else:
            options[label] = []
    return options
