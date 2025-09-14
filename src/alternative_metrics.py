# src/alternative_metrics.py
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.rfq_similarity import engineer_features, normalize_grade_keys
# -------------------------------
# Alternative metrics
# -------------------------------
def jaccard_similarity(set1, set2):
    set1, set2 = set(set1), set(set2)
    if not set1 and not set2:
        return 1.0
    return len(set1 & set2) / len(set1 | set2)

def iou_range(min1, max1, min2, max2):
    if pd.isna(min1) or pd.isna(max1) or pd.isna(min2) or pd.isna(max2):
        return 0.0

    # Calculate overlap and union
    overlap = max(0, min(max1, max2) - max(min1, min2))
    union = max(max1, max2) - min(min1, min2)

    if union <= 0:
        return 0.0

    iou = overlap / union

    # If no overlap, use distance-based fallback
    if iou == 0:
        mid1, mid2 = (min1 + max1) / 2, (min2 + max2) / 2
        return 1 / (1 + abs(mid1 - mid2))  # similarity decays with distance

    return iou


def cosine_numeric_similarity(df, cols):
    matrix = df[cols].fillna(0).values
    matrix = MinMaxScaler().fit_transform(matrix)
    return cosine_similarity(matrix)

def hybrid_similarity(feature_df, top_n=3, weights=None):
    if weights is None:
        weights = {'dimensional': 0.2, 'grade': 0.6, 'categorical': 0.2}

    n = len(feature_df)
    results = []

    # Precompute cosine for grades
    grade_cols = [c for c in feature_df.columns if '_mid' in c]
    grade_sim = cosine_numeric_similarity(feature_df, grade_cols)

    for i, rfq in feature_df.iterrows():
        sims = []
        for j, item in feature_df.iterrows():
            if i == j:
                continue

            # Dimensional IoU
            dim_iou = np.mean([
                iou_range(rfq['thickness_min'], rfq['thickness_max'], item['thickness_min'], item['thickness_max']),
                iou_range(rfq['width_min'], rfq['width_max'], item['width_min'], item['width_max']),
                iou_range(rfq['weight_min'], rfq['weight_max'], item['weight_min'], item['weight_max'])
            ])

            # Grade cosine (from precomputed)
            grade_cos = grade_sim[i, j]

            # Categorical Jaccard (binary same/different)
            cat_cols = ['coating', 'finish', 'form', 'surface_type']
            jaccards = [1.0 if rfq[c] == item[c] else 0.0 for c in cat_cols]
            cat_jacc = np.mean(jaccards)

            # Weighted hybrid
            score = (weights['dimensional'] * dim_iou +
                     weights['grade'] * grade_cos +
                     weights['categorical'] * cat_jacc)

            sims.append((item['id'], score))

        top_matches = sorted(sims, key=lambda x: x[1], reverse=True)[:top_n]
        for match_id, score in top_matches:
            results.append({'rfq_id': rfq['id'], 'match_id': match_id, 'similarity_score': score})

    return pd.DataFrame(results)

# -------------------------------
# Main Scenario C Function
# -------------------------------
def compute_alternative_metrics(rfq_file, reference_file, output_dir="outputs"):
    print("Loading data...")
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep='\t')

    rfqs['grade_normalized'] = rfqs['grade'].apply(normalize_grade_keys)
    references['grade_normalized'] = references['Grade/Material'].apply(normalize_grade_keys)

    merged_df = rfqs.merge(references, on='grade_normalized', how='left', suffixes=('', '_ref'))
    feature_df = engineer_features(merged_df)

    # Baseline cosine similarity
    print("Calculating baseline cosine similarity...")
    from src.rfq_similarity import vectorized_similarity
    baseline_df = vectorized_similarity(feature_df)
    baseline_df.to_csv(os.path.join(output_dir, "top3_baseline.csv"), index=False)

    # Hybrid alternative similarity
    print("Calculating hybrid similarity (Cosine + Jaccard + IoU)...")
    hybrid_df = hybrid_similarity(feature_df)
    hybrid_df.to_csv(os.path.join(output_dir, "top3_hybrid.csv"), index=False)

    # Compare average scores
    print("\nAverage similarity scores:")
    print(f"Baseline (cosine only): {baseline_df['similarity_score'].mean():.3f}")
    print(f"Hybrid (cosine+jaccard+IoU): {hybrid_df['similarity_score'].mean():.3f}")

    return baseline_df, hybrid_df

# -------------------------------
# Script entry point
# -------------------------------
def main():
    compute_alternative_metrics(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        inventory_file="outputs/inventory_dataset.csv",
        output_dir="outputs"
    )

if __name__ == "__main__":
    main()
