# Aiyagari (1994QJE): Uninsured Idiosyncratic Risk and Aggregate Saving

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/econ-ark/Aiyagari1994QJE/HEAD)

## Overview

This repository provides a computational implementation of the seminal **Aiyagari (1994)** model of uninsured idiosyncratic risk and aggregate saving. The model demonstrates how precautionary saving motives and liquidity constraints affect aggregate economic outcomes in a heterogeneous agent framework.

## Key Features

- **Solution Approach**: A fast, script-based computational backend with an interactive notebook frontend.
- **Complete Parameter Replication**: All 24 parameter combinations from original Aiyagari (1994) Table II.
- **High Accuracy Results**: Replication within 0.05 percentage points for interest rates.
- **Modern Tools**: `jupytext` for notebook versioning and `conda` for environment management.
- **Educational Focus**: Detailed documentation and a clear separation of logic for learning.

## Quick Start

### Minimal Reproduction (Quick Test)

This runs the baseline (single parameter) computation directly for a fast result.

```bash
./reproduce_min.sh
```

- **Runtime**: ~5-10 seconds.
- **Output**: Console display of the equilibrium interest and saving rates.

### Full Reproduction (Complete Analysis)

This runs the full 24-parameter sweep from the Aiyagari (1994) paper.

```bash
./reproduce.sh
```

- **Runtime**: ~2-3 minutes.
- **Output**: Console display of the results for all parameter combinations.

### Interactive Exploration

For an interactive experience, open the `AiyagariMarkovHARK.ipynb` notebook in Jupyter Lab. You can execute the cells to see how the model works step-by-step.

## Repository Contents

### Key Files

- **`aiyagari/core.py`**: The core computational library containing the model's logic.
- **`compute.py`**: The command-line script that runs the baseline or full replication.
- **`reproduce.sh`**: The official script for full reproduction (calls `compute.py`).
- **`reproduce_min.sh`**: The official script for minimal reproduction (calls `compute.py`).
- **`AiyagariMarkovHARK.ipynb`**: The interactive notebook for exploration and visualization.
- **`binder/environment.yml`**: The conda environment file for reproducibility.
- **`CITATION.cff`**: Bibliographic metadata for proper citation.

## Model Description

The Aiyagari model features:

- **Heterogeneous Agents**: Infinitely-lived households facing idiosyncratic income shocks.
- **Incomplete Markets**: No insurance against individual income risk.
- **Borrowing Constraints**: Agents cannot borrow against future income.
- **Precautionary Saving**: Individual risk leads to aggregate capital accumulation.
- **Equilibrium Analysis**: Endogenous interest rate clears asset market.

## Key Results

This implementation successfully replicates:

- **Table II from Aiyagari (1994)**: Interest rates and saving rates across parameter combinations.
- **Parameter Effects**: How risk aversion (θ), income persistence (ρ), and volatility (σ) affect outcomes.
- **Comparative Statics**: Systematic analysis of equilibrium responses.

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
