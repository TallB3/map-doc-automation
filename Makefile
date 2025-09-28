# Makefile for map-doc-automation project

# Virtual environment path
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: help run setup install clean

help:
	@echo "Available commands:"
	@echo "  make run     - Activate venv and run main.py"
	@echo "  make setup   - Create virtual environment and install dependencies"
	@echo "  make install - Install/update requirements"
	@echo "  make clean   - Remove virtual environment"

run:
	@echo "Running map-doc automation..."
	@$(PYTHON) main.py

setup:
	@echo "Setting up virtual environment..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Setup complete! Use 'make run' to start."

install:
	@echo "Installing requirements..."
	@$(PIP) install -r requirements.txt

clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)