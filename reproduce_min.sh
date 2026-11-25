#!/bin/bash
# Aiyagari (1994 QJE) - quick check (about a minute once the environments exist).
#
# Builds the pinned environments, solves the baseline economy (σ = 0.2, ρ = 0.6, μ = 3)
# with this repository's package aiyagari1994qje at its default, medium level, and checks every
# number against the committed baseline/numbers.json. Then solves it with dolo and DolARK at
# their low level, and checks that the interest rate is the record's (table-ii/dolark-low.json)
# and within 0.005 percentage points of HARK's at the same level (table-ii/hark-low.json).
# reproduce.sh runs everything.

set -euo pipefail
cd "$(dirname "$0")"

./setup_envs.sh

echo ""
echo "=== Testing the population code in both environments ==="
.venv-hark/bin/python tests/test_population.py
.venv-dolark/bin/python tests/test_population.py
.venv-hark/bin/python tests/test_rule_export.py
.venv-hark/bin/python tests/test_reference.py
.venv-hark/bin/python tests/test_readme_numbers.py

regenerated=$(mktemp -d)
trap 'rm -rf "$regenerated"' EXIT

echo ""
echo "=== Solving the baseline economy with the aiyagari1994qje package ==="
.venv-hark/bin/python - "$regenerated" <<'EOF'
import json, sys, time
from aiyagari1994qje import Calibration, solve_equilibrium

start = time.time()
eq = solve_equilibrium(Calibration())
print(f"Solved in {time.time() - start:.0f} s: interest rate {100 * eq.interest_rate:.4f}%, "
      f"saving rate {100 * eq.saving_rate:.2f}% (Aiyagari: 3.8767% and 24.25%)")
json.dump(eq.numbers(), open(f"{sys.argv[1]}/numbers.json", "w"), indent=2, ensure_ascii=False)
EOF

echo "=== Comparing with baseline/numbers.json ==="
.venv-hark/bin/python .github/check_baseline.py --numbers-only baseline "$regenerated"

echo ""
echo "=== Solving the baseline economy with dolo and DolARK (dolark-environment/aiyagari_dolark.py) ==="
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv-dolark/bin/python -W ignore - <<'PYTHON'
import json, sys, time
sys.path.insert(0, "dolark-environment")
from aiyagari_dolark import Economy

baseline = lambda path: next(c for c in json.load(open(path))["cells"] if (c["sigma"], c["rho"], c["mu"]) == (0.2, 0.6, 3))
start = time.time()
r = Economy(0.2, 0.6, 3, level="low").equilibrium()["interest_rate"]
recorded, hark = baseline("table-ii/dolark-low.json")["interest_rate"], baseline("table-ii/hark-low.json")["interest_rate"]
print(f"Solved in {time.time() - start:.0f} s: interest rate {100 * r:.4f}% (the record: {100 * recorded:.4f}%; HARK: {100 * hark:.4f}%)")
assert abs(r - recorded) < 1e-6, "DolARK's baseline is not the record's"
assert abs(r - hark) < 5e-5, "DolARK and HARK disagree at the baseline by more than 0.005 percentage points"
PYTHON

echo ""
echo "=== Quick check passed at $(date). Run reproduce.sh for everything. ==="
