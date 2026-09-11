# Data Dictionary

**DSU Smart Agriculture Hackathon, October 17–18, 2026.**
Master dataset version 1. Built September 11, 2026.

---

## What this dataset is

One row is one county, one crop, one year. The dataset covers 4 states (California, Delaware, Iowa, Nebraska), 4 crops (corn grain, soybeans, winter wheat, grain sorghum), and 26 years (2000–2025). It has 17,056 rows and 21 columns.

The question the dataset is sized to answer: given a county, a crop, and a year, what do the weather, drought, soil, and yield records tell you about agricultural risk, and what should a farmer, extension agent, or state agency do about it?

Everything joins on `fips`, the 5-digit county FIPS code. Load it as a string. If you let pandas read it as an integer, California counties lose their leading zero (`06001` becomes `6001`) and every join silently fails.

```python
import pandas as pd

master = pd.read_csv("data/master_dataset.csv", dtype={"fips": str})
# or
master = pd.read_parquet("data/master_dataset.parquet")  # fips is already a string
```

---

## Why these 4 states

They span the irrigation gradient. Iowa is rainfed. Delaware is rainfed and small enough to reason about as a whole. Nebraska is roughly half irrigated over the Ogallala Aquifer. California is almost entirely irrigated. A team comparing Iowa to Nebraska to California is comparing three kinds of agriculture inside the same columns.

## Why these 4 crops

Corn and soybeans give data density in Iowa and Nebraska. Winter wheat adds a season that crosses the calendar year (planted in fall, harvested the following summer), which forces you to think about temporal alignment. Grain sorghum is drought-tolerant by design, so the corn-vs-sorghum contrast in Nebraska is a built-in natural experiment.

**What the crop names actually filter:**

| `crop` value | What it is | What it excludes |
|---|---|---|
| `CORN` | Corn for grain | Corn for silage (reported in tons/acre, not bu/acre) |
| `SOYBEANS` | Soybeans | Nothing (NASS spells it plural — `SOYBEAN` returns zero rows) |
| `WHEAT` | Winter wheat only | Spring wheat, durum |
| `SORGHUM` | Grain sorghum | Sorghum for silage and syrup |

---

## Row universe

Not every county grows every crop. California doesn't grow soybeans at commercial scale. Iowa stopped growing grain sorghum before 2000. Those county-crop pairs produce no rows at all.

For the pairs that do exist, every year from 2000 to 2025 is present. If NASS published a yield, it's there. If NASS suppressed the yield for confidentiality, the row is there with `yield_per_acre = NaN` and `yield_status = suppressed`. If NASS published nothing for that county-crop-year, the row is there with `yield_status = not_reported`. This means every time series you plot is complete, and every gap is labelled.

**Coverage by state:**

| State | Counties | Rows | Why it matters |
|---|---|---|---|
| California | 37 | 2,158 | Irrigated. Yield-to-precipitation relationship is weak. |
| Delaware | 3 | 312 | Small, rainfed. Complete and easy to reason about. |
| Iowa | 99 | 5,876 | Rainfed. Best agricultural soil in the US. |
| Nebraska | 91 | 8,710 | Mixed irrigation. Has all 4 crops. Largest coverage. |

**Coverage by crop:**

| Crop | Counties | Rows | Note |
|---|---|---|---|
| Corn | 224 | 5,824 | Most widely reported crop in the dataset. |
| Soybeans | 183 | 4,758 | Not grown in California. |
| Winter wheat | 150 | 3,900 | Sparse in Iowa (28 counties). |
| Grain sorghum | 99 | 2,574 | Mostly Nebraska. No Iowa data post-2000. |

---

## Fields

### Identity (5 fields, never null)

