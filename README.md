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
- **17,056 rows**, but only 68% have a reported yield. The well-covered core is Iowa and Nebraska corn and soybeans, plus Nebraska wheat; California, Delaware, sorghum, and Iowa and Delaware wheat are thin. See the coverage table in the data dictionary before picking a project.

There is also an **extension dataset** with satellite-derived vegetation indices (NDVI and EVI) from NASA MODIS, covering the same counties and years. It joins on `fips + year` and adds a remote-sensing signal that complements the ground-level weather and yield data. A second extension gives NASS's **irrigated share and irrigated vs. dryland yields** by county, crop and year, mostly for Nebraska 2000–2018. Both join to the master; see the extension sections in the data dictionary for details and caveats.

Every field is documented in [`data/data_dictionary.md`](data/data_dictionary.md). Read it before you start — it explains what every NaN means, what the season windows are, and what the known limitations are.

## Quick start

### 1. Install

You need **Python 3.11 or newer** (3.12 recommended). Check with `python3 --version` (Windows: `py --version`). If it's older, install 3.12 from [python.org](https://www.python.org/downloads/). The `python3` that comes with macOS is 3.9 and won't work. The install downloads about 200 MB and uses about 900 MB of disk, so do it before the event rather than on event wifi.

**macOS / Linux:**
```bash
git clone https://github.com/ms-cc-org/DSU-Hackathon.git
cd DSU-Hackathon
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/ms-cc-org/DSU-Hackathon.git
cd DSU-Hackathon
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and activate again. In Command Prompt (cmd), activate with `.venv\Scripts\activate.bat` instead.

It worked if your prompt starts with `(.venv)`. In every new terminal, `cd DSU-Hackathon` and activate again.

If pip says `No matching distribution found for numpy==2.4.6`, the venv was made with Python older than 3.11. Delete the `.venv` folder and create it again with a newer Python.

### 2. Run the app

```bash
streamlit run app.py
```

The first time, Streamlit asks for an email address in the terminal. Press Enter to skip it; the app then opens in your browser.

The app loads the dataset, gives you sidebar filters for state, crop, and year range, and has a working yield chart in the Overview tab. The other three tabs (Weather & Yield, Drought Analysis, Soil & Risk) are yours to build.

### 3. Load data in a notebook or script

The starter notebook is at `notebooks/starter_notebook.ipynb`. To run it locally, start `jupyter lab` from the repo root with the venv active and open it there (or open it in VS Code and pick the `.venv` kernel). To run it without installing anything, open it in Google Colab and run the first cell, which fetches the data:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ms-cc-org/DSU-Hackathon/blob/main/notebooks/starter_notebook.ipynb)

Use the data loader; it handles file paths and types for you. Run these snippets from the repo root. From a subfolder such as `notebooks/`, add `import sys; sys.path.insert(0, "..")` first, as the starter notebook does.

```python
from src.data_loader import load_master

df = load_master()          # 17,056 rows x 21 columns, fips is already a string
```

Or load the raw panels for finer resolution:

```python
from src.data_loader import load_nass_raw, load_daily_weather, load_weekly_drought, load_soil, load_modis, load_irrigation, load_counties

nass    = load_nass_raw()         # 35K rows, yield/acres in long format per county
weather = load_daily_weather()    # 2.5M rows, daily tmax/tmin/precip per county
drought = load_weekly_drought()   # 343K rows, weekly D0-D4 per county
soil    = load_soil()             # 253 rows, one per county (static)
modis   = load_modis()            # 5,980 rows, annual NDVI/EVI per county (extension)
irrigation = load_irrigation()    # 3,716 rows, irrigated share and yields per county x crop x year (extension)
counties = load_counties()        # GeoJSON boundaries for maps, feature id = fips
```

For maps, the notebook's worked example shows `px.choropleth` with `load_counties()`. Plotly 7 removed `px.choropleth_mapbox` and `px.scatter_mapbox`, which older tutorials use; use `px.choropleth` or `px.choropleth_map` instead.

If you prefer to load directly without the helper:

```python
import pandas as pd

df = pd.read_parquet("data/master_dataset.parquet")
# or
df = pd.read_csv("data/master_dataset.csv", dtype={"fips": str})
```

**Important:** `fips` is a 5-character string, not a number. California is state FIPS `06`. If pandas reads it as an integer, `06001` becomes `6001` and every join silently fails. The parquet format and `data_loader.py` handle this automatically. If you use `read_csv`, pass `dtype={"fips": str}`. If you use `read_parquet`, three count columns come back as pandas `Int64`, which breaks numpy calls such as `np.nanmean`; `load_master()` converts them to float.

## Repo layout

```
app.py                          Streamlit app — run with: streamlit run app.py
requirements.txt                pinned dependencies (app, notebook, modelling)

