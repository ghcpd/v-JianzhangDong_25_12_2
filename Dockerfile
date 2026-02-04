# Python runtime with slim image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate a sample CSV so app.py can run by default
RUN python - <<'PY'
import pandas as pd
import numpy as np
from pathlib import Path
Path('sample.csv').write_text('')
try:
    df = pd.DataFrame({
        'target': np.arange(10),
        'feature1': np.arange(10)*2,
        'feature2': np.arange(10)*3,
    })
    df.to_csv('sample.csv', index=False)
except Exception as e:
    raise SystemExit(e)
PY

CMD ["python", "app.py"]
