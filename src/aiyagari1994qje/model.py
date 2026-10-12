"""The Aiyagari (1994) economy, solved with HARK's MarkovConsumerType.

This is the computation of AiyagariMarkovHARK.ipynb, packaged: the same household
problem, the same simulation and the same equilibrium search, so that for the same
calibration it returns the same numbers.

The steps, each usable on its own:

    x, P = tauchen_chain(n=7, tau=0.6, sigma=0.2)    # the labor endowment process
    households = make_households(Calibration(), (x, P))
    capital_supply(households, r, calibration)       # households' assets at interest rate r
    capital_demand(r, calibration, L)                # firms' demand for capital
    eq = solve_equilibrium(Calibration())            # the r at which the two are equal
"""

import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq

from HARK.ConsumptionSaving.ConsMarkovModel import MarkovConsumerType, markov_constructor_dict
from HARK.distributions import DiscreteDistributionLabeled, make_tauchen_ar1


@dataclass(frozen=True)
class Calibration:
    """Parameters of the economy. The defaults are Aiyagari's baseline (Table II, σ = 0.2, ρ = 0.6, μ = 3)."""

    discount_factor: float = 0.96
    relative_risk_aversion: float = 3
    capital_share: float = 0.36
    depreciation_rate: float = 0.08
    income_persistence: float = 0.6  # of the log labor endowment, an AR(1)
    income_standard_deviation: float = 0.2  # unconditional, of the log labor endowment
    income_states: int = 7  # points in the Tauchen approximation
    tauchen_bound: float = 3.0  # outermost points, in unconditional standard deviations
    households: int = 1000  # simulated
    periods: int = 1000  # simulated
    periods_averaged: int = 700  # statistics use simulated periods (periods - periods_averaged) to (periods - 2)


# Aiyagari (1994), Table II: (net return to capital in percent, saving rate in percent),
# keyed by (income_standard_deviation, income_persistence, relative_risk_aversion)
AIYAGARI_TABLE_II = {
    (0.2, 0.0, 1): (4.1666, 23.67), (0.2, 0.0, 3): (4.1456, 23.71), (0.2, 0.0, 5): (4.0858, 23.83),
    (0.2, 0.3, 1): (4.1365, 23.73), (0.2, 0.3, 3): (4.0432, 23.91), (0.2, 0.3, 5): (3.9054, 24.19),
    (0.2, 0.6, 1): (4.0912, 23.82), (0.2, 0.6, 3): (3.8767, 24.25), (0.2, 0.6, 5): (3.5857, 24.86),
    (0.2, 0.9, 1): (3.9305, 24.14), (0.2, 0.9, 3): (3.2903, 25.51), (0.2, 0.9, 5): (2.5260, 27.36),
    (0.4, 0.0, 1): (4.0649, 23.87), (0.4, 0.0, 3): (3.7816, 24.44), (0.4, 0.0, 5): (3.4177, 25.22),
    (0.4, 0.3, 1): (3.9554, 24.09), (0.4, 0.3, 3): (3.4188, 25.22), (0.4, 0.3, 5): (2.8032, 26.66),
    (0.4, 0.6, 1): (3.7567, 24.50), (0.4, 0.6, 3): (2.7835, 26.71), (0.4, 0.6, 5): (1.8070, 29.37),
    (0.4, 0.9, 1): (3.3054, 25.47), (0.4, 0.9, 3): (1.2894, 31.00), (0.4, 0.9, 5): (-0.3456, 37.63),
}


# ---- households

def tauchen_chain(n=7, tau=0.6, sigma=0.2, bound=3.0):
    """Tauchen's n-state approximation to the log labor endowment, an AR(1) with persistence tau
    and unconditional standard deviation sigma; the outermost states are bound standard deviations out.

    Returns (x, P): the log labor endowments x_j, and P[i, j], the probability of state j next period from state i.
    """
    return make_tauchen_ar1(n, sigma * (1 - tau**2) ** 0.5, tau, bound)


def _chain(cal):
    return tauchen_chain(cal.income_states, cal.income_persistence, cal.income_standard_deviation, cal.tauchen_bound)


