"""The Aiyagari (1994) economy, solved with HARK's MarkovConsumerType.

This is the computation of AiyagariMarkovHARK.ipynb, packaged: the same household
problem and the same equilibrium search, so that for the same calibration and settings
it returns the same numbers.

What the economy is (Calibration) is kept apart from how it is solved (Settings). A
Settings says on which grid HARK solves the household's problem, and how the population
of households is computed: by simulating them, as the notebook did through version 1.1,
or as the stationary distribution on a grid of its own (population.py). The two grids
are unrelated: one is where the rule is computed, the other where households are.

The steps, each usable on its own:

    x, P = tauchen_chain(n=7, tau=0.6, sigma=0.2)    # the labor endowment process
    households = make_households(Calibration(), (x, P))
    capital_supply(households, r, calibration)       # households' assets at interest rate r
    capital_demand(r, calibration, L)                # firms' demand for capital
    eq = solve_equilibrium(Calibration())            # the r at which the two are equal
    eq = solve_equilibrium(Calibration(), settings=LEVELS["high"])   # the same, converged
"""

import warnings
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field

import numpy as np
from scipy.optimize import brentq

from HARK.ConsumptionSaving.ConsMarkovModel import MarkovConsumerType, markov_constructor_dict
from HARK.distributions import DiscreteDistributionLabeled, make_tauchen_ar1

from aiyagari1994qje.population import Population, asset_grid


@dataclass(frozen=True)
class Calibration:
    """Parameters of the economy. The defaults are Aiyagari's baseline (Table II, σ = 0.2, ρ = 0.6, μ = 3).

    The income process is Aiyagari's: the AR(1) he states, represented, as he computed it, by
    Tauchen's seven-state chain; the chain, not the AR(1), is the process the households face.
    households, periods and periods_averaged are settings of the simulation, not parameters of
    the economy; they stay here so that code written for version 1.1 still runs.
    """

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


@dataclass(frozen=True)
class Settings:
    """How the economy is solved. The defaults are the medium level (LEVELS["medium"]); LEVELS["original"]
    is the notebook's through version 1.1.

    asset_grid_*: the grid of end-of-period assets, above the borrowing limit and in units of the
        wage, on which HARK's endogenous grid method computes the consumption rule. HARK builds
        it: asset_grid_points points from asset_grid_min to asset_grid_max, equally spaced after
        log(1 + x) is taken asset_grid_nesting times, with asset_grid_extra added.
    cubic_interpolation: whether HARK interpolates the consumption rule between the endogenous grid's
        points with cubic splines that match the rule's slopes there (HARK's CubicBool), instead of
        linearly. Linear interpolation of a concave rule understates consumption between the points,
        so it overstates saving and understates the interest rate: at the medium level's 200 points by
        0.0018 percentage points at the baseline and 0.0076 at σ = 0.4, ρ = 0.9, μ = 5, measured against
        the reference solution (reference.py). Cubic interpolation brings that to about 0.00001 at the
        same points, at about twice the cost of a solve. The default stays linear so that the published
        numbers stay those of version 2.0.
    population: "simulation", Calibration.households households simulated for Calibration.periods
        periods; or "histogram", the stationary distribution on a grid of its own (population.py):
        histogram_points points from 0 to histogram_max, in units of the wage, spaced as
        asset_grid(histogram_max, histogram_points, histogram_curvature).
    seed: the simulation's random seed (HARK's default is 0).
    """

    asset_grid_points: int = 200
    asset_grid_max: float = 100.0
    asset_grid_min: float = 0.001
    asset_grid_nesting: int = 3
    asset_grid_extra: tuple = (0.005, 0.01)
    cubic_interpolation: bool = False
    population: str = "histogram"
    histogram_points: int = 2000
    histogram_max: float = 300.0
    histogram_curvature: float = 3.0
    seed: int = 0

    def __post_init__(self):
        if self.population not in ("simulation", "histogram"):
            raise ValueError(f"population must be 'simulation' or 'histogram', not {self.population!r}")


