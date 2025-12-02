#!/bin/bash

# Test runner script for Linux/macOS
# Runs the application with the corrected dependencies

set -e

echo "==================================="
echo "Running Tests - Linux/macOS"
echo "==================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    bash setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Create a sample CSV file for testing
echo "Creating sample test data..."
python3 << 'EOF'
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

# Run the application
echo ""
echo "Running application..."
python3 app.py

echo ""
echo "==================================="
echo "Tests completed successfully!"
echo "==================================="
