"""Accessing 2020 ACS Data."""

from census import Census
from us import states
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv("../.env")


# Census API key
c = Census(os.environ.get("CENSUS_KEY"))

# Obtain appropriate variable names
acs_vars = ["NAME"]
for i in range(5, 18):
    if i < 10:
        acs_vars.append("DP05_000" + str(i) + "E")
    else:
        acs_vars.append("DP05_00" + str(i) + "E")
acs_vars = acs_vars + [
    "DP05_0037E",
    "DP05_0038E",
    "DP05_0039E",
    "DP05_0044E",
    "DP05_0065E",
    "DP05_0071E",
    "DP05_0002E",
    "DP05_0003E",
]


# Access ACS 2020 data in JSON format
data = c.acs5dp.state_county(
    tuple(acs_vars),
    states.NC.fips,
    "*",
    year=2020,
)

# Convert to DataFrame
df = pd.DataFrame(data)

# Rename variables to more intuitive
df = df.rename(
    {
        "NAME": "county",
        "state": "state_fips",
        "county": "county_fips",
        "DP05_0037E": "white_pop",
        "DP05_0038E": "black_pop",
        "DP05_0039E": "ai_an_pop",
        "DP05_0044E": "asian_pop",
        "DP05_0065E": "black_w_other_race_pop",
        "DP05_0071E": "hisp_any_race_pop",
        "DP05_0002E": "male_pop",
        "DP05_0003E": "female_pop",
        "DP05_0005E": "0-5_pop",
        "DP05_0006E": "5-9_pop",
        "DP05_0007E": "10-14_pop",
        "DP05_0008E": "15-19_pop",
        "DP05_0009E": "20-24_pop",
        "DP05_0010E": "25-34_pop",
        "DP05_0011E": "35-44_pop",
        "DP05_0012E": "45-54_pop",
        "DP05_0013E": "55-59_pop",
        "DP05_0014E": "60-64_pop",
        "DP05_0015E": "65-74_pop",
        "DP05_0016E": "75-84_pop",
        "DP05_0017E": "85_plus_pop",
    },
    axis=1,
)

df.to_csv("../00_source_data/2020_acs_demographics.csv", index=False)