| Field | Type | Description |
|---|---|---|
| `fips` | String, 5 chars | County FIPS code, starts with zero. `06001`, not `6001`. This is the join key across all datasets. |
| `county_name` | String | County name from Census 2020. Example: `Polk County`. |
| `state_alpha` | String, 2 chars | State abbreviation. One of `CA`, `DE`, `IA`, `NE`. |
| `year` | Integer | Harvest year. 2000 to 2025. For winter wheat, this is the year the crop was harvested, not planted. |
| `crop` | String | One of `CORN`, `SOYBEANS`, `WHEAT`, `SORGHUM`. |

### Yield (5 fields, from USDA NASS)

| Field | Type | Unit | Description |
|---|---|---|---|
| `yield_per_acre` | Float | Bushels per acre | County yield from NASS Quick Stats. NaN when not reported or suppressed. Never zero — a zero yield is a NASS suppression code, not an observation. All 4 crops use the same unit. |
| `yield_status` | String | — | Why the yield is or isn't there. `reported` = NASS published a number. `suppressed` = NASS withheld it (too few farms to disclose). `not_reported` = NASS published nothing for this county-crop-year. Never null. |
| `acres_planted` | Float | Acres | County acres planted. Available for soybeans and wheat. NASS does not publish county-level planted acres for corn or sorghum, so those are NaN by design, not by error. |
| `acres_harvested` | Float | Acres | County acres harvested. When both planted and harvested are present, the difference is abandonment — the most direct drought-impact signal NASS publishes. |
| `yield_anomaly_pct` | Float | Percent | How far this year's yield deviates from the county's 26-year trend. Positive = above trend, negative = below. Computed as an OLS residual divided by the fitted value, so it removes the secular rise from genetics and technology. NaN when the county-crop pair has fewer than 10 reported yields (trend is too unstable) or when yield itself is NaN. |

**Yield ranges observed in this dataset:**

| Crop | Min | Max | Typical |
|---|---|---|---|
| Corn | 32.5 | 277.1 | 160–190 (IA, NE recent years) |
| Soybeans | 15.0 | 75.5 | 48–56 (IA, NE recent years) |
| Winter wheat | 8.7 | 120.3 | 40–60 (NE) |
| Grain sorghum | 18.0 | 139.6 | 70–110 (NE) |

### Weather (5 fields, from NOAA ACIS)

All weather fields are aggregated over the crop's growing-season window (see "Season windows" below). Source is NOAA ACIS grid 1 (interpolated, county-mean, daily). Units are metric: Celsius and millimetres.

| Field | Type | Unit | Description |
|---|---|---|---|
| `precip_mm` | Float | Millimetres | Total precipitation during the growing season. This is the sum of daily county-mean precipitation. If you see a value around 30 for Iowa when you expect 800, your data is in inches — it shouldn't be, but check. |
| `precip_anomaly_pct` | Float | Percent | How far this season's precipitation deviates from the 26-year average for this county-crop. `(precip − mean) / mean × 100`. Positive = wetter than normal. |
| `tavg_c` | Float | °C | Mean daily average temperature over the growing season. Computed as the mean of daily `(tmax + tmin) / 2`. If you see 48 for Iowa instead of 9, the data is in Fahrenheit — it shouldn't be, but check. |
| `extreme_heat_days` | Integer | Days | Count of days in the season where daily max temperature reached or exceeded 35°C (95°F). This is near zero for winter wheat because the Sep-to-Jun window rarely hits 35°C. That's a property of the window, not evidence that wheat is heat-tolerant. |
| `gdd` | Float | Degree-days | Growing Degree Days, using crop-specific base and cap temperatures. The formula is: `daily GDD = max(0, (min(tmax, T_cap) + max(tmin, T_base)) / 2 − T_base)`. Seasonal GDD is the sum. |

**GDD parameters by crop:**

| Crop | T_base (°C) | T_cap (°C) |
|---|---|---|
| Corn | 10 | 30 |
| Soybeans | 10 | 30 |
| Winter wheat | 0 | 26 |
| Grain sorghum | 10 | 38 |

### Drought (3 fields, from U.S. Drought Monitor)