# Settings by name. "original" is the notebook's through version 1.1: a coarse grid for the rule, and a
# simulation whose 300 periods of burn-in are too few at interest rates near the time-preference rate.
# low, medium and high refine the rule's grid and compute the population as a histogram; the equilibrium
# converges as the level rises.
LEVELS = {
    "original": Settings(asset_grid_points=48, asset_grid_max=20.0, population="simulation"),
    "low": Settings(asset_grid_points=100, asset_grid_max=100.0, histogram_points=1000),
    "medium": Settings(),
    "high": Settings(asset_grid_points=800, asset_grid_max=200.0, histogram_points=3000),
}


# Aiyagari (1994), Table II: (net return to capital in percent, saving rate in percent),
# keyed by (income_standard_deviation, income_persistence, relative_risk_aversion).
# Every saving rate is 100 δα/(r + δ), rounded: the table holds one number per cell.
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


def stationary_probabilities(P):
    """The stationary distribution of the chain with transition matrix P."""
    values, vectors = np.linalg.eig(np.asarray(P).T)
    pi = np.real(vectors[:, np.argmin(np.abs(values - 1))])
    return pi / pi.sum()


def make_households(calibration, chain=None, settings=None):
    """The households: a HARK MarkovConsumerType with one Markov state per labor endowment.

    In state j a household earns exp(x_j). HARK solves the problem with the wage normalized
    to one, which loses nothing: with wage W, a household with market resources m consumes
    W c(m/W), and holds W times the assets. When the population is simulated, the returned
    households carry a drawn history of shocks, so every simulation of them, at any interest
    rate, replays the same shocks.

    chain: (x, P) from tauchen_chain; by default, the calibration's.
    settings: a Settings; by default, the medium level.
    """
    cal, s = calibration, settings or Settings()
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
        aXtraMin=s.asset_grid_min,  # the grid of end-of-period assets
        aXtraMax=s.asset_grid_max,
        aXtraExtra=np.array(s.asset_grid_extra),
        aXtraNestFac=s.asset_grid_nesting,
        aXtraCount=s.asset_grid_points,
        BoroCnstArt=0.0,  # no borrowing
        seed=s.seed,
        CubicBool=s.cubic_interpolation,
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
    households.settings = s
    households.chain = (np.asarray(x), np.asarray(P))
    households.T_sim = cal.periods
    households.track_vars = ["aNrm", "cNrm", "TranShk"]
    if s.population == "simulation":
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


def solve_households(households, r):
    """Solve the households' problem at net interest rate r; the rule is households.solution[0].cFunc."""
    households.Rfree = [np.array(households.MrkvArray[0].shape[0] * [1 + r])]
    households.solve()
    return households


def simulate(households, r):
    """Solve the households' problem at net interest rate r, then simulate them; the paths are in households.history.

    The first simulation of households made without a shock history draws one, which later simulations replay."""
    households.Rfree = [np.array(households.MrkvArray[0].shape[0] * [1 + r])]
    households.solve()
    with _quiet():
        if not households.read_shocks:
            households.make_shock_history()
        households.initialize_sim()
        households.simulate()
    return households


def stationary_population(households, r):
    """Solve the households' problem at net interest rate r, then compute their stationary population on
    the histogram grid of their settings, in units of the wage (population.Population)."""
    solve_households(households, r)
    s, (x, P) = households.settings, households.chain
    R, income, rule = 1 + r, np.exp(x), households.solution[0].cFunc
    grid = asset_grid(s.histogram_max, s.histogram_points, s.histogram_curvature)

    def next_assets(a, j):
        m = R * a + income[j]
        return m - rule[j](m)

    return Population(next_assets, P, grid)


