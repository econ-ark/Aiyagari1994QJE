"""The README's table of the baseline economy, against baseline/numbers.json at the precision the README quotes.

    python tests/test_readme_numbers.py

Prose that quotes numbers drifts when the computation changes; this fails when it has.
"""

import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def test_the_baseline_table():
    readme = open(os.path.join(ROOT, "README.md")).read()
    n = json.load(open(os.path.join(ROOT, "baseline", "numbers.json")))
    eq, wealth = n["equilibrium"], n["wealth_distribution"]
    published = n["aiyagari_1994"]
    rows = [
        f"| Equilibrium interest rate | {100 * eq['interest_rate']:.2f}% (Aiyagari: {100 * published['interest_rate']:.2f}%) |",
        f"| Saving rate | {100 * eq['saving_rate_from_capital']:.2f}% (Aiyagari: {100 * published['saving_rate']:.2f}%) |",
        f"higher ({100 * (n['capital_relative_to_complete_markets'] - 1):.1f}%) |",
        f"| Wealth Gini | {wealth['gini']:.2f} |",
        f"| Share of wealth held by the richest 1% | {100 * wealth['share_of_richest']['1_percent']:.1f}% |",
        f"| Share of households at the borrowing constraint | {100 * wealth['share_at_borrowing_constraint']:.2f}% |",
        f"| Average marginal propensity to consume | {n['average_marginal_propensity_to_consume']:.3f} |",
    ]
    missing = [row for row in rows if row not in readme]
    assert not missing, "README.md's baseline table does not match baseline/numbers.json:\n  " + "\n  ".join(missing)
    # "about 4% higher" must stay true
    assert round(100 * (n["capital_relative_to_complete_markets"] - 1)) == 4


if __name__ == "__main__":
    test_the_baseline_table()
    print("passed: test_the_baseline_table")
