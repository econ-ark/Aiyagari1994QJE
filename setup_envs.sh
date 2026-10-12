#!/bin/bash
# Build the two pinned environments and register their Jupyter kernels.
#
#   .venv-hark    from uv.lock: Python 3.14.7, econ-ark 0.17.2 and this repository's package
#                 aiyagari1994qje (editable)              runs AiyagariMarkovHARK.ipynb  (kernel: aiyagari-hark)
#   .venv-dolark  from dolark-environment/uv.lock: Python 3.9.23,
#                 dolark (pinned commit)                  runs AiyagariDolARK.ipynb      (kernel: aiyagari-dolark)
#
# The notebooks cannot share one environment; see dolark-environment/pyproject.toml.
# Safe to re-run: uv only installs what is missing. If a Python version is not installed,
# uv downloads it.
#
# Set SETUP_USER_KERNELS=1 to also register both kernels for the current user, so
# a Jupyter server outside these environments (for example, Binder's) can use them.

set -euo pipefail
cd "$(dirname "$0")"

python_version() {
    case "$1" in
        hark) echo "3.14.7" ;;
        dolark) echo "3.9.23" ;;
    esac
}

display_name() {
    case "$1" in
        hark) echo "Aiyagari (HARK 0.17.2)" ;;
        dolark) echo "Aiyagari (DolARK)" ;;
    esac
}

project() {
    case "$1" in
        hark) echo "." ;;
        dolark) echo "dolark-environment" ;;
    esac
}

for group in hark dolark; do
    echo "=== Syncing .venv-$group from $(project "$group")/uv.lock (Python $(python_version "$group")) ==="
    UV_PROJECT_ENVIRONMENT="$PWD/.venv-$group" uv sync --locked --project "$(project "$group")" \
        --python "$(python_version "$group")"
done

# Kernels run single-threaded. With a thread per visible core, the DolARK notebook took
# 143 s on a 16-core Mac (51 s single-threaded) and did not finish in an hour on Binder,
# which shows its 1-CPU session 24 cores; the HARK notebook runs equally fast either way.
THREADS=(--env OMP_NUM_THREADS 1 --env OPENBLAS_NUM_THREADS 1 --env MKL_NUM_THREADS 1 --env NUMBA_NUM_THREADS 1)

# Each environment's Jupyter sees both kernels, so either notebook opens from either one.
# (ipykernel warns that the other environment's prefix is not on its own search path;
# that is expected here, so the warning is dropped.)
for group in hark dolark; do
    for target in .venv-hark .venv-dolark; do
        ".venv-$group/bin/python" -m ipykernel install --prefix "$target" "${THREADS[@]}" \
            --name "aiyagari-$group" --display-name "$(display_name "$group")" \
            > /dev/null 2> >(grep -v 'The kernelspec may not be found' >&2)
    done
    if [[ "${SETUP_USER_KERNELS:-0}" == "1" ]]; then
        ".venv-$group/bin/python" -m ipykernel install --user "${THREADS[@]}" \
            --name "aiyagari-$group" --display-name "$(display_name "$group")"
    fi
done

echo "=== Environments ready: .venv-hark, .venv-dolark ==="