def rule_of(households):
    """The households' consumption rule as HARK holds it, written out as data (aiyagari1994qje.rules evaluates it
    without HARK): for each income state, the lower envelope of the unconstrained rule, linear between its knots and
    approaching its limiting line above the last, and the constraint c = m; market resources and consumption are in
    units of the wage.

    In econ-ark 0.17.2 the unconstrained rule's first knot is (0, 0) and the next ones lie at negative market
    resources, where HARK's endogenous grid starts from the one-period natural limit; HARK finds the segment by a
    binary search that is right for every positive m, which is all a household ever has, and so does rules.evaluate.

    Only a linearly interpolated rule can be written out this way; a rule solved with cubic_interpolation raises.
    """
    if getattr(households, "CubicBool", False):
        raise NotImplementedError("rule_of writes out linearly interpolated rules only; this one was solved with "
                                  "cubic_interpolation=True")
    states = []
    for envelope in households.solution[0].cFunc:
        pieces = []
        for f in envelope.functions:
            piece = {"form": "linear-interpolation", "x": [float(v) for v in f.x_list], "y": [float(v) for v in f.y_list],
                     "below": "extend" if f.lower_extrap else "undefined", "above": "extend"}
            if getattr(f, "decay_extrap", False):
                piece["above"] = {"intercept": float(f.intercept_limit), "slope": float(f.slope_limit),
                                  "gap": float(f.decay_extrap_A), "decay": float(f.decay_extrap_B)}
            pieces.append(piece)
        states.append({"form": "lower-envelope", "of": pieces})
    x, _ = households.chain
    return {
        "description": "HARK's consumption rule c(m) in each income state, as HARK holds it",
        "units": "market resources m and consumption c in units of the wage; in levels, consumption at market "
                 "resources M is W c(M / W)",
        "interest_factor": float(households.Rfree[0][0]),
        "labor_endowment_by_state": [float(v) for v in np.exp(x)],
        "states": states,
    }


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

    Each rate solves the households again, and simulates them or computes their stationary
    population, as their settings say: about a quarter of a second, or a second or two.
    """
    cal = calibration or households.calibration
    r = np.asarray(r, dtype=float)
    if households.settings.population == "histogram":
        supply = [wage(r_i, cal) * stationary_population(households, r_i).mean_assets for r_i in r.ravel()]
    else:
        supply = [wage(r_i, cal) * average_assets(simulate(households, r_i)) for r_i in r.ravel()]
    return np.array(supply).reshape(r.shape)


def solve_equilibrium(calibration=None, verbose=False, settings=None):
    """The stationary equilibrium: the interest rate at which households' saving equals firms' demand for capital.

    Brent's method on the gap between an assumed interest factor R and the one implied by the
    capital the households then hold, as in the notebook. At the default, medium level, about half
    a minute; at LEVELS["high"], about a minute; with LEVELS["original"], about ten seconds.
    """
    cal, s = calibration or Calibration(), settings or Settings()
    households = make_households(cal, settings=s)
    α, δ = cal.capital_share, cal.depreciation_rate

    if s.population == "simulation":
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
        return Equilibrium(cal, R, households, settings=s)

    x, P = households.chain
    L = stationary_probabilities(P) @ np.exp(x)  # the chain's mean labor endowment

    def gap(R):
        population = stationary_population(households, R - 1)
        k = wage(R - 1, cal) * population.mean_assets / L
        implied = 1.0 + α * k ** (α - 1.0) - δ
        if verbose:
            print("Input R:", R, "|| Implied R:", implied, "|| Difference", implied - R)
        return implied - R

    # Above the time-preference rate there is no stationary population, so the search stays below it
    R = brentq(gap, 0.99, 1 / cal.discount_factor - 1e-4)
    return Equilibrium(cal, R, households, settings=s, population=stationary_population(households, R - 1))


@dataclass
class Equilibrium:
    """The stationary equilibrium for a calibration; see solve_equilibrium."""

    calibration: Calibration
    interest_factor: float  # R* = 1 + r*
    households: MarkovConsumerType = field(repr=False)  # solved at R*, with the simulation at R* in households.history
    settings: Settings = None  # by default, the households'
    population: Population = field(default=None, repr=False)  # the stationary population, when it is a histogram

    def __post_init__(self):
        if self.settings is None:
            self.settings = getattr(self.households, "settings", None) or LEVELS["original"]
        cal = self.calibration
        x, self.transition_matrix = _chain(cal)
        self.labor_endowments = np.exp(x)
        self.interest_rate = self.interest_factor - 1
        self.time_preference_rate = 1 / cal.discount_factor - 1
        α, δ = cal.capital_share, cal.depreciation_rate
        if self.population is None:  # the population is the simulation's
            h, window = self.households.history, _window(self.households)
            self.labor_supply = h["TranShk"][window].mean()
        else:
            self.labor_supply = stationary_probabilities(self.transition_matrix) @ self.labor_endowments
        self.capital_per_unit_of_labor = capital_per_unit_of_labor(self.interest_rate, cal)
        self.wage = wage(self.interest_rate, cal)
        self.capital = self.labor_supply * self.capital_per_unit_of_labor
        self.capital_complete_markets = self.labor_supply * capital_per_unit_of_labor(self.time_preference_rate, cal)
        if self.population is None:
            # Wealth is end-of-period assets, in units of the wage; constrained households end the period with none
            self.wealth = np.sort(h["aNrm"][window].ravel())
            self.marginal_propensities_to_consume = h["MPCnow"][window].ravel().copy()
            consumption = h["cNrm"][window].mean()
            mean_wealth = self.wealth.mean()
        else:
            self.wealth = None
            self.marginal_propensities_to_consume = None
            rule, R = self.households.solution[0].cFunc, self.interest_factor
            income = self.labor_endowments
            consumption = self.population.mean_over_arrivals(lambda a, j: rule[j](R * a + income[j]))
            self._average_mpc = self.population.mean_over_arrivals(lambda a, j: rule[j].derivative(R * a + income[j]))
            mean_wealth = self.population.mean_assets
        # 1 - C/Y in the population, as the notebook's Table II; and δK/Y = δα/(r + δ), as Aiyagari's
        self.saving_rate = 1 - consumption / ((self.interest_rate + δ) * mean_wealth + self.labor_supply)
        self.saving_rate_from_capital = δ * α / (self.interest_rate + δ)
        self.saving_rate_complete_markets = δ * α / (self.time_preference_rate + δ)

    def rule(self):
        """The equilibrium's consumption rule as HARK holds it, written out as data, with the wage; see rule_of."""
        rule = rule_of(self.households)
        rule["wage"] = float(self.wage)
        return rule

    def consumption(self, m, state=None):
        """Consumption at market resources m = (1 + r)a + Wℓ, in levels, in one labor endowment state or (state=None) each."""
        cFunc, W = self.households.solution[0].cFunc, self.wage
        m = np.asarray(m, dtype=float)
        if state is not None:
            return W * cFunc[state](m / W)
        return np.array([W * c(m / W) for c in cFunc])

    @property
    def average_marginal_propensity_to_consume(self):
        """Mean slope of the consumption function at each household's market resources."""
        if self.population is not None:
            return self._average_mpc
        return self.marginal_propensities_to_consume.mean()

    @property
    def return_patience_factor(self):
        """Þ_R = (Rβ)^(1/μ)/R; 1 - Þ_R is the MPC of a consumer with no income risk and no borrowing constraint."""
        cal, R = self.calibration, self.interest_factor
        return (R * cal.discount_factor) ** (1 / cal.relative_risk_aversion) / R

    @property
    def gini(self):
        if self.population is not None:
            return self.population.gini
        n, w = self.wealth.size, self.wealth
        return 2 * np.sum(np.arange(1, n + 1) * w) / (n * w.sum()) - (n + 1) / n

    def share_of_richest(self, fraction):
        """Share of wealth held by the richest `fraction` of households."""
        if self.population is not None:
            return self.population.share_of_richest(fraction)
        n = self.wealth.size
        return self.wealth[int(round((1 - fraction) * n)) :].sum() / self.wealth.sum()

    @property
    def share_at_borrowing_constraint(self):
        if self.population is not None:
            return self.population.mass_at_or_below(0.0)
        return np.mean(self.wealth == 0)

    def lorenz_curve(self, points=1001):
        """Population shares (poorest first) and the share of wealth they hold."""
        if self.population is not None:
            return self.population.lorenz_curve(points)
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
        if self.population is not None:
            solve_households(self.households, self.interest_rate)
        else:
            simulate(self.households, self.interest_rate)
        return supply

    # ---- what was solved, and how well

    def effective_member(self):
        """The economy the households actually face: the chain that represents the AR(1), with its moments."""
        x, P = self.households.chain
        pi = stationary_probabilities(P)
        sd = float(np.sqrt(pi @ (x - pi @ x) ** 2))
        autocorrelation = float((pi * (x - pi @ x)) @ (P @ (x - pi @ x))) / sd**2
        return {
            "income_process": f"Tauchen's method: {len(x)} states, the outermost {self.calibration.tauchen_bound:g} "
            "unconditional standard deviations out",
            "log_labor_endowment_by_state": [float(v) for v in x],
            "transition_matrix": [[float(p) for p in row] for row in P],
            "stationary_probabilities": [float(p) for p in pi],
            "mean_labor_endowment": float(pi @ np.exp(x)),
            "standard_deviation_of_log_endowment": sd,
            "autocorrelation_of_log_endowment": autocorrelation,
            "borrowing_limit": 0.0,
        }

    def _population_points(self):
        """(m, state, weight) of the households at the start of a period, in units of the wage."""
        if self.population is not None:
            nu = self.population.arriving_mass
            R, income = self.interest_factor, self.labor_endowments
            m = R * self.population.grid[:, None] + income[None, :]
            state = np.broadcast_to(np.arange(income.size), m.shape)
            keep = nu > 1e-14
            return m[keep], state[keep], nu[keep] / nu[keep].sum()
        h, window = self.households.history, _window(self.households)
        m, income = h["mNrm"][window].ravel(), h["TranShk"][window].ravel()
        # a household's state is the one whose income it receives: TranShk is exactly exp(x_j) in state j
        state = np.abs(income[:, None] - self.labor_endowments[None, :]).argmin(axis=1)
        return m, state, np.full(m.size, 1 / m.size)

    def euler_equation_errors(self):
        """The rule's errors in the Euler equation, where households hold assets: ĉ/c - 1, with ĉ the
        consumption the Euler equation implies, u'(ĉ) = βR E[u'(c')], from the rule itself next period.
        Returns (m, state, weight, error) at the population's points, constrained points omitted."""
        cal, R = self.calibration, self.interest_factor
        rule, P, income = self.households.solution[0].cFunc, self.transition_matrix, self.labor_endowments
        μ, β = cal.relative_risk_aversion, cal.discount_factor
        m, state, weight = self._population_points()
        c = np.empty_like(m)
        for j in range(income.size):
            c[state == j] = rule[j](m[state == j])
        a = m - c
        held = a > 1e-10
        expected = np.zeros(m.size)
        for j_next in range(income.size):
            m_next = R * a + income[j_next]
            expected += P[state, j_next] * rule[j_next](m_next) ** (-μ)
        implied = (β * R * expected) ** (-1 / μ)
        return m[held], state[held], weight[held] / weight[held].sum(), implied[held] / c[held] - 1

    def diagnostics(self):
        """Checks that need no reference solution."""
        _, _, weight, error = self.euler_equation_errors()
        m, state, w = self._population_points()
        rule = self.households.solution[0].cFunc
        last_knot = np.array([f.functions[0].x_list[-1] for f in rule])
        cal = self.calibration
        L = self.labor_supply
        if self.population is not None:
            supply = self.wage * self.population.mean_assets
        else:
            supply = self.wage * self.wealth.mean()
        demand = capital_demand(self.interest_rate, cal, L)
        return {
            "euler_equation_error": {
                "mean_absolute": float(weight @ np.abs(error)),
                "largest_absolute": float(np.abs(error).max()),
            },
            "market_clearing_residual": float(supply / demand - 1),
            "goods_market_residual": float(self.saving_rate - self.saving_rate_from_capital),
            "share_beyond_the_rule_s_grid": float(w[m > last_knot[state]].sum()),
            "share_beyond_the_population_s_grid": None if self.population is None else self.population.mass_beyond_top,
        }

    def numbers(self):
        """The equilibrium's numbers, with the calibration and definitions, as in baseline/numbers.json."""
        return _numbers(self)


