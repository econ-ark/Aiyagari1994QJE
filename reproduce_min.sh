#!/bin/bash
# Aiyagari (1994 QJE) - quick check (about 15 seconds once the environments exist).
#
# Builds the pinned environments, solves the baseline economy (σ = 0.2, ρ = 0.6, μ = 3)
# with this repository's package aiyagari1994qje, and checks every number against the
# committed baseline/numbers.json. reproduce.sh runs everything.

set -euo pipefail
cd "$(dirname "$0")"

./setup_envs.sh

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
echo "=== Quick check passed at $(date). Run reproduce.sh for everything. ==="
