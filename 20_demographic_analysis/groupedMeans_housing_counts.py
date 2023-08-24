"""Repeat analysis for housing counts."""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

merged_pop = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
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
housing_merge = pd.merge(
    merged_pop,
    housing,
    left_on="county_x",
    right_on="CTYNAME",
    validate="1:1",
)
assert housing_merge.shape[0] == 100
housing_merge["housing_perc_change"] = (
    100
    * (housing_merge["total_housing"] - housing_merge["HUESTIMATE042020"])
    / housing_merge["HUESTIMATE042020"]
)
housing_merge["housing_count_cat"] = "Neither overcount or Undercount"
housing_merge.loc[
    housing_merge["housing_perc_change"] >= 5, "housing_count_cat"
] = "Overcount"
housing_merge.loc[
    housing_merge["housing_perc_change"] <= -5, "housing_count_cat"
] = "Undercount"

housing_merge["county_fips"] = housing_merge["FIPS"].astype(str).str[-3:]
gdf = gpd.read_file("../00_source_data/cb_2018_us_county_20m")
nc_county = gdf[gdf["STATEFP"] == "37"]
temp = housing_merge[["county_fips", "housing_perc_change"]]
final_graph = nc_county.merge(
    temp, left_on="COUNTYFP", right_on="county_fips", how="inner"
)
cmap = "RdBu"
fig, ax = plt.subplots(1, 1, figsize=(10, 20))
final_graph.plot(
    column="housing_perc_change",
    cmap=cmap,
    legend=True,
    legend_kwds={"shrink": 0.15, "label": "Percent Difference"},
    missing_kwds={
        "color": "grey",
        "label": "Missing values",
    },
    alpha=0.8,
    edgecolor="#808080",
    linewidth=0.6,
    ax=ax,
)

ax.set_axis_off()
ax.set_title(label="% Change in Housing between 2020 Census  and Estimates", size=15)
fig.savefig("../50_results/images/county_changes_housing.png", bbox_inches="tight", dpi=400)

housing_merge["diff"] = (
    housing_merge["housing_perc_change"] - housing_merge["percent_change"]
).abs()
temp = housing_merge[["county_fips", "diff"]]
final_graph = nc_county.merge(
    temp, left_on="COUNTYFP", right_on="county_fips", how="inner"
)

fig, ax = plt.subplots(1, 1, figsize=(10, 20))
final_graph.plot(
    column="diff",
    cmap=cmap,
    legend=True,
    legend_kwds={"shrink": 0.15, "label": "Absolute Difference"},
    missing_kwds={
        "color": "grey",
        "label": "Missing values",
    },
    alpha=0.8,
    edgecolor="#808080",
    linewidth=0.6,
    ax=ax,
)

ax.set_axis_off()
ax.set_title(
    label="Absolute Difference between Housing and Population % Change", size=15
)
fig.savefig("../50_results/images/county_diff_pop_housing.png", bbox_inches="tight", dpi=400)


from scipy.stats import ttest_ind


def groupedMeans(data, col):
    # normalize
    data["normalized_col"] = data[col] / data["POPESTIMATE2020"]
    print(
        data[["normalized_col", "housing_count_cat"]]
        .groupby("housing_count_cat", as_index=False)
        .mean()
    )
    pval = ttest_ind(
        data[data["housing_count_cat"] == "Neither overcount or Undercount"][
            "normalized_col"
        ],
        data[data["housing_count_cat"] == "Undercount"]["normalized_col"],
    )[1]
    print(f"t-test pvalue: {pval}")


groupedMeans(housing_merge, "black_pop")
groupedMeans(housing_merge, "hisp_any_race_pop")
groupedMeans(housing_merge, "annual_growth_rate")
housing_merge["over65"] = (
    housing_merge["65-74_pop"]
    + housing_merge["75-84_pop"]
    + housing_merge["85_plus_pop"]
)
groupedMeans(housing_merge, "over65")
groupedMeans(housing_merge, "85_plus_pop")
housing_merge["under20"] = (
    housing_merge["0-5_pop"] + housing_merge["5-9_pop"] + housing_merge["15-19_pop"]
)
groupedMeans(housing_merge, "under20")
groupedMeans(housing_merge, "0-5_pop")
groupedMeans(housing_merge, "fatalityCount")
groupedMeans(housing_merge, "BIRTHS2020")
groupedMeans(housing_merge, "DEATHS2020")
groupedMeans(housing_merge, "NATURALINC2020")
groupedMeans(housing_merge, "INTERNATIONALMIG2020")
groupedMeans(housing_merge, "DOMESTICMIG2020")


def groupedMeans(data, col, cond=0):
    # normalize
    data["normalized_col"] = data[col] / data["POPESTIMATE2020"]
    data["indicator"] = np.where(data["normalized_col"] > cond, 1, 0)
    print(
        data[["housing_perc_change", "indicator"]]
        .groupby("indicator", as_index=False)
        .mean()
    )
    pval = ttest_ind(
        data[data["indicator"] == 0]["housing_perc_change"],
        data[data["indicator"] == 1]["housing_perc_change"],
    )[1]
    print(f"t-test pvalue: {pval}")



