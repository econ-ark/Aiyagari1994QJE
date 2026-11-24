"""Table II of Aiyagari (1994) solved cell by cell by one toolkit at one level, written to table-ii/<toolkit>-<level>.json.

    .venv-hark/bin/python   table-ii/record.py hark high      [--processes N]
    .venv-dolark/bin/python table-ii/record.py dolark high    [--processes N]

hark solves with the package aiyagari1994qje at the level's Settings (aiyagari1994qje.LEVELS: original,
low, medium, high); dolark with dolark-environment/aiyagari_dolark.py at its own LEVELS (low, medium,
high). Each cell is solved in its own single-threaded process. The file records, beside each cell's
numbers, the commit and whether the tree was dirty, the versions, the machine and each cell's duration:
a duration is read with its machine beside it.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(name, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CELLS = [(s, r, m) for s in (0.2, 0.4) for r in (0.0, 0.3, 0.6, 0.9) for m in (1, 3, 5)]


def solve_hark(cell, level):
    import warnings
    warnings.filterwarnings("ignore")
    from aiyagari1994qje import LEVELS, Calibration, solve_equilibrium

    σ, ρ, μ = cell
    eq = solve_equilibrium(Calibration(income_standard_deviation=σ, income_persistence=ρ, relative_risk_aversion=μ),
                           settings=LEVELS[level])
    member = eq.effective_member()
    return {
        "interest_rate": eq.interest_rate, "wage": eq.wage, "capital": eq.capital, "labor_supply": float(eq.labor_supply),
        "capital_relative_to_complete_markets": eq.capital / eq.capital_complete_markets,
        "saving_rate": float(eq.saving_rate), "saving_rate_from_capital": eq.saving_rate_from_capital,
        "gini": float(eq.gini),
        "share_of_richest": {f"{round(100 * q)}_percent": float(eq.share_of_richest(q)) for q in (0.01, 0.05, 0.10, 0.20, 0.30)},
        "share_at_borrowing_constraint": float(eq.share_at_borrowing_constraint),
        "average_marginal_propensity_to_consume": float(eq.average_marginal_propensity_to_consume),
        "chain": {k: member[k] for k in ("mean_labor_endowment", "standard_deviation_of_log_endowment",
                                         "autocorrelation_of_log_endowment")},
        "diagnostics": eq.diagnostics(),
    }


def solve_dolark(cell, level):
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, os.path.join(REPO, "dolark-environment"))
    from aiyagari_dolark import Economy

    σ, ρ, μ = cell
    out = Economy(σ, ρ, μ, level=level).equilibrium()
    return {k: v for k, v in out.items() if k not in ("sigma", "rho", "mu", "level", "settings")}


def _solve(job):
    toolkit, level, cell = job
    start = time.time()
    try:
        result = (solve_hark if toolkit == "hark" else solve_dolark)(cell, level)
        result["error"] = None
    except Exception as err:  # a cell that fails is recorded as failed, and the others still run
        result = {"error": f"{type(err).__name__}: {err}"}
    result.update({"sigma": cell[0], "rho": cell[1], "mu": cell[2], "seconds": round(time.time() - start, 1)})
    print(f"{toolkit} {level} σ={cell[0]} ρ={cell[1]} μ={cell[2]}: "
          + (f"r* = {100 * result['interest_rate']:.4f}%" if result["error"] is None else result["error"])
          + f", {result['seconds']:.0f}s", flush=True)
    return result


def _provenance(toolkit):
    git = lambda *args: subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout.strip()
    from importlib.metadata import version, PackageNotFoundError

    def v(name):
        try:
            return version(name)
        except PackageNotFoundError:
            return None

    packages = ["numpy", "scipy"] + (["econ-ark"] if toolkit == "hark" else ["dolo", "dolark", "dolang"])
    return {
        "commit": git("rev-parse", "HEAD") or None,
        "dirty": bool(git("status", "--porcelain", "--", ".", ":!table-ii/*.json")),
        "python": platform.python_version(),
        "packages": {p: v(p) for p in packages},
        "machine": {"system": platform.system(), "machine": platform.machine(), "processor": platform.processor() or None,
                    "cpus": os.cpu_count()},
        "threads_per_process": 1,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("toolkit", choices=["hark", "dolark"])
    parser.add_argument("level")
    parser.add_argument("--processes", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    from multiprocessing import get_context

    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    t = time.time()
    with get_context("spawn").Pool(args.processes) as pool:
        cells = pool.map(_solve, [(args.toolkit, args.level, c) for c in CELLS], chunksize=1)
    settings = None
    if args.toolkit == "hark":
        from dataclasses import asdict
        from aiyagari1994qje import LEVELS
        settings = {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(LEVELS[args.level]).items()}
    else:
        sys.path.insert(0, os.path.join(REPO, "dolark-environment"))
        from aiyagari_dolark import LEVELS
        settings = LEVELS[args.level]
    record = {
        "description": f"Aiyagari (1994), Table II, every cell solved by {args.toolkit} at the level {args.level!r}",
        "toolkit": args.toolkit, "level": args.level, "settings": settings,
        "units": "Rates and shares are fractions; capital, the wage and labor supply are levels for a population of mass one",
        "provenance": dict(_provenance(args.toolkit), started=started, processes=args.processes,
                           wall_seconds=round(time.time() - t, 1)),
        "cells": cells,
    }
    path = os.path.join(HERE, f"{args.toolkit}-{args.level}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=1, ensure_ascii=False)
        f.write("\n")
    failed = [c for c in cells if c["error"]]
    print(f"wrote {path}: {len(cells) - len(failed)} cells solved, {len(failed)} failed, {time.time() - t:.0f}s")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
