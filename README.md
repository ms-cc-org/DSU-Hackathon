# DSU Smart Agriculture Hackathon

Master dataset and starter repo for the Delaware State University Smart Agriculture Hackathon, **October 17 to 18, 2026**.

One row is one county, one crop, one year. 253 counties across California, Nebraska, Iowa, and Delaware. Corn grain, soybeans, winter wheat, and grain sorghum, from 2000 to 2025, with weather, drought, soil, and yield on every row. 17,056 rows, 21 fields.

## Status

**Build complete.** All four data sources collected, processed, validated, and joined into the master dataset. 25 internal validation checks passing.

## Quick start

```python
import pandas as pd

df = pd.read_csv("data/master_dataset.csv", dtype={"fips": str})
```

Or with parquet (recommended — smaller, preserves types automatically):

```python
df = pd.read_parquet("data/master_dataset.parquet")
```

## Setup

Only needed if you want to re-run the data pipelines. The master dataset files are ready to use without any setup.

```bash
pip install pandas numpy requests python-dotenv
```

To re-run the NASS pipeline, get a free API key from [quickstats.nass.usda.gov/api](https://quickstats.nass.usda.gov/api) and set it in a `.env` file:

```
NASS_API_KEY=your_key_here
```

NOAA ACIS, the U.S. Drought Monitor, and USDA SSURGO need no key. Never commit `.env`.

## Repo layout

```
data/
|-- master_dataset.csv          the dataset (CSV, 2.3 MB)
|-- master_dataset.parquet      the dataset (Parquet, 412 KB)
|-- data_dictionary.md          every field explained
|-- processed/                  intermediate parquets, one per source
│   |-- nass/                   crop yield and acreage (35k rows)
│   |-- acis/                   daily county weather (2.5M rows)
│   |-- drought/                weekly drought severity (349k rows)
│   |-- soil/                   county soil properties (253 rows, static)
│   |-- master_build_log.json   build metadata and validation results
└── raw/                        archived API responses (gitignored, ~454 MB)

src/build/                      data collection and processing pipelines
|-- NASS_data_pull.py           USDA NASS Quick Stats: yield, acres planted/harvested
|-- ACIS_data_pull.py           NOAA ACIS GridData: daily precip, tmax, tmin
|-- USDM_data_pull.py           U.S. Drought Monitor: weekly D0-D4 by county
|-- SSURGO_data_pull.py         USDA NRCS Soil Data Access: AWS, droughty, NCCPI
└── build_master.py             joins 4 sources into the master dataset

docs/                           project documentation
|-- dataset_specification.md    technical contract: fields, filters, calculations
|-- technical_Implementation_plan.md   scope, geographic rationale, design decisions
|-- timeline.md                 milestone schedule (Sep 4 → Oct 2)

notebooks/                      starter notebooks (planned for Sep 18)

validate_sources.py             source data validation (see below)
nass_validation.py              NASS-specific structural checks
```

## validate_sources.py

Source data validation.

Tests that the numbers in the 4 source parquet files are factually correct,
not just structurally sound. Each section checks against independent ground
truth or well-known facts that would catch unit errors, wrong filters, or
corrupted downloads.

Run: `python validate_sources.py`

## Note on FIPS codes

`fips` is a 5-character string, not a number. California is state FIPS `06`, so reading the CSV without forcing the type turns `06001` into `6001` and silently breaks every join.

```python
pd.read_csv("data/master_dataset.csv", dtype={"fips": str})
```

The parquet format preserves the string type automatically.

## Data sources

| Source | What it provides | API |
|--------|-----------------|-----|
| USDA NASS Quick Stats | Crop yield and acreage | Key required (free) |
| NOAA ACIS GridData | Daily precipitation, temperature | No key needed |
| U.S. Drought Monitor | Weekly drought severity (D0-D4) | No key needed |
| USDA NRCS SSURGO | Soil water capacity, productivity index | No key needed |

Census 2020 county boundaries are the join backbone. All sources are public federal data. See [`docs/dataset_specification.md`](docs/dataset_specification.md) for the exact queries and filters.
