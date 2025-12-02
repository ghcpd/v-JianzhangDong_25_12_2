@echo off
REM Quick test script for Windows (cmd)
python -m venv test_env
call test_env\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

if exist app.py (
  python app.py || echo App exited with non-zero code
)

echo Completed run_test for requirements.txt
