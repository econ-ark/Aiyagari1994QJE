"""Aiyagari (1994), "Uninsured Idiosyncratic Risk and Aggregate Saving", solved with HARK.

    from aiyagari1994qje import Calibration, solve_equilibrium
    eq = solve_equilibrium(Calibration())  # Aiyagari's baseline, about ten seconds
    eq.interest_rate, eq.saving_rate_from_capital, eq.capital, eq.gini, eq.numbers()

The steps of the computation are public too: tauchen_chain, make_households, simulate,
capital_supply and capital_demand. The plot_* functions draw an Equilibrium's figures on
a matplotlib Axes and do nothing else.

The computation of the REMARK econ-ark/Aiyagari1994QJE: for the same calibration it
returns the numbers its notebook writes to baseline/numbers.json.

Each name is imported from its module when it is first used, so that a module that needs
no HARK, such as aiyagari1994qje.population, can be imported where HARK is not installed.
"""

import importlib

_EXPORTS = {
    "US_WEALTH_LORENZ": "figures",
    "plot_capital_market": "figures",
    "plot_consumption_functions": "figures",
    "plot_wealth_lorenz": "figures",
    "supply_rates": "figures",
    "AIYAGARI_TABLE_II": "model",
    "Calibration": "model",
    "Equilibrium": "model",
    "average_assets": "model",
    "capital_demand": "model",
    "capital_per_unit_of_labor": "model",
    "capital_supply": "model",
    "interest_rate": "model",
    "labor_supply": "model",
    "make_households": "model",
    "simulate": "model",
    "solve_equilibrium": "model",
    "table_ii": "model",
    "tauchen_chain": "model",
    "wage": "model",
    "LEVELS": "model",
    "Settings": "model",
    "solve_households": "model",
    "stationary_population": "model",
    "stationary_probabilities": "model",
    "rule_of": "model",
    "Population": "population",
    "asset_grid": "population",
    "evaluate_rule": "rules",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name):
    if name in _EXPORTS:
        value = getattr(importlib.import_module(f"aiyagari1994qje.{_EXPORTS[name]}"), name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'aiyagari1994qje' has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
