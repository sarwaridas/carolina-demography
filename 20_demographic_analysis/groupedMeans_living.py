"""Calculating indicator variable for group living data."""
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def groupedMeans(data, col, cond=0):
    # normalize
    data["normalized_col"] = data[col] / data["POPESTIMATE2020"]
    data["indicator"] = np.where(data["normalized_col"] > cond, 1, 0)
    print(
        data[["percent_change", "indicator"]]
        .groupby("indicator", as_index=False)
        .mean()
    )
    pval = ttest_ind(
        data[data["indicator"] == 0]["percent_change"],
        data[data["indicator"] == 1]["percent_change"],
    )[1]
    print(f"t-test pvalue: {pval}")


pop = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
groupedMeans(pop, "college_housing")
groupedMeans(pop, "military_housing")
groupedMeans(pop, "adult_jail", 0.03)
