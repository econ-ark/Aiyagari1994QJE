"""Tests of the population code, against populations known exactly. Runs in either environment:

    .venv-hark/bin/python tests/test_population.py
    .venv-dolark/bin/python tests/test_population.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from aiyagari1994qje.population import Population, asset_grid  # noqa: E402


def test_a_point_between_two_grid_points():
    # Everyone ends every period with assets 0.3 on a grid 0, 0.25, 0.5, ...: the lottery puts 80 percent at 0.25
    # and 20 percent at 0.5, and keeps mean assets at 0.3
    grid = np.linspace(0, 1, 5)
    pop = Population(lambda a, j: np.full(a.shape, 0.3), np.eye(1), grid)
    assert np.allclose(pop.asset_mass, [0, 0.8, 0.2, 0, 0], atol=1e-14)
    assert abs(pop.mean_assets - 0.3) < 1e-14
    assert pop.stationarity_residual < 1e-14


def test_income_states_and_their_chain():
    # Two income states; assets next period depend only on the income state: 0 in the first, 0.5 in the second.
    # The population's states are the chain's stationary distribution (2/3, 1/3), whatever the assets
    P = np.array([[0.9, 0.1], [0.2, 0.8]])
    grid = asset_grid(1.0, 101, curvature=1.0)
    pop = Population(lambda a, j: np.full(a.shape, 0.0 if j == 0 else 0.5), P, grid)
    assert np.allclose(pop.mass.sum(axis=0), [2 / 3, 1 / 3], atol=1e-12)
    assert abs(pop.mean_assets - 0.5 / 3) < 1e-12
    assert abs(pop.mass_at_or_below(0.0) - 2 / 3) < 1e-12
    # with half the population holding nothing and the rest equal shares, the Gini is the share holding nothing
    assert abs(pop.gini - 2 / 3) < 1e-9
    assert abs(pop.share_of_richest(1 / 3) - 1) < 1e-6


def test_mass_beyond_the_top():
    grid = np.linspace(0, 1, 11)
    pop = Population(lambda a, j: np.full(a.shape, 2.0), np.eye(1), grid)
    assert abs(pop.mass_beyond_top - 1) < 1e-14
    assert abs(pop.asset_mass[-1] - 1) < 1e-14


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("passed:", name)
