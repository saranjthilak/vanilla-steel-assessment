#!/usr/bin/env python
import argparse
from src import data_cleaning

# Import RFQ similarity
from src import rfq_similarity

def run_scenario_a():
    print("Running Scenario A: Supplier Data Cleaning...")
    data_cleaning.run_supplier_cleaning(input_dir="data", output_dir="outputs")
    print("✅ Scenario A complete: outputs/inventory_dataset.csv generated.")

def run_scenario_b():
    print("Running Scenario B: RFQ Similarity...")
    rfq_similarity.compute_top3(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        inventory_file="outputs/inventory_dataset.csv",
        output_file="top3.csv",  # only filename
        output_dir="outputs"     # folder to save in
    )
    print("✅ Scenario B complete: outputs/top3.csv generated.")

def main():
    parser = argparse.ArgumentParser(description="Vanilla Steel Assessment Runner")
    parser.add_argument(
        "--run",
        type=str,
        required=True,
        help="Comma-separated scenarios to run: A,B"
    )
    args = parser.parse_args()
    scenarios = [s.strip().upper() for s in args.run.split(",")]

    if "A" in scenarios:
        run_scenario_a()
    if "B" in scenarios:
        run_scenario_b()

if __name__ == "__main__":
    main()
