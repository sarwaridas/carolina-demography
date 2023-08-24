import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def groupedMeans(data, col):
    # normalize
    data["normalized_col"] = data[col] / data["POPESTIMATE2020"]
    print(
        data[["normalized_col", "undercount_5_prc"]]
        .groupby("undercount_5_prc", as_index=False)
        .mean()
    )
    pval = ttest_ind(
        data[data["undercount_5_prc"] == 0]["normalized_col"],
        data[data["undercount_5_prc"] == 1]["normalized_col"],
    )[1]
    print(f"t-test pvalue: {pval}")
