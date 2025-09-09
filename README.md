# Vanilla Steel — Data Science Case

This repository contains my solution for the **Vanilla Steel Junior Data Scientist Assessment**.

---

##  Project Overview

This project addresses two main scenarios:

- **Scenario A: Supplier Data Cleaning**  
  Process and clean supplier inventory data; the output is:
  - `outputs/inventory_dataset.csv`

- **Scenario B: RFQ Similarity Matching**  
  Identify the top-3 most similar inventory items for each RFQ request. This partially completed output is:
  - `outputs/top3.csv`
  - rfq_id — identifier of the RFQ

  - match_id — identifier of the matching inventory article

  - similarity_score — computed similarity value (higher is better)

---

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


---

## Installation

You can install dependencies either via **Poetry** or **pip**.

### Poetry (recommended)
```bash
# Install poetry if not already installed
pip install poetry

# Install dependencies
poetry install
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

Easy reproducibility with Poetry / pip dependency management.

## Dependencies

Core dependencies (from requirements.txt / pyproject.toml) include:

Python 3.9+

pandas — data manipulation

numpy — numerical operations

scikit-learn — similarity and ML utilities

tqdm — progress tracking

(Exact versions are pinned in pyproject.toml.)

## Configuration

Input data files should be placed inside the data/ directory.

Outputs will automatically be written to the outputs/ directory.

You can customize the workflow by editing parameters inside scripts under src/.

# 🧹 Task A.1 — Supplier Data Cleaning Methodology

## 1. Decimal Separators
- **Supplier 1** sometimes used `,` instead of `.` in numeric fields (`Thickness (mm)`, `Width (mm)`).
- Standardized all numeric values to `.` and cast them to floats.

---

## 2. Column Naming / Schema Alignment
- Suppliers used different column names for the same concepts.
- Renamed into a **common schema**:
  thickness_mm, width_mm, gross_weight_kg, quantity,
grade, finish, quality_choice, description,
article_id, reserved


- Added a `source` column to track origin (`supplier1` / `supplier2`).

---

## 3. Text Normalization
- For categorical fields (`quality_choice`, `grade`, `finish`, `reserved`):
  - Trimmed whitespace
  - Converted all values to uppercase

---

## 4. Missing Values
- **Categorical/object fields** (`article_id`, `quality_choice`, `finish`, `reserved`, `thickness_mm`, `width_mm`):  
  Replaced missing values with the string `"NaN"`.
- **Numeric fields** (`gross_weight_kg`, `quantity`):  
  Kept missing values as `NaN` (float) so they remain usable in calculations.

---

## 5. Supplier-Specific Differences
- **Supplier 2** lacked thickness, width, finish, and quality info → filled with `NaN`.  
- **Supplier 1** lacked reserved/article_id → filled with `NaN`.

---

## 6. Output
- Final unified dataset:  
 Contains records from both suppliers under the standardized schema.





# 📊Similarity Matching Methodology (Scenario B)

## 1. Data Normalization
- Text features like **grade** and **finish** are uppercased and stripped of whitespace.  
- Grade aliases (e.g., `S235J0`) are mapped to standardized formats (e.g., `S235JR`).  

## 2. Reference Join
- Inventory records are merged with a **reference dataset** on normalized grade.  
- This enriches the inventory with additional properties for matching.  

## 3. Numeric Range Parsing
- RFQ specifications provided as ranges (e.g., `thickness_min`, `thickness_max`) are converted into **numeric intervals**.  
- For singleton values, `min = max`.  

## 4. Feature Engineering & Scoring

### a. Numeric Similarity
- Uses **Intersection over Union (IoU)** between RFQ intervals and inventory measurements.  

### b. Categorical Similarity
- Exact matches for features like **grade** and **finish** (`1` for match, `0` otherwise).  

### c. Aggregate Similarity Score
- Total_score = 0.6 × numeric_score + 0.4 × categorical_score

## 5. Top-3 Selection
- For each RFQ, the **three inventory items** with the highest similarity scores are selected.  
- Results exclude any **exact self-matches**

## 6. Output

- outputs/top3.csv

- Columns:
  rfq_id, match_id, similarity_score


