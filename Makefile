# Makefile for Vanilla Steel Assessment

# Default target
.PHONY: all
all: help

# Activate poetry shell
.PHONY: shell
shell:
	poetry shell

# Install dependencies
.PHONY: install
install:
	poetry install

# Run Scenario A (Supplier Data Cleaning)
.PHONY: scenario-a
scenario-a:
	poetry run python run.py --run A

# Run Scenario B (RFQ Similarity)
.PHONY: scenario-b
scenario-b:
	poetry run python run.py --run B

# Run both scenarios
.PHONY: run-all
run-all:
	poetry run python run.py --run A,B

# Clean outputs
.PHONY: clean
clean:
	rm -rf outputs/*.csv

# Show help
.PHONY: help
help:
	@echo "Makefile targets:"
	@echo "  install     - Install dependencies with Poetry"
	@echo "  shell       - Open a Poetry shell"
	@echo "  scenario-a  - Run Scenario A (Data Cleaning)"
	@echo "  scenario-b  - Run Scenario B (RFQ Similarity)"
	@echo "  run-all     - Run both scenarios"
	@echo "  clean       - Delete generated CSV outputs"