All drought fields are aggregated over the crop's growing-season window. Source is the USDM weekly county-level categorical data (D0–D4 categories, each representing the percent of a county's area in that drought severity class).

| Field | Type | Range | Description |
|---|---|---|---|
| `max_drought_severity` | Integer | 0–5 | Worst drought category observed in any week of the season, where more than 1% of the county was affected. 0 = no drought, 1 = D0 (abnormally dry), 2 = D1 (moderate), 3 = D2 (severe), 4 = D3 (extreme), 5 = D4 (exceptional). Note: this scale is offset by 1 from the USDM's own D0–D4 labels. |
| `weeks_in_d2_plus` | Integer | 0–43 | Number of weeks during the season where severe drought or worse (D2 + D3 + D4) covered more than 1% of the county. A quick measure of drought duration. |
| `mean_dsci` | Float | 0–500 | Mean weekly Drought Severity and Coverage Index over the season. Computed as `D0×1 + D1×2 + D2×3 + D3×4 + D4×5` using categorical (non-overlapping) percentages. 0 means no drought all season. 500 means the entire county was in D4 every week. |

**Do not confuse the scales.** `max_drought_severity` is 0–5. `mean_dsci` is 0–500. They are not the same thing and neither is a percentage.

The 1% area threshold matters. Without it, a 0.01% sliver of a county in D4 during one week would set `max_drought_severity` to 5, making the field noisy and hard to defend.

### Soil (3 fields, from USDA NRCS SSURGO)

Soil is time-invariant. These 3 values are the same for every year of a county. They join on `fips` alone.

| Field | Type | Unit | Description |
|---|---|---|---|
| `aws_100cm_mm` | Float | Millimetres | Available Water Supply in the top 100 cm of soil, area-weighted across the county's soil map units. Think of it as how much water the soil can hold for plant use. High value = the soil carries the crop further between rains. Iowa averages ~179 mm. California desert counties are 70–90 mm. |
| `droughty_pct` | Float | Percent (0–100) | Percent of the county's area on drought-vulnerable soil (defined as ≤ 152 mm of available water storage). Iowa median is 14%. California has 57 of 58 counties above 50%. This is a threshold view of the same idea as `aws_100cm_mm`, easier to reason about. |
| `nccpi_crop` | Float | 0 to 1 | National Commodity Crop Productivity Index, matched to the crop in the row. 0 = unproductive, 1 = most productive soil in the US for this crop. Iowa corn counties average ~0.74. This is the control variable that lets you separate "bad yield because bad weather" from "bad yield because bad soil." |

**`nccpi_crop` mapping:**

| Crop | NCCPI submodel used | Note |
|---|---|---|
| Corn | NCCPI Corn | |
| Soybeans | NCCPI Soybeans | |
| Wheat | NCCPI Small Grains | |
| Sorghum | NCCPI Corn | No sorghum model exists. Corn is the proxy — same season, similar management. Documented approximation. |

---

## Season windows

Weather and drought fields are aggregated over crop-specific growing seasons, not the calendar year. The window boundaries are fixed across all 4 states.

| Crop | Season start | Season end | Days | Year rule |
|---|---|---|---|---|
| Corn | May 1 | Sep 30 | 153 | Harvest year |
| Soybeans | May 1 | Oct 31 | 184 | Harvest year |
| Winter wheat | Sep 1 | Jun 30 | 303–304 | Sep 1 of year−1 through Jun 30 of harvest year |
| Grain sorghum | Jun 1 | Oct 31 | 153 | Harvest year |

**Winter wheat crosses the calendar year.** The row with `year = 2012` and `crop = WHEAT` aggregates weather from September 1, 2011 through June 30, 2012. If you filter by calendar year alone you'll get the wrong days.

