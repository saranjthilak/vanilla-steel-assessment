import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------
# Helper functions
# -------------------------

# Handels missing data and extract only relevant parts of the grade strings
def normalize_grade_keys(grade_str):
    if pd.isna(grade_str) or grade_str == '':
        return None
    grade = str(grade_str).upper().strip()
    grade = grade.replace('STEEL', '').replace('GRADE','').replace(' ','').replace('_','').replace('-','')
    return grade

# value_str can be a single value or a range (e.g., "0.20-0.25") and returns (min, max, mid)
def parse_range_value(value_str):
    if pd.isna(value_str) or value_str in ['', '-']:
        return None, None, None

    value_str = str(value_str).strip()

    if '-' in value_str:
        parts = value_str.split('-')
        if len(parts) == 2:
            try:
                min_val = float(''.join(c for c in parts[0] if c.isdigit() or c=='.'))
                max_val = float(''.join(c for c in parts[1] if c.isdigit() or c=='.'))
                return min_val, max_val, (min_val + max_val) / 2
            except:
                pass

    try:
        val = float(''.join(c for c in value_str if c.isdigit() or c == '.'))
        return val, val, val
    except:
        return None, None, None
# Numeric conversion of dimensions and grades, handling missing data, categorical normalization
def engineer_features(df):
    feature_df = df.copy()
    dim_cols = ['thickness_min','thickness_max','width_min','width_max','weight_min','weight_max']
    for col in dim_cols:
        if col in feature_df.columns:
            feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce')
    for min_col, max_col in [('thickness_min','thickness_max'),('width_min','width_max'),('weight_min','weight_max')]:
        if min_col in feature_df.columns and max_col in feature_df.columns:
            mask = feature_df[max_col].isna() & feature_df[min_col].notna()
            feature_df.loc[mask, max_col] = feature_df.loc[mask, min_col]
            mask = feature_df[min_col].isna() & feature_df[max_col].notna()
            feature_df.loc[mask, min_col] = feature_df.loc[mask, max_col]
    grade_cols = ['Carbon (C)','Manganese (Mn)','Silicon (Si)','Tensile strength','Yield strength']
    for col in grade_cols:
        if col in feature_df.columns:
            parsed = feature_df[col].apply(parse_range_value)
            feature_df[f'{col}_min'] = [x[0] for x in parsed]
            feature_df[f'{col}_max'] = [x[1] for x in parsed]
            feature_df[f'{col}_mid'] = [x[2] for x in parsed]
    cat_cols = ['coating','finish','form','surface_type','surface_protection']
    for col in cat_cols:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].fillna('unknown').str.lower()
    return feature_df
# computig weighted cosine similarity for different feature sets
def vectorized_similarity(feature_df, top_n=3, weights=None, use_features=None):
    if weights is None:
        weights = {'dimensional':0.4,'grade_properties':0.3,'categorical':0.3}
    if use_features is None:
        use_features = ['dimensional','grade_properties','categorical']

    df = feature_df.copy()
    n = len(df)
    sim_matrices = {}

    # Dimensional similarity
    if 'dimensional' in use_features:
        dim_cols = ['thickness_min','thickness_max','width_min','width_max','weight_min','weight_max']
        dim_matrix = df[dim_cols].fillna(0).values
        dim_matrix = MinMaxScaler().fit_transform(dim_matrix)
        sim_matrices['dimensional'] = cosine_similarity(dim_matrix)
    else:
        sim_matrices['dimensional'] = np.zeros((n,n))

    # Grade similarity
    if 'grade_properties' in use_features:
        grade_cols = [col for col in df.columns if '_mid' in col]
        grade_matrix = df[grade_cols].fillna(0).values
        grade_matrix = MinMaxScaler().fit_transform(grade_matrix)
        sim_matrices['grade_properties'] = cosine_similarity(grade_matrix)
    else:
        sim_matrices['grade_properties'] = np.zeros((n,n))

    # Categorical similarity
    if 'categorical' in use_features:
        cat_cols = ['coating','finish','form','surface_type','surface_protection']
        cat_matrix = pd.get_dummies(df[cat_cols], dummy_na=True)
        sim_matrices['categorical'] = cosine_similarity(cat_matrix)
    else:
        sim_matrices['categorical'] = np.zeros((n,n))

    # Aggregate similarity
    aggregate_sim = np.zeros((n,n))
    for key in use_features:
        aggregate_sim += sim_matrices[key] * weights.get(key,0)

    np.fill_diagonal(aggregate_sim, 0)

    results = []
    for i, rfq_id in enumerate(df['id']):
        top_indices = aggregate_sim[i].argsort()[::-1][:top_n]
        for idx in top_indices:
            results.append({
                'rfq_id': rfq_id,
                'match_id': df.iloc[idx]['id'],
                'similarity_score': aggregate_sim[i, idx]
            })
    return pd.DataFrame(results)

# -------------------------
# Main compute + average similarity (evaluaates different ablation scenarios)
# -------------------------
def compute_and_report(rfq_file, reference_file, inventory_file, output_dir='outputs', ablation=False):
    print("Loading data...")
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep='\t')
    inventory = pd.read_csv(inventory_file)

    rfqs['grade_normalized'] = rfqs['grade'].apply(normalize_grade_keys)
    references['grade_normalized'] = references['Grade/Material'].apply(normalize_grade_keys)
    merged_df = rfqs.merge(references, on='grade_normalized', how='left', suffixes=('','_ref'))

    feature_df = engineer_features(merged_df)

    scenarios = [
        {'name':'all_features','use_features':['dimensional','grade_properties','categorical'],'weights':{'dimensional':0.4,'grade_properties':0.3,'categorical':0.3}},
        {'name':'dimensions_only','use_features':['dimensional'],'weights':{'dimensional':1.0}},
        {'name':'grade_only','use_features':['grade_properties'],'weights':{'grade_properties':1.0}},
        {'name':'categorical_only','use_features':['categorical'],'weights':{'categorical':1.0}},
        {'name':'adjusted_weights','use_features':['dimensional','grade_properties','categorical'],'weights':{'dimensional':0.5,'grade_properties':0.2,'categorical':0.3}}
    ]

    os.makedirs(output_dir, exist_ok=True)

    avg_scores = {}
    for scenario in scenarios:
        print(f"Calculating top-3 for scenario: {scenario['name']}...")
        top3_df = vectorized_similarity(feature_df, use_features=scenario['use_features'], weights=scenario['weights'])
        out_path = os.path.join(output_dir, f"top3_{scenario['name']}.csv")
        top3_df.to_csv(out_path, index=False)
        avg_scores[scenario['name']] = top3_df['similarity_score'].mean()

    print("\nAverage similarity scores:")
    for s, score in avg_scores.items():
        print(f"{s}: {score:.3f}")

    return avg_scores

# -------------------------
# Run script
# -------------------------
if __name__ == "__main__":
    compute_and_report(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        inventory_file="outputs/inventory_dataset.csv",
        output_dir="outputs",
        ablation=True
    )
