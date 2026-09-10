import pandas as pd
df = pd.read_parquet("data/processed/nass/nass_raw.parquet")

# Shape and columns
print(df.shape)
print(df.dtypes)

# Sample rows
print(df.head(5).to_string())

# Distribution by crop, statistic, state
print(df.groupby(["crop", "statistic", "state_abbr"]).size().to_string())

# Value stats for yield rows only
yield_df = df[df["statistic"] == "YIELD"]
print(yield_df.groupby(["crop"])["value"].describe())