data/
├── master_dataset.csv          the dataset (2.3 MB)
├── master_dataset.parquet      same data, smaller and faster (412 KB)
├── data_dictionary.md          every field, every warning, every known gap
├── counties.geojson            county boundaries for maps (253 counties)
└── processed/                  source parquets (for advanced teams)
    ├── acis/                   daily county weather, 1999–2025
    ├── drought/                weekly drought severity, 2000–2025
    ├── irrigation/             irrigated share and yields, mostly Nebraska (extension)
    ├── modis/                  annual NDVI/EVI per county (extension)
    ├── nass/                   crop yield and acreage
    └── soil/                   county soil properties (static)

src/
├── data_loader.py              load_master(), load_nass_raw(), load_daily_weather(), etc.
└── build/                      pipelines that built the dataset (reference only)
    └── validate_sources.py     sanity checks across all 4 sources

notebooks/
└── starter_notebook.ipynb      load the data, worked example, places to start

docs/
├── Smart Agriculture Hackathon at Delaware State University.md   event concept, judging rubric
├── dataset_specification.md    technical build contract — fields, filters, formulas
├── technical_implementation_plan.md   scope, state/crop rationale, pipeline
└── timeline.md                 organizer prep timeline
```

## What you can build

Every strong project answers three questions: **who uses it, what do they decide with it, and how do you know it helps?** Below are seven directions the data supports. Each one has a simple starting point and a way to go further, so any team can pick one. You can also combine two or bring your own idea.

| Direction | Who it's for and what they decide | What success looks like | Start here → Go further |
|---|---|---|---|
| **Crop Loss Early Warning** | A crop insurance office in Iowa and Nebraska decides, on August 1 (mid-season, about two months before harvest, when they plan where to send staff), which counties to send loss inspectors to first. | A ranked list of counties to watch. When you test it on past years, a higher share of the counties it flags had a bad year (10% or more below their normal yield) than the same number of counties picked by severe drought alone. If it can't beat that on August 1, showing honestly why is a valid result. | **Start:** use the weekly drought panel to list counties in severe drought (D2 or worse) on the last weekly map dated before August 1 each year, then check how many really had a bad year. **Go further:** add weather up to August 1 from the daily panel and build a prediction model. Don't use the master's weather and drought columns here: they cover the whole season, including weeks after August 1. |
| **Drought Assistance Targeting** | A state drought program decides which counties get help first, and what drought rule should trigger that help. | A county "report card" anyone can read in under 2 minutes: how often the county was in drought, how much yield it lost, how vulnerable its soil is. A ranking built from 2000–2015 that picks the counties hit hardest in 2016–2025 better than chance. Don't rank by average `yield_anomaly_pct`: each county's anomalies average to about zero over 2000–2025, so one period's average mirrors the other's. | **Start:** build the report card from the master dataset (`weeks_in_d2_plus`, `max_drought_severity`, `yield_anomaly_pct`, soil fields). **Go further:** test drought rules (for example, "8 weeks in a row of severe drought") with the weekly drought panel, and count how often each rule gives help where there was no loss, or misses a real loss. |
| **Heat-Stress Advisory** | An extension crop specialist in Iowa and Nebraska decides when to warn corn and soybean growers that heat is hurting their crop. | A heat rule (how hot, for how many days) backed by yield evidence, that works on years you didn't use to choose it and does better than the master's fixed count of days at 35 °C or hotter. | **Start:** compare yields in years with many vs few `extreme_heat_days`. **Go further:** build your own heat measures from the daily weather panel (days above 30 or 32 °C, heat in July only, hot spells), and check that heat still matters once drought is taken into account, since hot summers are often dry. |
| **Soil and Crop Resilience Planning** | A soil conservation office decides where long-term soil programs would cut drought losses the most, and which crop holds up best in drought-prone Nebraska counties. | A priority map of counties, plus an estimate (with a range) of how much soil water storage changes drought losses, comparing counties with similar soil quality. Check whether the result holds when you split by state or time period. A well-supported "no detectable effect" is a valid result. | **Start:** map the soil fields (`aws_100cm_mm`, `droughty_pct`, `nccpi_crop`) and compare drought-year losses for counties with high vs low water storage. **Go further:** fit a model with drought, soil and their combination, and report uncertainty. Note that soil has one value per county, so you have as many soil data points as counties, not rows. |
| **Grain Supply Outlook** | An Iowa ethanol plant decides whether to buy extra corn from outside its local area this year. | An estimate, with a range, of how much corn a group of counties will produce. Tested on past years, it's closer to the real number than a guess based on the long-term trend alone. | **Start:** compute production (`yield_per_acre` × `acres_harvested`) for a group of Iowa counties that report every year (adding up counties that drop in and out makes production jump), and chart it over time with a trend line. **Go further:** add weather and drought to improve the estimate, and check how often the real number falls inside your range. |
| **Frost-Safe Planting Calendar** | An extension agronomist decides the earliest date to recommend planting frost-sensitive crops in each county. | A planting date for each county, built from 2000–2018, that is followed by a frost in no more than 1 in 10 county-years in 2019–2025. | **Start:** use the daily weather panel to find each county's last day from January to June with `tmin_c` at or below 0 °C, then take a high percentile of those dates. A year with no spring frost (some California counties) counts as frost-free. **Go further:** choose a safety margin and map the dates; add the first fall frost to get season length. These are county-average temperatures, so low-lying fields can frost later than the data shows. |
| **Drought Category Reality Check** | A state drought task force decides whether a drought category (for example D3) should trigger the same response in Iowa as in Nebraska. | A "drought category → expected yield loss" table for Iowa and Nebraska corn and soybeans, built on 2000–2012, that predicts 2013–2025 within about 4 points on average. | **Start:** group the master by `max_drought_severity` (offset by one: 4 = D3), state and crop, average `yield_anomaly_pct`, and check how many rows each cell has. **Go further:** use the weekly drought panel to test drought duration and timing, and split by `irrigated_share` from the irrigation extension. |
| **AgriAdvisor** *(optional)* | A county extension agent decides how to answer a farmer's question with evidence from the data. | It answers a set of test questions correctly (answers you checked by hand), says "the data can't answer that" when it can't, and every number matches the dataset. | **Start:** write Python functions that answer a few common questions and show the rows behind each answer. **Go further:** let an AI model call those functions. Needs your own AI model access (an API key or a local model). |

**Testing on past years:** build your tool using some years and test it on years it hasn't seen (for example, build on 2000–2018 and test on 2019–2025). That's how you show it would have worked in a real season. `yield_anomaly_pct` comes from a trend fitted on all of 2000–2025, including your test years; for a strict test, refit each county's trend on your training years only.

**Optional, advanced: the 2026 season.** The dataset ends in 2025, but the ACIS and Drought Monitor APIs serve 2026 data with no key. `src/build/ACIS_data_pull.py` and `USDM_data_pull.py` show the requests (the drought API's JSON uses lowercase `d0`–`d4`). USDA's monthly *Crop Production* reports give official 2026 state yield forecasts to compare against.

**By checkpoint 1 (Saturday afternoon), name your user and the decision your tool helps them make.**

## Research questions the data can answer

1. When a county is in D2+ drought during its growing season, how far does yield fall below trend?
2. In rainfed Iowa, do counties with higher soil water storage (`aws_100cm_mm`) lose less yield in drought years? (Don't pool Nebraska: its lowest-storage counties are the most heavily irrigated, so they look drought-resistant for reasons the soil fields can't show.)
3. In Nebraska, sorghum's yield falls further below trend than corn's in drought years, even though sorghum is the "drought-tolerant" crop. What could explain that? (Hint: which crop is usually irrigated? Check how many sorghum counties report after 2010.)
4. Is precipitation a stronger yield predictor in rainfed Iowa than in irrigated California?
5. Is there an extreme heat threshold above which yield drops sharply? Does it differ by crop?
6. Once you control for soil quality (`nccpi_crop`), how much of the yield gap is left for drought to explain?

## Data sources

| Source | What it provides | Access |
|---|---|---|
| [USDA NASS Quick Stats](https://quickstats.nass.usda.gov/api) | Crop yield and acreage, irrigated split | API key (free) |
| [NOAA ACIS GridData](https://docs.rcc-acis.org/acisws/) | Daily precipitation, temperature | No key |
| [U.S. Drought Monitor](https://droughtmonitor.unl.edu/) | Weekly drought severity (D0–D4) | No key |
| [USDA NRCS Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/) | Soil water capacity, productivity | No key |
| [NASA MODIS MOD13Q1 v061](https://lpdaac.usgs.gov/products/mod13q1v061/) | Satellite vegetation indices (NDVI, EVI) | GEE (free) |

All sources are public federal data. The master dataset and all processed files are included in the repo — no API calls needed to start working.

## Rebuilding the data (optional)

You never need to rebuild the data for the hackathon. Everything is already in `data/`. This section is for organizers refreshing it.

Get a free [NASS API key](https://quickstats.nass.usda.gov/api) and add it to a `.env` file in the repo root:

```
NASS_API_KEY=your_key_here
```

Then run the scripts in `src/build/` in this order:

1. `NASS_data_pull.py`
2. `USDM_data_pull.py`
3. `ACIS_data_pull.py`
4. `SSURGO_data_pull.py`
5. `validate_sources.py`: checks the four source files
6. `build_master.py`: builds `data/master_dataset.csv` and `.parquet`

The scripts work from any directory. USDM, ACIS and SSURGO cache API responses in `data/raw/`, so a re-run only downloads what's missing. `data/raw/` is not in the repo, so on a fresh clone every script downloads everything. NASS always downloads fresh.

**Irrigation extension.** `NASS_irrigation_pull.py` runs after `NASS_data_pull.py` and uses the same NASS key.

**MODIS extension (organizer only).** `MODIS_gee_pull.py` runs after `build_master.py` and needs a Google Earth Engine account linked to a Google Cloud project:

```bash
pip install earthengine-api
earthengine authenticate
```

Then add `EE_PROJECT=your-cloud-project-id` to `.env`.

Never commit `.env`.
