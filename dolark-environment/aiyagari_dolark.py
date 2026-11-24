"""Aiyagari's (1994) economy solved with dolo and DolARK: the computation of AiyagariDolARK.ipynb, packaged.

The model file, ../Aiyagari.yaml, states the household's problem and the economy that closes it. For a
cell of Table II this module puts the cell's income chain and parameters into it and solves:

  - the household's rule at given prices, by dolo's time iteration, on the rule's grid: points of
    beginning-of-period assets, dense near the borrowing limit, with linear interpolation;
  - the stationary population, on a grid of its own, by the REMARK's population code
    (src/aiyagari1994qje/population.py), the code that computes HARK's population too;
  - the equilibrium: the capital K at which DolARK's projection (the interest rate and the wage that
    firms pay with capital K) makes households hold K, by Brent's method.

    from aiyagari_dolark import Economy
    eq = Economy(sigma=0.2, rho=0.6, mu=3).equilibrium()     # Aiyagari's baseline
    eq["interest_rate"], eq["capital"], eq["gini"]

It runs in the DolARK environment (Python 3.9, numpy 1), where the package aiyagari1994qje is not
installed: its population module needs only numpy and scipy, and is imported from ../src.
"""

import contextlib
import io
import os
import re
import sys
import tempfile

import numpy as np
from scipy import stats
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if os.path.join(REPO, "src") not in sys.path:
    sys.path.insert(0, os.path.join(REPO, "src"))
from aiyagari1994qje.population import Population, asset_grid  # noqa: E402

from dolark import HModel  # noqa: E402
from dolark.shocks import inject_process  # noqa: E402
from dolo import improved_time_iteration, time_iteration  # noqa: E402

MODEL_FILE = os.path.join(REPO, "Aiyagari.yaml")

# How the economy is solved. The rule's grid: rule_points points of beginning-of-period assets from the
# borrowing limit to rule_top, spaced as asset_grid(rule_top, rule_points, curvature=2). The population's
# grid: population_points points of end-of-period assets from 0 to population_top, spaced as
# asset_grid(population_top, population_points, curvature=3). Assets are in levels.
LEVELS = {
    "low": dict(rule_points=100, rule_top=150.0, population_points=1000, population_top=300.0),
    "medium": dict(rule_points=200, rule_top=150.0, population_points=2000, population_top=300.0),
    "high": dict(rule_points=800, rule_top=150.0, population_points=3000, population_top=300.0),
}


def tauchen_chain(n=7, rho=0.6, sigma=0.2, bound=3.0):
    """Tauchen's n-state chain for the log labor endowment, an AR(1) with persistence rho and unconditional
    standard deviation sigma: HARK's make_tauchen_ar1, step for step, so that both toolkits face one chain.

    Returns (x, P): the log labor endowments x_j, and P[i, j], the probability of state j next period from state i.
    """
    innovation = sigma * (1 - rho**2) ** 0.5
    x = np.linspace(-bound * sigma, bound * sigma, n)
    cuts = np.concatenate(([-np.inf], (x[1:] + x[:-1]) / 2.0, [np.inf]))
    dist = (cuts[None, :] - rho * x[:, None]) / innovation
    cdf, sf = stats.norm.cdf(dist), stats.norm.sf(dist)
    P = np.maximum(cdf[:, 1:] - cdf[:, :-1], sf[:, :-1] - sf[:, 1:])
    return x, P / P.sum(axis=1, keepdims=True)


def stationary_probabilities(P):
    values, vectors = np.linalg.eig(np.asarray(P).T)
    pi = np.real(vectors[:, np.argmin(np.abs(values - 1))])
    return pi / pi.sum()


