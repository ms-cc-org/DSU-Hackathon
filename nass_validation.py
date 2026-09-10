"""
NASS parquet validation against dataset_specification.md.                                                                                                                                              

Checks applicable at this stage (NASS only, long format):
    V2  — no duplicate (fips, crop, year, statistic)
    V3  — all fips have correct state prefix (06/19/31/10)
    V4  — fips is string, length 5
    V5  — year span per (crop, state)
    V6  — exactly 4 crops, 4 states
    V7  — no non-null yield <= 0
    V8  — yield rows carry BU / ACRE, acreage rows carry ACRES
    V9  — acres_harvested <= acres_planted wherever both non-null
    V18 — zero CA soybeans, zero non-null IA sorghum yields                                                                                                                                              
                                                                                                                                                                                                         
Checks NOT run here (need other sources joined first):
    V1  V10  V11  V12  V13  V14  V15  V16  V17  V19                                                                                                                                                      
"""
import pandas as pd

PARQUET = "data/processed/nass/nass_raw.parquet"
STATE_FIPS = {"CA": "06", "IA": "19", "NE": "31", "DE": "10"}
VALID_CROPS  = {"CORN", "SOYBEANS", "WHEAT", "SORGHUM"}
VALID_STATES = {"CA", "IA", "NE", "DE"}

df = pd.read_parquet(PARQUET)
failures = []

def ok(label):
    print(f"  PASS  {label}")

def fail(label, detail):
    print(f"  FAIL  {label}: {detail}")
    failures.append(label)

print(f"\nLoaded {len(df):,} rows × {len(df.columns)} cols from {PARQUET}")
print(f"Columns: {list(df.columns)}\n")

# V2: No duplicate (fips, crop, year, statistic)

dups = df.duplicated(subset=["fips", "crop", "year", "statistic"]).sum()
if dups == 0:
    ok("V2  uniqueness (fips, crop, year, statistic)")
else:
    fail("V2  uniqueness", f"{dups} duplicate rows")

# V3: FIPS prefix matches state
bad_prefix = 0
for state, prefix in STATE_FIPS.items():
    state_rows = df[df["state_abbr"] == state]
    wrong = state_rows[~state_rows["fips"].str.startswith(prefix)]
    bad_prefix += len(wrong)
if bad_prefix == 0:
    ok("V3  FIPS prefix valid for all 4 states")
else:
    fail("V3  FIPS prefix", f"{bad_prefix} rows with wrong prefix")

# V4: fips is string, length 5
wrong_len = (df["fips"].str.len() != 5).sum()
wrong_type = not pd.api.types.is_string_dtype(df["fips"])
if wrong_len == 0 and not wrong_type:
    ok("V4  FIPS type=string, len=5")
else:
    fail("V4  FIPS", f"wrong_type={wrong_type}, wrong_len_rows={wrong_len}")

# V5: Year span per (crop, state)
print("\n  V5  Year span per (crop, state_abbr):")
spans = df.groupby(["crop", "state_abbr"])["year"].agg(["min", "max"])
v5_issues = spans[(spans["min"] > 2000) | (spans["max"] < 2025)]
if v5_issues.empty:
    ok("V5  all groups span 2000–2025")
else:
    print("       Groups NOT spanning 2000–2025 (expected for some — document):")
    print("  " + v5_issues.to_string().replace("\n", "\n  "))
    # Not a hard failure — sparse crops may start later
    print()

# V6: Exactly 4 crops, 4 states
crops  = set(df["crop"].unique())
states = set(df["state_abbr"].unique())
if crops == VALID_CROPS:
    ok(f"V6  crops = {sorted(crops)}")
else:
    fail("V6  crops", f"got {sorted(crops)}")
if states == VALID_STATES:
    ok(f"V6  states = {sorted(states)}")
else:
    fail("V6  states", f"got {sorted(states)}")

# ── V7: No non-null yield <= 0
yield_rows = df[df["statistic"] == "YIELD"]
bad_yields = yield_rows[yield_rows["value"].notna() & (yield_rows["value"] <= 0)]
if len(bad_yields) == 0:
    ok(f"V7  yield positivity ({len(yield_rows):,} yield rows checked)")
else:
    fail("V7  yield positivity", f"{len(bad_yields)} rows with value <= 0")

# V8: Units 
bad_yield_unit = yield_rows[yield_rows["unit"] != "BU / ACRE"]
acres_rows = df[df["statistic"].isin(["AREA HARVESTED", "AREA PLANTED"])]
bad_acres_unit = acres_rows[acres_rows["unit"] != "ACRES"]
if len(bad_yield_unit) == 0 and len(bad_acres_unit) == 0:
    ok("V8  units: yield=BU/ACRE, acreage=ACRES")
else:
    if len(bad_yield_unit): fail("V8  yield unit", f"{len(bad_yield_unit)} rows not BU/ACRE")
    if len(bad_acres_unit): fail("V8  acreage unit", f"{len(bad_acres_unit)} rows not ACRES")

# V9: acres_harvested <= acres_planted
# Pivot to wide to compare (only SOYBEANS and WHEAT have planted data)
planted  = df[df["statistic"] == "AREA PLANTED"][["fips","crop","year","value"]].rename(columns={"value":"planted"})
harvested = df[df["statistic"] == "AREA HARVESTED"][["fips","crop","year","value"]].rename(columns={"value":"harvested"})
acres = planted.merge(harvested, on=["fips","crop","year"], how="inner")
acres = acres[acres["planted"].notna() & acres["harvested"].notna()]
bad_acres = acres[acres["harvested"] > acres["planted"]]

if len(bad_acres) == 0:
    ok(f"V9  acres_harvested <= acres_planted ({len(acres):,} pairs checked)")
else:
    fail("V9  acreage consistency", f"{len(bad_acres)} rows where harvested > planted")
    print(bad_acres[["fips","crop","year","harvested","planted"]].head(10).to_string(index=False))

# V18: Known gaps present 
ca_soy = df[(df["crop"] == "SOYBEANS") & (df["state_abbr"] == "CA")]
if len(ca_soy) == 0:
    ok("V18  CA soybeans = 0 rows (expected gap)")
else:
    fail("V18  CA soybeans", f"found {len(ca_soy)} rows — should be 0")

ia_sorghum_yields = df[
    (df["crop"] == "SORGHUM") &
    (df["state_abbr"] == "IA") & 
    (df["statistic"] == "YIELD") &
    df["value"].notna()
    ]

if len(ia_sorghum_yields) == 0:
    ok("V18  IA sorghum non-null yields = 0 (expected gap)")
else:
    fail("V18  IA sorghum", f"found {len(ia_sorghum_yields)} non-null yields — should be 0")

# Summary

if failures:
    print(f"RESULT: {len(failures)} check(s) FAILED: {failures}")
else:
    print("RESULT: All applicable NASS checks passed.")