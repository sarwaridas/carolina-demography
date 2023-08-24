# %%
# Merging data
import pandas as pd
import numpy as np
from datetime import date

all_pop = pd.read_csv(
    "../05_intermediate_data/cleaned_all_pop_data.csv", index_col="Unnamed: 0"
)
covid_deaths = pd.read_csv(
    "../00_source_data/covid_deaths_NC.csv", index_col="Unnamed: 0"
)
# sex_age = pd.read_csv("../00_source_data/sex_age_NC.csv", index_col="Unnamed: 0")
# sex_race = pd.read_csv("../00_source_data/sex_race_NC.csv", index_col="Unnamed: 0")
acs_df = pd.read_csv("../00_source_data/2020_acs_demographics.csv")

# %%
# sex_race = sex_race.loc[sex_race.YEAR == 14]
# sex_race.insert(1, "FIPS", sex_race["COUNTY"].astype(int) + 37000)  # creating FIPS code
# sex_race.drop(
#     ["SUMLEV", "STATE", "STNAME", "CTYNAME", "COUNTY", "YEAR", "TOT_POP"],
#     axis=1,
#     inplace=True,
# )
# sex_race = pd.pivot(
#     sex_race, index=["FIPS"], columns=["AGEGRP"]
# )  # pivot by age gp - this adds a LOT of columns
# sex_race.columns = [
#     "".join(str(col)) for col in sex_race.columns.values
# ]  # getting rid of multilevel idx
# sex_race.reset_index(inplace=True)
# assert sex_race.shape[0] == 100
# sex_race.head()

# %%
covid_deaths = covid_deaths[~covid_deaths.FIPS.isin([80037.0, 90037.0])]
covid_deaths.sort_values(ascending=True, by="FIPS")
drop_covid_deaths = [
    "UID",
    "iso2",
    "iso3",
    "code3",
    "Admin2",
    "Province_State",
    "Country_Region",
    "Lat",
    "Long_",
    "Combined_Key",
]
covid_deaths = covid_deaths.drop(drop_covid_deaths, axis=1)
exc_end = ["/22", "/21"]  # removes any data from 2022 and 2021
exc_start = ["7", "8", "9", "10", "11", "12"]  # removes data july onwards
covid_deaths = covid_deaths[
    covid_deaths.columns[~(covid_deaths.columns.str.endswith(tuple(exc_end)))]
]  # removes any data from 2022 and 2021
covid_deaths = covid_deaths[
    covid_deaths.columns[~(covid_deaths.columns.str.startswith(tuple(exc_start)))]
]  # removes data july onwards
assert covid_deaths.shape[0] == 100
assert (
    covid_deaths.shape[1] == ((date(2020, 6, 30)) - (date(2020, 1, 22))).days + 3
)  # data starts on jan 22. counting days elapsed b/w jan 22 and june 30.
# Adding 2 (for extra columns already present in df) + 1 (for the day of june 30th)
covid_deaths["fatalityCount"] = covid_deaths.drop(["FIPS", "Population"], axis=1).sum(
    axis=1
)
covid_deaths = covid_deaths.loc[:, ["fatalityCount", "FIPS", "Population"]]
covid_deaths.rename(columns={"Population": "pop_covid_est"}, inplace=True)
covid_deaths.head()
# %%
# sex_age = sex_age.loc[sex_age.YEAR == 14]
# sex_age.insert(1, "FIPS", sex_age["COUNTY"].astype(int) + 37000)
# sex_age.drop(
#     ["SUMLEV", "STATE", "STNAME", "CTYNAME", "COUNTY", "YEAR", "POPESTIMATE"],
#     axis=1,
#     inplace=True,
# )
# assert sex_age.shape[0] == 100
# sex_age.head()

# %%
all_pop.insert(1, "FIPS", all_pop.county_fips.astype(int) + 37000)  # creating fips code
all_pop.sort_values(by="FIPS", ascending=True, inplace=True)
all_pop.head()

# %%
assert acs_df.shape[0] == 100
acs_df.insert(1, "FIPS", acs_df.county_fips.astype(int) + 37000)  # creating fips code

# %%
# merging pop data with covid deaths
merged_df = all_pop.merge(covid_deaths, how="inner", validate="1:1", on="FIPS")

# %%
# merging with acs data
merged_df = merged_df.merge(acs_df, how="inner", validate="1:1", on="FIPS")

