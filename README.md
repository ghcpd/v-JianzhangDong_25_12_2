# Dependency Maintenance & Test Harness

## Overview
- `requirements_backup.txt` — Original dependencies (likely outdated/vulnerable).
- `requirements.txt` — Corrected, pinned, compatible dependencies (2025-12-02).
- `report.json` — Summary of dependency issues and upgrades.
- `Dockerfile` — Reproducible container image (Python 3.11, installs `requirements.txt`).
- `setup.sh` — Linux/macOS helper to create a venv and install `requirements.txt`.
- `run_test.sh` / `run_test.bat` — Cross-platform runners for the automated test harness.
- `auto_test/auto_test.py` — Creates isolated venvs for backup vs corrected deps, installs, runs `app.py`, and logs results.
- `logs/test_run.log` — Detailed run log produced by the test harness.

## Prerequisites
- Python 3.9+ installed (3.11 recommended). For Python 3.14, nightly wheels will be used automatically by `auto_test`.
- Internet access for `pip install`.
- (Linux/macOS) `bash`; (Windows) `cmd` / PowerShell.

## Setup (Linux/macOS)
```bash
chmod +x setup.sh run_test.sh
./setup.sh  # creates .venv and installs requirements.txt
```

## Setup (Windows)
```bat
:: Optionally create .venv and install requirements
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run tests
### Linux/macOS
```bash
./run_test.sh           # runs auto_test for both backup and corrected deps
```

### Windows
```bat
run_test.bat            # runs auto_test for both backup and corrected deps
```

## auto_test.py usage
```bash
python auto_test/auto_test.py --both           # default; tests backup and corrected
python auto_test/auto_test.py --backup-only
python auto_test/auto_test.py --corrected-only
```
- Detects platform (Windows/Linux/Docker).
- Creates fresh venvs under `.venv_tests/<backup|corrected>`.
- Installs deps from the respective requirements file.
- Generates `sample.csv` and runs `app.py` to verify functionality.
- Writes results to `logs/test_run.log` and `logs/test_run_summary.json`.
```
## Logs
- Tail or open `logs/test_run.log` for detailed command output.
- Summary JSON: `logs/test_run_summary.json`.

## Docker
```bash
docker build -t dep-maintenance:latest .
docker run --rm dep-maintenance:latest
```

### Python 3.14 note
- Scientific packages may not yet provide wheels for CPython 3.14. The harness automatically enables pre-release installs and adds the Scientific Python nightly wheels index (`AUTO_TEST_NIGHTLY_INDEX` env var to override).
- If nightly wheels are unavailable, use Docker (Python 3.11) or install a supported Python version (≤3.13).
The container runs `run_test.sh` by default.

## Notes
- The corrected `requirements.txt` targets Python >= 3.9.
- If `sample.csv` is missing, the harness auto-generates it.
