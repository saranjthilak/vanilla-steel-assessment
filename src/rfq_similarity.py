import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

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
            except: pass
    try:
        val = float(''.join(c for c in value_str if c.isdigit() or c=='.'))
        return val, val, val
    except:
        return None, None, None

def engineer_features(df):
    feature_df = df.copy()
    # Dimensional columns
    dim_cols = ['thickness_min','thickness_max','width_min','width_max','weight_min','weight_max']
    for col in dim_cols:
        if col in feature_df.columns:
            feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce')

    # Singletons
    for min_col, max_col in [('thickness_min','thickness_max'),('width_min','width_max'),('weight_min','weight_max')]:
        if min_col in feature_df.columns and max_col in feature_df.columns:
            mask = feature_df[max_col].isna() & feature_df[min_col].notna()
            feature_df.loc[mask, max_col] = feature_df.loc[mask, min_col]
            mask = feature_df[min_col].isna() & feature_df[max_col].notna()
            feature_df.loc[mask, min_col] = feature_df.loc[mask, max_col]

    # Grade properties
    grade_cols = ['Carbon (C)','Manganese (Mn)','Silicon (Si)','Tensile strength (Rm)','Yield strength (Re or Rp0.2)']
    for col in grade_cols:
        if col in feature_df.columns:
            parsed = feature_df[col].apply(parse_range_value)
            feature_df[f'{col}_min'] = [x[0] for x in parsed]
            feature_df[f'{col}_max'] = [x[1] for x in parsed]
            feature_df[f'{col}_mid'] = [x[2] for x in parsed]

    # Categorical columns
    cat_cols = ['coating','finish','form','surface_type']
    for col in cat_cols:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].fillna('unknown').str.lower()

    return feature_df

def vectorized_similarity(feature_df, top_n=3):
    df = feature_df.copy()
    n = len(df)

    # Dimensional features
    dim_cols = ['thickness_min','thickness_max','width_min','width_max','weight_min','weight_max']
    dim_matrix = df[dim_cols].fillna(0).values
    dim_matrix = MinMaxScaler().fit_transform(dim_matrix)
    dim_sim = cosine_similarity(dim_matrix)

    # Grade midpoints
    grade_cols = [col for col in df.columns if '_mid' in col]
    grade_matrix = df[grade_cols].fillna(0).values
    grade_matrix = MinMaxScaler().fit_transform(grade_matrix)
    grade_sim = cosine_similarity(grade_matrix)

    # Categorical similarity (one-hot)
    cat_cols = ['coating','finish','form','surface_type']
    cat_matrix = pd.get_dummies(df[cat_cols], dummy_na=True)
    cat_sim = cosine_similarity(cat_matrix)

    # Weighted aggregate
    aggregate_sim = 0.4*dim_sim + 0.3*grade_sim + 0.3*cat_sim
    np.fill_diagonal(aggregate_sim, 0)  # Exclude self

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

def compute_top3(rfq_file, reference_file, inventory_file, output_file='top3.csv', output_dir='outputs'):
    print("Loading RFQ and reference data...")
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep='\t')
    inventory = pd.read_csv(inventory_file)

    # Normalize grades
    rfqs['grade_normalized'] = rfqs['grade'].apply(normalize_grade_keys)
    references['grade_normalized'] = references['Grade/Material'].apply(normalize_grade_keys)

    # Merge
    merged_df = rfqs.merge(references, on='grade_normalized', how='left', suffixes=('','_ref'))

    print("Engineering features...")
    feature_df = engineer_features(merged_df)

    print("Calculating top-3 similarities...")
    top3_df = vectorized_similarity(feature_df)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_file)
    top3_df.to_csv(out_path, index=False)
    print(f"[✓] Saved {out_path}")
    return top3_df
