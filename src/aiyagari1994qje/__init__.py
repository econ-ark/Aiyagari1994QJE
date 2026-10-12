"""Aiyagari (1994), "Uninsured Idiosyncratic Risk and Aggregate Saving", solved with HARK.

    from aiyagari1994qje import Calibration, solve_equilibrium
    eq = solve_equilibrium(Calibration())  # Aiyagari's baseline, about ten seconds
    eq.interest_rate, eq.saving_rate_from_capital, eq.capital, eq.gini, eq.numbers()

The steps of the computation are public too: tauchen_chain, make_households, simulate,
capital_supply and capital_demand. The plot_* functions draw an Equilibrium's figures on
a matplotlib Axes and do nothing else.

The computation of the REMARK econ-ark/Aiyagari1994QJE: for the same calibration it
returns the numbers its notebook writes to baseline/numbers.json.
"""

from aiyagari1994qje.figures import (
    US_WEALTH_LORENZ,
    plot_capital_market,
    plot_consumption_functions,
    plot_wealth_lorenz,
    supply_rates,
)
from aiyagari1994qje.model import (
    AIYAGARI_TABLE_II,
    Calibration,
    Equilibrium,
    average_assets,
    capital_demand,
    capital_per_unit_of_labor,
    capital_supply,
    interest_rate,
    labor_supply,
    make_households,
    simulate,
    solve_equilibrium,
    table_ii,
    tauchen_chain,
    wage,
)

__all__ = [
    "AIYAGARI_TABLE_II",
    "Calibration",
    "Equilibrium",
    "US_WEALTH_LORENZ",
    "average_assets",
    "capital_demand",
    "capital_per_unit_of_labor",
    "capital_supply",
    "interest_rate",
    "labor_supply",
    "make_households",
    "plot_capital_market",
    "plot_consumption_functions",
    "plot_wealth_lorenz",
    "simulate",
    "solve_equilibrium",
    "supply_rates",
    "table_ii",
    "tauchen_chain",
    "wage",
]
