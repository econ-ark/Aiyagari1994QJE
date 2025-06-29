#!/bin/bash

# Aiyagari (1994QJE) Model - Full Reproduction Script
# This script reproduces all computational results from the implementation

set -e  # Exit on any error

echo "=== Aiyagari (1994QJE) Model Reproduction ==="
echo "Starting reproduction at $(date)"

# Check if we're in a conda environment or need to use poetry
if [[ "$CONDA_DEFAULT_ENV" == "Aiyagari1994QJE" ]]; then
    echo "Using conda environment: $CONDA_DEFAULT_ENV"
    PYTHON_CMD="python"
    JUPYTER_CMD="jupyter"
elif command -v poetry &> /dev/null; then
    echo "Using Poetry environment"
    PYTHON_CMD="poetry run python"
    JUPYTER_CMD="poetry run jupyter"
else
    echo "Using system Python (not recommended for reproducibility)"
    PYTHON_CMD="python"
    JUPYTER_CMD="jupyter"
fi

# Create results directory if it doesn't exist
mkdir -p results

echo ""
echo "=== Executing AiyagariMarkovHARK notebook ==="
$JUPYTER_CMD nbconvert --to notebook --execute --inplace AiyagariMarkovHARK.ipynb
echo "✓ AiyagariMarkovHARK.ipynb completed successfully"

echo ""
echo "=== Executing AiyagariDolARK notebook ==="
$JUPYTER_CMD nbconvert --to notebook --execute --inplace AiyagariDolARK.ipynb
echo "✓ AiyagariDolARK.ipynb completed successfully"

echo ""
echo "=== Generating summary outputs ==="
# Extract key results and save to results directory
$PYTHON_CMD -c "
import json
from datetime import datetime

# Create a simple results summary
results = {
    'reproduction_date': datetime.now().isoformat(),
    'notebooks_executed': [
        'AiyagariMarkovHARK.ipynb',
        'AiyagariDolARK.ipynb'
    ],
    'status': 'success',
    'model': 'Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving'
}

with open('results/reproduction_summary.json', 'w') as f:
    json.dump(results, f, indent=2)

print('✓ Results summary saved to results/reproduction_summary.json')
"

echo ""
echo "=== Reproduction completed successfully at $(date) ==="
echo "All notebooks have been executed and outputs generated."
echo "Check the executed notebooks for detailed results and figures."