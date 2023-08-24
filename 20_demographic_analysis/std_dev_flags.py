# %%
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# reading in the data
pop = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")

# Selecting counties that have populations (% of total pop) at least 1 std. dev above mean for all counties

# we may be missing Vacant Housing Units and Housing Vacancy
# creating age group columns
pop["over_65"] = pop["85_plus_pop"] + pop["65-74_pop"] + pop["75-84_pop"]
pop["under_20"] = pop["0-5_pop"] + pop["5-9_pop"] + pop["10-14_pop"] + pop["15-19_pop"]
pop["norm_unocc"] = pop["unocc_housing"] / pop["total_housing"]
# keeping columns of interest
cols = [
    "county_x",
    "black_pop",
    "hisp_any_race_pop",
    "ai_an_pop",
    "college_housing",
    "military_housing",
    "adult_jail",
]
df = pop.loc[:, cols]
df.head()
total_pops = list(df.sum(axis=0))[1:]
df_norm = df.iloc[:, 1:] / total_pops
# %%
df_norm["norm_unocc"] = pop["norm_unocc"]
df_norm["county_x"] = df["county_x"]
df_norm.head()
# %%
def std_dev_flag(data, col):
    threshold = data[col].mean() + data[col].std()
    return list(data.loc[(data[col] > threshold)].county_x)


for column in df_norm.iloc[:, :-1]:
    print(f"List of counties with mean above one std dev.: {column}")
    print(std_dev_flag(df_norm, col=column))
    print("*****************")
