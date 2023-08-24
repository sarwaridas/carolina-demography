import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from groupedMeans_function import *

# reading in the data
pop = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
pop.head()

# printing column names
print(pop.columns)


# creating age group columns
pop["over_65"] = pop["85_plus_pop"] + pop["65-74_pop"] + pop["75-84_pop"]
pop["under_20"] = pop["0-5_pop"] + pop["5-9_pop"] + pop["10-14_pop"] + pop["15-19_pop"]

# getting grouped means for each age group
groupedMeans(pop, "85_plus_pop")
groupedMeans(pop, "over_65")
groupedMeans(pop, "under_20")
groupedMeans(pop, "0-5_pop")

# getting grouped means for hispanic pop
groupedMeans(pop, "hisp_any_race_pop")
