import os
import pandas as pd
import numpy as np

def compute_top3(rfq_file, reference_file, inventory_file, output_file="top3.csv", output_dir="outputs"):
    """
    Compute top-3 most similar inventory items for each RFQ.
    Handles lowercase column names, normalizes grades/finishes, parses ranges, and calculates similarity.
    """

    # --------------------------
    # Load files
    # --------------------------
    rfqs = pd.read_csv(rfq_file)
    references = pd.read_csv(reference_file, sep="\t")
    inventory = pd.read_csv(inventory_file)

    # Normalize column names
    rfqs.columns = rfqs.columns.str.strip().str.lower()
    inventory.columns = inventory.columns.str.strip().str.lower()
    references.columns = references.columns.str.strip().str.lower()

    # --------------------------
    # Normalize grades & finishes
    # --------------------------
    rfqs["grade_norm"] = rfqs["grade"].str.upper().str.strip()
    rfqs["finish_norm"] = rfqs["finish"].str.upper().str.strip()
    inventory["grade_norm"] = inventory["grade"].astype(str).str.upper().str.strip()
    inventory["finish_norm"] = inventory["finish"].astype(str).str.upper().str.strip()
    if "grade" in references.columns:
        references["grade_norm"] = references["grade"].str.upper().str.strip()
    else:
        references["grade_norm"] = None

    # --------------------------
    # Handle grade aliases (optional)
    # --------------------------
    grade_aliases = {
        # Add more aliases as needed
        "S235J0": "S235JR",
        "S235J2": "S235JR",
    }
    rfqs["grade_norm"] = rfqs["grade_norm"].map(lambda x: grade_aliases.get(x, x))
    inventory["grade_norm"] = inventory["grade_norm"].map(lambda x: grade_aliases.get(x, x))

    # --------------------------
    # Merge reference properties
    # --------------------------
    inventory = inventory.merge(references, on="grade_norm", how="left")

    # --------------------------
    # Parse numeric ranges (min/max)
    # --------------------------
    def parse_range(val):
        if pd.isna(val):
            return np.nan, np.nan
        val = str(val).replace(" ", "")
        if '-' in val:
            parts = val.split('-')
            return float(parts[0]), float(parts[1])
        else:
            v = float(val)
            return v, v

    for dim_min, dim_max in [("thickness_min", "thickness_max"),
                             ("width_min", "width_max"),
                             ("weight_min", "weight_max")]:
        if dim_min in rfqs.columns and dim_max in rfqs.columns:
            rfqs[dim_min+"_num"], rfqs[dim_max+"_num"] = zip(*rfqs.apply(lambda x: parse_range(x[dim_min]), axis=1))
            rfqs[dim_max+"_num"] = rfqs[dim_max+"_num"].combine_first(rfqs[dim_max])

    # --------------------------
    # Define similarity functions
    # --------------------------
    def interval_iou(min1, max1, min2, max2):
        if pd.isna(min1) or pd.isna(max1) or pd.isna(min2) or pd.isna(max2):
            return 0
        inter = max(0, min(max1, max2) - max(min1, min2))
        union = max(max1, max2) - min(min1, min2)
        return inter / union if union != 0 else 0

    def numeric_score(rfq_row, inv_row):
        score = 0
        count = 0
        mapping = [
            ("thickness_min_num", "thickness_max_num", "thickness_mm"),
            ("width_min_num", "width_max_num", "width_mm"),
            ("weight_min_num", "weight_max_num", "gross_weight_kg")
        ]
        for rfq_min, rfq_max, inv_col in mapping:
            if rfq_min in rfq_row and rfq_max in rfq_row and inv_col in inv_row:
                score += interval_iou(rfq_row[rfq_min], rfq_row[rfq_max], inv_row[inv_col], inv_row[inv_col])
                count += 1
        return score / count if count else 0

    def categorical_score(rfq_row, inv_row):
        score = 0
        features = ["grade_norm", "finish_norm"]
        for f in features:
            if pd.notna(rfq_row.get(f)) and pd.notna(inv_row.get(f)):
                score += 1 if rfq_row[f] == inv_row[f] else 0
        return score / len(features)

    # --------------------------
    # Compute top-3 matches
    # --------------------------
    results = []
    for idx, rfq in rfqs.iterrows():
        inventory["num_score"] = inventory.apply(lambda x: numeric_score(rfq, x), axis=1)
        inventory["cat_score"] = inventory.apply(lambda x: categorical_score(rfq, x), axis=1)
        inventory["total_score"] = inventory["num_score"] * 0.6 + inventory["cat_score"] * 0.4

        # Exclude self or exact matches if article_id == rfq_id (optional)
        top3 = inventory.nlargest(3, "total_score").copy()
        for _, row in top3.iterrows():
            results.append({
                "rfq_id": rfq["id"],
                "match_id": row["article_id"],
                "similarity_score": round(row["total_score"], 3)
            })

    # --------------------------
    # Save top3.csv
    # --------------------------
    final_df = pd.DataFrame(results)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_file)
    final_df.to_csv(out_path, index=False)
    print(f"[✓] Saved {out_path}")
