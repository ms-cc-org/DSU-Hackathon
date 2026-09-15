# DSU Smart Agriculture Hackathon

**October 17–18, 2026 | Delaware State University | 24 hours**

A farming community is facing increasing variability in rainfall, temperature, drought, and growing conditions. Your team has been asked to build a tool that helps an agricultural stakeholder understand these conditions and make a better decision.

This repo gives you the data and a working app scaffold. You bring the analysis.

---

## What's in the dataset

One row is one county, one crop, one year.

- **4 states:** California (irrigated), Iowa (rainfed), Nebraska (mixed), Delaware (rainfed, small)
- **4 crops:** Corn grain, soybeans, winter wheat, grain sorghum
- **26 years:** 2000–2025
- **21 fields** covering yield, weather, drought, and soil
- **17,056 rows**

Every field is documented in [`data/data_dictionary.md`](data/data_dictionary.md). Read it before you start — it explains what every NaN means, what the season windows are, and what the known limitations are.

## Quick start

### 1. Install

```bash
git clone <repo-url>
cd DSU_HACKATHON
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app loads the dataset, gives you sidebar filters for state, crop, and year range, and has a working yield chart in the Overview tab. The other three tabs (Weather & Yield, Drought Analysis, Soil & Risk) are yours to build.

### 3. Load data in a notebook or script

Use the data loader; it handles file paths and types for you:

```python
from src.data_loader import load_master

df = load_master()          # 17,056 rows x 21 columns, fips is already a string
```

Or load the raw panels for finer resolution:

```python
from src.data_loader import load_nass_raw, load_daily_weather, load_weekly_drought, load_soil

nass    = load_nass_raw()         # 35K rows, yield/acres in long format per county
weather = load_daily_weather()    # 2.5M rows, daily tmax/tmin/precip per county
drought = load_weekly_drought()   # 349K rows, weekly D0-D4 per county
soil    = load_soil()             # 253 rows, one per county (static)
```

If you prefer to load directly without the helper:

```python
import pandas as pd

df = pd.read_parquet("data/master_dataset.parquet")
# or
df = pd.read_csv("data/master_dataset.csv", dtype={"fips": str})
```

**Important:** `fips` is a 5-character string, not a number. California is state FIPS `06`. If pandas reads it as an integer, `06001` becomes `6001` and every join silently fails. The parquet format and `data_loader.py` handle this automatically. If you use `read_csv`, pass `dtype={"fips": str}`.

## Repo layout

```
app.py                          Streamlit app — run with: streamlit run app.py
requirements.txt                one pip install, everything works

data/
├── master_dataset.csv          the dataset (2.3 MB)
├── master_dataset.parquet      same data, smaller and faster (412 KB)
├── data_dictionary.md          every field, every warning, every known gap
└── processed/                  source parquets (for advanced teams)
    ├── acis/                   daily county weather, 1999–2025
    ├── drought/                weekly drought severity, 2000–2025
    ├── nass/                   crop yield and acreage
    └── soil/                   county soil properties (static)

src/
├── data_loader.py              load_master(), load_nass_raw(), load_daily_weather(), etc.
└── build/                      pipelines that built the dataset (reference only)
    └── validate_sources.py     ground-truth checks across all 4 sources

docs/
├── dataset_specification.md    technical build contract — fields, filters, formulas
└── technical_implementation_plan.md   scope, state/crop rationale, timeline
```

## What you can build

These directions are starting points. Pick one, combine them, or go somewhere else entirely.

| Direction | Example |
|---|---|
| **WaterWise** | Drought dashboard, irrigation decision tool, water-stress alerts |
| **CropGuard** | Yield prediction model, risk scoring, early-warning system |
| **Farm & Environment** | County risk maps, land-use comparison, geographic vulnerability |
| **AgriAdvisor** | AI assistant grounded in this data, evidence-based recommendations |

## Research questions the data can answer

1. When a county is in D2+ drought during its growing season, how far does yield fall below trend?
2. Do counties with higher soil water storage (`aws_100cm_mm`) lose less yield in drought years?
3. In Nebraska, how does corn's drought response differ from sorghum's?
4. Is precipitation a stronger yield predictor in rainfed Iowa than in irrigated California?
5. Is there an extreme heat threshold above which yield drops sharply? Does it differ by crop?
6. Once you control for soil quality (`nccpi_crop`), how much of the yield gap is left for drought to explain?

## Data sources

| Source | What it provides | Access |
|---|---|---|
| [USDA NASS Quick Stats](https://quickstats.nass.usda.gov/api) | Crop yield and acreage | API key (free) |
| [NOAA ACIS GridData](https://docs.rcc-acis.org/acisws/) | Daily precipitation, temperature | No key |
| [U.S. Drought Monitor](https://droughtmonitor.unl.edu/) | Weekly drought severity (D0–D4) | No key |
| [USDA NRCS Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/) | Soil water capacity, productivity | No key |

All sources are public federal data. The master dataset and all processed files are included in the repo — no API calls needed to start working.

## Rebuilding the data (optional)

Only needed if you want to re-run the pipelines. Get a free NASS API key and add it to a `.env` file:

```
NASS_API_KEY=your_key_here
```

Then run the scripts in `src/build/` in order: NASS --> USDM --> ACIS --> SSURGO --> `build_master.py`. Never commit `.env`.