def table_ii(verbose=False, settings=None):
    """Interest rate and saving rate (1 - C/Y), in percent, for each cell of Aiyagari's Table II: about ten
    minutes at the default, medium level, and 3.5 with LEVELS["original"].

    Returns {(σ, ρ, μ): (interest rate, saving rate)}, with the keys of AIYAGARI_TABLE_II.
    """
    results = {}
    for σ, ρ, μ in AIYAGARI_TABLE_II:
        cal = Calibration(income_standard_deviation=σ, income_persistence=ρ, relative_risk_aversion=μ)
        eq = solve_equilibrium(cal, verbose=verbose, settings=settings)
        results[(σ, ρ, μ)] = (100 * eq.interest_rate, 100 * eq.saving_rate)
    return results


# ---- numbers.json

def _sig(x):
    return float(f"{x:.6g}")  # six significant digits


def _rounded(tree):
    # six significant digits for every number in a nested dict; None stays None
    if isinstance(tree, dict):
        return {k: _rounded(v) for k, v in tree.items()}
    return None if tree is None else _sig(tree)


def _published(cal):
    # Aiyagari's Table II values, when the calibration is one of its cells
    defaults = Calibration()
    others = ("discount_factor", "capital_share", "depreciation_rate", "income_states", "tauchen_bound")
    if any(getattr(cal, name) != getattr(defaults, name) for name in others):
        return None
    cell = AIYAGARI_TABLE_II.get((cal.income_standard_deviation, cal.income_persistence, cal.relative_risk_aversion))
    return cell and {"interest_rate": _sig(cell[0] / 100), "saving_rate": _sig(cell[1] / 100)}


