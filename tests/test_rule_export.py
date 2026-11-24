"""HARK's rule, written out by rule_of and read back by rules.evaluate without HARK, against HARK's own evaluation:

    .venv-hark/bin/python tests/test_rule_export.py

The read-back must give HARK's consumption at every point a household can have, between the knots, at them,
and above the last, where HARK approaches its limiting line.
"""

import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
warnings.filterwarnings("ignore")
from aiyagari1994qje import LEVELS, Calibration, evaluate_rule, make_households, rule_of, solve_households  # noqa: E402


def test_the_rule_reads_back():
    cal = Calibration()
    households = make_households(cal, settings=LEVELS["low"])
    solve_households(households, 0.038)
    rule = json.loads(json.dumps(rule_of(households)))  # through JSON, as another program would read it
    rng = np.random.default_rng(0)
    worst = 0.0
    for j, function in enumerate(rule["states"]):
        knots = np.asarray(function["of"][0]["x"])
        m = np.concatenate([np.exp(rng.uniform(np.log(1e-4), np.log(500.0), 4000)), knots[knots > 0], [knots[-1] * 1.5]])
        hark = households.solution[0].cFunc[j](m)
        ours = evaluate_rule(function, m)
        worst = max(worst, float(np.max(np.abs(ours - hark) / np.maximum(1.0, np.abs(hark)))))
    assert worst <= 1e-12, f"the rule read back differs from HARK's by {worst:.1e}"


if __name__ == "__main__":
    test_the_rule_reads_back()
    print("passed: test_the_rule_reads_back")
