#!/usr/bin/env bash
set -euo pipefail

# Create a virtual environment named .venv and install the updated requirements
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"