def model_text(x, P, rule_points=200, rule_top=150.0, path=MODEL_FILE):
    """The model file's text with the income chain (x, P) and the rule's grid put in."""
    text = open(path).read()
    values = "[" + ", ".join(f"[{float(v)!r}]" for v in x) + "]"
    rows = "[\n            " + ",\n            ".join("[" + ", ".join(repr(float(p)) for p in row) + "]" for row in P) + "]"
    nodes = asset_grid(rule_top, rule_points, curvature=2.0, bottom=-1e-10)
    text, n1 = re.subn(r"values: \[.*?\]\]\n", f"values: {values}\n", text, flags=re.S)
    text, n2 = re.subn(r"transitions: \[\n.*?\]\]\n", f"transitions: {rows}\n", text, flags=re.S)
    text, n3 = re.subn(r"(grid: !NonUniformCartesian\n\s+- )\[.*?\]\n",
                       lambda m: m.group(1) + "[" + ", ".join(f"{v!r}" for v in nodes) + "]\n", text, flags=re.S)
    text, n4 = re.subn(r"a_max: [0-9.]+", f"a_max: {rule_top}", text)
    assert (n1, n2, n3, n4) == (1, 1, 1, 1), "the model file's layout changed: values, transitions, grid and a_max not found"
    return text


@contextlib.contextmanager
def _silent():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


