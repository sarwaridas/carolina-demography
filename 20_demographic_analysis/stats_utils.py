import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def checkNormality(data, col, dist=True):
    from scipy import stats
    import matplotlib.pyplot as plt

    if dist:
        dist = data[col].plot(kind="hist", title=f"Distribution")
    else:
        qq = stats.probplot(data[col], dist="norm", plot=plt)


def checkEqualVariance(data, col):
    import scipy.stats

    group1 = (data[data["undercount_5_prc"] == 0][col],)
    group2 = data[data["undercount_5_prc"] == 1][col]
    f = np.var(group1, ddof=1) / np.var(group2, ddof=1)
    nun = np.array(group1).size - 1
    dun = np.array(group1).size - 1
    p_value = 1 - scipy.stats.f.cdf(f, nun, dun)
    print(f"F stat:{f}\np-value:{p_value}")
