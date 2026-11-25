"""A reference solution of the Aiyagari economy, independent of HARK and of dolo, to measure their errors against.

The household's rule is solved by the endogenous grid method in plain numpy, on Aiyagari's stated chain (built here
step for step as docs/model.md states it, not with HARK's make_tauchen_ar1), on a fine grid of end-of-period assets
in levels, to a relative change of 1e-13 in consumption. The population is the REMARK's stationary histogram
(population.py) on a grid of its own. Only numpy and scipy are used, so it runs in every environment of the REMARK.

    from aiyagari1994qje.reference import Household, solve_equilibrium
    hh = Household(sigma=0.2, rho=0.6, mu=3).solve(r, w)   # the rule at prices (r, w)
    hh.next_assets(a, j)                                    # end-of-period assets of a household arriving with a in state j
    eq = solve_equilibrium(0.2, 0.6, 3)                     # about a minute at the defaults

Measured on 2026-11-25 at three cells of Table II, at fixed prices: doubling the rule's points from 4,000 to 8,000 moves
the interest rate by under 0.000005 percentage points, and the population's grid of 6,000 points is within 0.000015 of
its limit. Against it, the toolkits' linearly interpolated rules at the medium level understate the interest rate by
up to 0.0076 percentage points (docs/model.md, "A register of conventions").
"""

import numpy as np
from scipy import stats
from scipy.optimize import brentq

from aiyagari1994qje.population import Population, asset_grid

BETA, ALPHA, DELTA = 0.96, 0.36, 0.08


def tauchen_chain(n=7, rho=0.6, sigma=0.2, bound=3.0):
    """Aiyagari's chain: n log endowments evenly spaced bound unconditional standard deviations either side of zero,
    and Tauchen's transition probabilities for an AR(1) with persistence rho and unconditional standard deviation
    sigma. Returns (x, P)."""
    innovation = sigma * (1 - rho**2) ** 0.5
    x = np.linspace(-bound * sigma, bound * sigma, n)
    cuts = np.concatenate(([-np.inf], (x[1:] + x[:-1]) / 2.0, [np.inf]))
    dist = (cuts[None, :] - rho * x[:, None]) / innovation
    cdf, sf = stats.norm.cdf(dist), stats.norm.sf(dist)
    P = np.maximum(cdf[:, 1:] - cdf[:, :-1], sf[:, :-1] - sf[:, 1:])
    return x, P / P.sum(axis=1, keepdims=True)


def prices(r):
    """Capital per unit of labor k and the wage w that go with the net interest rate r."""
    k = ((r + DELTA) / ALPHA) ** (1 / (ALPHA - 1))
    return k, (1 - ALPHA) * k**ALPHA


class Household:
    """The household's problem for one cell of Table II, with no borrowing; assets and income in levels."""

    def __init__(self, sigma=0.2, rho=0.6, mu=3, rule_points=4000, rule_top=500.0, curvature=3.0):
        self.mu = mu
        self.x, self.P = tauchen_chain(7, rho, sigma)
        self.labor = np.exp(self.x)
        self.a_end = asset_grid(rule_top, rule_points, curvature)  # end-of-period assets; a_end[0] = 0, the limit
        self.knots = None  # in each state, (m, c) at the endogenous points, one for each of a_end

    def consumption(self, m, j):
        """c(m) in state j: c = m below the first endogenous point (where the limit binds), linear between the
        points, and extended linearly beyond the last."""
        mk, ck = self.knots[j]
        m = np.asarray(m, dtype=float)
        c = np.interp(m, mk, ck)
        above = m > mk[-1]
        if np.any(above):
            slope = (ck[-1] - ck[-2]) / (mk[-1] - mk[-2])
            c = np.where(above, ck[-1] + slope * (m - mk[-1]), c)
        return np.where(m < mk[0], m, c)

    def solve(self, r, w, tol=1e-13, maxit=200000):
        """The rule at prices (r, w), from the last rule solved if there is one. Returns self."""
        R, mu, S = 1 + r, self.mu, len(self.x)
        if self.knots is None:  # start from consuming labor income and a small share of assets (positive at any r)
            self.knots = [(self.a_end + w * self.labor[j], 0.05 * self.a_end + w * self.labor[j]) for j in range(S)]
        for it in range(maxit):
            marginal = np.column_stack([self.consumption(R * self.a_end + w * self.labor[k], k) ** (-mu) for k in range(S)])
            c_now = (BETA * R * (marginal @ self.P.T)) ** (-1 / mu)  # c_now[:, j], from the Euler equation
            new = [(c_now[:, j] + self.a_end, c_now[:, j]) for j in range(S)]
            change = max(np.max(np.abs(new[j][1] - self.knots[j][1]) / new[j][1]) for j in range(S))
            self.knots = new
            if not np.isfinite(change):
                raise FloatingPointError(f"the iteration produced non-finite consumption at iteration {it}")
            if change < tol:
                break
        else:
            raise RuntimeError(f"no convergence in {maxit} iterations (last relative change {change:.1e})")
        self.R, self.w, self.iterations = R, w, it + 1
        return self

    def next_assets(self, a, j):
        m = self.R * np.asarray(a, dtype=float) + self.w * self.labor[j]
        return m - self.consumption(m, j)

    def population(self, points=6000, top=300.0):
        """The stationary population of the last rule solved, on asset_grid(top, points) in levels."""
        return Population(self.next_assets, self.P, asset_grid(top, points, 3.0))


def solve_equilibrium(sigma=0.2, rho=0.6, mu=3, rule_points=4000, population_points=6000, xtol=1e-12):
    """The stationary equilibrium, by Brent's method on r. Returns a dict of the interest rate, capital, wage and
    labor supply, with the population (population.Population) and the household (Household) at r*."""
    hh = Household(sigma, rho, mu, rule_points=rule_points)
    pi = np.linalg.matrix_power(hh.P.T, 4000)[:, 0]  # the chain's stationary probabilities
    L = float(pi @ hh.labor)

    def excess(r):
        k, w = prices(r)
        return hh.solve(r, w).population(population_points).mean_assets - L * k

    r = brentq(excess, -0.01, 1 / BETA - 1 - 1e-4, xtol=xtol)
    k, w = prices(r)
    population = hh.solve(r, w).population(population_points)
    return {"interest_rate": r, "capital": L * k, "wage": w, "labor_supply": L, "population": population, "household": hh}
