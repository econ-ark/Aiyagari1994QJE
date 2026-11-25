# The Aiyagari economy, stated exactly

This is the economy the REMARK solves, stated so that any toolkit can solve it and two toolkits' solutions can be
compared: the statement, the objects that make up the solution, the conditions under which it exists, the members
(the cells of Aiyagari's Table II), what a solution reports, how this REMARK solves it, and a register of the
conventions that, left unstated, made two solutions differ. [The HARK notebook](../AiyagariMarkovHARK.ipynb) states
the same economy for a reader. A comparison of toolkits, such as those of
[SCE Working Group 1](https://github.com/econ-ark/sce-wg-1), would start from this.

## The household

A continuum of households of mass one, each infinitely lived. A household's state at the start of a period is its
assets $a$ and its income state $j$; it chooses consumption $c$ and end-of-period assets $a'$:

$$
V(a, j) = \max_{c,\, a'} \; u(c) + \beta \sum_{j'} P_{jj'} V(a', j')
\quad \text{subject to} \quad c + a' = (1 + r)\,a + w\,\ell_j, \qquad a' \geq 0,
$$

with $u(c) = (c^{1-\mu} - 1)/(1 - \mu)$, and $u(c) = \log c$ when $\mu = 1$. Aiyagari's borrowing limit is
$a' \geq -\phi$ with $\phi = \min\{b, w \ell_{\min}/r\}$ for $r > 0$; Table II sets $b = 0$, so the limit is zero,
tighter than the natural limit at every interest rate. A period is a year.

## The income process

The labor endowment in state $j$ is $\ell_j = e^{x_j}$, for seven states. The log endowments are evenly spaced,
$x_j = -3\sigma + (j - 1)\sigma$ for $j = 1, \ldots, 7$, and the transition probabilities $P_{ij}$ are Tauchen's
(1986) for an AR(1) with persistence $\rho$ and innovation standard deviation $\sigma(1 - \rho^2)^{1/2}$: the
probability of the interval around $x_j$ bounded by the midpoints to its neighbors, with what lies beyond the
outermost midpoints assigned to the outermost states. `tauchen_chain` in the package and in
`dolark-environment/aiyagari_dolark.py` build it identically (HARK's `make_tauchen_ar1`).

**The economy is the chain, not the AR(1).** Aiyagari states the AR(1) and computes with the chain, and his
households face the chain. Its moments differ from the AR(1)'s, most at high persistence: at $\sigma = 0.4$ and
$\rho = 0.9$ the chain's log endowment has a standard deviation of 0.468 and an autocorrelation of 0.902; at the
baseline, 0.212 and 0.599. Labor supply $L = \sum_j \pi_j \ell_j$, with $\pi$ the chain's stationary distribution,
is 1.0227 at the baseline: the endowment is not normalized.

*Open for a comparison of toolkits:* whether its canonical income process is the AR(1), with each toolkit's chain
its representation and the number of states a setting refined without limit, or this stated chain. The two are
different economies. Table II is the stated chain's; a toolkit handed the AR(1) solves the other one, as the first
version of the DolARK notebook did.

## Firms and prices

Output is $Y = K^\alpha L^{1-\alpha}$ with $\alpha = 0.36$; capital depreciates at $\delta = 0.08$. Firms pay
$r = \alpha (K/L)^{\alpha - 1} - \delta$ and $w = (1 - \alpha)(K/L)^\alpha$. Complete markets would give
$r = \vartheta = 1/\beta - 1$ and capital $K^\vartheta = L\,((\vartheta + \delta)/\alpha)^{1/(\alpha - 1)}$.

## The solution: a stationary equilibrium

The solution consists of three objects:

- **the rule** $a'(a, j)$, or equivalently $c(m, j)$ with market resources $m = (1 + r)a + w\ell_j$;
- **the stationary distribution** $\lambda$ of households over end-of-period assets and the income state in which
  they were chosen, $(a', j)$;
- **the interest rate** $r^*$, with the wage $w^*$ and capital $K^*$ that go with it,

such that the rule solves the household's problem at $(r^*, w^*)$; $\lambda$ is the stationary distribution of the
chain on $(a', j)$ that $P$ and the rule generate; households hold the capital firms use, $K^* = \int a' \, d\lambda$;
and $(r^*, w^*)$ are firms' marginal products at $(K^*, L)$. The saving rate is gross investment over output,
$\delta K/Y = \delta\alpha/(r + \delta)$, a function of $r$; since $C + \delta K = Y$ in a stationary equilibrium,
$1 - C/Y$ equals it.

An approximation approaches the solution in three senses: the rule uniformly on bounded sets of assets, the
distribution weakly, and $r^*$ as a number.

## When it exists

- **$\beta(1 + r^*) < 1$**, the absolute impatience condition $\text{Þ} = (R\beta)^{1/\mu} < 1$ with $R = 1 + r$;
  with no growth it is also the growth impatience condition. Under it households' assets are bounded and the
  stationary distribution is unique (Aiyagari 1994). As $r$ rises to $\vartheta$, mean assets grow without limit,
  so $r^* < \vartheta$.
- **Income is bounded and positive**: $\ell_{\min} > 0$, so the zero borrowing limit can be met in every state.
- **One root.** Households' supply of capital rises with $r$ in every cell computed, so the market for capital
  clears at one rate; this is found, not proven.

## The members

Table II's 24 cells: $\sigma \in \{0.2, 0.4\}$, $\rho \in \{0, 0.3, 0.6, 0.9\}$, $\mu \in \{1, 3, 5\}$, with
$\beta = 0.96$, $\alpha = 0.36$ and $\delta = 0.08$. The baseline is $\sigma = 0.2$, $\rho = 0.6$, $\mu = 3$.
Aiyagari's published values ([`../table-ii/aiyagari-1994.json`](../table-ii/aiyagari-1994.json)) are his numerical
solutions: published values, not a reference. At the converged settings of this REMARK, two toolkits differ from
them by up to 0.26 percentage points, at $\sigma = 0.4$, $\rho = 0.9$, $\mu = 5$.

## What a solution reports

As the package's `numbers.json` and the records in [`../table-ii/`](../table-ii/README.md) report them:

- the equilibrium: $r^*$, $w^*$, $K^*$, $L$, $K^*/K^\vartheta$, and the saving rate both ways;
- the distribution of wealth: its Gini coefficient, the shares of the richest 1, 5, 10, 20 and 30 percent, the Lorenz
  curve, and the share of households at the borrowing limit;
- the mean marginal propensity to consume out of market resources;
- the economy actually solved, the *effective member*: the chain, with its stationary distribution and moments;
- diagnostics that need no reference solution: Euler equation errors where households hold assets, the residual of
  the market for capital, the goods-market residual $(1 - C/Y) - \delta K/Y$, and the share of households beyond the
  rule's grid and beyond the population's.

A comparison would add the rule at stated points of $(a, j)$ and households' supply of capital at stated interest
rates: the household compared as a household, before the economy is closed.

## How this REMARK solves it

Two toolkits solve the household's problem: HARK's `MarkovConsumerType`, by the endogenous grid method, and dolo's
time iteration, through DolARK's model file. One code computes the population from either toolkit's rule
([`src/aiyagari1994qje/population.py`](../src/aiyagari1994qje/population.py)): the stationary distribution on a grid
of end-of-period assets of its own, by Young's (2010) lottery, solved directly. The rule's grid and the population's
grid are unrelated, and each is refined on its own. The equilibrium is found by Brent's method, on the interest
factor (HARK) or on capital (DolARK).

The settings are named levels:

| level | HARK's rule | dolo's rule | population |
|---|---|---|---|
| original (HARK only) | 48 points to 20 wage units | — | 1,000 households simulated for 1,000 periods, the last 700 averaged |
| low | 100 points to 100 wage units | 100 points to 150 | 1,000 points |
| medium | 200 points to 100 wage units | 200 points to 150 | 2,000 points |
| high | 800 points to 200 wage units | 800 points to 150 | 3,000 points |

The population's grid runs to 300 (in wage units for HARK, in levels for dolo). At the medium level the two toolkits'
interest rates differ by at most 0.0032 percentage points across Table II, and at the high level by 0.00024; HARK's
medium is within 0.009 of its high.

**Agreement is not accuracy.** A third solution, independent of both toolkits
([`src/aiyagari1994qje/reference.py`](../src/aiyagari1994qje/reference.py): the endogenous grid method in plain numpy on
the stated chain, with up to 8,000 points for the rule), measures each one's error. Measured at fixed prices in three
cells (the baseline; σ = 0.4, ρ = 0.9, μ = 5; and σ = 0.2, ρ = 0, μ = 3), the reference is within about 0.00002
percentage points of its own limit.
- **At the medium level both toolkits understate the interest rate by about the same amount,** 0.0018 percentage
  points at the baseline, though they agree with each other to 0.00003. The shared cause is linear interpolation
  (the register below).
- **In the riskiest cell the two errors differ:** HARK's 0.0076 and dolo's 0.0043, and their difference is the
  0.0033 by which the toolkits disagree there.
- **HARK's `Settings.cubic_interpolation` removes the error:** about 0.00001 at the medium level's 200 points. It is
  off by default, so that the published numbers stay those of version 2.0.

## A register of conventions

Each of these made two solutions of the economy differ before it was found; each is now stated or fixed.

- **The form of the Euler equation.** The first DolARK model file wrote it $1 - (\beta(1 + r'))^{1/\theta}\, c/c'$,
  which is the CRRA Euler equation only when $\theta = 1$. Fixed: $1 - \beta(1 + r')(c'/c)^{-\theta}$.
- **An AR(1) handed to a toolkit.** The first DolARK model file gave dolo a `VAR1`, which dolo discretizes, by
  default, as a three-state Rouwenhorst chain. Fixed: the stated chain, written out.
- **One grid for the rule and the population.** dolark's `find_steady_state` computes the population on the rule's
  grid, with a dense linear system whose size grows with the square of the grid's; the first version used 75 points
  evenly spaced to 300, four units apart, where households hold six to twelve on average. Fixed: separate grids.
- **The labor supply used to report.** The first DolARK notebook solved with $L = e^{\sigma^2/2}$ and reported an
  interest rate recomputed with the chain's mean endowment. Fixed: the chain's mean endowment throughout.
- **A simulation's burn-in.** The original HARK settings simulated 1,000 households, starting poor, and averaged
  periods 300 to 998. At the baseline $\beta(1 + r) = 0.997$, the distribution's upper tail fills in over centuries,
  and those periods' mean assets fall 3 percent short of the stationary mean. Fixed: the stationary distribution,
  computed directly.
- **The rule's grid.** The original HARK settings computed the rule on 48 points up to 20 wage units; at the baseline's
  interest rate that rule overstates mean assets by about 9 percent. The two errors pulled in opposite directions,
  and the original equilibrium, 3.8622 percent, was within 0.02 of Aiyagari's for that reason.
- **The kink.** dolo's rule is linear between fixed points of assets and has no point at the kink where households
  begin to save, so its Euler equation errors are largest there (up to 3.4 percent at the medium level) and its share
  of households at the borrowing limit converges more slowly than HARK's, whose endogenous grid has a point at the
  kink. `Economy(..., restore_kink=True)` in `dolark-environment/aiyagari_dolark.py` puts the kink back when the rule
  is evaluated:
  - in each income state, the first saving segment is extended down to the limit;
  - this cuts the error in the share at the limit about fivefold, against the reference;
  - it leaves the interest rate and the Gini unchanged.

  It is off by default.
- **Linear interpolation of the rule.** Both toolkits interpolate the rule linearly between their points. Consumption
  is concave in resources, so a straight line between two points lies below it: households consume too little and
  save too much, and the interest rate comes out too low.
  - **The size of the error:** each toolkit's falls fourfold when its points double. At the medium level it is
    0.0018 percentage points at the baseline for both, and 0.0076 (HARK) and 0.0043 (dolo) at σ = 0.4, ρ = 0.9,
    μ = 5.
  - **So agreement says little:** the toolkits agree at the medium level largely because they make the same error.
  - **HARK's remedy:** cubic interpolation (`Settings.cubic_interpolation`, HARK's `CubicBool`) matches the rule's
    slopes at its points and is within about 0.00001 at 200 points, at twice the cost of a solve. Linear
    interpolation needs about 3,200 points for that.
  - **dolo's remedy:** dolo offers cubic interpolation only on evenly spaced grids, so it needs more points: 800 (its
    high level) for 0.0003.
- **The population's grid, in different units.** The two toolkits' populations are on grids of the same number of
  points, in units of the wage for HARK and in levels for dolo. That is a difference between the toolkits that has
  nothing to do with their rules; it accounts for about a fifth of their gap at the baseline and less elsewhere.
- **The population's solve.** The stationary distribution was found by replacing one of its equations with "the
  masses sum to one", a row with no zeros in an otherwise sparse matrix. That made the solve take 25 seconds on
  3,000 points and more than 7 GB on 20,000.
  - Fixed: one mass is fixed instead (the largest, from a few hundred steps of the chain), and the result is scaled
    to sum to one.
  - The answer is the same to round-off, about 16 times faster at 3,000 points, so finer population grids are cheap.
- **dolo's convergence.** dolo's improved time iteration returns its last iterate, without an error, when it does not
  converge. Fixed: the dolo route now requires its convergence flag, and falls back to plain time iteration when it is
  not set.
- **The threshold for the borrowing limit.** The dolo route counted a household at the limit if it ended the period
  with assets of at most 1e-8, which is improved time iteration's own tolerance, so solver noise could decide who was
  counted. Fixed: at most zero, as HARK's are counted. dolo's limit is −1e-10.
- **A knife edge at the limit.** In the cell σ = 0.2, ρ = 0.9, μ = 3, the share of households at the borrowing limit
  turns on where one income state's kink falls.
  - In the third-lowest income state, a household with no assets has market resources only 0.000014 below the kink
    at which households start to save, so it is (just) at the limit.
  - Households with no assets are about 1.1 percent of the population. Every solution that misplaces that kink by
    more than 0.000014 moves them out of the share at the limit.
  - The reference's share at the limit is 2.73 percent. In `table-ii/`, DolARK's high level has 2.70 percent, while
    HARK's levels (about 1.57) and DolARK's medium (1.51) have misplaced the kink.
  - An interest rate about 0.003 percentage points higher would put those households on the other side.
- **HARK's Markov rule.** In econ-ark 0.17.2, `MarkovConsumerType`'s unconstrained consumption function for a state
  in which the artificial limit binds starts with the knot $(0, 0)$ and continues at negative market resources, where
  the endogenous grid begins from the one-period natural limit. HARK finds a segment by a binary search that is right
  for every positive $m$, which is all a household ever has; a reader of its knots has to know that the first is out of
  order (`Equilibrium.rule` writes them out, and `aiyagari1994qje.evaluate_rule` reads them as HARK does).
