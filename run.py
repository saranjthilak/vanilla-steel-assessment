#!/usr/bin/env python
import argparse
from src import data_cleaning
from src import rfq_similarity
from src import ablation_analysis
from src import alternative_metrics
from src import clustering  # <- new clustering module

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
        output_file="top3.csv",
        output_dir="outputs"
    )
    print("✅ Scenario B complete: outputs/top3.csv generated.")

def run_ablation():
    print("Running Ablation Analysis...")
    from src import ablation_analysis
    ablation_analysis.compute_and_report(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        inventory_file="outputs/inventory_dataset.csv",
        output_dir="outputs",
        ablation=True
    )
    print("✅ Ablation Analysis complete.")


def run_alternative_metrics():
    print("Running Scenario C: Alternative Metrics (cosine vs hybrid)...")
    alternative_metrics.compute_alternative_metrics(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        inventory_file="outputs/inventory_dataset.csv",
        output_dir="outputs"
    )
    print("✅ Scenario C complete: outputs/top3_baseline.csv & outputs/top3_hybrid.csv generated.")

def run_clustering():
    print("Running Clustering Analysis...")
    clustering.cluster_rfqs(
        rfq_file="data/rfq.csv",
        reference_file="data/reference_properties.tsv",
        output_dir="outputs",
        n_clusters=4
    )
    print("✅ Clustering complete: outputs/rfq_clusters.csv generated.")

def main():
    parser = argparse.ArgumentParser(description="Vanilla Steel Assessment Runner")
    parser.add_argument(
        "--run",
        type=str,
        required=True,
        help="Comma-separated scenarios to run: A,B,AB,C,CL"
    )
    args = parser.parse_args()
    scenarios = [s.strip().upper() for s in args.run.split(",")]

    if "A" in scenarios:
        run_scenario_a()
    if "B" in scenarios:
        run_scenario_b()
    if "AB" in scenarios:
        run_ablation()
    if "C" in scenarios:
        run_alternative_metrics()
    if "CL" in scenarios:
        run_clustering()

if __name__ == "__main__":
    main()