def make_households(calibration, chain=None):
    """The households: a HARK MarkovConsumerType with one Markov state per labor endowment.

    In state j a household earns exp(x_j). HARK solves the problem with the wage normalized
    to one, which loses nothing: with wage W, a household with market resources m consumes
    W c(m/W), and holds W times the assets. The returned households carry a drawn history of
    shocks, so every simulation of them, at any interest rate, replays the same shocks.

    chain: (x, P) from tauchen_chain; by default, the calibration's.
    """
    cal = calibration
    x, P = chain if chain is not None else _chain(cal)
    N = len(x)
    households = MarkovConsumerType(
        CRRA=cal.relative_risk_aversion,
        Rfree=[np.array(N * [1.03])],
        DiscFac=cal.discount_factor,
        LivPrb=[np.array(N * [1.0])],
        AgentCount=cal.households,
        kLogInitMean=0.0,  # initial assets are lognormal
        kLogInitStd=1.0,
        PermGroFacAgg=1.0,
        T_age=None,
        T_cycle=1,
        aXtraMin=0.001,  # the grid of end-of-period assets
        aXtraMax=20,
        aXtraExtra=np.array([0.005, 0.01]),
        aXtraNestFac=3,
        aXtraCount=48,
        BoroCnstArt=0.0,  # no borrowing
        CubicBool=False,
        vFuncBool=False,
        global_markov=False,
        cycles=0,  # infinite horizon
        PermGroFac=[np.array(N * [1.0])],
        MrkvPrbsInit=np.array(N * [1 / N]),
        # The labor endowment process is set here, so HARK's constructors for it are switched off
        constructors={**markov_constructor_dict, "IncShkDstn": None, "MrkvArray": None},
        MrkvArray=[P],
        IncShkDstn=[
            [
                DiscreteDistributionLabeled(
                    pmv=np.ones(1), atoms=np.array([[1.0], [np.exp(x_j)]]), var_names=["PermShk", "TranShk"]
                )
                for x_j in x
            ]
        ],
    )
    households.calibration = cal
    households.T_sim = cal.periods
    households.track_vars = ["aNrm", "cNrm", "TranShk"]
    with _quiet():
        households.make_shock_history()
    return households


@contextmanager
def _quiet():
    # Replaying a stored shock history, HARK warns that it does not store the aggregate
    # productivity level PlvlAgg; that level is constant here (PermGroFacAgg = 1).
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The option for reading shocks was activated")
        yield


def simulate(households, r):
    """Solve the households' problem at net interest rate r, then simulate them; the paths are in households.history."""
    households.Rfree = [np.array(households.MrkvArray[0].shape[0] * [1 + r])]
    households.solve()
    with _quiet():
        households.initialize_sim()
        households.simulate()
    return households


def _window(households):
    cal = households.calibration
    return slice(cal.periods - cal.periods_averaged, cal.periods - 1)


def _aggregate(households, var):
    # Sum over households, averaged over the periods that count (as AverageAggregateVar in the notebook)
    return np.mean(np.sum(households.history[var][_window(households)], axis=1))


def average_assets(households):
    """Mean end-of-period assets per household in the last simulation, in units of the wage."""
    return _aggregate(households, "aNrm") / households.AgentCount


def labor_supply(households):
    """L, the mean labor endowment in the simulation; the same at every interest rate."""
    return _aggregate(households, "TranShk") / households.AgentCount


# ---- firms: Cobb-Douglas, Y = K^α L^(1-α)

def capital_per_unit_of_labor(r, calibration):
    """k at which the marginal product of capital net of depreciation equals r."""
    α, δ = calibration.capital_share, calibration.depreciation_rate
    return ((1 + r - 1.0 + δ) / α) ** (1.0 / (α - 1.0))


def wage(r, calibration):
    """The wage W = (1 - α) k^α that goes with interest rate r."""
    α = calibration.capital_share
    return (1.0 - α) * capital_per_unit_of_labor(r, calibration) ** α


