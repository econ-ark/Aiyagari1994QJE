"""HARK's rule against the reference solution (aiyagari1994qje.reference), at fixed prices. Runs in .venv-hark:

    .venv-hark/bin/python tests/test_reference.py

At the baseline's interest rate, households' capital supply from HARK's rule at the medium level's 200 points, put
through one population grid in levels, against the reference's on the same grid:
  - linearly interpolated (the default), HARK overstates saving by more than 0.4 percent, the error that both
    toolkits share at the medium level (docs/model.md, "A register of conventions");
  - with cubic_interpolation, HARK is within 0.01 percent of the reference.
"""

import os
import sys
import time
import warnings
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
warnings.filterwarnings("ignore")
from aiyagari1994qje import LEVELS, Calibration, Population, asset_grid, make_households, rule_of, solve_households  # noqa: E402
from aiyagari1994qje.reference import Household, prices  # noqa: E402

R_BASELINE = 0.0387833  # HARK's high-level equilibrium rate at the baseline (table-ii/hark-high.json), rounded
GRID = asset_grid(300.0, 2000, 3.0)  # the population's grid, in levels


def hark_supply(cubic):
    cal = Calibration()
    households = make_households(cal, settings=replace(LEVELS["medium"], cubic_interpolation=cubic))
    solve_households(households, R_BASELINE)
    _, w = prices(R_BASELINE)
    rule, (x, P), R = households.solution[0].cFunc, households.chain, 1 + R_BASELINE
    labor = np.exp(x)

    def next_assets(a, j):  # levels in and out; HARK's rule is in units of the wage
        m = R * np.asarray(a) / w + labor[j]
        return w * (m - rule[j](m))
    return Population(next_assets, P, GRID).mean_assets, households


def test_cubic_interpolation_matches_the_reference():
    start = time.time()
    _, w = prices(R_BASELINE)
    reference = Population(Household(0.2, 0.6, 3, rule_points=4000).solve(R_BASELINE, w).next_assets,
                           Household(0.2, 0.6, 3).P, GRID).mean_assets
    linear, _ = hark_supply(cubic=False)
    cubic, households = hark_supply(cubic=True)
    print(f"capital supply at r = {100 * R_BASELINE:.5f}%: reference {reference:.6f}, HARK linear {linear:.6f} "
          f"({linear / reference - 1:+.2e}), HARK cubic {cubic:.6f} ({cubic / reference - 1:+.2e}), "
          f"{time.time() - start:.0f} s")
    assert linear / reference - 1 > 0.004, "linear interpolation should overstate saving at the medium level"
    assert abs(cubic / reference - 1) < 1e-4, "cubic interpolation should match the reference"
    try:
        rule_of(households)
    except NotImplementedError:
        pass
    else:
        raise AssertionError("rule_of should refuse a cubically interpolated rule")


if __name__ == "__main__":
    test_cubic_interpolation_matches_the_reference()
    print("passed: test_cubic_interpolation_matches_the_reference")
