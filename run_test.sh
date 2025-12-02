#!/usr/bin/env bash
set -euo pipefail

echo "Running quick tests using requirements.txt"

python3 -m venv test_env
source test_env/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# try to run the app (if available)
if [ -f app.py ]; then
  python app.py || true
fi

echo "Completed run_test for requirements.txt"