def interest_rate(k, calibration):
    """The net interest rate α k^(α - 1) - δ that goes with capital per unit of labor k."""
    α, δ = calibration.capital_share, calibration.depreciation_rate
    return 1.0 + α * k ** (α - 1.0) - δ - 1


def capital_demand(r, calibration, L):
    """Capital that firms demand at net interest rate r, with labor L."""
    return L * capital_per_unit_of_labor(np.asarray(r, dtype=float), calibration)


# ---- the capital market

def capital_supply(households, r, calibration=None):
    """Households' mean assets in levels at net interest rate(s) r: wage times assets in units of the wage.

    Each rate solves and simulates the households again, about a quarter of a second.
    """
    cal = calibration or households.calibration
    r = np.asarray(r, dtype=float)
    supply = [wage(r_i, cal) * average_assets(simulate(households, r_i)) for r_i in r.ravel()]
    return np.array(supply).reshape(r.shape)


def solve_equilibrium(calibration=None, verbose=False):
    """The stationary equilibrium: the interest rate at which households' saving equals firms' demand for capital.

    Brent's method on the gap between an assumed interest factor R and the one implied by the
    capital the households then hold, as in the notebook. About ten seconds at the defaults.
    """
    cal = calibration or Calibration()
    households = make_households(cal)
    α, δ = cal.capital_share, cal.depreciation_rate

    def gap(R):
        simulate(households, R - 1)
        K = _aggregate(households, "aNrm") * wage(R - 1, cal)  # assets are in units of the wage
        k = K / _aggregate(households, "TranShk")
        implied = 1.0 + α * k ** (α - 1.0) - δ
        if verbose:
            print("Input R:", R, "|| Implied R:", implied, "|| Difference", implied - R)
        return implied - R

    R = brentq(gap, 0.99, 1.05)
    households.track_vars = ["aNrm", "cNrm", "TranShk", "mNrm", "MPCnow"]
    simulate(households, R - 1)
    return Equilibrium(cal, R, households)


@dataclass
class Equilibrium:
    """The stationary equilibrium for a calibration; see solve_equilibrium."""

    calibration: Calibration
    interest_factor: float  # R* = 1 + r*
    households: MarkovConsumerType = field(repr=False)  # solved at R*, with the simulation at R* in households.history

    def __post_init__(self):
        cal, h, window = self.calibration, self.households.history, _window(self.households)
        x, self.transition_matrix = _chain(cal)
        self.labor_endowments = np.exp(x)
        self.interest_rate = self.interest_factor - 1
        self.time_preference_rate = 1 / cal.discount_factor - 1
        self.labor_supply = h["TranShk"][window].mean()
        self.capital_per_unit_of_labor = capital_per_unit_of_labor(self.interest_rate, cal)
        self.wage = wage(self.interest_rate, cal)
        self.capital = self.labor_supply * self.capital_per_unit_of_labor
        self.capital_complete_markets = self.labor_supply * capital_per_unit_of_labor(self.time_preference_rate, cal)
        # Wealth is end-of-period assets, in units of the wage; constrained households end the period with none
        self.wealth = np.sort(h["aNrm"][window].ravel())
        self.marginal_propensities_to_consume = h["MPCnow"][window].ravel().copy()
        consumption = h["cNrm"][window].mean()
        α, δ = cal.capital_share, cal.depreciation_rate
        # 1 - C/Y in the simulation, as the notebook's Table II; and δK/Y = δα/(r + δ), as Aiyagari's
        self.saving_rate = 1 - consumption / ((self.interest_rate + δ) * self.wealth.mean() + self.labor_supply)
        self.saving_rate_from_capital = δ * α / (self.interest_rate + δ)
        self.saving_rate_complete_markets = δ * α / (self.time_preference_rate + δ)

    def consumption(self, m, state=None):
        """Consumption at market resources m = (1 + r)a + Wℓ, in levels, in one labor endowment state or (state=None) each."""
        cFunc, W = self.households.solution[0].cFunc, self.wage
        m = np.asarray(m, dtype=float)
        if state is not None:
            return W * cFunc[state](m / W)
        return np.array([W * c(m / W) for c in cFunc])

    @property
    def average_marginal_propensity_to_consume(self):
        """Mean slope of the consumption function at each simulated household's market resources."""
        return self.marginal_propensities_to_consume.mean()

    @property
    def return_patience_factor(self):
        """Þ_R = (Rβ)^(1/μ)/R; 1 - Þ_R is the MPC of a consumer with no income risk and no borrowing constraint."""
        cal, R = self.calibration, self.interest_factor
        return (R * cal.discount_factor) ** (1 / cal.relative_risk_aversion) / R

    @property
    def gini(self):
        n, w = self.wealth.size, self.wealth
        return 2 * np.sum(np.arange(1, n + 1) * w) / (n * w.sum()) - (n + 1) / n

    def share_of_richest(self, fraction):
        """Share of wealth held by the richest `fraction` of households."""
        n = self.wealth.size
        return self.wealth[int(round((1 - fraction) * n)) :].sum() / self.wealth.sum()

    @property
    def share_at_borrowing_constraint(self):
        return np.mean(self.wealth == 0)

    def lorenz_curve(self, points=1001):
        """Population shares (poorest first) and the share of wealth they hold."""
        n = self.wealth.size
        population = np.linspace(0, 1, points)
        cumulative = np.concatenate(([0.0], np.cumsum(self.wealth))) / self.wealth.sum()
        return population, np.interp(population, np.arange(n + 1) / n, cumulative)

    def capital_demand(self, r):
        """Capital that firms demand at net interest rate r."""
        return capital_demand(r, self.calibration, self.labor_supply)

    def capital_supply(self, r):
        """Households' mean assets in levels at net interest rate(s) r; leaves the households at r*."""
        supply = capital_supply(self.households, r, self.calibration)
        simulate(self.households, self.interest_rate)
        return supply

    def numbers(self):
        """The equilibrium's numbers, with the calibration and definitions, as in baseline/numbers.json."""
        return _numbers(self)


