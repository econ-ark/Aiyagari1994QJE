# Aiyagari (1994 QJE): Uninsured Idiosyncratic Risk and Aggregate Saving

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/econ-ark/Aiyagari1994QJE/HEAD)
[![reproduce](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml/badge.svg)](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml)

**A Reproducible REMARK (Tier 2)** replicating Table II of Aiyagari, S. Rao (1994), "Uninsured Idiosyncratic Risk and Aggregate Saving," *Quarterly Journal of Economics*, 109(3), 659–684.

**Author**: Adam Edwards, Johns Hopkins University

**Website**: the notebooks, rendered with their outputs, at https://econ-ark.github.io/Aiyagari1994QJE/

## Overview

This repository computes the steady-state interest rate and aggregate saving rate of the **Aiyagari (1994)** economy for every parameter combination in the paper's Table II, in two independent ways, and compares both with the published numbers. The model shows how precautionary saving by households facing uninsurable income risk and a borrowing constraint raises aggregate capital and lowers the interest rate.

For the baseline calibration, the HARK notebook also draws the consumption functions, the distribution of wealth, and the supply of and demand for capital, and writes those figures and the economy's key numbers to `baseline/` for other documents to use. The HARK computation is also a Python package, `aiyagari1994qje`, that other programs can install to compute the same numbers and draw the same figures.

## Key Features

- **Two Solution Approaches**: HARK's `MarkovConsumerType`, and DolARK (dolo's extension to heterogeneous agents)
- **Complete Parameter Replication**: All 24 parameter combinations of Aiyagari (1994) Table II
- **Baseline Figures and Numbers**: Consumption functions, the wealth distribution and the capital market at the baseline calibration, as PNG and SVG files and a JSON file of numbers
- **Installable Package**: `aiyagari1994qje`, the model code, installs with pip on Python 3.11 to 3.14 and returns the notebook's numbers exactly
- **Current Software**: The HARK notebook runs on econ-ark 0.17.2, numpy 2 and Python 3.14
- **Pinned Environments**: Every package version is fixed in `uv.lock`; a `Dockerfile` reproduces everything in a container
- **Educational Focus**: Notebooks that walk through the fixed-point problem step by step

## Quick Start

### Option 1: Docker

```bash
docker build -t aiyagari1994qje .
docker run --rm -v "$PWD/results:/app/results" -v "$PWD/baseline:/app/baseline" aiyagari1994qje
```

The executed notebooks appear in `results/`, and the regenerated baseline figures and numbers in `baseline/`.

### Option 2: uv (recommended for native runs)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and git. CI uses uv 0.12.19; an older uv may not be able to download Python 3.14.7.

```bash
./reproduce.sh       # full reproduction, both notebooks (about 6 minutes)
./reproduce_min.sh   # quick check: solves the baseline and checks it against baseline/numbers.json (about 15 seconds)
```

Both scripts first run `setup_envs.sh`, which builds the environments from `uv.lock`; uv downloads Python 3.14.7 and 3.9.23 if they are not already installed.

### Option 3: Conda

```bash
conda env create -f binder/environment.yml   # installs Python 3.9 and uv; uv downloads Python 3.14 for HARK
conda activate Aiyagari1994QJE
./reproduce.sh
```

### Option 4: Cloud Execution

Click the Binder badge above to open the notebooks in your browser without installing anything. Choose the kernel named after each notebook's method: **Aiyagari (HARK 0.17.2)** or **Aiyagari (DolARK)**.

## Why There Are Two Environments

The two notebooks need package versions that cannot be installed together. The HARK notebook runs on the current `econ-ark` with `numpy` 2. `dolark` has never been released to PyPI, supports only Python earlier than 3.10, and every release of `dolo` it can use requires `numpy` 1 and `xarray` earlier than 2023. So each has its own project and lockfile: the repository root (`pyproject.toml`, `uv.lock`), which is also the package `aiyagari1994qje`, and `dolark-environment/`:

