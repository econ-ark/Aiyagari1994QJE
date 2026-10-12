"""Figures of an Equilibrium.

Each function draws on the Axes it is given (or on a new one) and returns it. None sets
styles or rcParams, saves or shows a figure: the caller does that.
"""

import matplotlib.pyplot as plt
import numpy as np

# Krusell and Smith (1998, Table 1): the richest 30, 20, 10, 5 and 1 percent of U.S. households
# hold 88, 79, 64, 51 and 30 percent of wealth. As points on the Lorenz curve:
US_WEALTH_LORENZ = {
    "population_share": [0.70, 0.80, 0.90, 0.95, 0.99],
    "wealth_share": [0.12, 0.21, 0.36, 0.49, 0.70],
}


def supply_rates(eq, points=48, r_min=-0.005, closest=0.00015):
    """Interest rates at which to compute the supply of capital: from r_min up to `closest` below the
    time-preference rate ϑ, spaced geometrically toward ϑ, where the supply bends and grows without limit."""
    ϑ = eq.time_preference_rate
    return ϑ - (ϑ - r_min) * (closest / (ϑ - r_min)) ** (np.arange(points) / (points - 1))


def _axes(ax):
    return ax if ax is not None else plt.subplots()[1]


def plot_consumption_functions(eq, ax=None, m_max=12, c_max=2.2):
    """Consumption against market resources, one line per labor endowment state, with the 45-degree line."""
    ax = _axes(ax)
    m = np.linspace(0, m_max, 1201)
    N = eq.labor_endowments.size
    colors = plt.cm.viridis(np.linspace(0, 0.85, N))
    for j in range(N):
        rank = " (lowest)" if j == 0 else " (highest)" if j == N - 1 else ""
        ax.plot(m, eq.consumption(m, j), color=colors[j], label=f"ℓ = {eq.labor_endowments[j]:.2f}{rank}")
    ax.plot(m, m, color="gray", linestyle="--", linewidth=1, label="45-degree line, c = m")
    ax.set(xlim=(0, m_max), ylim=(0, c_max), xlabel="Market resources, m", ylabel="Consumption, c")
    ax.legend(title="Labor productivity", loc="lower right", fontsize="small")
    return ax


def plot_wealth_lorenz(eq, ax=None, us_data=True):
    """The Lorenz curve of wealth, with (us_data=True) Krusell and Smith's U.S. shares."""
    ax = _axes(ax)
    population, lorenz = eq.lorenz_curve()
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1, label="Equal wealth (45-degree line)")
    ax.plot(population, lorenz, color="C0", label="Model")
    if us_data:
        ax.plot(US_WEALTH_LORENZ["population_share"], US_WEALTH_LORENZ["wealth_share"], "o", color="C3",
                label="U.S. data (Krusell and Smith 1998)")
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal", xlabel="Share of households, poorest first", ylabel="Share of wealth")
    ax.legend(loc="upper left", fontsize="small")
    return ax


def plot_capital_market(eq, ax=None, supply=None, K_max=14, r_min=-0.005, r_max=0.05):
    """Supply of and demand for capital against the interest rate in percent.

    supply: (rates, capital), with capital from eq.capital_supply; when not given, computed
    at supply_rates(eq) (about 25 seconds). Marks the equilibrium K* and the complete-markets
    capital K^ϑ, where demand meets the time-preference rate ϑ = 1/β - 1.
    """
    ax = _axes(ax)
    if supply is None:
        rates = supply_rates(eq, r_min=r_min)
        supply = (rates, eq.capital_supply(rates))
    r_supply, K_supply = supply
    r_demand = np.linspace(r_min, r_max, 221)
    ϑ, bottom = eq.time_preference_rate, 100 * r_min
    ax.plot(K_supply, 100 * np.asarray(r_supply), color="C0")
    ax.plot(eq.capital_demand(r_demand), 100 * r_demand, color="C1")
    ax.axhline(100 * ϑ, color="k", linestyle="--", linewidth=1)
    ax.text(1.6, 1.0, "Supply of capital\n(household saving)", color="C0")
    ax.text(9.2, 1.0, "Demand for capital\n(firms)", color="C1")
    ax.text(K_max - 0.2, 100 * ϑ + 0.12, f"Complete markets: r = 1/β − 1 = {100 * ϑ:.2f}%", ha="right", fontsize="small")
    for K, r, name, side in [(eq.capital, eq.interest_rate, "$K^*$", "left"),
                             (eq.capital_complete_markets, ϑ, r"$K^\vartheta$", "right")]:
        ax.plot(K, 100 * r, "o", color="k", markersize=4)
        ax.vlines(K, bottom, 100 * r, colors="gray", linestyles=":", linewidth=1)
        ax.annotate(name, (K, bottom), xytext=(4 if side == "left" else -4, 4), textcoords="offset points", ha=side)
    ax.set(xlim=(0, K_max), ylim=(bottom, 100 * r_max), xlabel="Capital, K", ylabel="Interest rate, r (percent)")
    return ax
