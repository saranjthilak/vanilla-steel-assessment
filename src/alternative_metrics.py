# src/alternative_metrics.py
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# Utility functions
# -------------------------------
def normalize_grade_keys(grade_str):
    if pd.isna(grade_str) or grade_str == '':
        return None
    grade = str(grade_str).upper().strip()
    grade = grade.replace('STEEL', '').replace('GRADE','').replace(' ','').replace('_','').replace('-','')
    return grade

def parse_range_value(value_str):
    if pd.isna(value_str) or value_str in ['', '-']:
        return None, None, None
    value_str = str(value_str).strip()
    if '–' in value_str or '-' in value_str:
        parts = value_str.replace('–','-').split('-')
        if len(parts) == 2:
            try:
                min_val = float(''.join(c for c in parts[0] if c.isdigit() or c=='.'))
                max_val = float(''.join(c for c in parts[1] if c.isdigit() or c=='.'))
                return min_val, max_val, (min_val+max_val)/2
            except:
                pass
    try:
        val = float(''.join(c for c in value_str if c.isdigit() or c=='.'))
        return val, val, val
    except:
        return None, None, None

def engineer_features(df):
    feature_df = df.copy()

    # Parse dimensions
    dim_cols = ['thickness_min','thickness_max','width_min','width_max','weight_min','weight_max']
    for col in dim_cols:
        if col in feature_df.columns:
            feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce')

    # Fill missing min/max if only one exists
    for min_col, max_col in [('thickness_min','thickness_max'),
                             ('width_min','width_max'),
                             ('weight_min','weight_max')]:
        if min_col in feature_df.columns and max_col in feature_df.columns:
            mask = feature_df[max_col].isna() & feature_df[min_col].notna()
            feature_df.loc[mask, max_col] = feature_df.loc[mask, min_col]
            mask = feature_df[min_col].isna() & feature_df[max_col].notna()
            feature_df.loc[mask, min_col] = feature_df.loc[mask, max_col]

    # Parse grade properties
    grade_cols = ['Carbon (C)','Manganese (Mn)','Silicon (Si)',
                  'Tensile strength (Rm)','Yield strength (Re or Rp0.2)']
    for col in grade_cols:
        if col in feature_df.columns:
            parsed = feature_df[col].apply(parse_range_value)
            feature_df[f'{col}_min'] = [x[0] for x in parsed]
            feature_df[f'{col}_max'] = [x[1] for x in parsed]
            feature_df[f'{col}_mid'] = [x[2] for x in parsed]

    # Normalize categorical
    cat_cols = ['coating','finish','form','surface_type']
    for col in cat_cols:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].fillna('unknown').str.lower()

    return feature_df

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
        return 0
    overlap = max(0, min(max1, max2) - max(min1, min2))
    union = max(max1, max2) - min(min1, min2)
    return overlap / union if union > 0 else 0

def cosine_numeric_similarity(df, cols):
    matrix = df[cols].fillna(0).values
    matrix = MinMaxScaler().fit_transform(matrix)
    return cosine_similarity(matrix)

def hybrid_similarity(feature_df, top_n=3, weights=None):
    if weights is None:
        weights = {'dimensional':0.4,'grade':0.3,'categorical':0.3}

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

            # Categorical Jaccard
            cat_cols = ['coating','finish','form','surface_type']
            jaccards = []
            for c in cat_cols:
                jaccards.append(1.0 if rfq[c] == item[c] else 0.0)
            cat_jacc = np.mean(jaccards)

            # Weighted hybrid
            score = (weights['dimensional']*dim_iou +
                     weights['grade']*grade_cos +
                     weights['categorical']*cat_jacc)

            sims.append((item['id'], score))

        top_matches = sorted(sims, key=lambda x: x[1], reverse=True)[:top_n]
        for match_id, score in top_matches:
            results.append({'rfq_id': rfq['id'], 'match_id': match_id, 'similarity_score': score})

    return pd.DataFrame(results)

# -------------------------------
# Run comparison
# -------------------------------
def main():
    rfq_file = "data/rfq.csv"
    reference_file = "data/reference_properties.tsv"
    inventory_file = "outputs/inventory_dataset.csv"
    output_dir = "outputs"

    print("Loading data...")
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep='\t')
    inventory = pd.read_csv(inventory_file)

    rfqs['grade_normalized'] = rfqs['grade'].apply(normalize_grade_keys)
    references['grade_normalized'] = references['Grade/Material'].apply(normalize_grade_keys)

    merged_df = rfqs.merge(references, on='grade_normalized', how='left', suffixes=('','_ref'))

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

if __name__ == "__main__":
    main()
