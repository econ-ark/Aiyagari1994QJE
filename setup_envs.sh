#!/bin/bash
# Build the two pinned environments from uv.lock and register their Jupyter kernels.
#
#   .venv-hark    econ-ark 0.13.0          runs AiyagariMarkovHARK.ipynb  (kernel: aiyagari-hark)
#   .venv-dolark  dolark (pinned commit)   runs AiyagariDolARK.ipynb      (kernel: aiyagari-dolark)
#
# The notebooks cannot share one environment; see the comment in pyproject.toml.
# Safe to re-run: uv only installs what is missing.
#
# Set SETUP_USER_KERNELS=1 to also register both kernels for the current user, so
# a Jupyter server outside these environments (for example, Binder's) can use them.

set -euo pipefail
cd "$(dirname "$0")"

for group in hark dolark; do
    echo "=== Syncing .venv-$group from uv.lock ==="
    UV_PROJECT_ENVIRONMENT=".venv-$group" uv sync --locked --group "$group"
done

display_name() {
    case "$1" in
        hark) echo "Aiyagari (HARK 0.13.0)" ;;
        dolark) echo "Aiyagari (DolARK)" ;;
    esac
}

# Each environment's Jupyter sees both kernels, so either notebook opens from either one.
for group in hark dolark; do
    for target in .venv-hark .venv-dolark; do
        ".venv-$group/bin/python" -m ipykernel install --prefix "$target" \
            --name "aiyagari-$group" --display-name "$(display_name "$group")" > /dev/null
    done
    if [[ "${SETUP_USER_KERNELS:-0}" == "1" ]]; then
        ".venv-$group/bin/python" -m ipykernel install --user \
            --name "aiyagari-$group" --display-name "$(display_name "$group")"
    fi
done

echo "=== Environments ready: .venv-hark, .venv-dolark ==="
