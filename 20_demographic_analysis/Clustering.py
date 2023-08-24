# %%
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer

# reading in the data
merged_df = pd.read_csv("../05_intermediate_data/merged_pop_data_revised.csv")
merged_df["over_65"] = (
    merged_df["85_plus_pop"] + merged_df["65-74_pop"] + merged_df["75-84_pop"]
)

merged_df["under_20"] = (
    merged_df["0-5_pop"]
    + merged_df["5-9_pop"]
    + merged_df["10-14_pop"]
    + merged_df["15-19_pop"]
)
merged_df["norm_unocc"] = merged_df["unocc_housing"] / merged_df["total_housing"]
merged_df.columns

dict = {
    "Percent of adults with less than a high school diploma, 2016-20": "lessthanHSdiploma",
    "Percent of adults with a high school diploma only, 2016-20": "HSdiploma",
    "Percent of adults completing some college or associate's degree, 2016-20": "SomeCollege",
    "Percent of adults with a bachelor's degree or higher 2016-20": "College",
}

# call rename () method
merged_df.rename(columns=dict, inplace=True)


# %%
features_to_use = [
    "POPESTIMATE2020",
    "over_65",
    "under_20",
    "norm_unocc",
    "total_housing",
    "occ_housing",
    "unocc_housing",
    "total_group",
    "total_inst",
    "adult_jail",
    "juvenille_jail",
    "nursing_homes",
    "other_inst",
    "non_inst_total",
    "college_housing",
    "military_housing",
    "BIRTHS2020",
    "DEATHS2020",
    "NATURALINC2020",
    "INTERNATIONALMIG2020",
    "DOMESTICMIG2020",
    "fatalityCount",
    "white_pop",
    "black_pop",
    "ai_an_pop",
    "asian_pop",
    "black_w_other_race_pop",
    "hisp_any_race_pop",
    "male_pop",
    "female_pop",
    "farm_man",
    "recreation",
    "retirement_metro",
    "retirement_non_metro",
    "PCTPOVALL_2020",
    "POV017_2020",
    "MEDHHINC_2020",
    "Unemployed_2019",
    "Employed_2019",
    "Civilian_labor_force_2019",
    "lessthanHSdiploma",
    "HSdiploma",
    "SomeCollege",
    "College",
]

# %%
# Separating out the features
# x = merged_df.loc[:, features_to_use].values
df = merged_df.loc[:, features_to_use]
cor_matrix = df.corr().abs()
upper_tri = cor_matrix.where(np.triu(np.ones(cor_matrix.shape), k=1).astype(bool))
to_drop = [
    column for column in upper_tri.columns if any(upper_tri[column] > 0.95)
]  # removing highly correlated features
df1 = df.drop(to_drop, axis=1)

# %%

# Standardizing the features
# x = StandardScaler().fit_transform(x)

from sklearn.preprocessing import Normalizer

x = df1.values
# x = StandardScaler().fit_transform(x)
transformer = Normalizer().fit(x)
x = transformer.transform(x)

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# spectral clustering
from sklearn.cluster import SpectralClustering

# function for K Means Clustering
def Cluster_fct(numb_cl, x_values, type):
    """numb_cl is the number of clusters, x_values is the data being clustered,
    and type is the type of clustering being used"""
    # creating clusters
    if type == "K_Means":
        labels = KMeans(n_clusters=numb_cl, random_state=30).fit_predict(x_values)
    if type == "Spectral":
        labels = SpectralClustering(
            n_clusters=numb_cl, assign_labels="discretize", random_state=0
        ).fit_predict(x_values)
    # combing original df with cluster labels
    cluster_lbls = pd.DataFrame(labels)
    cluster_lbls2 = cluster_lbls.rename({0: "Clusters"}, axis="columns")
    # merging cluster labels with original df
    df_withKMclusters = pd.concat([merged_df, cluster_lbls2], axis=1)

    # looping thorugh all of the clusters
    for cluster_nb in range(0, numb_cl):
        # fliered data for only one cluster
        filtered_label = df_withKMclusters[df_withKMclusters["Clusters"] == cluster_nb]
        # printing means
        print(
            type,
            "Cluster",
            cluster_nb,
            "Absolute Percent Error: ",
            round(filtered_label["abs_percent_error"].mean(), 2),
        )

        print(
            type,
            "Cluster",
            cluster_nb,
            "Percent Error: ",
            round(filtered_label["percent_error"].mean(), 2),
        )
    return df_withKMclusters


