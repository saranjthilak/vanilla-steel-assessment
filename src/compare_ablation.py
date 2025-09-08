import pandas as pd

# -------------------------
# Config
# -------------------------
scenarios = [
    "all_features",
    "dimensions_only",
    "grade_only",
    "categorical_only",
    "adjusted_weights"
]
output_dir = "outputs"

# -------------------------
# Load top3 CSVs
# -------------------------
dfs = {s: pd.read_csv(f"{output_dir}/top3_{s}.csv") for s in scenarios}

# -------------------------
# Average similarity per scenario
# -------------------------
avg_scores = {s: dfs[s]['similarity_score'].mean() for s in scenarios}

print("Average similarity scores:")
for s, score in avg_scores.items():
    print(f"{s}: {score:.3f}")
