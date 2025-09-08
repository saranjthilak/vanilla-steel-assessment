# -----------------------------
# Vanilla Steel Assessment Makefile
# -----------------------------

# Python environment (Poetry)
PYTHON := poetry run python

# -----------------------------
# Scenario A: Supplier cleaning
# -----------------------------
scenario-a:
	@echo "Running Scenario A: Supplier Data Cleaning..."
	$(PYTHON) run.py --run A
	@echo "[✓] Scenario A complete."

# -----------------------------
# Scenario B: RFQ Similarity
# -----------------------------
scenario-b:
	@echo "Running Scenario B: RFQ Similarity..."
	$(PYTHON) run.py --run B
	@echo "[✓] Scenario B complete."

# -----------------------------
# Ablation Analysis
# -----------------------------
ablation-analysis:
	@echo "Running Ablation Analysis..."
	$(PYTHON) run.py --run AB
	@echo "[✓] Ablation Analysis complete."

# -----------------------------
# Alternative Metrics
# -----------------------------
alternative-metrics:
	@echo "Running Alternative Metrics (cosine vs hybrid)..."
	$(PYTHON) run.py --run C
	@echo "[✓] Alternative Metrics complete."

# -----------------------------
# Clustering
# -----------------------------
clustering:
	@echo "Running Clustering Analysis..."
	$(PYTHON) run.py --run CL
	@echo "[✓] Clustering complete."

# -----------------------------
# Clean outputs
# -----------------------------
clean:
	@echo "Cleaning output files..."
	rm -rf outputs/*.csv
	@echo "[✓] Clean complete."

# -----------------------------
# Run all
# -----------------------------
all: scenario-a scenario-b ablation-analysis alternative-metrics clustering
	@echo "[✓] All steps complete."
