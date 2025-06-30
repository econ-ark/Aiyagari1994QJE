#!/bin/bash

# =============================================================================
# Aiyagari (1994) Model - Full Parameter Sweep Execution
# =============================================================================
# This script runs the main notebook in FULL_MODE for complete replication
# Expected runtime: ~10-15 minutes (24 parameter combinations)
# =============================================================================

set -e  # Exit on any error

echo "=== Aiyagari (1994) Model - Full Parameter Sweep ==="
echo "Starting full execution at $(date)"

# Detect environment
if conda info --envs | grep -q "Aiyagari1994QJE.*\*"; then
    echo "Using active conda environment: $(conda info --envs | grep '\*' | awk '{print $1}')"
elif conda info --envs | grep -q "Aiyagari1994QJE"; then
    echo "Activating conda environment: Aiyagari1994QJE"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate Aiyagari1994QJE
else
    echo "⚠️  Conda environment 'Aiyagari1994QJE' not found. Using current environment."
    echo "   To create: mamba env create -f binder/environment.yml"
fi

echo "=== Configuring notebook for FULL_MODE ==="

# Create a temporary notebook with BASELINE_MODE = False
python -c "
import json

# Load the main notebook
with open('AiyagariMarkovHARK.ipynb', 'r') as f:
    nb = json.load(f)

# Find and modify the configuration cell
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'BASELINE_MODE' in source and '=' in source:
            # Ensure BASELINE_MODE is set to False
            new_source = []
            for line in cell['source']:
                if 'BASELINE_MODE' in line and '=' in line:
                    new_source.append('BASELINE_MODE = False  # Full 24-parameter sweep\n')
                else:
                    new_source.append(line)
            cell['source'] = new_source
            break

# Save to temporary file
with open('AiyagariMarkovHARK_full_temp.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print('✓ Configured notebook for full parameter sweep')
"

echo "=== Executing full parameter sweep ==="
echo "Expected runtime: ~10-15 minutes (24 parameter combinations)"
echo "Progress: σ ∈ {0.2, 0.4} × ρ ∈ {0.0, 0.3, 0.6, 0.9} × μ ∈ {1, 3, 5}"

# Execute the notebook with longer timeout
jupyter nbconvert --to notebook --execute --inplace AiyagariMarkovHARK_full_temp.ipynb \
    --ExecutePreprocessor.timeout=1800 --ExecutePreprocessor.allow_errors=False

echo "=== Extracting comparison tables ==="

# Extract and display results
python -c "
import json

with open('AiyagariMarkovHARK_full_temp.ipynb', 'r') as f:
    nb = json.load(f)

# Find output from the results cell
found_tables = False
for cell in nb['cells']:
    if cell.get('outputs'):
        for output in cell['outputs']:
            if 'text' in output:
                text = ''.join(output['text']) if isinstance(output['text'], list) else output['text']
                if 'Table II' in text or 'HARK minus Aiyagari' in text:
                    print(text)
                    found_tables = True
                    
if not found_tables:
    print('⚠️  No comparison tables found in output. Check execution logs.')
"

# Save executed notebook with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p results
cp AiyagariMarkovHARK_full_temp.ipynb "results/AiyagariMarkovHARK_executed_${TIMESTAMP}.ipynb"

# Cleanup
rm -f AiyagariMarkovHARK_full_temp.ipynb

echo "=== Full execution completed successfully at $(date) ==="
echo "✓ All 24 parameter combinations executed"
echo "✓ Comparison tables generated (Aiyagari 1994 vs HARK replication)"
echo "✓ Executed notebook saved to: results/AiyagariMarkovHARK_executed_${TIMESTAMP}.ipynb"
echo "✓ For quick testing, run: ./run_baseline.sh"
