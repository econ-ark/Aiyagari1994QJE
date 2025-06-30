#!/bin/bash

# =============================================================================
# Aiyagari (1994) Model - Baseline Mode Execution
# =============================================================================
# This script runs the main notebook in BASELINE_MODE for quick testing/CI
# Expected runtime: ~30 seconds (single parameter combination)
# =============================================================================

set -e  # Exit on any error

echo "=== Aiyagari (1994) Model - Baseline Mode ==="
echo "Starting baseline execution at $(date)"

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

echo "=== Configuring notebook for BASELINE_MODE ==="

# Create a temporary notebook with BASELINE_MODE = True
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
            # Ensure BASELINE_MODE is set to True
            new_source = []
            for line in cell['source']:
                if 'BASELINE_MODE' in line and '=' in line:
                    new_source.append('BASELINE_MODE = True  # Quick single-parameter execution\n')
                else:
                    new_source.append(line)
            cell['source'] = new_source
            break

# Save to temporary file
with open('AiyagariMarkovHARK_baseline_temp.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print('✓ Configured notebook for baseline mode')
"

echo "=== Executing notebook in baseline mode ==="
echo "Expected runtime: ~30 seconds"

# Execute the notebook
jupyter nbconvert --to notebook --execute --inplace AiyagariMarkovHARK_baseline_temp.ipynb \
    --ExecutePreprocessor.timeout=300 --ExecutePreprocessor.allow_errors=False

echo "=== Extracting baseline results ==="

# Extract and display results
python -c "
import json

with open('AiyagariMarkovHARK_baseline_temp.ipynb', 'r') as f:
    nb = json.load(f)

# Find output from the results cell
for cell in nb['cells']:
    if cell.get('outputs'):
        for output in cell['outputs']:
            if 'text' in output:
                text = ''.join(output['text']) if isinstance(output['text'], list) else output['text']
                if 'BASELINE RESULTS' in text or 'Parameter combination' in text:
                    print(text)
                    break
"

# Cleanup
rm -f AiyagariMarkovHARK_baseline_temp.ipynb

echo "=== Baseline execution completed successfully at $(date) ==="
echo "✓ Single parameter combination (σ=0.2, ρ=0.6, μ=1) executed"
echo "✓ For full parameter sweep (24 combinations), run: ./reproduce.sh" 