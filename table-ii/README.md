# Table II: the results of record

Aiyagari's (1994) Table II solved cell by cell, by two toolkits at named levels of settings, beside his published
table. Each file but `aiyagari-1994.json` was written by `record.py`, which solves the 24 cells in parallel, each in
its own single-threaded process:

```bash
.venv-hark/bin/python   table-ii/record.py hark   original|low|medium|high   [--processes N]
.venv-dolark/bin/python table-ii/record.py dolark low|medium|high            [--processes N]
```

| file | what it holds |
|---|---|
| `aiyagari-1994.json` | Aiyagari's published Table II: the interest rate and saving rate of each cell, in percent |
| `hark-original.json` | HARK with version 1.1's settings: the rule on 48 points to 20 wage units, the population simulated |
| `hark-low.json`, `hark-medium.json`, `hark-high.json` | HARK at the package's levels (`aiyagari1994qje.LEVELS`), the population as the stationary histogram |
| `dolark-low.json`, `dolark-medium.json`, `dolark-high.json` | dolo and DolARK at the levels of `dolark-environment/aiyagari_dolark.py`, with the same population code |

Each cell records the equilibrium interest rate, wage, capital and labor supply; capital relative to its
complete-markets level; the saving rate both ways (δK/Y and 1 − C/Y); the wealth Gini, the shares of the richest 1,
5, 10, 20 and 30 percent and the share at the borrowing limit; the mean MPC; the diagnostics (Euler equation errors,
the residuals of the markets for capital and goods, the shares beyond the rule's grid and the population's); and how
long the cell took. Each file records the settings, the commit and whether the tree was dirty, the versions of the
toolkit and of numpy and scipy, the machine, and the wall time. A duration is read with its machine beside it: the
cells ran in parallel, and their times include the contention between them.

## What they establish

- **The levels converge.** HARK's medium level is within 0.009 percentage points of its high level in every cell,
  and 0.003 on average; its low level within 0.04; version 1.1's original settings within 0.13.
- **The toolkits agree.** HARK's and DolARK's interest rates differ by at most 0.017 percentage points at the low
  level, 0.0032 at the medium level and 0.00024 at the high level, largest in every case at σ = 0.4,
  ρ = 0.9, μ = 5.
- **Their agreement is not their accuracy.** Measured against a solution independent of both
  (`src/aiyagari1994qje/reference.py`) at fixed prices in three cells, both toolkits' medium levels understate the
  interest rate by about the same amount: 0.0018 percentage points at the baseline.
  - In the riskiest cell, HARK understates it by 0.0076 and DolARK by 0.0043.
  - At the high level the errors are under 0.0005.
  - The cause is linear interpolation of the rule, which both use (`docs/model.md`, "A register of conventions").
- **Aiyagari's numbers are not exact.** At the high level, HARK's interest rates differ from his by up to 0.26
  percentage points, 0.07 on average: above his where income is persistent (ρ = 0.9) and volatile, below where it is
  not (ρ = 0, σ = 0.2). His saving rates are δα/(r + δ) at his interest rates, rounded, in every cell.
- **The diagnostics are clean.** At the high level, HARK's largest Euler equation error is below 0.1 percent, its
  goods-market residual below 10⁻¹⁰, and no household lies beyond either grid.

## What they do not establish

- **That the high level is the exact solution.** It is the most refined level computed.
  - The reference solution puts each toolkit's high level within 0.0005 percentage points, in the three cells where
    it has been compared.
  - Both toolkits use the same population code, so its own error is common to them. At its grids it is about 0.0001
    at the medium level, measured against finer grids.
- **The share at the borrowing limit at σ = 0.2, ρ = 0.9, μ = 3, in HARK's records.** That share is a knife edge in
  this cell (`docs/model.md`).
  - The reference gives 2.73 percent; DolARK's high level has 2.70.
  - HARK's records (about 1.57 at every level) and DolARK's medium level (1.51) leave out the 1.1 percent of
    households who have no assets and are in the third-lowest income state.
- **DolARK's share at the limit, as the code now counts it.** These records counted a household at the limit if its
  assets were at most 1e-8. The code now counts at most zero, as HARK does. The records have not been rewritten
  since.
- **Why Aiyagari's numbers differ.** That would need his code and his grids; it is not in the paper.
- **Anything about the AR(1) economy.** Every cell is the seven-state chain's economy, as Aiyagari's table is.
