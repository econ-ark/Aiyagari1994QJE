#!/bin/bash
set -e

echo "====================================================="
echo "=== Aiyagari (1994) Model - Full Replication ==="
echo "====================================================="

# Activate conda environment if it exists but is not active
if conda info --envs | grep -q "Aiyagari1994QJE" && [[ "$CONDA_DEFAULT_ENV" != "Aiyagari1994QJE" ]]; then
    echo "Activating conda environment: Aiyagari1994QJE"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate Aiyagari1994QJE
fi

echo "\nRunning full replication via compute.py..."
python compute.py --mode=full

echo "\n=== Full replication completed successfully. ==="