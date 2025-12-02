# Dependency maintenance and automated verification

This repository now includes a safer, up-to-date pinned dependency list and an automated verification harness to compare the original dependencies against the corrected set.

Files added or updated
- `requirements_backup.txt` — original dependency file preserved as a backup.
- `requirements.txt` — updated, secure and compatible package pins (use to reproduce the corrected environment).
- `report.json` — a compact JSON report that lists each changed package, original and updated versions, and the reason.
- `Dockerfile` — reproducible Docker environment that installs `requirements.txt` and runs `app.py`.
- `setup.sh` — convenience shell script to create a venv and install `requirements.txt` (Linux/macOS).
- `run_test.sh` — quick script to create a test venv and attempt to run the project (Linux/macOS).
- `run_test.bat` — quick script to create a test venv and attempt to run the project (Windows/cmd).
- `auto_test/auto_test.py` — automated test harness that:
  - detects the current runtime environment (Windows / Linux / Docker)
  - creates clean venvs for `requirements_backup.txt` and `requirements.txt`
  - installs the packages and runs basic import/version checks and attempts to run `app.py`
  - writes detailed logs to `logs/test_run.log` and a JSON summary to `logs/summary.json`.

Why these changes
- The original file contained several old package pins (pandas 1.2, numpy 1.19, scikit-learn 0.22.2, etc.) that are outdated and may contain bugs or security issues and often cause incompatibilities during install with modern Python and package versions. These were updated to stable, compatible versions to reduce security and installation risks.

Quick setup — Linux / macOS

1. Create an environment and install dependencies (updated file):

```bash
./setup.sh
```

2. Run a quick test using the test script:

```bash
./run_test.sh
```

Quick setup — Windows (PowerShell / cmd)

1. Create a virtual environment and install:

```powershell
python -m venv .\test_env
.\test_env\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2. Run quick test using the batch script (cmd.exe):

```cmd
run_test.bat
```

#### 🛠️ Windows — install Visual C++ build tools (needed for compiling some packages)

If you see build errors mentioning distutils.msvccompiler, cl.exe, or "Failed to build numpy", you likely need the Microsoft Visual C++ Build Tools.

Options to install:

- Using Chocolatey (recommended if you already use choco):

```powershell
choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive" -y
```

- Manual download / installer:

Visit https://visualstudio.microsoft.com/visual-cpp-build-tools/ and run the "Build Tools for Visual Studio" installer. Make sure to include the "C++ build tools" workload.

After installing, open a fresh terminal and run:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

You can also use the helper script added to this repo to check for build tools:

```powershell
.\windows_check_buildtools.ps1
```


Reproducible Docker image

```bash
docker build -t myapp:latest .
docker run --rm myapp:latest
```

Automated verification with auto_test.py

The harness will create two isolated virtual environments, install both dependency sets, and run a few checks and an attempt to run `app.py`.

From the repository root run:

```bash
python auto_test/auto_test.py
# or with explicit files
python auto_test/auto_test.py requirements_backup.txt requirements.txt
```

Logs

- Full chronological logs are written to `logs/test_run.log`.
- A JSON summary is written to `logs/summary.json`.

What to expect

- The environment created with `requirements_backup.txt` is expected to show installation issues and/or runtime errors; the environment created from `requirements.txt` should install cleanly and run the same basic checks successfully.

If you want me to also run the auto_test script here and diagnose the results, tell me and I'll run it (or run it locally and paste logs). 
