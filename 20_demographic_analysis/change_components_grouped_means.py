# %%
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from groupedMeans_function import *

df = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
df.head()

# %%
df.columns
# %%
vars = [
    "annual_growth_rate",
    "fatalityCount",
    "BIRTHS2020",
    "DEATHS2020",
    "NATURALINC2020",
    "INTERNATIONALMIG2020",
    "DOMESTICMIG2020",
]

for i in vars:
    print(f"The variable of interest is {i}")
    # getting grouped means for each variable
    groupedMeans(df, i)
    print("####################################")