**The windows are fixed and challengeable.** California plants corn from mid-March and winter wheat from mid-October — both earlier than these windows. Delaware double-crops soybeans after wheat, pushing planting into July. These are real limitations, not errors. Teams that want state-specific or year-specific windows can use the daily weather panel (`data/processed/acis/weather_daily.parquet`) to build their own.

---

## Missing data — read this section

NaN is not zero. Do not fill it with zero. Do not drop it without understanding why it's missing.

| What you see | What it means | What to do |
|---|---|---|
| `yield_per_acre` is NaN, `yield_status` = `suppressed` | NASS measured it but withheld the number. Too few farms in that county to publish without revealing an individual operation's data. | Leave as NaN. Use `acres_harvested` if you need to know the crop was grown. |
| `yield_per_acre` is NaN, `yield_status` = `not_reported` | NASS published no estimate for that county-crop-year. The crop may not have been grown, or NASS didn't survey it. | Leave as NaN. The row exists so your time series is complete. |
| No row at all for a county-crop combination | That crop has no NASS record in this state for the entire 2000–2025 window. | Nothing to do. California soybeans and Iowa sorghum are the known cases. |
| `acres_planted` is NaN for corn or sorghum | NASS does not publish county-level planted acres for corn or sorghum. This is a data limitation, not a pipeline error. | Use `acres_harvested` instead. Planted acres are available for soybeans and wheat. |
| Drought fields are NaN, row is `WHEAT` year `2000` | The wheat season starts September 1, 1999. The USDM archive starts January 4, 2000. Only about 25 of the 43 season weeks have drought data. We set all 3 fields to NaN rather than publish a value from 58% of a season. | Exclude wheat year 2000 from drought analysis or note it as incomplete. Weather is complete for this row. |
| `yield_anomaly_pct` is NaN but `yield_per_acre` is not | The county-crop pair has fewer than 10 reported yields across 2000–2025. The trend is too unstable to detrend meaningfully. | Exclude from anomaly-based analysis. You can still use raw `yield_per_acre`. |

---

## Companion datasets

The master CSV is built from 4 source datasets. The daily and weekly panels are included for teams that want finer resolution.

| File | What it is | Rows | Join key |
|---|---|---|---|
| `data/processed/acis/weather_daily.parquet` | Daily tmax, tmin, precipitation for every county, 1999–2025 | 2,495,086 | `fips` + `date` |
| `data/processed/drought/drought_weekly.parquet` | Weekly D0–D4 percentages and DSCI for every county, 2000–2025 | 348,634 | `fips` + `map_date` |
| `data/processed/nass/nass_raw.parquet` | NASS yield, harvested acres, planted acres in long format | 35,067 | `fips` + `crop` + `year` |
| `data/processed/soil/soil_county.parquet` | Static soil properties per county | 253 | `fips` |

**When to use the panels instead of the master:** if you want to define your own season windows, look at sub-seasonal patterns (was the drought early or late in the season?), compute your own GDD parameters, or examine daily weather extremes. The master aggregates these panels into one row per county-crop-year. The panels give you the daily and weekly resolution to disaggregate.

---

## Known limitations

These are real constraints, not defects. They're listed here so you can design around them rather than discover them in your results.

1. **Irrigation is invisible.** California yields are largely decoupled from precipitation because the crops are irrigated. `aws_100cm_mm` measures what the soil can hold, not what's applied. California precipitation-to-yield relationships will be weak for this reason. USGS irrigation water-use data is available as an advanced extension.

2. **Season windows are fixed.** They don't shift by state or year. California corn actually starts in March; these windows start in May. The daily panel ships alongside so you can build better windows if you want to.

3. **Sparse coverage is expected.** California corn has 31 counties, not 58. Iowa wheat has 28 counties, not 99. Delaware sorghum has 3 counties. This is not an error — not every county grows every crop. Small samples are real but require care in analysis.

4. **WHEAT means winter wheat only.** Spring wheat, durum, and other classes are excluded. NASS distinguishes them by `class_desc`.

