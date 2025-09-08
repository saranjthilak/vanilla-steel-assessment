import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from src.ablation_analysis import engineer_features, normalize_grade_keys

def cluster_rfqs(rfq_file, reference_file, output_dir="outputs", n_clusters=4):
    print("Loading RFQ and reference data...")
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep="\t")

    # Normalize grades
    rfqs["grade_normalized"] = rfqs["grade"].apply(normalize_grade_keys)
    references["grade_normalized"] = references["Grade/Material"].apply(normalize_grade_keys)

    # Merge reference properties
    merged_df = rfqs.merge(references, on="grade_normalized", how="left", suffixes=("", "_ref"))

    print("Engineering features...")
    feature_df = engineer_features(merged_df)

    # Select numeric + categorical
    num_cols = [c for c in feature_df.columns if c.endswith("_min") or c.endswith("_max") or c.endswith("_mid")]
    dim_cols = ["thickness_min", "thickness_max", "width_min", "width_max", "weight_min", "weight_max"]
    cat_cols = ["coating", "finish", "form", "surface_type"]

    # Encode features
    num_matrix = feature_df[num_cols + dim_cols].fillna(0).values
    num_matrix = MinMaxScaler().fit_transform(num_matrix)
    cat_matrix = pd.get_dummies(feature_df[cat_cols].fillna("unknown")).values

    # Combine numeric + categorical
    X = pd.DataFrame(
        MinMaxScaler().fit_transform(
            pd.concat([pd.DataFrame(num_matrix), pd.DataFrame(cat_matrix)], axis=1)
        )
    )

    print(f"Clustering into {n_clusters} families...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    feature_df["cluster"] = kmeans.fit_predict(X)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "rfq_clusters.csv")
    feature_df[["id", "cluster"]].to_csv(out_path, index=False)
    print(f"[✓] Saved clustering results to {out_path}\n")

    # -------------------------
    # Insights
    # -------------------------
    print("Generating cluster insights...\n")

    # 1. Cluster sizes
    cluster_counts = feature_df['cluster'].value_counts().sort_index()
    print("Number of RFQs per cluster:")
    print(cluster_counts, "\n")

    # 2. Average numeric features per cluster
    cluster_avg = feature_df.groupby('cluster')[num_cols + dim_cols].mean()
    print("Average numeric features per cluster:")
    print(cluster_avg, "\n")

    return feature_df
