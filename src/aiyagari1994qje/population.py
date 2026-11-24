"""The stationary population of the Aiyagari economy, from any toolkit's consumption rule.

The population is computed on a grid of its own: the grid on which a toolkit solves the
household's problem says nothing about where households are, and the grid of the population
says nothing about how the rule is solved. Every toolkit's rule is turned into a population by
this one code, so that two toolkits' populations differ only because their rules do.

The method is Young's (2010) lottery: a household that would end next period with assets a'
between two points of the grid is placed on the two points, with the probabilities that keep
its expected assets equal to a'. The population is the stationary distribution of the
resulting Markov chain on (assets, income state), solved directly.

A state of the population is (k, j): end-of-period assets grid[k], chosen in income state j.
Next period the household moves to state j' with probability P[j, j'], receives its income,
and ends the period with assets next_assets(grid[k], j').

Only numpy and scipy are used, so that this module runs in every environment of the REMARK,
the DolARK notebook's included.
"""

import numpy as np
import scipy.sparse
import scipy.sparse.linalg


def asset_grid(top, points, curvature=3.0, bottom=0.0):
    """Points of end-of-period assets from bottom to top, denser near the bottom, where the
    borrowing constraint makes the distribution change fastest: bottom + (top - bottom) (k/(points - 1))^curvature."""
    return bottom + (top - bottom) * (np.arange(points) / (points - 1)) ** curvature


def _lottery(grid, values):
    """For each value, the lower grid index and the probability of the upper point."""
    clipped = np.clip(values, grid[0], grid[-1])
    lower = np.clip(np.searchsorted(grid, clipped, side="right") - 1, 0, grid.size - 2)
    upper_probability = (clipped - grid[lower]) / (grid[lower + 1] - grid[lower])
    return lower, np.clip(upper_probability, 0.0, 1.0)


class Population:
    """The stationary population on a grid of end-of-period assets.

    next_assets(a, j_next): the end-of-period assets, next period, of households that end this
        period with assets a (an array) and are in income state j_next next period
    transition_matrix: P[j, j'], the probability of income state j' next period from state j
    grid: the population's grid of end-of-period assets, increasing; grid[0] is the borrowing limit
    """

    def __init__(self, next_assets, transition_matrix, grid):
        self.grid = np.asarray(grid, dtype=float)
        self.transition_matrix = P = np.asarray(transition_matrix, dtype=float)
        K, S = self.grid.size, P.shape[0]
        # where each household goes, before the lottery: next_values[k, j'] = next_assets(grid[k], j')
        self.next_values = np.column_stack([np.asarray(next_assets(self.grid, j), dtype=float) for j in range(S)])
        rows, cols, probs = [], [], []
        k = np.arange(K)
        for j_next in range(S):
            lower, upper_probability = _lottery(self.grid, self.next_values[:, j_next])
            for j in range(S):
                if P[j, j_next] == 0.0:
                    continue
                rows += [j * K + k, j * K + k]
                cols += [j_next * K + lower, j_next * K + lower + 1]
                probs += [P[j, j_next] * (1.0 - upper_probability), P[j, j_next] * upper_probability]
        T = scipy.sparse.csr_matrix(
            (np.concatenate(probs), (np.concatenate(rows), np.concatenate(cols))), shape=(S * K, S * K))
        self.mass = self._stationary(T).reshape(S, K).T  # mass[k, j]
        self._T = T

    @staticmethod
    def _stationary(T):
        """The row vector m with m T = m and sum(m) = 1, by a sparse direct solve."""
        n = T.shape[0]
        A = (T.T - scipy.sparse.identity(n, format="csr")).tolil()
        A[n - 1, :] = np.ones(n)
        b = np.zeros(n)
        b[-1] = 1.0
        m = scipy.sparse.linalg.spsolve(A.tocsc(), b)
        m = np.where(m < 0, 0.0, m)  # round-off below zero
        return m / m.sum()

    # ---- the residual of the fixed point, a check on the solve
    @property
    def stationarity_residual(self):
        """max |m T - m| over states: zero for an exact solve."""
        m = self.mass.T.ravel()
        return float(np.abs(self._T.T @ m - m).max())

    # ---- the population at the start of a period
    @property
    def arriving_mass(self):
        """mass_next[k, j']: households that ended last period at grid[k] and are in state j' now."""
        return self.mass @ self.transition_matrix

    def mean_over_arrivals(self, f):
        """The population mean of f(a, j'), where a is last period's end-of-period assets (on the
        grid) and j' the current state: for example consumption, from a toolkit's rule."""
        nu = self.arriving_mass
        S = self.transition_matrix.shape[0]
        return float(sum(nu[:, j] @ np.asarray(f(self.grid, j), dtype=float) for j in range(S)))

    # ---- end-of-period assets
    @property
    def asset_mass(self):
        """Mass at each grid point of end-of-period assets, over income states."""
        return self.mass.sum(axis=1)

    @property
    def mean_assets(self):
        return float(self.asset_mass @ self.grid)

    @property
    def mass_beyond_top(self):
        """Mass of households whose assets next period would lie above the grid's top (they are put
        at the top): zero when the grid covers the population."""
        nu = self.arriving_mass
        return float(nu[self.next_values > self.grid[-1]].sum())

    def mass_at_or_below(self, level):
        """Mass of households that end the period with assets at or below level, from their
        exact assets before the lottery."""
        nu = self.arriving_mass
        return float(nu[self.next_values <= level].sum())

    def _lorenz_points(self):
        # The Lorenz curve is linear between these points: the population and the assets held, poorest first,
        # cumulated over the grid. Where a grid point has no mass, two points coincide, which interpolation allows.
        w, a = self.asset_mass, self.grid
        population = np.concatenate(([0.0], np.cumsum(w)))
        wealth = np.concatenate(([0.0], np.cumsum(w * a))) / (w @ a)
        return population / population[-1], wealth

    def lorenz_curve(self, points=1001):
        """Population shares (poorest first) and the share of assets they hold."""
        population, wealth = self._lorenz_points()
        shares = np.linspace(0, 1, points)
        return shares, np.interp(shares, population, wealth)

    @property
    def gini(self):
        """Gini coefficient of end-of-period assets: one minus twice the area under the Lorenz curve."""
        population, wealth = self._lorenz_points()
        return float(1.0 - np.sum(np.diff(population) * (wealth[1:] + wealth[:-1])))

    def share_of_richest(self, fraction):
        """Share of assets held by the richest fraction of households."""
        population, wealth = self._lorenz_points()
        return float(1.0 - np.interp(1.0 - fraction, population, wealth))