| Environment | Python | Pinned key packages | Runs |
|---|---|---|---|
| `.venv-hark` | 3.14.7 | `econ-ark` 0.17.2, `numpy` 2.5.4, `scipy` 1.18.1, `pandas` 3.0.6 | `AiyagariMarkovHARK.ipynb` |
| `.venv-dolark` | 3.9.23 | `dolark` at commit `b0eef38`, `dolo` 0.4.9.20, `dolang` 0.0.20, `numpy` 1.26.4 | `AiyagariDolARK.ipynb` |

`.venv-hark` holds the package `aiyagari1994qje` as an editable install, so the notebook uses the code in `src/`. To work in the notebooks interactively after running `./setup_envs.sh`:

```bash
.venv-hark/bin/jupyter lab   # both kernels are available from either environment
```

## Repository Contents

### Notebooks

- **`AiyagariMarkovHARK.ipynb`**: Primary implementation using HARK's `MarkovConsumerType` (about 4–5 minutes)
  - Solves the household problem and simulates 1,000 agents for 1,000 periods
  - Finds the equilibrium interest rate with Brent's method
  - Draws the baseline economy (σ = 0.2, ρ = 0.6, μ = 3) and saves the figures and numbers to `baseline/`
  - Reproduces all of Table II and tabulates the differences from the published values

- **`AiyagariDolARK.ipynb`**: Alternative implementation using DolARK (about 1 minute)
  - The household problem is written in `Aiyagari.yaml` and solved by time iteration
  - Steady states found with `dolark.equilibrium.find_steady_state`
  - Reproduces all of Table II for comparison

### Key Files

| File | Purpose |
|---|---|
| `reproduce.sh` | Full reproduction: builds the environments and executes both notebooks into `results/` |
| `reproduce_min.sh` | Quick check: solves the baseline with the package and checks every number against `baseline/numbers.json` |
| `setup_envs.sh` | Builds `.venv-hark` and `.venv-dolark` from their lockfiles and registers their Jupyter kernels |
| `src/aiyagari1994qje/` | The package: the model (`model.py`) and its figures (`figures.py`) |
| `pyproject.toml`, `uv.lock` | The package and the HARK notebook's environment, and the lockfile that pins every version |
| `dolark-environment/` | The DolARK notebook's environment (`pyproject.toml`) and its lockfile |
| `Dockerfile` | Container that runs `reproduce.sh` |
| `binder/environment.yml`, `binder/postBuild` | Binder and REMARK-tooling adapter: installs uv, then builds the environments |
| `myst.yml`, `.github/workflows/myst-deploy.yml` | Publishes the notebooks as a website on GitHub Pages on every push to `main` |
| `.github/workflows/reproduce.yml`, `.github/check_baseline.py` | CI: on every push, runs `reproduce_min.sh`, installs the package with pip on Python 3.11 to 3.14 and checks its numbers, and builds the Docker image; on release tags and on demand, runs the full reproduction in Docker and checks the regenerated `baseline/` against the committed one |
| `baseline/` | The baseline economy's figures (`consumption-functions`, `wealth-lorenz`, `capital-supply-demand`, each as PNG and SVG) and `numbers.json`; written by the HARK notebook |
| `Aiyagari.yaml` | The DolARK model definition |
| `CITATION.cff`, `REMARK.md` | Citation and REMARK metadata |

## Model Description

The Aiyagari model features:

- **Heterogeneous Agents**: Infinitely-lived households facing idiosyncratic labor-endowment shocks
- **Incomplete Markets**: No insurance against individual income risk
- **Borrowing Constraints**: Households cannot borrow (assets must be nonnegative)
- **Income Process**: Log labor endowment follows an AR(1), discretized as a seven-state Markov chain with the Tauchen method
- **Equilibrium**: The interest rate is the one at which households' asset holdings equal the capital that firms demand

Parameters follow the paper: β = 0.96, capital share α = 0.36, depreciation δ = 0.08, with σ ∈ {0.2, 0.4}, ρ ∈ {0, 0.3, 0.6, 0.9} and relative risk aversion μ ∈ {1, 3, 5}.

## Key Results

Each notebook prints its version of Table II next to Aiyagari's and tabulates the difference. Across the 24 cells, compared with the published values:

