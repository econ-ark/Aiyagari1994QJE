---
# REMARK metadata (econ-ark/REMARK STANDARD.md) and Econ-ARK website fields
remark-name: Aiyagari1994QJE
tier: 2
github_repo_url: https://github.com/econ-ark/Aiyagari1994QJE
title-original-paper: "Uninsured idiosyncratic risk and aggregate saving"
notebooks:
  - AiyagariMarkovHARK.ipynb
  - AiyagariDolARK.ipynb
tags:
  - REMARK
  - Replication
  - Notebook
keywords:
  - heterogeneous agents
  - incomplete markets
  - precautionary saving
  - stationary equilibrium
  - HARK
  - dolo
---

# Abstract

This REMARK computes the stationary equilibrium of Aiyagari's (1994) economy, in which households facing uninsurable
income risk and a borrowing limit save more than they would with complete markets, raising capital and lowering the
interest rate. It reproduces every cell of his Table II with two toolkits, HARK's `MarkovConsumerType` and dolo with
DolARK, given one economy, his seven-state Tauchen chain for income, and one code for the stationary population of
households. At its most refined settings the two toolkits' interest rates agree to within 0.00024 percentage points
across the table; Aiyagari's published values differ from both by up to 0.26 percentage points, most where income is
persistent and volatile and households averse to risk.

The REMARK's first version reproduced Aiyagari's baseline within 0.02 percentage points because two numerical errors
cancelled: a coarse grid for the household's rule overstated saving, and a simulation too short to reach the
stationary distribution understated it. The HARK notebook shows both, and the DolARK notebook shows how its first
version solved a different economy. For the baseline calibration the HARK notebook draws the consumption functions,
the distribution of wealth and the market for capital, and saves them with the economy's numbers for other documents
to use; the HARK computation is also an installable Python package, `aiyagari1994qje`.

# What it establishes

- Table II's stationary equilibria, converged: each toolkit's solution at named levels of settings in `table-ii/`,
  with diagnostics that need no reference solution.
- That two toolkits agree once they solve one economy with one population code, and that the remaining gaps from
  Aiyagari's table are his numerical solution's, not the model's.
- An exact statement of the economy, with a register of the conventions that made two solutions differ
  ([`docs/model.md`](docs/model.md)), from which a comparison of toolkits can start.

# Using it

The [README](README.md) explains how to reproduce the results with Docker, with uv, with conda or on Binder, what
each file is for, and how to use the package and the baseline's figures and numbers in another program. The HARK
notebook runs in about 15 minutes and the DolARK notebook, at its default level, in about 10 more.

# For teaching

**Prerequisites:** graduate macroeconomic theory (dynamic programming, the consumption-saving problem, competitive
equilibrium), some Python, and Markov chains.

**What a student learns:** to define a stationary equilibrium with heterogeneous households and incomplete markets,
and to say why its interest rate lies below the rate of time preference; to solve a household's problem under
uninsurable risk with HARK and with dolo; to compute a stationary distribution by simulation and directly, and to
recognize the errors of each; and to tell a numerical solution's error from a model's property, by converging
settings, comparing toolkits, and reading a published table as one computation among others. The HARK notebook ends
with exercises: no risk, other chains, the simulation's sampling error, the saving-rate identity, and who is
constrained.
