#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python - <<'PY'
import pandas as pd
import numpy as np
from pathlib import Path

# Generate a small sample dataset for the app
Path('sample.csv').write_text('')
df = pd.DataFrame({
    'target': np.arange(10),
    'feature1': np.arange(10) * 2,
    'feature2': np.arange(10) * 3,
})
df.to_csv('sample.csv', index=False)
print('sample.csv generated')
PY

python app.py
