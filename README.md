# VANILLA-STEEL-ASSESSMENT

**Transform Case Data into Strategic Procurement Power**

[![Open in GitHub](https://img.shields.io/badge/GitHub-Open-blue?logo=github)](https://github.com/saranjthilak/vanilla-steel-assessment)

Built with: ![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python) ![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Manager-green) ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange) ![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-red)

---

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)

---

## Overview

**vanilla-steel-assessment** contains my solution for data preprocessing, analysis, and optimization within supply chain workflows. It integrates multiple tasks into a scalable pipeline for data normalization, RFQ similarity assessment, and matching, enhancing procurement decision-making accuracy and strategic insights.

### Why vanilla-steel-assessment?
This project helps streamline workflows, save effort, and improve matching accuracy. The core features include:

- **Data Cleaning & Normalization:** Standardize supplier datasets for consistent analysis.
- **RFQ Similarity Assessment:** Find the top-3 matches for RFQs to facilitate efficient sourcing.
- **Workflow Orchestration:** Automates preprocessing tasks with reproducible steps.
- **Clustering & Segmentation:** Groups SKUs for improved insights.
- **Metrics & Model Analysis:** Supports evaluation of feature importance and alternative similarity measures.

---

## Getting Started

### Prerequisites
This project requires the following dependencies:

- Programming language: **Python**
- Package Manager: **Poetry**

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/saranjthilak/vanilla-steel-assessment.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd vanilla-steel-assessment
3. **Install the dependencies:**

   Using poetry:
   ```bash
   poetry install
##  Repository Structure

```
project-root/
├── data/ # Input data files
├── outputs/ # Generated outputs (cleaned data and results)
│ ├── inventory_dataset.csv
│ └── top3.csv
├── src/ # Python scripts for data cleaning and similarity logic
├── run.py # Main runner
├── Makefile # Build automation
├── pyproject.toml # Poetry
└── README.md # Project overview and instructions
```

## Usage
Using Python directly
```
python run.py
```
## Using Makefile
```
# Run the full pipeline
make run

# Clean outputs
make clean
```
The generated outputs will be stored in the outputs/ directory.

## Features

Data preprocessing and cleaning for supplier inventory.

Similarity-based matching of RFQ requests to inventory items.

Automated pipeline via Makefile.

Easy reproducibility with Poetry dependency management.

## Configuration

Input data files should be placed inside the data/ directory.

Outputs will automatically be written to the outputs/ directory.

You can customize the workflow by editing parameters inside scripts under src/.

# 🧹 Task A — Supplier Data Cleaning Methodology

## 1. Decimal Separators
- **Supplier 1** occasionally used `,` instead of `.` in numeric fields (`Thickness (mm)`, `Width (mm)`).
- Standardized all numeric values to `.` and cast them to floats.

---

## 2. Schema Harmonization
- Suppliers used inconsistent column names for the same attributes.
- Renamed columns into a **unified schema**:

- Added a `source` column to track data origin (`supplier1` / `supplier2`).

---

## 3. Text Normalization
- Applied to categorical fields (`quality_choice`, `grade`, `finish`, `reserved`):
- Trimmed whitespace
- Converted values to **UPPERCASE**

---

## 4. Missing Values
- **Categorical / object fields** (`article_id`, `quality_choice`, `finish`, `reserved`, `thickness_mm`, `width_mm`):
→ Filled with string `"NaN"`.

- **Numeric fields** (`gross_weight_kg`, `quantity`):
→ Retained as float `NaN` to preserve compatibility with calculations.

---

## 5. Supplier-Specific Gaps
- **Supplier 2** lacked `thickness`, `width`, `finish`, `quality` → filled with `NaN`.
- **Supplier 1** lacked `reserved` and `article_id` → filled with `NaN`.

---

## 6. Final Output
- Unified dataset consolidating both suppliers under the standardized schema.
- Stored at: `outputs/inventory_dataset.csv`

---

# 📊 Task B — RFQ Similarity Matching Methodology

## 1. Data Normalization
- Text features (`grade`, `finish`) standardized to uppercase, trimmed, and mapped to canonical aliases (e.g., `S235J0 → S235JR`).

---

## 2. Reference Enrichment
- Inventory joined with a **reference dataset** on normalized `grade`.
- Enriches records with additional material properties.

---

## 3. Numeric Range Handling
- RFQ specs (`thickness_min`, `thickness_max`, etc.) parsed into **numeric intervals**.
- Singleton values represented as `min = max`.

---

## 4. Feature Engineering & Scoring

### a. Numeric Similarity
- Computed using **Intersection over Union (IoU)** between RFQ intervals and inventory dimensions.

### b. Categorical Similarity
- Exact matching for fields like `grade` and `finish`:
- `1` for match, `0` otherwise.

### c. Aggregate Score
- Weighted scoring formula: total_score = 0.6 × numeric_score + 0.4 × categorical_score

---

## 5. Candidate Selection
- For each RFQ: select **Top-3 inventory items** ranked by `total_score`.
- Exclude **exact self-matches** to avoid trivial results.

---

## 6. Final Output
- Results stored at:
- `outputs/top3.csv`

With fields:
rfq_id, match_id, similarity_score

# 🎯 Bonus / Stretch Goals Methodology

## 1. Ablation Analysis
- Designed experiments to evaluate the contribution of each feature group:
  - **Dimensions only** (thickness, width)
  - **Grade only**
  - **Full feature set** (dimensions + categorical)
- Compared similarity results across settings to assess robustness and identify the most influential features.
- Findings highlight whether numeric ranges or material grades dominate the matching performance.

---

## 2. Alternative Similarity Metrics
- Explored beyond the baseline IoU + categorical match:

  - **Cosine Similarity (weighted):** Captures directional similarity between normalized feature vectors.
  - **Jaccard Similarity:** Evaluates overlap between categorical sets (e.g., grade families, finishes).
  - **Hybrid Scoring:** Weighted combination of IoU (numeric) + cosine (vectorized categorical) + Jaccard (set-based).

- Compared these metrics against IoU-based scoring to assess trade-offs between precision and generalization.

---

## 3. Clustering RFQs
- Applied **unsupervised clustering** k-means to group RFQs into families.
- Features considered:
  - `grade`, `finish`, `thickness_mm`, `width_mm`
- Produced cluster labels enabling:
  - Identification of recurring request families
  - Insights into supplier demand patterns
  - Potential optimization opportunities for procurement strategy

- Short interpretation: Clusters reveal natural groupings of RFQs (e.g., common grades with similar dimension ranges), which can guide supplier negotiation and inventory planning.

## 🔮 Future Work

- **Feature Enrichment**: Add more material, supplier, and market data to improve similarity accuracy.
- **Advanced Metrics**: Explore weighted, domain-specific similarity approaches.
- **Clustering Improvements**: Use dynamic cluster selection and generate business-friendly cluster summaries.
- **Scalability**: Integrate vector search like FAISS and optimize with DBs for larger datasets.
- **User Interface**: Build a Streamlit dashboard or API for real-time RFQ similarity lookup.