## KMeans Clusters

# getting values for 2 clusters
cluster2_df = Cluster_fct(2, x, "K_Means")
# getting values for 3 clusters
cluster3_df = Cluster_fct(3, x, "K_Means")
# getting values for 4 clusters
cluster4_df = Cluster_fct(4, x, "K_Means")
# getting values for 5 clusters
cluster5_df = Cluster_fct(5, x, "K_Means")
# getting values for  clusters
cluster6_df = Cluster_fct(6, x, "K_Means")

# saving cluster dfs
from pathlib import Path

PARENT = "carolina-demography"
path = Path(PARENT).parent / "../05_intermediate_data"
cluster2_df.to_csv(path / "tableau_data_cluster2.csv")
cluster3_df.to_csv(path / "tableau_data_cluster3.csv")
cluster4_df.to_csv(path / "tableau_data_cluster4.csv")
cluster5_df.to_csv(path / "tableau_data_cluster5.csv")
cluster6_df.to_csv(path / "tableau_data_cluster6.csv")

# %%
import geopandas as gpd

gdf = gpd.read_file("../00_source_data/cb_2018_us_county_20m")
gdf = gdf[gdf["STATEFP"] == "37"]
gdf["FIPS"] = ("37" + gdf.COUNTYFP).astype(int)
cluster_geo = gdf.merge(
    cluster3_df, how="left", validate="1:1", left_on="FIPS", right_on="FIPS"
)
assert cluster_geo.shape[0] == 100

# import matplotlib.colors as colors
min_val, max_val = 0.3, 1.0
n = 10
orig_cmap = plt.cm.Blues
colors = orig_cmap(np.linspace(min_val, max_val, n))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", colors)

# import matplotlib.colors as colors
cluster_geo["label"] = "Cluster " + ((cluster_geo["Clusters"] + 1).astype(str))
# color_dict = {'0':'blue', '1':'purple', '2':'teal'}
fig, ax = plt.subplots(1, 1, figsize=(10, 20))
cluster_geo.plot(
    column="label",
    # cmap="Blues",
    legend=True,
    legend_kwds={"loc": "lower right"},
    # cmap=colors.ListedColormap(list(color_dict.values())),
    cmap=cmap,
    alpha=0.8,
    edgecolor="#808080",
    linewidth=0.6,
    ax=ax,
)
ax.set_axis_off()
ax.set_title(label="Counties by Cluster label ", size=15)
plt.show()


#%%
cluster3_df.groupby("Clusters")["percent_error"].mean()

# %%
import statsmodels.api as sm

X = df1
X = sm.add_constant(X)
y = merged_df.percent_error
model = sm.OLS(y, X).fit()
predictions = model.predict(X)
print_model = model.summary()
print(print_model)
# sigf: juvenille_jail, unocc_housing, retirement_metro, retirement_non_metro, PCTPOVALL_2020, MEDHHINC_2020
# adjr2: 0.44
# %%
cluster3_df["juvenilejail_norm"] = (
    cluster3_df["juvenille_jail"] / cluster3_df["POPESTIMATE2020"]
)
# retirement_non_metro
cluster3_df["PCTPOVALL_2020_norm"] = (
    cluster3_df["PCTPOVALL_2020"] / cluster3_df["POPESTIMATE2020"]
)
cluster3_df["fatalityCount_norm"] = (
    cluster3_df["fatalityCount"] / cluster3_df["POPESTIMATE2020"]
)
cluster3_df["black_pop_norm"] = (
    cluster3_df["black_pop"] / cluster3_df["POPESTIMATE2020"]
)
cluster3_df["Unemployed_2019_norm"] = (
    cluster3_df["Unemployed_2019"] / cluster3_df["POPESTIMATE2020"]
)


# %%
import seaborn as sns

for i in [
    "juvenilejail_norm",
    "PCTPOVALL_2020_norm",
    "MEDHHINC_2020",
    "fatalityCount_norm",
    "black_pop_norm",
    "Unemployed_2019_norm",
    "retirement_non_metro",
    "POPESTIMATE2020",
]:
    print("*" * 70)
    print(i)
    ax = sns.boxplot(
        x=cluster3_df.Clusters, y=cluster3_df[i], data=cluster3_df, color="#99c2a2"
    )
    plt.show()
    print(cluster3_df.groupby("Clusters")[i].mean())