def _numbers(eq):
    cal, s = eq.calibration, eq.settings
    simulated = eq.population is None
    numbers = {
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
        "effective_member": eq.effective_member(),
        "settings": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(s).items()},
    }
    if simulated:
        numbers["simulation"] = {
            "households": cal.households,
            "periods": cal.periods,
            "first_period_averaged": cal.periods - cal.periods_averaged,
            "last_period_averaged": cal.periods - 2,
            "observations_pooled": eq.wealth.size,
        }
    numbers.update({
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
        "diagnostics": _rounded(eq.diagnostics()),
        "aiyagari_1994": _published(cal),
        "definitions": {
            "effective_member": "The income process the households face: the chain that represents the AR(1) of the "
            "calibration, with its own moments, which differ from the AR(1)'s",
            "settings": "How the economy was solved: the grid of HARK's rule (asset_grid_*, in units of the wage), whether "
            "the rule is interpolated cubically or linearly (cubic_interpolation) and how the population was computed "
            "(population: simulation or histogram; histogram_*, its grid)",
            "simulation": "Households are simulated for periods 0 to periods - 1; the equilibrium's averages and the "
            "statistics of the distribution use every household in first_period_averaged to last_period_averaged",
            "equilibrium.interest_rate": "r*, the net return on capital at which households' saving equals firms' demand for capital",
            "equilibrium.saving_rate": "1 - C/Y in the population, with Y = (r* + depreciation_rate) K* + W L: as the REMARK's "
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
            "diagnostics.euler_equation_error": "ĉ/c - 1 where households hold assets, with ĉ the consumption that the Euler "
            "equation implies from the rule next period: its mean absolute value over the population and its largest",
            "diagnostics.market_clearing_residual": "households' assets over firms' capital, minus one, at r*",
            "diagnostics.goods_market_residual": "(1 - C/Y) - δK/Y: zero in an exact stationary equilibrium, where C + δK = Y",
            "diagnostics.share_beyond_the_rule_s_grid": "Share of households whose market resources lie above the last "
            "point of HARK's rule, where the rule is extrapolated",
            "diagnostics.share_beyond_the_population_s_grid": "Share of the histogram's households whose assets would lie "
            "above its grid (null for a simulation)",
            "aiyagari_1994": "Aiyagari (1994), Table II, when the calibration is one of its cells (otherwise null)",
        },
    })
    if not simulated:
        del numbers["definitions"]["simulation"]
    return numbers
