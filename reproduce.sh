#!/bin/bash
# Aiyagari (1994 QJE) - full reproduction.
#
# Builds the pinned environments (setup_envs.sh), then executes both notebooks,
# each in its own environment. Executed copies, with all tables and figures,
# are written to results/; the notebooks in the repository are left unchanged.
#
# Requires uv (https://docs.astral.sh/uv/); binder/environment.yml installs it.

set -euo pipefail
cd "$(dirname "$0")"

echo "=== Aiyagari (1994 QJE) reproduction, started $(date) ==="

./setup_envs.sh

mkdir -p results

run_notebook() {
    local notebook="$1" group="$2"
    echo ""
    echo "=== Executing $notebook (environment .venv-$group) ==="
    ".venv-$group/bin/jupyter" nbconvert --to notebook --execute \
        --ExecutePreprocessor.kernel_name="aiyagari-$group" \
        --ExecutePreprocessor.timeout=-1 \
        --output-dir results "$notebook"
    echo "Executed copy written to results/$notebook"
}

run_notebook AiyagariMarkovHARK.ipynb hark
run_notebook AiyagariDolARK.ipynb dolark

echo ""
echo "=== Reproduction completed successfully at $(date) ==="
