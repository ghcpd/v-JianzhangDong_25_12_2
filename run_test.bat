@echo off
REM Test runner script for Windows
REM Runs the application with the corrected dependencies

setlocal enabledelayedexpansion

echo ===================================
echo Running Tests - Windows
echo ===================================

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Creating it...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

REM Create a sample CSV file for testing
echo Creating sample test data...
python << 'EOF'
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = {
    'target': np.random.rand(50) * 100,
    'feature1': np.random.rand(50) * 50,
    'feature2': np.random.rand(50) * 30,
    'feature3': np.random.rand(50) * 20
}
df = pd.DataFrame(data)
df.to_csv('sample.csv', index=False)
print("Sample CSV created: sample.csv")
EOF

REM Run the application
echo.
echo Running application...
python app.py
if errorlevel 1 (
    echo Error: Application failed to run
    exit /b 1
)

echo.
echo ===================================
echo Tests completed successfully!
echo ===================================

endlocal
