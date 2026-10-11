# Aiyagari (1994 QJE): Uninsured Idiosyncratic Risk and Aggregate Saving

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/econ-ark/Aiyagari1994QJE/HEAD)
[![reproduce](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml/badge.svg)](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml)

**A Reproducible REMARK (Tier 2)** replicating Table II of Aiyagari, S. Rao (1994), "Uninsured Idiosyncratic Risk and Aggregate Saving," *Quarterly Journal of Economics*, 109(3), 659–684.

**Author**: Adam Edwards, Johns Hopkins University

**Website**: the notebooks, rendered with their outputs, at https://econ-ark.github.io/Aiyagari1994QJE/

## Overview

This repository computes the steady-state interest rate and aggregate saving rate of the **Aiyagari (1994)** economy for every parameter combination in the paper's Table II, in two independent ways, and compares both with the published numbers. The model shows how precautionary saving by households facing uninsurable income risk and a borrowing constraint raises aggregate capital and lowers the interest rate.

## Key Features

- **Two Solution Approaches**: HARK's `MarkovConsumerType`, and DolARK (dolo's extension to heterogeneous agents)
- **Complete Parameter Replication**: All 24 parameter combinations of Aiyagari (1994) Table II
- **Pinned Environments**: Every package version is fixed in `uv.lock`; a `Dockerfile` reproduces everything in a container
- **Educational Focus**: Notebooks that walk through the fixed-point problem step by step

## Quick Start

### Option 1: Docker

```bash
docker build -t aiyagari1994qje .
docker run --rm -v "$PWD/results:/app/results" aiyagari1994qje
```

The executed notebooks appear in `results/`.

### Option 2: uv (recommended for native runs)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and git.

```bash
./reproduce.sh       # full reproduction, both notebooks (about 8 minutes)
./reproduce_min.sh   # quick check, one parameter combination (about 1 minute)
```

Both scripts first run `setup_envs.sh`, which builds the environments from `uv.lock`; uv downloads Python 3.9 if it is not already installed.

### Option 3: Conda

```bash
conda env create -f binder/environment.yml   # installs Python 3.9 and uv
conda activate Aiyagari1994QJE
./reproduce.sh
```

### Option 4: Cloud Execution

Click the Binder badge above to open the notebooks in your browser without installing anything. Choose the kernel named after each notebook's method: **Aiyagari (HARK 0.13.0)** or **Aiyagari (DolARK)**.

## Why There Are Two Environments

The two notebooks need package versions that cannot be installed together. `econ-ark` 0.13.0 requires `xarray` 2023 or later, while every release of `dolo` that `dolark` can use requires `xarray` earlier than 2023. `dolark` itself has never been released to PyPI and supports only Python earlier than 3.10. So `pyproject.toml` defines two dependency groups, which `uv.lock` pins separately:

| Environment | Pinned key packages | Runs |
|---|---|---|
| `.venv-hark` | `econ-ark` 0.13.0, `numpy` 1.26.4 | `AiyagariMarkovHARK.ipynb` |
| `.venv-dolark` | `dolark` at commit `b0eef38`, `dolo` 0.4.9.20, `dolang` 0.0.20 | `AiyagariDolARK.ipynb` |

Both use Python 3.9. To work in the notebooks interactively after running `./setup_envs.sh`:

```bash
.venv-hark/bin/jupyter lab   # both kernels are available from either environment
```

## Repository Contents

### Notebooks

- **`AiyagariMarkovHARK.ipynb`**: Primary implementation using HARK's `MarkovConsumerType` (about 5–6 minutes)
  - Solves the household problem and simulates 1,000 agents for 1,000 periods
  - Finds the equilibrium interest rate with Brent's method
  - Reproduces all of Table II and tabulates the differences from the published values

- **`AiyagariDolARK.ipynb`**: Alternative implementation using DolARK (about 2.5 minutes)
  - The household problem is written in `Aiyagari.yaml` and solved by time iteration
  - Steady states found with `dolark.equilibrium.find_steady_state`
  - Reproduces all of Table II for comparison

### Key Files

| File | Purpose |
|---|---|
| `reproduce.sh` | Full reproduction: builds the environments and executes both notebooks into `results/` |
| `reproduce_min.sh` | Quick check: one parameter combination (σ = 0.2, ρ = 0.6, μ = 1) with sanity checks |
| `setup_envs.sh` | Builds `.venv-hark` and `.venv-dolark` from `uv.lock` and registers their Jupyter kernels |
| `pyproject.toml`, `uv.lock` | Dependency specification and the lockfile that pins every version |
| `Dockerfile` | Container that runs `reproduce.sh` |
| `binder/environment.yml`, `binder/postBuild` | Binder and REMARK-tooling adapter: installs uv, then builds the environments |
| `myst.yml`, `.github/workflows/myst-deploy.yml` | Publishes the notebooks as a website on GitHub Pages on every push to `main` |
| `.github/workflows/reproduce.yml` | CI: runs `reproduce_min.sh` and builds the Docker image on every push; runs the full reproduction in Docker on release tags and on demand |
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
| HARK (`MarkovConsumerType`) | 0.20 pp | 0.04 pp | 0.94 pp |
| DolARK | 1.85 pp | 0.47 pp | 7.32 pp |

Both gaps are largest for the most persistent and most volatile income process (ρ = 0.9, σ = 0.4), where the HARK implementation stays close to the published values and the DolARK one does not.

## Output Guide

`reproduce.sh` writes executed copies of both notebooks to `results/` (the notebooks in the repository are left unchanged). In each, the final cells hold the replicated Table II, the published Table II, and their difference. The earlier cells of the HARK notebook show the consumption functions, the simulated asset path, and capital supply and demand at the baseline parameters (σ = 0.2, ρ = 0.6, μ = 3).

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
- **Household Problem**: HARK's `MarkovConsumerType` solver (endogenous grid method); dolo's time iteration in the DolARK notebook
- **Equilibrium**: Brent's method (`scipy.optimize.brentq`) on the gap between the assumed and the implied interest rate
- **Aggregation**: Monte Carlo simulation of 1,000 agents for 1,000 periods, averaging the last 700; HARK's default random seed makes the simulation repeatable

### System Requirements

- Tested on macOS (Apple silicon), with uv directly and through the conda adapter in `binder/environment.yml`, and on Linux (arm64) through the `Dockerfile`; all three produce identical tables. The run times quoted above were measured on an Apple M4 Max
- About 1.2 GB of disk for the two environments
- A single core suffices; the HARK notebook is the slow step

## Troubleshooting

- **`uv: command not found`**: install uv, or use the conda route, which installs it.
- **`uv sync` fails with a lockfile error**: run the scripts unchanged; `--locked` refuses to proceed if `pyproject.toml` and `uv.lock` disagree, which means one of them was edited.
- **Jupyter reports a missing kernel**: run `./setup_envs.sh`, then start Jupyter from `.venv-hark` or `.venv-dolark`.

## Citation

If you use this implementation, please cite:

```bibtex
@software{edwards2024aiyagari,
  author = {Edwards, Adam},
  title = {Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving - Computational Implementation},
  url = {https://github.com/econ-ark/Aiyagari1994QJE},
  version = {1.0.1},
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