def table_ii(verbose=False):
    """Interest rate and saving rate (1 - C/Y), in percent, for each cell of Aiyagari's Table II; about 3.5 minutes.

    Returns {(σ, ρ, μ): (interest rate, saving rate)}, with the keys of AIYAGARI_TABLE_II.
    """
    results = {}
    for σ, ρ, μ in AIYAGARI_TABLE_II:
        cal = Calibration(income_standard_deviation=σ, income_persistence=ρ, relative_risk_aversion=μ)
        eq = solve_equilibrium(cal, verbose=verbose)
        results[(σ, ρ, μ)] = (100 * eq.interest_rate, 100 * eq.saving_rate)
    return results


# ---- numbers.json

def _sig(x):
    return float(f"{x:.6g}")  # six significant digits


def _published(cal):
    # Aiyagari's Table II values, when the calibration is one of its cells
    defaults = Calibration()
    others = ("discount_factor", "capital_share", "depreciation_rate", "income_states", "tauchen_bound")
    if any(getattr(cal, name) != getattr(defaults, name) for name in others):
        return None
    cell = AIYAGARI_TABLE_II.get((cal.income_standard_deviation, cal.income_persistence, cal.relative_risk_aversion))
    return cell and {"interest_rate": _sig(cell[0] / 100), "saving_rate": _sig(cell[1] / 100)}


