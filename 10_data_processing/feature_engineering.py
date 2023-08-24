import pandas as pd
import numpy as np
from pathlib import Path
import geopandas as gpd
import contextily as cx
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt


# importing the census count data
PARENT = "carolina-demography"
path = Path(PARENT).parent / "../00_source_data/2020_counts_NC.csv"
counts = pd.read_csv(path, sep=",", header="infer", dtype=str, encoding="latin-1")
counts.head()

# importing the estimate data
PARENT2 = "carolina-demography"
path2 = Path(PARENT2).parent / "../00_source_data/co-est2020-alldata.csv"
estimates = pd.read_csv(path2, sep=",", header="infer", dtype=str, encoding="latin-1")
estimates.head()

# looking at the column names
print(estimates.columns)

# subsetting estimates for only NC
nc_est = estimates.loc[estimates["STNAME"] == "North Carolina", :]
nc_est.head()

# checking the shapes of both data frames
print(counts.shape)
print(nc_est.shape)

# Removing the row for NC totals
nc_est2 = nc_est.loc[nc_est.loc[:, "CTYNAME"] != "North Carolina", :]
nc_est2.head()

# checking the shapes of both data frames again
print(counts.shape)
print(nc_est2.shape)

# create classification for components of change
nc_est2.loc[:, "total_births"] = (
    nc_est2.filter(regex="BIRTHS....").astype(int).sum(axis=1)
)
nc_est2.loc[:, "total_deaths"] = (
    nc_est2.filter(regex="DEATHS....").astype(int).sum(axis=1)
)
nc_est2["nat_inc"] = nc_est2["total_births"] - nc_est2["total_deaths"]

nc_est2.loc[:, "net_migration"] = (
    nc_est2.filter(regex="^NETMIG....").astype(int).sum(axis=1).copy()
)

nc_est2["comp_change_cat"] = ""
nc_est2.loc[
    (nc_est2["nat_inc"] > 0) & (nc_est2["net_migration"] > 0), "comp_change_cat"
] = "Natural Increase/Net In-Migration"
nc_est2.loc[
    (nc_est2["nat_inc"] > 0) & (nc_est2["net_migration"] < 0), "comp_change_cat"
] = "Natural Increase/Net Out-Migration"
nc_est2.loc[
    (nc_est2["nat_inc"] < 0) & (nc_est2["net_migration"] > 0), "comp_change_cat"
] = "Natural Decrease/Net In-Migration"
nc_est2.loc[
    (nc_est2["nat_inc"] < 0) & (nc_est2["net_migration"] < 0), "comp_change_cat"
] = "Natural Decrease/Net Out-Migration"

# Removing all unnecessary columns
nc_est2 = nc_est2[
    [
        "POPESTIMATE2020",
        "CENSUS2010POP",
        "comp_change_cat",
        "BIRTHS2020",
        "DEATHS2020",
        "NATURALINC2020",
        "INTERNATIONALMIG2020",
        "DOMESTICMIG2020",
        "COUNTY",
        "POPESTIMATE2010",
    ]
]


# changing the county fips title in estimate data
nc_est2.columns = nc_est2.columns.str.replace(
    "COUNTY",
    "county_fips",
)
nc_est2.head()

# merging the two dataframes based on county fips code
all_pop_data = pd.merge(counts, nc_est2)
all_pop_data.head()

# checking the size of the dataframe
print(all_pop_data.shape)

# making pop estimates to ints
all_pop_data["POPESTIMATE2020"] = all_pop_data["POPESTIMATE2020"].astype("float")
all_pop_data["POPESTIMATE2010"] = all_pop_data["POPESTIMATE2010"].astype("float")
all_pop_data["pop_count"] = all_pop_data["pop_count"].astype("float")

# creating over and undercount calculations
all_pop_data["error"] = all_pop_data["pop_count"] - all_pop_data["POPESTIMATE2020"]
all_pop_data.head()

# Rearranging the order of the columns
pop_change = all_pop_data.pop("POPESTIMATE2020")
all_pop_data.insert(2, "POPESTIMATE2020", pop_change)

# making a column for the population difference absolute value
all_pop_data["abs_error"] = abs(all_pop_data["error"])
all_pop_data.head()

# creating categorical columns for over counts and undercounts
all_pop_data["overcount"] = np.where(all_pop_data["error"] > 0, 1, 0)
all_pop_data["undercount"] = np.where(all_pop_data["error"] < 0, 1, 0)
all_pop_data.head()

# changing the columns positions
overcount_change = all_pop_data.pop("overcount")
all_pop_data.insert(3, "overcount", overcount_change)

undercount_change = all_pop_data.pop("undercount")
all_pop_data.insert(4, "undercount", undercount_change)
all_pop_data.head()

pop_diffs_change = all_pop_data.pop("error")
all_pop_data.insert(5, "error", pop_diffs_change)
all_pop_data.head()

