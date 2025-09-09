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

## Running
```bash
pip install -r requirements.txt
python run.py --run A,B
```
# Similarity Matching Methodology (Scenario B)

## 1. Data Normalization
- Text features like **grade** and **finish** are uppercased and stripped of whitespace.  
- Grade aliases (e.g., `S235J0`) are mapped to standardized formats (e.g., `S235JR`).  

---

## 2. Reference Join
- Inventory records are merged with a **reference dataset** on normalized grade.  
- This enriches the inventory with additional properties for matching.  

---

## 3. Numeric Range Parsing
- RFQ specifications provided as ranges (e.g., `thickness_min`, `thickness_max`) are converted into **numeric intervals**.  
- For singleton values, `min = max`.  

---

## 4. Feature Engineering & Scoring

### a. Numeric Similarity
- Uses **Intersection over Union (IoU)** between RFQ intervals and inventory measurements.  

### b. Categorical Similarity
- Exact matches for features like **grade** and **finish** (`1` for match, `0` otherwise).  

### c. Aggregate Similarity Score
- Total_score = 0.6 × numeric_score + 0.4 × categorical_score

---

## 5. Top-3 Selection
- For each RFQ, the **three inventory items** with the highest similarity scores are selected.  
- Results exclude any **exact self-matches** 

