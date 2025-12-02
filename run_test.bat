@echo off
REM Test runner script for Windows
REM This script activates the virtual environment and runs tests

echo ==========================================
echo Running Tests
echo ==========================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment not found.
    echo Please create the environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Create sample data if it doesn't exist
if not exist "sample.csv" (
    echo.
    echo Creating sample data file...
    (
        echo target,feature1,feature2,feature3
        echo 10.5,1.2,3.4,5.6
        echo 20.3,2.1,4.5,6.7
        echo 15.7,1.8,3.9,5.2
        echo 25.1,2.5,5.1,7.3
        echo 18.9,2.0,4.2,6.1
    ) > sample.csv
)

REM Run the application
echo.
echo Running application...
python app.py

REM Run auto tests if available
if exist "auto_test\" (
    echo.
    echo ==========================================
    echo Running Automated Tests
    echo ==========================================
    python auto_test\auto_test.py
)

echo.
echo ==========================================
echo Tests completed!
echo ==========================================
echo.
echo Check logs\test_run.log for detailed results.
echo.

REM Deactivate virtual environment
call deactivate
