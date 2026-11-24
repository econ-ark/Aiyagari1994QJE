"""What the first version of AiyagariDolARK.ipynb got wrong, one change at a time.

Through version 1.1 of the REMARK, the model file Aiyagari.yaml stated an economy that is not Aiyagari's,
and the notebook solved it with dolark's find_steady_state, which computes the population on the grid
where it solves the rule. This script takes that model file from the tag v1.1.2 and solves three cells
of Table II with each departure undone in turn, the others left in place:

    .venv-dolark/bin/python dolark-environment/first_version.py      # about ten minutes; needs git and the tag

It prints the table that AiyagariDolARK.ipynb quotes. The departures:
  euler   the Euler equation, written 1 - (β(1+r'))^(1/θ) c/c', the CRRA equation only when θ = 1
  chain   the income process, a VAR1 that dolo turns into a three-state Rouwenhorst chain, where
          Aiyagari has his seven-state Tauchen chain
  labor   the interest rate reported, recomputed with the chain's mean labor endowment, where the
          equilibrium was solved with exp(σ²/2)
  grid    the rule and the population on one grid of 75 points evenly spaced to 300
"""

import contextlib
import io
import multiprocessing
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

EULER = "1-( (β*(1+r[t+1]))^(1/θ) )*(c[t]/c[t+1])"
EULER_CRRA = "1 - β*(1+r[t+1])*(c[t+1]/c[t])^(-θ)"
VAR1 = "    e: !VAR1\n        ρ: ρ_param\n        Σ: [[Σ_param]]"
CELLS = [(0.2, 0.0, 1), (0.2, 0.6, 3), (0.4, 0.9, 5)]
# The first version's starting values for capital in these cells (its list load_capital)
START = {(0.2, 0.0, 1): 5.718341702347233, (0.2, 0.6, 3): 6.066502939823299, (0.4, 0.9, 5): 8.67333741118939}


def first_model_file():
    return subprocess.run(["git", "-C", REPO, "show", "v1.1.2:Aiyagari.yaml"], capture_output=True, text=True, check=True).stdout


def solve(job):
    name, euler_fixed, chain_fixed, cell = job
    from dolark import HModel
    from dolark.equilibrium import find_steady_state
    from aiyagari_dolark import tauchen_chain, stationary_probabilities

    σ, ρ, μ = cell
    text = first_model_file()
    assert EULER in text and VAR1 in text
    if euler_fixed:
        text = text.replace(EULER, EULER_CRRA)
    innovation_variance = (σ * (1 - ρ**2) ** 0.5) ** 2
    L = np.exp(σ**2 / 2)  # the first version's mean labor endowment
    if chain_fixed:
        x, P = tauchen_chain(7, ρ, σ)
        values = "[" + ", ".join(f"[{v!r}]" for v in x) + "]"
        rows = "[" + ", ".join("[" + ", ".join(repr(p) for p in row) + "]" for row in P) + "]"
        text = text.replace(VAR1, f"    e: !MarkovChain\n        values: {values}\n        transitions: {rows}")
        L = float(stationary_probabilities(P) @ np.exp(x))
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(text)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            model = HModel(f.name)
            model.model.set_calibration(θ=μ, ρ_param=ρ, Σ_param=innovation_variance)
            model.set_calibration(L=L, K=START[cell])
            eq = find_steady_state(model, verbose=False)
        df = eq.as_df()
        e, i, w = (np.asarray(df[c], dtype=float) for c in ("e", "i", "μ"))
        K = float(np.inner(i, w))
        α, δ = 0.36, 0.08
        faced = α * (L / K) ** (1 - α) - δ                                  # the rate households faced
        reported = α * (float(np.inner(np.exp(e), w)) / K) ** (1 - α) - δ   # the first version's report
        return name, cell, 100 * faced, 100 * reported
    except Exception:
        return name, cell, float("nan"), float("nan")
    finally:
        os.unlink(f.name)


def main():
    variants = [("first version, as it reported", False, False), ("first version, the rate its households faced", False, False),
                ("with the Euler equation corrected", True, False), ("with Aiyagari's chain", False, True),
                ("with both", True, True)]
    jobs = [(name, e, c, cell) for name, e, c in variants[1:] for cell in CELLS]
    with multiprocessing.get_context("spawn").Pool(min(len(jobs), 6, os.cpu_count() or 1)) as pool:
        results = pool.map(solve, jobs, chunksize=1)
    print("| first version's model, solved by find_steady_state | " + " | ".join(f"σ = {s}, ρ = {r}, μ = {m}" for s, r, m in CELLS) + " |")
    print("|---" * (len(CELLS) + 1) + "|")
    table = {(name, cell): (faced, reported) for name, cell, faced, reported in results}
    for name, _, _ in variants:
        source, column = (variants[1][0], 1) if name == variants[0][0] else (name, 0)
        print(f"| {name} | " + " | ".join(
            "fails" if np.isnan(table[(source, c)][column]) else f"{table[(source, c)][column]:.4f}%" for c in CELLS) + " |")


if __name__ == "__main__":
    main()
