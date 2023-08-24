"""Accessing 2020 Census Data."""

from census import Census
from us import states
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv("../.env")


# Census API key
c = Census(os.environ.get("CENSUS_KEY"))

# Access redistricting 2020 data in JSON format for county level.
data = c.pl.state_county(
    (
        "NAME",
        "P1_001N",
        "H1_001N",
        "H1_002N",
        "H1_003N",
        "P5_001N",
        "P5_002N",
        "P5_003N",
        "P5_004N",
        "P5_005N",
        "P5_006N",
        "P5_007N",
        "P5_008N",
        "P5_009N",
        "P5_010N",
    ),
    states.NC.fips,
    "*",
    year=2020,
)

# Convert to DataFrame
df = pd.DataFrame(data)

#  Remove 'North Carolina' from column names
df["NAME"] = df["NAME"].str.replace(", North Carolina", "")

# Rename variables as appropriate
df = df.rename(
    {
        "NAME": "county",
        "P1_001N": "pop_count",
        "state": "state_fips",
        "county": "county_fips",
        "H1_001N": "total_housing",
        "H1_002N": "occ_housing",
        "H1_003N": "unocc_housing",
        "P5_001N": "total_group",
        "P5_002N": "total_inst",
        "P5_003N": "adult_jail",
        "P5_004N": "juvenille_jail",
        "P5_005N": "nursing_homes",
        "P5_006N": "other_inst",
        "P5_007N": "non_inst_total",
        "P5_008N": "college_housing",
        "P5_009N": "military_housing",
        "P5_010N": "other_non_inst",
    },
    axis=1,
)

# Ensure have data for 100 counties
assert df.shape[0] == 100

df.to_csv("../00_source_data/2020_counts_NC.csv", index=False)

# Access redistricting 2020 data in JSON format for tract level.
tracts = c.pl.state_county_tract(
    (
        "NAME",
        "P1_001N",
        "H1_001N",
        "H1_002N",
        "H1_003N",
        "P5_001N",
        "P5_002N",
        "P5_003N",
        "P5_004N",
        "P5_005N",
        "P5_006N",
        "P5_007N",
        "P5_008N",
        "P5_009N",
        "P5_010N",
    ),
    states.NC.fips,
    "*",
    "*",
    year=2020,
)

# Convert to DataFrame
tracts = pd.DataFrame(tracts)

#  Remove 'North Carolina' from column names
tracts["NAME"] = tracts["NAME"].str.replace(", North Carolina", "")


# Rename variables as appropriate
tracts = tracts.rename(
    {
        "NAME": "county_and_tra",
        "P1_001N": "pop_count",
        "state": "state_fips",
        "county": "county_fips",
        "tract": "tract_fips",
        "H1_001N": "total_housing",
        "H1_002N": "occ_housing",
        "H1_003N": "unocc_housing",
        "P5_001N": "total_group",
        "P5_002N": "total_inst",
        "P5_003N": "adult_jail",
        "P5_004N": "juvenille_jail",
        "P5_005N": "nursing_homes",
        "P5_006N": "other_inst",
        "P5_007N": "non_inst_total",
        "P5_008N": "college_housing",
        "P5_009N": "military_housing",
        "P5_010N": "other_non_inst",
    },
    axis=1,
)
tracts["full_fips"] = (
    tracts["state_fips"] + tracts["county_fips"] + tracts["tract_fips"]
)

tracts.to_csv("../00_source_data/2020_counts_NC_tract.csv", index=False)