5. **CORN and SORGHUM mean grain only.** Corn for silage is reported in tons per acre, not bushels, and is excluded.

6. **SSURGO is static.** Soil properties don't change over 26 years in this dataset. Land-use change, erosion, and soil amendments are not captured.

7. **Vernalization is not modelled.** Winter wheat GDD uses a simple heat sum (T_base = 0°C). Real wheat physiology requires a period of cold to trigger grain development. The GDD field doesn't capture that.

8. **`nccpi_crop` for sorghum uses the corn model.** NCCPI has no sorghum-specific submodel. Corn is used as a proxy because they share similar growing conditions. This is a documented approximation, not a precise match.

9. **`extreme_heat_days` is near zero for wheat.** The September-to-June window rarely reaches 35°C. The field is correct but uninformative for wheat. Focus on GDD or precipitation anomaly for wheat analysis.

10. **USDM starts January 4, 2000.** Wheat year 2000 is missing the September–December 1999 portion of its drought window. Those 3 drought fields are NaN.

---

## How the dataset was built

The pipeline is in `src/build/`. Each script is self-contained, caches every API response to `data/raw/`, and writes a processed parquet plus a failures log.

| Script | Source | Output |
|---|---|---|
| `NASS_data_pull.py` | USDA NASS Quick Stats API | `data/processed/nass/nass_raw.parquet` |
| `ACIS_data_pull.py` | NOAA ACIS GridData API | `data/processed/acis/weather_daily.parquet` |
| `USDM_data_pull.py` | U.S. Drought Monitor API | `data/processed/drought/drought_weekly.parquet` |
| `SSURGO_data_pull.py` | NRCS Soil Data Access | `data/processed/soil/soil_county.parquet` |
| `build_master.py` | All 4 parquets above | `data/master_dataset.csv` + `.parquet` |

The master build passed 25 internal validation checks and 29 ground-truth checks (spot-checked against known NASS yields, known drought events, known temperature ranges, and known soil geography).

Design decisions for every pipeline are documented in `docs/decisions/`.

---

## Research questions the dataset can answer

These are what the field set was sized against. They're starting points, not limits.

1. When a county is in D2 drought or worse during its growing season, how far does yield fall below its own trend?
2. Do counties with higher `aws_100cm_mm` (more soil water storage) lose less yield in drought years?
3. In Nebraska, how does corn's drought response differ from sorghum's? (Sorghum is drought-tolerant by design — this is a natural experiment.)
4. Is growing-season precipitation a stronger predictor of yield anomaly in rainfed Iowa than in irrigated California?
5. Is there a number of `extreme_heat_days` above which yield anomaly turns sharply negative? Does it differ by crop?
6. Once you control for `nccpi_crop` (soil quality), how much of the yield gap between counties is left for drought to explain?

Question 6 is the most defensible analysis a team can present. It separates what the soil determines from what the weather determines.

---

## Sources

| Source | Access | Documentation |
|---|---|---|
| USDA NASS Quick Stats | REST API, free key | [quickstats.nass.usda.gov/api](https://quickstats.nass.usda.gov/api) |
| NOAA ACIS | REST API, no key needed | [docs.rcc-acis.org](https://docs.rcc-acis.org/acisws/) |
| U.S. Drought Monitor | REST API, no key needed | [droughtmonitor.unl.edu](https://droughtmonitor.unl.edu/data-maps-tools/us-drought-monitor) |
| USDA NRCS Soil Data Access | SQL-over-HTTP, no key | [sdmdataaccess.nrcs.usda.gov](https://sdmdataaccess.nrcs.usda.gov/) |
| DSCI definition | — | [NDMC fact sheet](https://droughtmonitor.unl.edu/data/docs/DSCI_fact_sheet.pdf) |
| Season windows | — | [USDA Usual Planting and Harvesting Dates](https://swat.tamu.edu/media/90113/crops-typicalplanting-harvestingdates-by-states.pdf) |
