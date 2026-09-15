from pathlib import Path
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]

def load_master():
    # The 21-field county × crop × year dataset
    return pd.read_parquet(_ROOT / "data/master_dataset.parquet")

def load_daily_weather():
    # Daily tmax, tmin, precipitation — 1999-2025, all counties
    return pd.read_parquet(_ROOT / "data/processed/acis/weather_daily.parquet")

def load_weekly_drought():
    # Weekly D0-D4 percentages and DSCI — 2000-2025, all counties
    return pd.read_parquet(_ROOT / "data/processed/drought/drought_weekly.parquet")

def load_nass_raw():
    # NASS yield, harvested acres, planted acres in long format
    return pd.read_parquet(_ROOT / "data/processed/nass/nass_raw.parquet")

def load_soil():
    # Static soil properties — one row per county
    return pd.read_parquet(_ROOT / "data/processed/soil/soil_county.parquet")