def _numbers(eq):
    cal = eq.calibration
    return {
        "description": "The stationary equilibrium of the Aiyagari (1994) economy at this calibration, computed by the "
        "aiyagari1994qje package (econ-ark/Aiyagari1994QJE)",
        "units": "Rates and shares are fractions (0.0386 is 3.86 percent). Capital, the wage and market resources are levels "
        "for a population of mass one. The labor endowment is not normalized, so labor supply L is about 1.02.",
        "calibration": {
            "discount_factor": cal.discount_factor,
            "relative_risk_aversion": cal.relative_risk_aversion,
            "capital_share": cal.capital_share,
            "depreciation_rate": cal.depreciation_rate,
            "income_persistence": cal.income_persistence,
            "income_standard_deviation": cal.income_standard_deviation,
            "income_states": cal.income_states,
            "tauchen_bound": cal.tauchen_bound,
            "borrowing_limit": 0.0,
            "labor_endowment_by_state": [_sig(v) for v in eq.labor_endowments],
        },
        "simulation": {
            "households": cal.households,
            "periods": cal.periods,
            "first_period_averaged": cal.periods - cal.periods_averaged,
            "last_period_averaged": cal.periods - 2,
            "observations_pooled": eq.wealth.size,
        },
        "equilibrium": {
            "interest_rate": _sig(eq.interest_rate),
            "saving_rate": _sig(eq.saving_rate),
            "saving_rate_from_capital": _sig(eq.saving_rate_from_capital),
            "wage": _sig(eq.wage),
            "labor_supply": _sig(eq.labor_supply),
            "capital": _sig(eq.capital),
            "capital_per_unit_of_labor": _sig(eq.capital_per_unit_of_labor),
        },
        "complete_markets": {
            "interest_rate": _sig(eq.time_preference_rate),
            "saving_rate": _sig(eq.saving_rate_complete_markets),
            "capital": _sig(eq.capital_complete_markets),
        },
        "capital_relative_to_complete_markets": _sig(eq.capital / eq.capital_complete_markets),
        "wealth_distribution": {
            "gini": _sig(eq.gini),
            "share_of_richest": {f"{round(100 * p)}_percent": _sig(eq.share_of_richest(p)) for p in (0.01, 0.05, 0.10, 0.20, 0.30)},
            "share_at_borrowing_constraint": _sig(eq.share_at_borrowing_constraint),
        },
        "average_marginal_propensity_to_consume": _sig(eq.average_marginal_propensity_to_consume),
        "return_patience_factor": _sig(eq.return_patience_factor),
        "perfect_foresight_marginal_propensity_to_consume": _sig(1 - eq.return_patience_factor),
        "aiyagari_1994": _published(cal),
        "definitions": {
            "simulation": "Households are simulated for periods 0 to periods - 1; the equilibrium's averages and the "
            "statistics of the distribution use every household in first_period_averaged to last_period_averaged",
            "equilibrium.interest_rate": "r*, the net return on capital at which households' saving equals firms' demand for capital",
            "equilibrium.saving_rate": "1 - C/Y in the simulation, with Y = (r* + depreciation_rate) K* + W L: as the REMARK's "
            "replication of Table II computes it",
            "equilibrium.saving_rate_from_capital": "δK*/Y* = depreciation_rate capital_share / (r* + depreciation_rate): "
            "gross investment over output in a steady state, as Aiyagari (1994) computes the saving rate",
            "equilibrium.wage": "W = (1 - capital_share) k*^capital_share",
            "equilibrium.labor_supply": "L, the mean labor endowment",
            "equilibrium.capital": "K* = L k*",
            "equilibrium.capital_per_unit_of_labor": "k*, at which the marginal product of capital net of depreciation equals r*",
            "complete_markets.interest_rate": "ϑ, the time-preference rate 1/discount_factor - 1",
            "complete_markets.saving_rate": "depreciation_rate capital_share / (ϑ + depreciation_rate)",
            "complete_markets.capital": "K^ϑ, the capital firms demand at the time-preference rate",
            "capital_relative_to_complete_markets": "K*/K^ϑ",
            "wealth_distribution": "Of end-of-period assets",
            "wealth_distribution.share_of_richest": "Share of wealth held by the richest 1, 5, 10, 20 and 30 percent of households",
            "wealth_distribution.share_at_borrowing_constraint": "Share of households whose end-of-period assets are zero",
            "average_marginal_propensity_to_consume": "Mean slope of the consumption function at each household's market "
            "resources m = (1 + r*) a + W ℓ, annual (a period is a year)",
            "return_patience_factor": "Þ_R = (R β)^(1/relative_risk_aversion) / R, at R = 1 + r* and β = discount_factor",
            "perfect_foresight_marginal_propensity_to_consume": "1 - Þ_R, the MPC of a consumer with no income risk and no borrowing constraint",
            "aiyagari_1994": "Aiyagari (1994), Table II, when the calibration is one of its cells (otherwise null)",
        },
    }
