# Aiyagari (1994 QJE): Uninsured Idiosyncratic Risk and Aggregate Saving

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/econ-ark/Aiyagari1994QJE/HEAD)
[![reproduce](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml/badge.svg)](https://github.com/econ-ark/Aiyagari1994QJE/actions/workflows/reproduce.yml)

**A Reproducible REMARK (Tier 2)** replicating Table II of Aiyagari, S. Rao (1994), "Uninsured Idiosyncratic Risk and Aggregate Saving," *Quarterly Journal of Economics*, 109(3), 659–684.

**Author**: Adam Edwards, Johns Hopkins University

**Website**: the notebooks, rendered with their outputs, at https://econ-ark.github.io/Aiyagari1994QJE/

## Overview

This repository computes the stationary equilibrium of the **Aiyagari (1994)** economy, its interest rate and saving rate, for every cell of the paper's Table II, with two toolkits: HARK's `MarkovConsumerType`, and dolo with its extension to heterogeneous agents, DolARK. The model shows how precautionary saving by households facing uninsurable income risk and a borrowing constraint raises aggregate capital and lowers the interest rate.

The two toolkits solve one economy, Aiyagari's seven-state Tauchen chain for income, and their populations of households are computed by one code: the stationary distribution on a grid of its own (`src/aiyagari1994qje/population.py`). Their equilibrium interest rates then differ by at most 0.0032 percentage points at the notebooks' medium level across Table II, and by 0.00024 at the high level. Aiyagari's published values differ from both by up to 0.26 percentage points, where income is most persistent and volatile and households most averse to risk: they are his numerical solution, and they are not exact.

For the baseline calibration, the HARK notebook also draws the consumption functions, the distribution of wealth, and the supply of and demand for capital, and writes those figures and the economy's key numbers to `baseline/` for other documents to use. The HARK computation is also a Python package, `aiyagari1994qje`, that other programs can install to compute the same numbers and draw the same figures. [`docs/model.md`](docs/model.md) states the economy exactly, for a comparison of toolkits.

## What Changed in Version 2.0

Version 2.0 changes the REMARK's numbers, because its earlier ones were not converged.

- **The HARK replication's two errors.** Through version 1.1 the HARK notebook computed households' rule on 48 points of assets up to 20 wage units, and their population by simulating 1,000 households for 1,000 periods and averaging the last 700. At the baseline the coarse rule overstates households' saving by about 9 percent at a given interest rate, and the simulation understates it by about 3 percent, because at $\beta(1+r) = 0.997$ the distribution's upper tail takes centuries to fill in and 300 periods of burn-in are too few. The two errors pulled in opposite directions, and the equilibrium, 3.8622 percent, came within 0.02 percentage points of Aiyagari's 3.8767 for that reason. Converged, it is 3.8783 percent. The HARK notebook now shows both errors.
- **The population on a grid of its own.** The package computes the stationary distribution directly (Young's 2010 lottery method), on a grid unrelated to the rule's, and refines the rule's grid. `aiyagari1994qje.LEVELS` names the settings: `original` (version 1.1's, number for number), `low`, `medium` (the default) and `high`.
- **The DolARK notebook solves Aiyagari's economy.** Through version 1.1 its model file stated another: an Euler equation that is the CRRA one only for log utility; a `VAR1` that dolo turned into a three-state Rouwenhorst chain where Aiyagari's households face a seven-state Tauchen chain; and one grid of 75 points evenly spaced to 300 for both the rule and the population. Its gap of up to 1.85 percentage points from Aiyagari's table came from the economy, not the method. The notebook now says how much each difference mattered (`dolark-environment/first_version.py`).
- **The results of record.** `table-ii/` holds Table II solved by each toolkit at each level, with the commit, the versions, the machine and diagnostics for every cell (`table-ii/record.py`).

The baseline's quoted numbers change little: the interest rate is 3.88 percent (3.86 before), capital is about 4 percent above its complete-markets level (3.8 percent; 4.0 before), the wealth Gini 0.39 (0.38), the richest 1 percent hold 3.8 percent of wealth (3.6), 0.34 percent of households are at the borrowing constraint (0.26), and the average MPC is 0.055 (0.054).

## Key Features

- **Two Toolkits, One Economy**: HARK's `MarkovConsumerType` and dolo/DolARK, given the same income chain and the same population code
- **Complete Parameter Replication**: All 24 parameter combinations of Aiyagari (1994) Table II
- **Converged Results, Shown to Converge**: named levels of settings, with the record of each toolkit at each level in `table-ii/`
- **Diagnostics That Need No Reference Solution**: Euler equation errors, the residuals of the markets for capital and goods, and the share of households beyond each grid, for every equilibrium
- **Baseline Figures and Numbers**: consumption functions, the wealth distribution and the capital market at the baseline calibration, as PNG and SVG files and a JSON file of numbers that records the economy actually solved
- **Installable Package**: `aiyagari1994qje`, the model code, installs with pip on Python 3.11 to 3.14
- **Pinned Environments**: Every package version is fixed in `uv.lock` and `dolark-environment/uv.lock`; a `Dockerfile` reproduces everything in a container
- **Educational Focus**: Notebooks that build the economy step by step, show what makes a numerical solution wrong and how to tell, and end with exercises

## Quick Start

### Option 1: Docker

```bash
docker build -t aiyagari1994qje .
docker run --rm -v "$PWD/results:/app/results" -v "$PWD/baseline:/app/baseline" aiyagari1994qje
```

The executed notebooks appear in `results/`, and the regenerated baseline figures and numbers in `baseline/`.

### Option 2: uv (recommended for native runs)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and git. CI uses uv 0.12.19; an older uv may not be able to download Python 3.14.7 (uv 0.9 cannot).

```bash
./reproduce.sh       # full reproduction, both notebooks (about 25 minutes on one core)
./reproduce_min.sh   # quick check: solves the baseline with both toolkits and checks it against the committed numbers (about a minute)
```

Both scripts first run `setup_envs.sh`, which builds the environments from the lockfiles; uv downloads Python 3.14.7 and 3.9.23 if they are not already installed.

### Option 3: Conda

```bash
conda env create -f binder/environment.yml   # installs Python 3.9 and uv; uv downloads Python 3.14 for HARK
conda activate Aiyagari1994QJE
./reproduce.sh
```

### Option 4: Cloud Execution

Click the Binder badge above to open the notebooks in your browser without installing anything. Choose the kernel named after each notebook's method: **Aiyagari (HARK 0.17.2)** or **Aiyagari (DolARK)**. Binder's machines are slower than a laptop and vary; both notebooks take longer there.

## Why There Are Two Environments

The two notebooks need package versions that cannot be installed together. The HARK notebook runs on the current `econ-ark` with `numpy` 2. `dolark` has never been released to PyPI, supports only Python earlier than 3.10, and every release of `dolo` it can use requires `numpy` 1 and `xarray` earlier than 2023. So each has its own project and lockfile: the repository root (`pyproject.toml`, `uv.lock`), which is also the package `aiyagari1994qje`, and `dolark-environment/`:

| Environment | Python | Pinned key packages | Runs |
|---|---|---|---|
| `.venv-hark` | 3.14.7 | `econ-ark` 0.17.2, `numpy` 2.5.4, `scipy` 1.18.1, `pandas` 3.0.6 | `AiyagariMarkovHARK.ipynb` |
| `.venv-dolark` | 3.9.23 | `dolark` at commit `b0eef38`, `dolo` 0.4.9.20, `dolang` 0.0.20, `numpy` 1.26.4 | `AiyagariDolARK.ipynb` |

`.venv-hark` holds the package `aiyagari1994qje` as an editable install, so the notebook uses the code in `src/`. The DolARK notebook imports the package's population module from `src/` directly: it needs only numpy and scipy, and the package's names are imported lazily, so importing it there does not import HARK. To work in the notebooks interactively after running `./setup_envs.sh`:

```bash
.venv-hark/bin/jupyter lab   # both kernels are available from either environment
```

## Repository Contents

### Notebooks

- **`AiyagariMarkovHARK.ipynb`**: the economy, step by step, with HARK (about 15 minutes)
  - States the economy, builds Aiyagari's income chain, and solves the household's problem with HARK's `MarkovConsumerType`
  - Computes the population of households two ways, by simulation and as the stationary distribution, and shows the first version's two numerical errors
  - Finds the equilibrium, and shows it converging as the settings are refined
  - Draws the baseline economy (σ = 0.2, ρ = 0.6, μ = 3) and saves the figures and numbers to `baseline/`
  - Reproduces all of Table II at the medium level, compares it with Aiyagari's and DolARK's, and ends with exercises

- **`AiyagariDolARK.ipynb`**: the same economy with dolo and DolARK (about 10 minutes at its default, low level)
  - The household's problem is written in `Aiyagari.yaml` and solved by dolo's time iteration; the population by the REMARK's population code
  - Checks that its income chain is HARK's, finds the baseline equilibrium, and reproduces Table II
  - Says what the first version of the notebook got wrong, and how much each difference mattered

### Key Files

| File | Purpose |
|---|---|
| `reproduce.sh` | Full reproduction: builds the environments and executes both notebooks into `results/` |
| `reproduce_min.sh` | Quick check: solves the baseline with the package and checks every number against `baseline/numbers.json`, then with DolARK and checks it against the record and HARK's |
| `setup_envs.sh` | Builds `.venv-hark` and `.venv-dolark` from their lockfiles and registers their Jupyter kernels |
| `src/aiyagari1994qje/` | The package: the model (`model.py`), the population code (`population.py`) and the figures (`figures.py`) |
| `pyproject.toml`, `uv.lock` | The package and the HARK notebook's environment, and the lockfile that pins every version |
| `dolark-environment/` | The DolARK notebook's environment (`pyproject.toml`, `uv.lock`), its computation packaged (`aiyagari_dolark.py`), and the account of its first version (`first_version.py`) |
| `Aiyagari.yaml` | The model file that dolo and DolARK read |
| `table-ii/` | Table II solved by each toolkit at each level, Aiyagari's published table, and `record.py`, which writes them |
| `docs/model.md` | The economy stated exactly, with a register of the conventions that made two solutions differ |
| `tests/` | Tests: the population code against populations known exactly, in both environments; HARK's rule read back from its export; the README's baseline table against `baseline/numbers.json` |
| `Dockerfile` | Container that runs `reproduce.sh` |
| `binder/environment.yml`, `binder/postBuild` | Binder and REMARK-tooling adapter: installs uv, then builds the environments |
| `myst.yml`, `.github/workflows/myst-deploy.yml` | Publishes the notebooks as a website on GitHub Pages on every push to `main` |
| `.github/workflows/reproduce.yml`, `.github/check_baseline.py` | CI: on every push, runs `reproduce_min.sh`, installs the package with pip on Python 3.11 to 3.14 and checks its numbers, and builds the Docker image; on release tags and on demand, runs the full reproduction in Docker and checks the regenerated `baseline/` against the committed one |
| `baseline/` | The baseline economy's figures (`consumption-functions`, `wealth-lorenz`, `capital-supply-demand`, each as PNG and SVG) and `numbers.json`; written by the HARK notebook |
| `CITATION.cff`, `REMARK.md` | Citation and REMARK metadata |

## Model Description

Infinitely lived households face idiosyncratic shocks to their labor endowment, cannot insure them, and cannot borrow. The log endowment is an AR(1), which Aiyagari represents, and his households face, as a seven-state Markov chain built by Tauchen's method; the chain's moments differ from the AR(1)'s, most at high persistence. Firms produce with Cobb-Douglas technology. In the stationary equilibrium, households hold the capital firms use, at the interest rate firms pay.

Parameters follow the paper: β = 0.96, capital share α = 0.36, depreciation δ = 0.08, with σ ∈ {0.2, 0.4}, ρ ∈ {0, 0.3, 0.6, 0.9} and relative risk aversion μ ∈ {1, 3, 5}. [`docs/model.md`](docs/model.md) states the economy exactly: the household's problem, the chain, the solution and its objects, when it exists, and what a solution reports.

## Key Results

Across the 24 cells of Table II, compared with Aiyagari's published interest rates:

| Solution | Largest gap | Mean gap |
|---|---|---|
| HARK, high level | 0.26 pp | 0.07 pp |
| DolARK, high level | 0.26 pp | 0.07 pp |
| HARK, version 1.1's original settings | 0.20 pp | 0.04 pp |
| DolARK, version 1.1's model file | 1.85 pp | 0.47 pp |

The converged gaps are largest where income is most persistent and most volatile and households most averse to risk (σ = 0.4, ρ = 0.9, μ = 5), where Aiyagari's interest rates are lower than the converged ones. The original settings' table was closer to Aiyagari's than the converged one, by its mean gap: agreement with a published table is not evidence of accuracy.

HARK and DolARK agree with each other far more closely than either agrees with Aiyagari: their interest rates differ by at most 0.017 percentage points at the low level, 0.0032 at the medium level and 0.00024 at the high level. HARK's medium level is within 0.009 percentage points of its high level in every cell. Aiyagari's saving rate is $\delta\alpha/(r + \delta)$ at his interest rate in every cell, rounded, so his table holds one number per cell.

### The Baseline Economy

At the baseline calibration (σ = 0.2, ρ = 0.6, μ = 3), at the medium level, from `baseline/numbers.json`:

| Quantity | Value |
|---|---|
| Equilibrium interest rate | 3.88% (Aiyagari: 3.88%) |
| Saving rate | 24.25% (Aiyagari: 24.25%) |
| Capital, relative to complete markets (r = 1/β − 1 = 4.17%) | about 4% higher (3.8%) |
| Wealth Gini | 0.39 |
| Share of wealth held by the richest 1% | 3.8% |
| Share of households at the borrowing constraint | 0.34% |
| Average marginal propensity to consume | 0.055 |

The labor endowment is not normalized: labor supply L, the chain's mean endowment, is 1.02, and capital and the wage are levels for a population of mass one. `numbers.json` also records the economy actually solved (the chain, with its moments), the settings, and the diagnostics.

### Using the Model in Another Program: the `aiyagari1994qje` Package

The HARK computation is a package that installs with pip or uv on Python 3.11 to 3.14. Pin a commit, so that your results do not change when this repository does:

```bash
pip install "aiyagari1994qje @ git+https://github.com/econ-ark/Aiyagari1994QJE@<commit>"
```

```python
from aiyagari1994qje import Calibration, LEVELS, solve_equilibrium, plot_capital_market

eq = solve_equilibrium(Calibration())   # Aiyagari's baseline, at the medium level; about half a minute
eq.interest_rate, eq.saving_rate_from_capital, eq.capital, eq.gini
eq.numbers()                            # everything in baseline/numbers.json
eq.diagnostics()                        # Euler equation errors, market residuals, shares beyond the grids
plot_capital_market(eq, ax)             # draws on a matplotlib Axes; about a minute

solve_equilibrium(Calibration(), settings=LEVELS["high"])       # converged further; about a minute
solve_equilibrium(Calibration(), settings=LEVELS["original"])   # version 1.1's settings, number for number
```

`Calibration` takes any of the paper's parameters, for example `Calibration(income_standard_deviation=0.4, income_persistence=0.9, relative_risk_aversion=5)`; `Settings` takes the method's choices: the grid of HARK's rule, how the population is computed (`"histogram"` or `"simulation"`), the population's grid, and the simulation's seed. The steps of the computation are public too, for showing them one at a time: `tauchen_chain`, `make_households` (a HARK `MarkovConsumerType`), `solve_households`, `stationary_population`, `simulate`, `capital_supply` and `capital_demand`; `aiyagari1994qje.population` computes a stationary population from any toolkit's rule, and `eq.rule()` writes HARK's rule out as data, which `aiyagari1994qje.evaluate_rule` evaluates without HARK. The plotting functions only draw on the Axes they are given; they set no styles and neither save nor show a figure. `table_ii()` recomputes all of Table II, in about ten minutes at the medium level.

The package's dependencies are ranges (`econ-ark>=0.17`, `numpy>=2`, and current `scipy`, `matplotlib` and `sympy`), so it fits into other projects' environments. With econ-ark 0.17.2 it returns exactly the notebook's numbers: CI installs it with pip on Python 3.11 to 3.14 and checks every number against `baseline/numbers.json`.

The saving rate comes two ways. `saving_rate_from_capital` is δK/Y = δα/(r + δ), gross investment over output in a steady state, which is how Aiyagari computes it: at his interest rates it gives his Table II saving rates exactly. `saving_rate` is 1 − C/Y in the population. In a stationary equilibrium the two are equal, since C + δK = Y, and they are at the medium level; with the original settings' simulation they differ by 0.05 percentage points, because its population had not settled.

### Using the Baseline Figures and Numbers Elsewhere

The files in `baseline/` are committed, so other documents can also use them directly, without installing anything. To keep a document from changing when this repository does, link a specific commit rather than a branch or a tag, for example `https://raw.githubusercontent.com/econ-ark/Aiyagari1994QJE/<commit>/baseline/capital-supply-demand.png`. `numbers.json` records the calibration, the settings and the chain solved, and defines every number.

The committed files are those the Docker image writes. They carry no timestamps or version stamps, so rerunning the notebook on the same platform rewrites every file byte for byte. On another platform the numbers, the SVG files and every pixel of the PNG files come out the same, but the PNG files' bytes can differ, because the compression depends on the zlib library that writes them. On every release, the full CI run regenerates `baseline/` in Docker and checks the numbers and pixels against the committed files with `.github/check_baseline.py`.

## The Results of Record

`table-ii/` holds Table II solved cell by cell by each toolkit at each level, each file written by `table-ii/record.py` with each cell's numbers and diagnostics, the commit, the versions, the machine and each cell's duration; [`table-ii/README.md`](table-ii/README.md) says what they establish. The notebooks read them to compare one toolkit with the other.

## Preparing for a Comparison of Toolkits

The REMARK is arranged so that a comparison of toolkits' solutions, such as those [SCE Working Group 1](https://github.com/econ-ark/sce-wg-1) builds, can start from it:

- **An exact statement** of the economy, its solution and its objects, the conditions under which it exists, and what a solution reports ([`docs/model.md`](docs/model.md));
- **Members**: Table II's 24 cells, with Aiyagari's numbers as published values, not a reference;
- **The economy actually solved** recorded with each solution: the chain and its moments;
- **The parameters apart from the settings**, and named levels of settings that converge;
- **One population code for every toolkit**, on a grid of its own, so that toolkits differ only by their rules;
- **Diagnostics that need no reference solution**, and a high-level record from two toolkits that agree to within its tolerance;
- **A register of conventions** that made two solutions differ ([`docs/model.md`](docs/model.md)).

Still open for such a comparison: whether its canonical income process is the AR(1) or Aiyagari's stated chain, which are different economies.

## Output Guide

`reproduce.sh` writes executed copies of both notebooks to `results/` (the notebooks in the repository are left unchanged). In the HARK notebook, the cells show, in order, the economy's statement, Aiyagari's chain and its moments, the consumption functions at 3 percent, the market for capital, the population computed by simulation and as a stationary distribution, the rule's grid refined, the equilibrium at each level, the baseline economy's figures and numbers, and Table II with its comparisons. Running the HARK notebook also rewrites the files in `baseline/`.

## Educational Applications

### Prerequisites
- Graduate-level macroeconomic theory: dynamic programming, the consumption-saving problem, competitive equilibrium
- Some Python programming experience
- Familiarity with Markov chains

### Learning Objectives
- Define a stationary equilibrium with heterogeneous households and incomplete markets, and say why its interest rate lies below the rate of time preference
- Solve a household's problem under uninsurable risk and a borrowing limit with HARK, and the same problem with dolo
- Compute a stationary distribution two ways, and recognize the errors of each
- Tell a numerical solution's error from a model's property: converge settings, compare toolkits, and read a published table as one computation among others

## Technical Implementation

### Solution Methods

- **Income**: Aiyagari's seven-state Tauchen chain, built identically for both toolkits
- **Household problem**: HARK's `MarkovConsumerType` (endogenous grid method), with the wage normalized to one; dolo's time iteration, with linear interpolation on a grid dense near the borrowing limit
- **Population**: the stationary distribution on a grid of end-of-period assets of its own, by Young's (2010) lottery, solved directly; the same code for both toolkits. The original settings simulate 1,000 households for 1,000 periods instead
- **Equilibrium**: Brent's method (`scipy.optimize.brentq`), on the interest factor (HARK) or on capital (DolARK)

### System Requirements

- Version 1.1 was tested on macOS (Apple silicon), with uv and through the conda adapter, and on Linux through the `Dockerfile`; version 2.0 was run on Linux (x86-64) with uv, and CI builds its Docker image on every push and runs it on release tags. Run times quoted are for one core of a recent machine; Binder's machines are slower and vary
- About 1.4 GB of disk for the two environments, plus about 100 MB for Python 3.14.7 if uv downloads it
- The Jupyter kernels are registered single-threaded (`OMP_NUM_THREADS=1` and similar). With a thread per core, the DolARK notebook ran nearly three times slower on a Mac and did not finish in an hour on Binder, whose sessions get one CPU but see every core of the host
- `table-ii/record.py` solves the 24 cells in parallel, one core each; dolo's high level needs about 2 GB of memory per process

## Troubleshooting

- **`uv: command not found`**: install uv, or use the conda route, which installs it.
- **`No interpreter found for Python 3.14.7`**: uv is too old to download it; update uv (`uv self update`) or install Python 3.14.7 yourself.
- **`uv sync` fails with a lockfile error**: run the scripts unchanged; `--locked` refuses to proceed if a `pyproject.toml` and its `uv.lock` disagree, which means one of them was edited.
- **Jupyter reports a missing kernel**: run `./setup_envs.sh`, then start Jupyter from `.venv-hark` or `.venv-dolark`.

## Citation

If you use this implementation, please cite:

```bibtex
@software{edwards2024aiyagari,
  author = {Edwards, Adam},
  title = {Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving - Computational Implementation},
  url = {https://github.com/econ-ark/Aiyagari1994QJE},
  version = {2.0.0},
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
