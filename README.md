# DSU Smart Agriculture Hackathon

Master dataset and starter repo for the Delaware State University Smart Agriculture Hackathon, **October 17 to 18, 2026**.

One row is one county, one crop, one year. 253 counties across California, Nebraska, Iowa, and Delaware. Corn grain, soybeans, winter wheat, and grain sorghum, from 2000 to 2025, with weather, drought, soil, and yield on every row.

## Status

Pre-build. The NASS collection pipeline is written and awaiting run 5; the other three sources are not started. Open work is tracked in [`docs/issues_log.md`](docs/issues_log.md).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # add your NASS API key
```

A free NASS Quick Stats API key comes from [quickstats.nass.usda.gov/api](https://quickstats.nass.usda.gov/api). NOAA ACIS and the U.S. Drought Monitor need no key.

Never commit `.env`. It's in `.gitignore` and it stays there.

## Layout

```
docs/                   plan, specification, decisions, issues
data/raw/               archived API responses (gitignored)
data/processed/         one parquet per source
data/master/            master_dataset.csv and .parquet
src/                    pipeline and student utilities
notebooks/              starter notebook
```

## Note on FIPS codes

`fips` is a 5-character string, not a number. California is state FIPS `06`, so reading the CSV without forcing the type turns `06001` into `6001` and silently breaks every join.

```python
pd.read_csv("data/master/master_dataset.csv", dtype={"fips": str})
```

`src/data_loader.py` handles this. The parquet copy preserves the type on its own.

## Data sources

USDA NASS Quick Stats, NOAA ACIS, U.S. Drought Monitor (National Drought Mitigation Center), and USDA NRCS SSURGO. Census 2020 county boundaries are the join backbone. All are public federal data; see `docs/dataset_specification.md` for the exact queries and the snapshot date.
