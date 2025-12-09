import pandas as pd
from pathlib import Path

def extract_carrier(group: str) -> str|None:
    """
    Extract a single carrier code from a TK_CARRIER_GROUP string
    
    Parameter -- group: str
                    A ticketing carrier group string (e.g. "AA:AA:UA" or "--:AA:UA")

    Returns -- str: the first part (a 2-letter carrier code) that is not "--"
            -- pd.NA: only if entire string only contains "--" or is missing value
    """

    if pd.isna(group):
        return None # return None if string is missing value
    
    codes = str(group).split(":")
    for c in codes: # iterate the splitted-out terms
        c = c.strip()
        if c and c != "--": # check if current part is "--"
            return c # return the first non-"--" part as carrier

    return None  # return None if string contains all "--"

raw_dir = Path("../data/raw")
csv_files = sorted(raw_dir.glob("bts_*.csv")) # store the file names for convenience
dfs = [] # create a list to store all quarter dataframes

# apply extract_carrier(group) to column `TK_CARRIER_GROUP` and store into a new column
for path in csv_files:
    df = pd.read_csv(path)
    df["CARRIER"] = df["TK_CARRIER_GROUP"].apply(extract_carrier)
    dfs.append(df) # append to list

# combine all quarter dataframes into one big DataFrame
all_data = pd.concat(dfs, ignore_index=True)
print("Combined shape:", all_data.shape)

# find top 10 ORIGIN–DEST pairs
top10_routes = (all_data.value_counts(["ORIGIN", "DEST"]) # group by ORIGIN-DEST pairs
                .reset_index(name="count") # store the counts as column `count`
                .sort_values("count", ascending=False)
                ).head(10) # sort by count in decreasing order and extract the top 10
print(f"Top 10 routes:\n{top10_routes}")

# inner-join by columns `ORIGIN` and `DEST`
    # so that only the matching rows with top 10 ORIGIN-DEST pair are kept
filtered_data = all_data.merge(
    top10_routes[["ORIGIN", "DEST"]],
    on=["ORIGIN", "DEST"], how="inner"
    )

# save cleaned data as ../data/processed/cleaned_data.csv
processed_dir = Path("../data/processed")
processed_dir.mkdir(parents=True, exist_ok=True) # make directory just in case
out_path = processed_dir / "cleaned_data.csv"
filtered_data.to_csv(out_path, index=False)