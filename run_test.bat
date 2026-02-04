@echo off
setlocal enabledelayedexpansion

if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python -c "import pandas as pd; import numpy as np; df = pd.DataFrame({'target': range(10), 'feature1': [i*2 for i in range(10)], 'feature2': [i*3 for i in range(10)]}); df.to_csv('sample.csv', index=False); print('sample.csv generated')"

python app.py

endlocal