| Notebook | Largest interest-rate gap | Mean interest-rate gap | Largest saving-rate gap |
|---|---|---|---|
| HARK (`MarkovConsumerType`) | 0.20 pp | 0.04 pp | 0.93 pp |
| DolARK | 1.85 pp | 0.47 pp | 7.32 pp |

Both gaps are largest for the most persistent and most volatile income process (ρ = 0.9, σ = 0.4), where the HARK implementation stays close to the published values and the DolARK one does not.

### The Baseline Economy

At the baseline calibration (σ = 0.2, ρ = 0.6, μ = 3), from `baseline/numbers.json`:

| Quantity | Value |
|---|---|
| Equilibrium interest rate | 3.86% (Aiyagari: 3.88%) |
| Saving rate | 24.33% (Aiyagari: 24.25%) |
| Capital, relative to complete markets (r = 1/β − 1 = 4.17%) | 4.0% higher |
| Wealth Gini | 0.38 |
| Share of wealth held by the richest 1% | 3.6% |
| Share of households at the borrowing constraint | 0.26% |
| Average marginal propensity to consume | 0.054 |

The labor endowment is not normalized: labor supply L, the mean endowment, is 1.02, and capital and the wage are levels for a population of mass one. The distribution statistics pool the 1,000 simulated households over the periods that determine the equilibrium.

### Using the Model in Another Program: the `aiyagari1994qje` Package

The HARK computation is a package that installs with pip or uv on Python 3.11 to 3.14. Pin a commit, so that your results do not change when this repository does:

```bash
pip install "aiyagari1994qje @ git+https://github.com/econ-ark/Aiyagari1994QJE@<commit>"
```

```python
from aiyagari1994qje import Calibration, solve_equilibrium, plot_capital_market

eq = solve_equilibrium(Calibration())   # Aiyagari's baseline; about 10 seconds
eq.interest_rate, eq.saving_rate_from_capital, eq.capital, eq.gini
eq.numbers()                            # everything in baseline/numbers.json
plot_capital_market(eq, ax)             # draws on a matplotlib Axes; about 25 seconds
```

`Calibration` takes any of the paper's parameters, for example `Calibration(income_standard_deviation=0.4, income_persistence=0.9, relative_risk_aversion=5)`. The steps of the computation are public too, for showing them one at a time: `tauchen_chain`, `make_households` (a HARK `MarkovConsumerType`), `simulate`, `capital_supply` and `capital_demand`. The plotting functions only draw on the Axes they are given; they set no styles and neither save nor show a figure. `table_ii()` recomputes all of Table II in about 3.5 minutes.

The package's dependencies are ranges (`econ-ark>=0.17,<0.18`, `numpy>=2`, and current `scipy`, `matplotlib` and `sympy`), so it fits into other projects' environments. With econ-ark 0.17.2 it returns exactly the notebook's numbers: CI installs it with pip on Python 3.11 to 3.14 and checks every number against `baseline/numbers.json`, and the notebook asserts that the package finds the same interest rate, to the last bit, as its own step-by-step computation.

The saving rate comes two ways. `saving_rate_from_capital` is δK/Y = δα/(r + δ), gross investment over output in a steady state, which is how Aiyagari computes it: at his interest rates it gives his Table II saving rates exactly. `saving_rate` is 1 − C/Y in the simulation, which the notebooks' replications of Table II report; at the baseline the two are 24.28% and 24.33%.

### Using the Baseline Figures and Numbers Elsewhere

The files in `baseline/` are committed, so other documents can also use them directly, without installing anything. To keep a document from changing when this repository does, link a specific commit rather than a branch or a tag, for example `https://raw.githubusercontent.com/econ-ark/Aiyagari1994QJE/<commit>/baseline/capital-supply-demand.png`. `numbers.json` records the calibration and defines every number.

The committed files are those the Docker image writes. They carry no timestamps or version stamps, so rerunning the notebook on the same platform rewrites every file byte for byte. On another platform the numbers, the SVG files and every pixel of the PNG files come out the same, but the PNG files' bytes can differ, because the compression depends on the zlib library that writes them. On every release, the full CI run regenerates `baseline/` in Docker and checks the numbers and pixels against the committed files with `.github/check_baseline.py`.

