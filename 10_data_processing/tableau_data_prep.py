# %%
import pandas as pd
import numpy as np

# reading in the data
merged_df = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
merged_df["over_65"] = (
    merged_df["85_plus_pop"] + merged_df["65-74_pop"] + merged_df["75-84_pop"]
)

merged_df["under_20"] = (
    merged_df["0-5_pop"]
    + merged_df["5-9_pop"]
    + merged_df["10-14_pop"]
    + merged_df["15-19_pop"]
)
merged_df["norm_unocc"] = merged_df["unocc_housing"] / merged_df["total_housing"]

dict = {
    "Percent of adults with less than a high school diploma, 2016-20": "lessthanHSdiploma",
    "Percent of adults with a high school diploma only, 2016-20": "HSdiploma",
    "Percent of adults completing some college or associate's degree, 2016-20": "SomeCollege",
    "Percent of adults with a bachelor's degree or higher 2016-20": "College",
}

# call rename () method
merged_df.rename(columns=dict, inplace=True)
# %%
merged_df.head()
# %%
# creating a list for variables that need to be made into a percent
vars = [
    "under_20",
    "over_65",
    "Employed_2019",
    "Unemployed_2019",
    "college_housing",
    "military_housing",
    "white_pop",
    "black_pop",
    "ai_an_pop",
    "asian_pop",
    "black_w_other_race_pop",
    "hisp_any_race_pop",
]

for col in vars:
    merged_df[col] = (merged_df[col] / merged_df["POPESTIMATE2020"]) * 100

# creating column for housing counts error
merged_df["housing_perc_change"] = (
    100
    * (merged_df["total_housing"] - merged_df["HUESTIMATE042020"])
    / merged_df["HUESTIMATE042020"]
)

merged_df
# %%
# saving new data
from pathlib import Path

PARENT = "carolina-demography"
path = Path(PARENT).parent / "../05_intermediate_data"
merged_df.to_csv(path / "tableau_data.csv")