# changing the column position
pop_diffs_abs_change = all_pop_data.pop("abs_error")
all_pop_data.insert(6, "abs_error", pop_diffs_abs_change)
all_pop_data.head()

# getting descriptive statistics
print(all_pop_data["error"].describe())

# calculating percent change
all_pop_data["percent_error"] = (
    (all_pop_data["pop_count"] - all_pop_data["POPESTIMATE2020"])
    / (all_pop_data["POPESTIMATE2020"])
) * 100
all_pop_data["abs_percent_error"] = (
    (abs(all_pop_data["pop_count"] - all_pop_data["POPESTIMATE2020"]))
    / (all_pop_data["POPESTIMATE2020"])
) * 100

# changing the column position of percent change
per_change = all_pop_data.pop("percent_error")
all_pop_data.insert(7, "percent_error", per_change)
all_pop_data.head()

abs_per_change = all_pop_data.pop("abs_percent_error")
all_pop_data.insert(8, "abs_percent_error", abs_per_change)
all_pop_data.head()

# getting descriptive stats of percent change
print(all_pop_data["percent_error"].describe())

# seeing if any have a diff of 0
correct_counts = all_pop_data[all_pop_data["percent_error"] == 0]
correct_counts

# flagging differences over/under 5%
all_pop_data["overcount_5_prc"] = np.where(all_pop_data["percent_error"] > 5, 1, 0)
all_pop_data["undercount_5_prc"] = np.where(all_pop_data["percent_error"] < -5, 1, 0)

# changing column indexes
overcount_5_prc_change = all_pop_data.pop("overcount_5_prc")
all_pop_data.insert(7, "overcount_5_prc", overcount_5_prc_change)

undercount_5_prc_change = all_pop_data.pop("undercount_5_prc")
all_pop_data.insert(8, "undercount_5_prc", undercount_5_prc_change)
all_pop_data.head()

# flagging differences over/under 10%
all_pop_data["overcount_10_prc"] = np.where(all_pop_data["percent_error"] > 10, 1, 0)
all_pop_data["undercount_10_prc"] = np.where(all_pop_data["percent_error"] < -10, 1, 0)

# changing column indexe10
overcount_10_prc_change = all_pop_data.pop("overcount_10_prc")
all_pop_data.insert(9, "overcount_10_prc", overcount_10_prc_change)

undercount_10_prc_change = all_pop_data.pop("undercount_10_prc")
all_pop_data.insert(10, "undercount_10_prc", undercount_10_prc_change)
all_pop_data.head(20)

# seeing how many have an over/under count of 5%
under_5_subset = all_pop_data[all_pop_data["undercount_5_prc"] == 1]
print("Number of counties with an undercount greater than 5%:", len(under_5_subset))

over_5_subset = all_pop_data[all_pop_data["overcount_5_prc"] == 1]
print("Number of counties with an overcount greater than 5%:", len(over_5_subset))

# seeing how many have an over/under count of 10%
under_10_subset = all_pop_data[all_pop_data["undercount_10_prc"] == 1]
print("Number of counties with an undercount greater than 10%:", len(under_10_subset))

over_10_subset = all_pop_data[all_pop_data["overcount_10_prc"] == 1]
print("Number of counties with an overcount greater than 10%:", len(over_10_subset))

# Calculating annual growth rate
all_pop_data["annual_growth_rate"] = (
    all_pop_data["POPESTIMATE2020"]
    - all_pop_data["POPESTIMATE2010"] / all_pop_data["POPESTIMATE2010"]
) / 10

# changing the location of growth rate
annual_growth_rate_change = all_pop_data.pop("annual_growth_rate")
all_pop_data.insert(11, "annual_growth_rate", annual_growth_rate_change)
all_pop_data.head()

# removing 2010 estimate column
all_pop_data = all_pop_data.drop("POPESTIMATE2010", axis=1)
all_pop_data.head()

# reading in geo data and merging with population data
# saving the data in a new folder
path3 = Path(PARENT).parent / "../05_intermediate_data"
all_pop_data.to_csv(path3 / "cleaned_all_pop_data.csv")

# reading in geo data and merging with population data

gdf = gpd.read_file("../00_source_data/cb_2018_us_county_20m")
nc_county = gdf[gdf["STATEFP"] == "37"]
temp = all_pop_data[["county_fips", "percent_error"]]
final_graph = nc_county.merge(
    temp, left_on="COUNTYFP", right_on="county_fips", how="inner"
)

# creating plot
vmin, vmax, vcenter = (
    final_graph.percent_error.min(),
    final_graph.percent_error.max(),
    0,
)
# norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
cmap = "RdBu"
# cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
fig, ax = plt.subplots(1, 1, figsize=(10, 20))
final_graph.plot(
    column="percent_error",
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
ax.set_title(label="% Change in Population between 2020 Census  and Estimates", size=15)
# fig.colorbar(cbar, shrink = 0.15, extend = "both")
# cx.add_basemap(ax)
fig.savefig("../50_results/images/county_changes.png", bbox_inches="tight", dpi=400)
