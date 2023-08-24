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
pop["total_jail"] = pop["adult_jail"] + pop["juvenille_jail"]

# keeping columns of interest
cols = [
    "black_pop",
    "hisp_any_race_pop",
    "ai_an_pop",
    "over_65",
    "under_20",
    "total_jail",
    "college_housing",
    "military_housing",
]
df = pop


def std_dev_flag(data, col):
    threshold = (data[col] / data["POPESTIMATE2020"]).mean() + (
        data[col] / data["POPESTIMATE2020"]
    ).std()
    return (data[col] / data["POPESTIMATE2020"]) > threshold


for column in cols:
    print(f"Counties with mean above one std dev.: {column}")
    df["temp"] = std_dev_flag(df, col=column)
    group = (
        df[
            [
                "temp",
                "error",
                "abs_error",
                "percent_error",
                "abs_percent_error",
            ]
        ]
        .groupby("temp")
        .agg(["mean", "count"])
    )
    print(group.sort_index(ascending=False))
    print("*****************")
    for i in df.loc[df["temp"], "county_x"]:
        print(i, end=", ")


cols2 = ["farm_man", "recreation", "retirement_metro", "retirement_non_metro"]
for column in cols2:
    group = (
        df[
            [
                column,
                "error",
                "abs_error",
                "percent_error",
                "abs_percent_error",
            ]
        ]
        .groupby(column)
        .agg(["mean", "count"])
    )
    print(group.sort_index(ascending=False))
    print("*****************")


df["housing_error"] = df["total_housing"] - df["HUESTIMATE042020"]
df["housing_abs_error"] = df["housing_error"].abs()
df["housing_percent_error"] = 100 * df["housing_error"] / df["HUESTIMATE042020"]
df["housing_abs_percent_error"] = 100 * df["housing_abs_error"] / df["HUESTIMATE042020"]

for column in cols:
    print(f"Counties with mean above one std dev.: {column}")
    df["temp"] = std_dev_flag(df, col=column)
    group = (
        df[
            [
                "temp",
                "housing_error",
                "housing_abs_error",
                "housing_percent_error",
                "housing_abs_percent_error",
            ]
        ]
        .groupby("temp")
        .agg(["mean", "count"])
    )
    print(group.sort_index(ascending=False))
    print("*****************")

cols2 = ["farm_man", "recreation", "retirement_metro", "retirement_non_metro"]
for column in cols2:
    group = (
        df[
            [
                column,
                "housing_error",
                "housing_abs_error",
                "housing_percent_error",
                "housing_abs_percent_error",
            ]
        ]
        .groupby(column)
        .agg(["mean", "count"])
    )
    print(group.sort_index(ascending=False))
    print("*****************")
