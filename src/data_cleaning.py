import os
import pandas as pd
import numpy as np

def run_supplier_cleaning(input_dir="data", output_dir="outputs"):
    """
    Clean and join supplier datasets into inventory_dataset.csv
    """
    # Load supplier files
    s1 = pd.read_excel(os.path.join(input_dir, "supplier_data1.xlsx"))
    s2 = pd.read_excel(os.path.join(input_dir, "supplier_data2.xlsx"))

    # --- Supplier 1 ---
    s1["Thickness (mm)"] = s1["Thickness (mm)"].replace(",", ".", regex=True).astype(float)
    s1["Width (mm)"] = s1["Width (mm)"].replace(",", ".", regex=True).astype(float)
    s1["Gross weight (kg)"] = s1["Gross weight (kg)"].astype(float)

    s1_clean = s1.rename(columns={
        "Quality/Choice": "quality_choice",
        "Grade": "grade",
        "Finish": "finish",
        "Thickness (mm)": "thickness_mm",
        "Width (mm)": "width_mm",
        "Description": "description",
        "Gross weight (kg)": "gross_weight_kg",
        "Quantity": "quantity"
    })

    # String normalization
    for col in ["quality_choice", "grade", "finish"]:
        if col in s1_clean.columns:
            s1_clean[col] = s1_clean[col].astype(str).str.strip().str.upper()

    s1_clean["source"] = "supplier1"

    # --- Supplier 2 ---
    s2["Weight (kg)"] = s2["Weight (kg)"].astype(float)
    s2_clean = s2.rename(columns={
        "Material": "grade",
        "Description": "description",
        "Article ID": "article_id",
        "Weight (kg)": "gross_weight_kg",
        "Quantity": "quantity",
        "Reserved": "reserved"
    })

    # String normalization
    for col in ["grade", "reserved"]:
        if col in s2_clean.columns:
            s2_clean[col] = s2_clean[col].astype(str).str.strip().str.upper()

    # Add missing columns
    s2_clean["thickness_mm"] = np.nan
    s2_clean["width_mm"] = np.nan
    s2_clean["finish"] = np.nan
    s2_clean["quality_choice"] = np.nan
    s2_clean["source"] = "supplier2"

    # Align columns
    common_cols = [
        "source", "article_id", "quality_choice", "grade", "finish",
        "thickness_mm", "width_mm", "description", "gross_weight_kg",
        "quantity", "reserved"
    ]
    s1_final = s1_clean.reindex(columns=common_cols)
    s2_final = s2_clean.reindex(columns=common_cols)

    # Merge datasets
    inventory = pd.concat([s1_final, s2_final], ignore_index=True)

    # Fill missing categorical/object columns including article_id and description
    categorical_cols = ["article_id", "quality_choice", "thickness_mm", "finish", "reserved", "width_mm"]
    for col in categorical_cols:
        if col in inventory.columns:
            inventory[col] = inventory[col].fillna("NaN")


    # Save output
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "inventory_dataset.csv")
    inventory.to_csv(out_path, index=False)
    print(f"[✓] Saved {out_path}")
