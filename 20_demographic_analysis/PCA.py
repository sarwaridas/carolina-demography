# %%
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import Normalizer
import seaborn as sns

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

dict = {
    "Percent of adults with less than a high school diploma, 2016-20": "lessthanHSdiploma",
    "Percent of adults with a high school diploma only, 2016-20": "HSdiploma",
    "Percent of adults completing some college or associate's degree, 2016-20": "SomeCollege",
    "Percent of adults with a bachelor's degree or higher 2016-20": "College",
}

# call rename () method
merged_df.rename(columns=dict, inplace=True)


# %%
features_to_norm = [
    "over_65",
    "under_20",
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
    "Unemployed_2019",
    # "Employed_2019",
    "Civilian_labor_force_2019",
]

features_to_not_norm = [
    "norm_unocc",
    "farm_man",
    "recreation",
    "retirement_metro",
    "retirement_non_metro",
    "PCTPOVALL_2020",
    "POV017_2020",
    "lessthanHSdiploma",
    "HSdiploma",
    "SomeCollege",
    "College",
    "total_housing",
    "occ_housing",
    "unocc_housing",
    "MEDHHINC_2020",
]
# %%
# Separating out the features
x_norm = merged_df.loc[:, features_to_norm]
x_norm = x_norm.div(merged_df.POPESTIMATE2020, axis=0)
x_not_normed = merged_df.loc[:, features_to_not_norm]
x_df = pd.concat([x_norm, x_not_normed], axis=1)
x = x_df.values

# %%
# Exploring correlations
# sns.heatmap(x_df, annot=True)
x_df.corr().unstack().sort_values(ascending=False).drop_duplicates()

# %%

# Standardizing the features
from sklearn.preprocessing import StandardScaler

x = StandardScaler().fit_transform(x)
y = merged_df.percent_error

# %%

# apply pca
pca = PCA(n_components=42)
principalComponents = pca.fit_transform(x)
# principalDf = pd.DataFrame(
#     data=principalComponents, columns=["principal component 1", "principal component 2"]
# )

# %%
import matplotlib.pyplot as plt

t = 90

fraction_variance_explained = np.cumsum(pca.explained_variance_) / np.sum(
    pca.explained_variance_
)
n_pcs = np.arange(1, len(fraction_variance_explained) + 1)
plt.figure(figsize=(12, 8))
plt.plot(n_pcs, fraction_variance_explained, "k.-")
plt.title("Fraction of variance explained over PCA components", size=14)
plt.xlabel("Number of principal components")
plt.ylabel("Fraction of variance explained")
plt.axis([0, n_pcs[-1], 0, 1.05])
plt.yticks(np.linspace(0, 1, 11))
plt.grid(True)
plt.show()


# %%
variance_unexplained = 1 - fraction_variance_explained[1]
print(variance_unexplained)

# %%
# Principal components correlation coefficients
loadings = pca.components_

# Number of features before PCA
n_features = pca.n_features_

# Feature names before PCA
feature_names = x_df.columns

# PC names
pc_list = [f"PC{i}" for i in list(range(1, n_features + 1))]

# # Match PC names to loadings
pc_loadings = {k: v for k, v in zip(pc_list, loadings)}

# # Matrix of corr coefs between feature names and PCs
loadings_df = pd.DataFrame.from_dict(pc_loadings)
loadings_df["feature_names"] = feature_names
loadings_df = loadings_df.set_index("feature_names")
# loadings_df.iloc[:, :2]
print("Top 10 in Component 1 disregarding relationship:")
print(loadings_df.PC1.abs().sort_values(ascending=False)[:10])

# %%
import matplotlib.pyplot as plt

plt.style.use("seaborn-white")
plt.figure(figsize=(12, 8))
plt.scatter(x[:, 0], x[:, 1], s=40, c=y, cmap="magma")
plt.title("Linear trend: PCA Component 1 vs Component 2", size=20)
plt.yticks(fontsize=20)
plt.xticks(fontsize=20)
plt.colorbar()
plt.show()

# %%
# define cross validation method
from sklearn import model_selection
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

X_reduced = x
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

regr = LinearRegression()
mse = []
# Calculate MSE with only the intercept
score = (
    -1
    * model_selection.cross_val_score(
        regr, np.ones((len(X_reduced), 1)), y, cv=cv, scoring="neg_mean_squared_error"
    ).mean()
)
mse.append(score)

# Calculate MSE using cross-validation, adding one component at a time
for i in np.arange(1, 6):
    score = (
        -1
        * model_selection.cross_val_score(
            regr, X_reduced[:, :i], y, cv=cv, scoring="neg_mean_squared_error"
        ).mean()
    )
    mse.append(score)

# Plot cross-validation results
plt.figure(figsize=(12, 8))
plt.plot(mse)
plt.xlabel("Number of Principal Components", size=16)
plt.ylabel("MSE", size=16)
plt.title("Seems like first two components are enough to model error", size=16)
# %%

## Clustering
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


# %%
## KMeans Clusters
# getting values for clusters
for i in [2, 3, 4, 5]:
    print(f"Number of K_means clusters:{i}")
    Cluster_fct(i, x, "K_Means")
    print("-" * 20)

# %%
## Spectral Clusters
for i in [2, 3, 4, 5]:
    print(f"Number of Spectral clusters:{i}")
    Cluster_fct(i, x, "Spectral")
    print("-" * 20)
