"""A consumption rule written out as data, and evaluated without the toolkit that computed it.

Equilibrium.rule() writes HARK's rule in two forms, each evaluated here by HARK's own arithmetic, the same
operations in the same order, so that a program that does not run HARK reads the rule HARK computed:

  linear-interpolation  knots x and y; on the segment to the right of knot i - 1, intercept + slope x, with the
                        segment found as HARK finds it (searchsorted on the knots but the last); below the first
                        knot "undefined" (NaN) or "extend"; above the last, "extend", or the limiting line
                        approached: intercept + slope x - gap exp(-decay (x - x_top))
  lower-envelope        the least of the functions in "of" at each point, NaNs ignored

Only numpy is used.
"""

import numpy as np


def evaluate_rule(function, x):
    """The value of a rule's function at the points x (evaluate's name in the package)."""
    return evaluate(function, x)


def evaluate(function, x):
    """The value of a rule's function at the points x."""
    x = np.asarray(x, dtype=float)
    if function["form"] == "lower-envelope":
        values = np.vstack([evaluate(f, x) for f in function["of"]])
        return np.nanmin(values, axis=0)
    if function["form"] != "linear-interpolation":
        raise ValueError(f"unknown form {function['form']!r}")
    knots, values = np.asarray(function["x"], dtype=float), np.asarray(function["y"], dtype=float)
    slopes = (values[1:] - values[:-1]) / (knots[1:] - knots[:-1])
    intercepts = values[:-1] - slopes * knots[:-1]
    i = np.maximum(np.searchsorted(knots[:-1], x), 1) - 1
    y = intercepts[i] + slopes[i] * x
    if function.get("below", "undefined") == "undefined":
        y[x < knots[0]] = np.nan
    above = function.get("above", "extend")
    if above != "extend":
        top = x > knots[-1]
        decay = above["gap"] * np.exp(-above["decay"] * (x[top] - knots[-1]))
        y[top] = above["intercept"] + above["slope"] * x[top] - decay
    return y