class Economy:
    """One cell of Table II: sigma, the unconditional standard deviation of log labor endowment; rho, its
    persistence; mu, relative risk aversion. The other parameters are the model file's: β = 0.96, α = 0.36,
    δ = 0.08, and no borrowing."""

    def __init__(self, sigma=0.2, rho=0.6, mu=3, level="medium", chain=None):
        self.sigma, self.rho, self.mu, self.level = sigma, rho, mu, level
        self.settings = LEVELS[level] if isinstance(level, str) else dict(level)
        self.x, self.P = chain if chain is not None else tauchen_chain(7, rho, sigma, 3.0)
        self.pi = stationary_probabilities(self.P)
        self.L = float(self.pi @ np.exp(self.x))  # the chain's mean labor endowment
        text = model_text(self.x, self.P, self.settings["rule_points"], self.settings["rule_top"])
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(text)
        with _silent():
            self.hmodel = HModel(f.name)
        os.unlink(f.name)
        self.hmodel.model.set_calibration(θ=mu)
        self.hmodel.set_calibration(L=self.L)
        cal = self.hmodel.model.calibration["parameters"]
        names = self.hmodel.model.symbols["parameters"]
        self.beta = float(cal[names.index("β")])
        agg = dict(zip(self.hmodel.symbols["parameters"], self.hmodel.calibration["parameters"]))
        self.alpha, self.delta = float(agg["α"]), float(agg["δ"])
        self.population_grid = asset_grid(self.settings["population_top"], self.settings["population_points"])
        self._rule = None

    # ---- prices
    def prices(self, K):
        """(r, w) that firms pay with capital K: DolARK's projection."""
        q = self.hmodel.projection(self.hmodel.calibration["exogenous"], np.array([K]), self.hmodel.calibration["parameters"])
        return float(q[0]), float(q[1])

    def capital_demand(self, r):
        return self.L * ((r + self.delta) / self.alpha) ** (1 / (self.alpha - 1))

    # ---- the household
    def rule(self, K):
        """dolo's rule at the prices that go with K: end-of-period assets i(j, a) for state j and beginning-of-period
        assets a. Each solve starts from the last rule; where improved time iteration fails, plain time iteration
        takes over, from the last rule and then from the model file's."""
        dp = inject_process(np.array(self.prices(K)), self.hmodel.model.exogenous)
        nodes = self.hmodel.model.endo_grid.nodes
        finite = lambda rule: rule is not None and all(np.all(np.isfinite(rule(j, nodes))) for j in range(len(self.x)))
        with _silent():
            try:
                dr = time_iteration(self.hmodel.model, dr0=self._rule, dprocess=dp, verbose=False,
                                    maxit=10 if self._rule is None else 3, interp_method="linear").dr
                dr = improved_time_iteration(self.hmodel.model, dr0=dr, dprocess=dp, verbose=False, interp_method="linear").dr
            except Exception:
                dr = None
            for start in (self._rule, None):  # time iteration from the last rule, then from the model file's
                if finite(dr):
                    break
                try:
                    dr = time_iteration(self.hmodel.model, dr0=start, dprocess=dp, verbose=False, maxit=2000,
                                        interp_method="linear").dr
                    dr = improved_time_iteration(self.hmodel.model, dr0=dr, dprocess=dp, verbose=False,
                                                 interp_method="linear").dr
                except Exception:
                    dr = None
        if not finite(dr):
            raise RuntimeError(f"dolo found no rule at K = {K}")
        self._rule = dr
        return dr

    def population(self, K):
        """The stationary population at the prices that go with K, from dolo's rule."""
        dr = self.rule(K)
        return Population(lambda a, j: dr(j, a[:, None])[:, 0], self.P, self.population_grid)

    # ---- the equilibrium
    def equilibrium(self, xtol=1e-10):
        """The stationary equilibrium, with its statistics and diagnostics, as a dict."""
        ϑ = 1 / self.beta - 1
        self.population(self.capital_demand(0.03))  # a first rule, at an interest rate where dolo has no trouble
        excess = lambda K: self.population(K).mean_assets - K
        r_low = ϑ - 0.02
        while excess(self.capital_demand(r_low)) > 0:  # households still hold too much: the rate is lower still
            r_low -= 0.005
        K = brentq(excess, self.capital_demand(ϑ - 1e-5), self.capital_demand(r_low), xtol=xtol)
        return self.describe(K)

    def describe(self, K):
        pop, (r, w) = self.population(K), self.prices(K)
        dr, R, income = self._rule, 1 + r, w * np.exp(self.x)
        α, δ = self.alpha, self.delta
        consumption = lambda a, j: R * a + income[j] - dr(j, a[:, None])[:, 0]
        h = 1e-7
        mpc = lambda a, j: 1 - (dr(j, a[:, None] + h)[:, 0] - dr(j, a[:, None])[:, 0]) / (h * R)
        C, A = pop.mean_over_arrivals(consumption), pop.mean_assets
        Y = K**α * self.L ** (1 - α)
        Kc = self.capital_demand(1 / self.beta - 1)  # with complete markets, r is the time-preference rate
        shares = {f"{round(100 * q)}_percent": pop.share_of_richest(q) for q in (0.01, 0.05, 0.10, 0.20, 0.30)}
        # Euler equation errors where households hold assets: ĉ/c - 1, ĉ from the rule next period
        nu = pop.arriving_mass
        a, j = np.meshgrid(pop.grid, np.arange(len(self.x)), indexing="ij")
        a, j, weight = a.ravel(), j.ravel(), nu.ravel()
        keep = weight > 1e-14
        a, j, weight = a[keep], j[keep], weight[keep]
        c = np.empty(a.size)
        saved = np.empty(a.size)
        for s in range(len(self.x)):
            sel = j == s
            saved[sel] = dr(s, a[sel][:, None])[:, 0]
            c[sel] = R * a[sel] + income[s] - saved[sel]
        held = saved > 1e-8
        expected = np.zeros(a.size)
        for s_next in range(len(self.x)):
            c_next = R * saved + income[s_next] - dr(s_next, saved[:, None])[:, 0]
            expected += self.P[j, s_next] * c_next ** (-self.mu)
        error = (self.beta * R * expected) ** (-1 / self.mu) / c - 1
        weight_held = weight[held] / weight[held].sum()
        return {
            "sigma": self.sigma, "rho": self.rho, "mu": self.mu, "level": self.level, "settings": self.settings,
            "interest_rate": r, "wage": w, "capital": K, "labor_supply": self.L,
            "capital_relative_to_complete_markets": K / Kc,
            "saving_rate": 1 - C / ((r + δ) * A + w * self.L),
            "saving_rate_from_capital": δ * K / Y,
            "gini": pop.gini, "share_of_richest": shares,
            "share_at_borrowing_constraint": pop.mass_at_or_below(1e-8),
            "average_marginal_propensity_to_consume": pop.mean_over_arrivals(mpc),
            "diagnostics": {
                "euler_equation_error": {"mean_absolute": float(weight_held @ np.abs(error[held])),
                                         "largest_absolute": float(np.abs(error[held]).max())},
                "market_clearing_residual": A / K - 1,
                "goods_market_residual": (1 - C / ((r + δ) * A + w * self.L)) - δ * K / Y,
                "share_beyond_the_rule_s_grid": float(weight[a > self.settings["rule_top"]].sum()),
                "share_beyond_the_population_s_grid": pop.mass_beyond_top,
            },
        }
