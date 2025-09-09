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