# %%
# merging data with sex_age
# merged_df = merged_df.merge(sex_age, how="inner", validate="1:1", on="FIPS")

# %%
# merging data with sex_race
# merged_df = merged_df.merge(sex_race, how="inner", validate="1:1", on="FIPS")

# %%
assert merged_df.shape[0] == 100

# %%
# Include county codes data
county_codes = pd.read_csv("../00_source_data/2015CountyTypologyCodes.csv")
county_codes = county_codes[county_codes["State"] == "NC"]
county_codes["farm_man"] = 0
county_codes.loc[
    (county_codes["Manufacturing_2015_Update"] == 1)
    | (county_codes["Farming_2015_Update"] == 1),
    "farm_man",
] = 1
county_codes["recreation"] = 0
county_codes.loc[
    (county_codes["Recreation_2015_Update"] == 1),
    "recreation",
] = 1
county_codes["retirement_metro"] = 0
county_codes.loc[
    (county_codes["Retirement_Dest_2015_Update"] == 1)
    & (county_codes["Metro-nonmetro status, 2013 0=Nonmetro 1=Metro"] == 1),
    "retirement_metro",
] = 1
county_codes["retirement_non_metro"] = 0
county_codes.loc[
    (county_codes["Retirement_Dest_2015_Update"] == 1)
    & (county_codes["Metro-nonmetro status, 2013 0=Nonmetro 1=Metro"] == 0),
    "retirement_non_metro",
] = 1
county_codes = county_codes[
    [
        "County_name",
        "farm_man",
        "recreation",
        "retirement_metro",
        "retirement_non_metro",
    ]
]
merged_df = pd.merge(
    merged_df,
    county_codes,
    left_on="county_x",
    right_on="County_name",
    validate="1:1",
).drop("County_name", axis=1)

# %%
housing = pd.read_csv("../00_source_data/housing_counts_NC.csv")
housing = housing[housing["CTYNAME"] != "North Carolina"]
housing = housing[
    [
        "CTYNAME",
        "CENSUS2010HU",
        "HUESTIMATESBASE2010",
        "HUESTIMATE2020",
        "HUESTIMATE042020",
    ]
]
assert housing.shape[0] == 100
merged_df = pd.merge(
    merged_df,
    housing,
    left_on="county_x",
    right_on="CTYNAME",
    validate="1:1",
)
merged_df = merged_df.drop(["CTYNAME"], axis=1)

# %%
## Adding economic and education data
pov = pd.read_excel("../00_source_data/PovertyEstimates.xlsx", skiprows=[0, 1, 2, 3])
pov = pov[(pov["Stabr"] == "NC") & (pov["Area_name"] != "North Carolina")]
pov = pov[["Area_name", "PCTPOVALL_2020", "POV017_2020", "MEDHHINC_2020"]]
unemp = pd.read_excel("../00_source_data/Unemployment.xlsx", skiprows=[0, 1, 2, 3])
unemp = unemp[(unemp["State"] == "NC") & (unemp["Area_name"] != "North Carolina")]
unemp["Area_name"] = unemp["Area_name"].str.rstrip(", NC")
unemp = unemp[
    ["Area_name", "Unemployed_2019", "Employed_2019", "Civilian_labor_force_2019"]
]
educ = pd.read_excel("../00_source_data/Education.xlsx", skiprows=[0, 1, 2, 3])
educ = educ[(educ["State"] == "NC") & (educ["Area name"] != "North Carolina")]
educ["Area_name"] = educ["Area name"]
educ = educ[
    [
        "Area_name",
        "Percent of adults with less than a high school diploma, 2016-20",
        "Percent of adults with a high school diploma only, 2016-20",
        "Percent of adults completing some college or associate's degree, 2016-20",
        "Percent of adults with a bachelor's degree or higher 2016-20",
    ]
]
pov_unemp = pov.merge(unemp, on="Area_name", validate="1:1", how="outer")
pov_unemp_educ = pov_unemp.merge(educ, on="Area_name", validate="1:1", how="outer")
merged_df = merged_df.merge(
    pov_unemp_educ,
    left_on="county_x",
    right_on="Area_name",
    validate="1:1",
    how="outer",
)
# %%

merged_df.to_csv("../05_intermediate_data/merged_pop_data_revised.csv", index=None)