## Output Guide

`reproduce.sh` writes executed copies of both notebooks to `results/` (the notebooks in the repository are left unchanged). In each, the final cells hold the replicated Table II, the published Table II, and their difference. The earlier cells of the HARK notebook show the consumption functions and the simulated asset path at an interest rate of 3%, then the baseline economy (σ = 0.2, ρ = 0.6, μ = 3) at its equilibrium. Running the HARK notebook also rewrites the files in `baseline/`.

## Educational Applications

### Prerequisites
- Graduate-level macroeconomic theory
- Some Python programming experience  
- Basic dynamic programming knowledge
- Familiarity with numerical methods

### Learning Objectives
- Understand incomplete markets with heterogeneous agents
- Master HARK computational framework
- Analyze precautionary saving effects
- Compare numerical with analytical solutions

## Technical Implementation

### Solution Methods

- **Tauchen Discretization**: AR(1) income process → seven-state Markov chain
- **Household Problem**: HARK's `MarkovConsumerType` solver (endogenous grid method), with the wage normalized to one; dolo's time iteration in the DolARK notebook
- **Code**: the HARK notebook walks through the computation step by step, then uses the package `aiyagari1994qje`, which packages the same steps, for the baseline economy's figures and numbers
- **Equilibrium**: Brent's method (`scipy.optimize.brentq`) on the gap between the assumed and the implied interest rate
- **Aggregation**: Monte Carlo simulation of 1,000 agents for 1,000 periods, averaging the last 700; HARK's default random seed makes the simulation repeatable

### System Requirements

- Tested on macOS (Apple silicon), with uv directly and through the conda adapter in `binder/environment.yml`; on Linux through the `Dockerfile`, locally (arm64) and in CI (amd64); and on mybinder.org. All produce identical tables and the same baseline numbers and figures. The run times quoted above were measured on an Apple M4 Max; mybinder.org's machines are slower and vary, and in one test there the HARK notebook took 28 minutes
- About 1.4 GB of disk for the two environments, plus about 100 MB for Python 3.14.7 if uv downloads it
- The Jupyter kernels are registered single-threaded (`OMP_NUM_THREADS=1` and similar). With a thread per core, the DolARK notebook ran nearly three times slower on a Mac and did not finish in an hour on Binder, whose sessions get one CPU but see every core of the host; the HARK notebook runs equally fast either way
- A single core suffices; the HARK notebook is the slow step

## Troubleshooting

- **`uv: command not found`**: install uv, or use the conda route, which installs it.
- **`uv sync` fails with a lockfile error**: run the scripts unchanged; `--locked` refuses to proceed if a `pyproject.toml` and its `uv.lock` disagree, which means one of them was edited.
- **Jupyter reports a missing kernel**: run `./setup_envs.sh`, then start Jupyter from `.venv-hark` or `.venv-dolark`.

## Citation

If you use this implementation, please cite:

```bibtex
@software{edwards2024aiyagari,
  author = {Edwards, Adam},
  title = {Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving - Computational Implementation},
  url = {https://github.com/econ-ark/Aiyagari1994QJE},
  version = {1.1.0},
  year = {2024}
}
```

And the original paper:

```bibtex
@article{aiyagari1994uninsured,
  title = {Uninsured idiosyncratic risk and aggregate saving},
  author = {Aiyagari, S. Rao},
  journal = {The Quarterly Journal of Economics},
  volume = {109},
  number = {3},
  pages = {659--684},
  year = {1994},
  publisher = {Oxford University Press},
  doi = {10.2307/2118417}
}
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

This is part of the [Econ-ARK](https://econ-ark.org) project. For questions or contributions, please:

1. Check the [Econ-ARK documentation](https://docs.econ-ark.org)
2. Open an issue on GitHub
3. Contact the development team

## Acknowledgments

- **Original Research**: S. Rao Aiyagari (1994)
- **Implementation**: Adam Edwards, Johns Hopkins University
- **Framework**: [HARK](https://github.com/econ-ark/HARK) development team
- **Infrastructure**: [Econ-ARK](https://econ-ark.org) project
