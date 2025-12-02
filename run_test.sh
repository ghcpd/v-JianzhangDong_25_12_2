#!/bin/bash

# Test runner script for Linux/macOS
# This script activates the virtual environment and runs tests

set -e  # Exit on error

echo "=========================================="
echo "Running Tests"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run setup.sh first to create the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Create sample data if it doesn't exist
if [ ! -f "sample.csv" ]; then
    echo ""
    echo "Creating sample data file..."
    cat > sample.csv << 'EOF'
target,feature1,feature2,feature3
10.5,1.2,3.4,5.6
20.3,2.1,4.5,6.7
15.7,1.8,3.9,5.2
25.1,2.5,5.1,7.3
18.9,2.0,4.2,6.1
EOF
fi

# Run the application
echo ""
echo "Running application..."
python app.py

# Run auto tests if available
if [ -d "auto_test" ]; then
    echo ""
    echo "=========================================="
    echo "Running Automated Tests"
    echo "=========================================="
    python auto_test/auto_test.py
fi

echo ""
echo "=========================================="
echo "Tests completed!"
echo "=========================================="
echo ""
echo "Check logs/test_run.log for detailed results."
echo ""

# Deactivate virtual environment
deactivate
