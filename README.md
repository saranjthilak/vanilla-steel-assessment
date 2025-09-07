# Vanilla Steel — Data Science Case

This repository contains my solution for the **Vanilla Steel Junior Data Scientist Assessment**.

## Deliverables
- **Scenario A**: Supplier Data Cleaning → `outputs/inventory_dataset.csv`
- **Scenario B**: RFQ Similarity → `outputs/top3.csv` (WIP)

## Project Structure
- `data/` — input Excel/CSV/TSV files
- `outputs/` — generated cleaned inventory and similarity results
- `src/` — scripts for cleaning and similarity
- `run.py` — main runner script
- `requirements.txt` — dependencies

## Running
```bash
pip install -r requirements.txt
python run.py --run A,B
