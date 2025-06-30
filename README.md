# Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/econ-ark/Aiyagari1994QJE/HEAD)

## Overview

This repository provides a computational implementation of the seminal **Aiyagari (1994)** model of uninsured idiosyncratic risk and aggregate saving. The model demonstrates how precautionary saving motives and liquidity constraints affect aggregate economic outcomes in a heterogeneous agent framework.

## Key Features

- **Two Solution Approaches**: MarkovConsumerType and DolARK methods using the HARK framework
- **Complete Parameter Replication**: All parameter combinations from original Aiyagari (1994) Table II
- **High Accuracy Results**: Replication within 0.05 percentage points for interest rates
- **Modern Tools**: Poetry and conda environment management for reproducibility
- **Educational Focus**: Detailed documentation for learning heterogeneous agent models

## Quick Start

### Option 1: Poetry (Recommended for Development)
```bash
# Install dependencies
poetry install

# Quick baseline test (~30 seconds)
./run_baseline.sh

# Full parameter sweep (~10-15 minutes)  
./run_full.sh
```

### Option 2: Conda (MyBinder Compatible)
```bash
# Create environment
conda env create -f binder/environment.yml
conda activate Aiyagari1994QJE

# Quick baseline test (~30 seconds)
./run_baseline.sh

# Full parameter sweep (~10-15 minutes)
./run_full.sh
```

### Option 3: Docker (Containerized Environment)
```bash
# Start Jupyter Lab environment
docker-compose up aiyagari-notebook
# Then open http://localhost:8888

# Quick baseline test (~30 seconds)
docker-compose --profile baseline up aiyagari-baseline

# Full parameter sweep (~10-15 minutes)
docker-compose --profile full up aiyagari-full
```

### Option 4: Cloud Execution
Click the Binder badge above to run in your browser without local installation.

### Execution Modes

The repository provides dedicated scripts for different execution modes:

#### Quick Testing (Baseline Mode)
```bash
./run_baseline.sh
```
- **Runtime**: ~30 seconds
- **Purpose**: Single parameter combination (σ=0.2, ρ=0.6, μ=1)
- **Use case**: Quick verification, CI testing, development

#### Full Replication (Complete Analysis)
```bash
./run_full.sh
```
- **Runtime**: ~10-15 minutes  
- **Purpose**: All 24 parameter combinations with comparison tables
- **Use case**: Complete research replication, final results

#### Legacy Scripts (Alternative)
```bash
# Quick demonstration (one notebook, ~5 minutes)
./reproduce_min.sh

# Full reproduction (both notebooks, ~20 minutes)
./reproduce.sh
```

## Repository Contents

### Notebooks
- **`AiyagariMarkovHARK.ipynb`**: Primary implementation using MarkovConsumerType
  - Detailed equilibrium analysis
  - Complete parameter space exploration
  - Comparison with original Aiyagari results
  
- **`AiyagariDolARK.ipynb`**: Alternative implementation using DolARK methods
  - Different solution approach for verification
  - Computational method comparison

### Key Files
- **`CITATION.cff`**: Bibliographic metadata for proper citation
- **`reproduce.sh`**: Complete reproduction script (both notebooks)
- **`reproduce_min.sh`**: Quick demonstration script (primary notebook only)
- **`run_baseline.sh`**: Quick testing script (30 seconds)
- **`run_full.sh`**: Full replication script (10-15 minutes)
- **`pyproject.toml`**: Poetry configuration for local development
- **`binder/environment.yml`**: Conda environment for reproducibility
- **`Dockerfile`**: Container image specification
- **`docker-compose.yml`**: Multi-service container orchestration
- **`DOCKER.md`**: Comprehensive Docker usage guide

## Model Description

The Aiyagari model features:

- **Heterogeneous Agents**: Infinitely-lived households facing idiosyncratic income shocks
- **Incomplete Markets**: No insurance against individual income risk
- **Borrowing Constraints**: Agents cannot borrow against future income
- **Precautionary Saving**: Individual risk leads to aggregate capital accumulation
- **Equilibrium Analysis**: Endogenous interest rate clears asset market

## Key Results

This implementation successfully replicates:

- **Table II from Aiyagari (1994)**: Interest rates and saving rates across parameter combinations
- **Parameter Effects**: How risk aversion (θ), income persistence (ρ), and volatility (σ) affect outcomes
- **Comparative Statics**: Systematic analysis of equilibrium responses

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
- **Tauchen Discretization**: AR(1) income process → discrete Markov chain
- **Value Function Iteration**: Individual dynamic programming
- **Bisection Search**: Equilibrium interest rate computation
- **Monte Carlo Simulation**: Aggregate consistency verification

### Computational Features
- Vectorized operations for efficiency
- Robust numerical methods
- Comprehensive error handling
- Detailed logging and progress tracking

## Citation

If you use this implementation, please cite:

```bibtex
@software{edwards2024aiyagari,
  author = {Edwards, Adam},
  title = {Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving - Computational Implementation},
  url = {https://github.com/econ-ark/Aiyagari1994QJE},
  version = {1.0.0},
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
