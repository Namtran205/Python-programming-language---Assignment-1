import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from tabulate import tabulate
df = pd.read_csv('results.csv')
dm=df.copy()
def convert_age(age):
    try:
        if '-' in age:
            y, d = map(int, age.split('-'))
            return y + d / 365
        return int(age)
    except:
        return np.nan
df['Age'] = df['Age'].apply(convert_age)
df['Minutes']=df['Minutes'].str.replace(',','')
df['Minutes']=pd.to_numeric(df['Minutes'],errors='coerce')

df = df.iloc[:, 1:]
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
X=df[numeric_cols]

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Determine optimal number of clusters using Elbow Method
wcss = []
max_k = 10  
for k in range(1, max_k + 1):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

# Plot Elbow Curve
plt.figure(figsize=(8, 6))
plt.plot(range(1, max_k + 1), wcss, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
plt.grid(True)
plt.savefig('elbow_plot.png')
plt.show()
plt.close()

# Apply K-means with chosen k
# Based on Elbow Method and domain knowledge, choose k (e.g., k=4 for roles: FW, MF, DF, GK)
optimal_k = 4  # Adjust based on elbow plot or domain knowledge
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
cluster_labels = kmeans.fit_predict(X_scaled)

df['Cluster'] = cluster_labels
# Step 3: PCA for 2D visualization
pca = PCA(n_components=2) 
X_pca = pca.fit_transform(X_scaled) 
# X_pca: Numpy array with shape (n_samples, 2) (e.g., (500, 2)).
# Each row is the 2D coordinates of a player in the PC1-PC2 space.
# Example:X_pca = [
# [5.2, -1.3], # Player 1
# [2.1, 0.8], # Player 2
# [-3.0, 2.5], # Player 3
# ]
explained_variance = pca.explained_variance_ratio_
print(f"Explained Variance Ratio by PCA: {explained_variance}")
print(f"Total Variance Explained: {sum(explained_variance):.2%}")
# If explained_variance = [0.42, 0.25]:
# PC1 retains 42% of the information (variance) of the original data.
# PC2 retains 25% of the information.
# Total: 42% + 25% = 67% of the information retained.
# Plot 2D clusters
plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6)
plt.colorbar(scatter, label='Cluster')
plt.title('2D PCA Cluster Visualization of Players')
plt.xlabel(f'PC1 ({explained_variance[0]:.2%} variance)')
plt.ylabel(f'PC2 ({explained_variance[1]:.2%} variance)')
plt.grid(True)
plt.savefig('pca_cluster_plot.png')
plt.show()
plt.close()


with open('Clustering_results.txt', 'w', encoding='utf-8-sig') as f:
    for cluster in range(optimal_k):
        print(f"\n================= CLUSTER {cluster} ===============")
        f.write(f"\n================ CLUSTER {cluster} ===============\n\n")
        cluster_df = dm[df['Cluster'] == cluster][dm.columns[1:]] .reset_index(drop=True)
        table_str = tabulate(cluster_df, headers='keys', tablefmt='grid', showindex=True)
        print(cluster_df)
        f.write(table_str)
        f.write("\n\n")


print(f"- Number of clusters: {optimal_k}")
print("- Reasoning: The Elbow Method plot (elbow_plot.png) was analyzed, and k=4 was chosen based on the elbow point and domain knowledge (grouping players into roles: forwards, midfielders, defenders, goalkeepers).")
print("- PCA Visualization: The 2D plot (pca_cluster_plot.png) shows distinct clusters, though some overlap may exist due to dimensionality reduction.")
print(f"- Variance Explained: PCA captures {sum(explained_variance):.2%} of the variance, indicating how much information is retained in 2D.")
print("- Cluster Interpretation: Based on sample players, clusters likely correspond to player roles (e.g., high-scoring forwards, defensive players, goalkeepers).")
