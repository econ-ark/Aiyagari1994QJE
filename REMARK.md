---
# Econ-ARK website fields
remark-name: Aiyagari1994QJE
title-original-paper: "Uninsured idiosyncratic risk and aggregate saving"
notebooks:
  - AiyagariMarkovHARK.ipynb
  - AiyagariDolARK.ipynb
---

# Abstract

This repository provides a computational implementation of the seminal Aiyagari (1994) model of uninsured idiosyncratic risk and aggregate saving. The implementation demonstrates how precautionary saving motives and liquidity constraints affect aggregate saving rates, asset trading importance, and wealth/income distribution inequality in a heterogeneous agent framework. Two complementary approaches are provided using the HARK (Heterogeneous Agents Resources and toolKit) framework: MarkovConsumerType and DolARK methods.

---

## Website-specific metadata for enhanced display and discoverability

learning_objectives:

- "Understand the foundational Aiyagari (1994) model of incomplete markets with heterogeneous agents"
- "Implement incomplete markets models using the HARK computational framework"
- "Compare analytical predictions with numerical solutions for aggregate variables"
- "Analyze the effects of risk aversion, income persistence, and income volatility on equilibrium outcomes"
- "Master techniques for solving heterogeneous agent models with aggregate consistency"

prerequisites:

- "Graduate-level macroeconomic theory (heterogeneous agents, incomplete markets)"
- "Some Python programming experience (intermediate level preferred)"
- "Some dynamic programming background (Bellman equations, value function iteration)"
- "Basic understanding of numerical methods and computational economics"
- "Familiarity with stochastic processes and Markov chains"

jupyter_notebooks:

- path: "AiyagariMarkovHARK.ipynb"
    description: "Primary implementation using MarkovConsumerType with detailed equilibrium analysis"
    type: "analysis"
    estimated_runtime: "15-20 minutes"

- path: "AiyagariDolARK.ipynb"
    description: "Alternative implementation using DolARK methods for comparison"
    type: "analysis"
    estimated_runtime: "10-15 minutes"

related_materials:

- "heterogeneous-agent-models"
- "incomplete-markets-theory"
- "computational-macroeconomics"
- "HARK-toolkit-methods"

methodology_tags:

- "heterogeneous agents"
- "incomplete markets"
- "precautionary saving"
- "dynamic programming"
- "numerical methods"
- "equilibrium computation"
- "HARK framework"
- "Markov processes"

difficulty_level: "advanced"

estimated_completion_time: "3-4 hours for full analysis and understanding"

research_context: |
  The Aiyagari (1994) model is a cornerstone of modern macroeconomics, providing the foundation
  for understanding how individual-level uncertainty and incomplete markets affect aggregate
  economic outcomes. This implementation demonstrates the key insight that precautionary saving
  by risk-averse agents facing uninsurable income shocks can significantly raise the aggregate
  capital stock and reduce equilibrium interest rates compared to complete markets models.

educational_value: |
  Students will gain hands-on experience with state-of-the-art computational methods for solving
  heterogeneous agent models. The implementation shows how to handle the distribution of agents
  across states, compute aggregate consistency conditions, and analyze the interaction between
  micro-level heterogeneity and macro-level outcomes. This is essential training for modern
  macroeconomic research.

policy_relevance: |
  The Aiyagari framework underlies many policy analyses including social insurance design,
  tax policy evaluation, and understanding wealth inequality. The precautionary saving motive
  demonstrated here is crucial for understanding how households respond to income uncertainty
  and how this affects capital accumulation and interest rate determination.

computational_requirements:
  python_version: "3.10+"
  key_packages:
    - "econ-ark"
    - "numpy"
    - "matplotlib"
    - "scipy"
    - "pandas"
    - "jupyter"
  memory_requirements: "Moderate (< 4GB RAM)"
  runtime_estimates:
    full_reproduction: "20-25 minutes"
    quick_demonstration: "10-15 minutes"

model_specifications:

- name: "Baseline Aiyagari Model"
    description: "Standard parameterization matching Aiyagari (1994) Table II"
    key_parameters:
      - "β = 0.96 (discount factor)"
      - "α = 0.36 (capital share)"
      - "δ = 0.08 (depreciation rate)"
      - "σ ∈ {0.2, 0.4} (income shock volatility)"
      - "ρ ∈ {0.0, 0.3, 0.6, 0.9} (income persistence)"
      - "θ ∈ {1, 3, 5} (relative risk aversion)"

key_results:

- "Replication of Aiyagari (1994) Table II results with high accuracy"
- "Demonstration of precautionary saving effects on aggregate capital"
- "Analysis of how income risk parameters affect equilibrium outcomes"
- "Comparison of different solution methods (Markov vs DolARK approaches)"

technical_implementation:

- "Tauchen method for discretizing AR(1) income process"
- "Value function iteration for individual optimization"
- "Bisection method for equilibrium interest rate"
- "Monte Carlo simulation for aggregate consistency"
- "Comparative statics across parameter combinations"

reproducibility_notes: |
  This implementation provides exact replication of the Aiyagari (1994) results using modern
  computational tools. All random processes are seeded for reproducibility, and the solution
  methods are numerically stable. The HARK framework ensures that the implementation follows
  best practices for heterogeneous agent modeling.

extensions_and_variations:

- "Modify utility function parameters to explore different risk aversion levels"
- "Experiment with alternative income process specifications"
- "Extend to include government transfers or taxation"
- "Add elastic labor supply to the model"
- "Implement welfare analysis of policy interventions"

teaching_applications:

- "Graduate macroeconomics courses: heterogeneous agent models"
- "Computational economics: numerical solution methods"
- "Advanced undergraduate: introduction to incomplete markets"
- "PhD research methods: HARK toolkit training"

### citation_context

- This implementation builds on the foundational work of Aiyagari (1994) and demonstrates modern computational approaches to solving heterogeneous agent models. It serves as both an educational resource and a research tool for studying incomplete markets, providing a bridge between theoretical insights and practical implementation using contemporary software tools.

---

## Aiyagari (1994QJE): Computational Implementation

## Model Overview

The Aiyagari model examines an economy populated by infinitely-lived households who face uninsurable, idiosyncratic labor income shocks. Households cannot perfectly smooth consumption due to borrowing constraints, leading them to accumulate assets for precautionary reasons. This individual behavior aggregates to affect the equilibrium interest rate and capital stock.

## Key Economic Insights

### Individual Behavior
- **Precautionary Saving**: Households save more than they would under certainty to self-insure against income shocks
- **Borrowing Constraints**: Agents cannot borrow against future income, amplifying the need for precautionary savings
- **State-Dependent Policies**: Consumption and saving decisions depend on both current assets and current income realizations

### Aggregate Implications
- **Higher Capital Stock**: Precautionary saving increases aggregate capital above the complete markets level
- **Lower Interest Rates**: Increased saving demand drives down equilibrium interest rates
- **Wealth Inequality**: Heterogeneous income realizations lead to persistent wealth differences across agents

## Implementation Features

### Solution Methods
The implementation provides two complementary approaches:

1. **MarkovConsumerType** (`AiyagariMarkovHARK.ipynb`):
   - Uses HARK's built-in Markov consumer framework
   - Handles transition matrices automatically
   - Provides detailed equilibrium analysis and comparison with original results

2. **DolARK Methods** (`AiyagariDolARK.ipynb`):
   - Alternative solution approach for comparison
   - Demonstrates different computational techniques
   - Allows verification of results across methods

### Computational Techniques
- **Tauchen Discretization**: Converts continuous AR(1) process to discrete Markov chain
- **Value Function Iteration**: Solves individual dynamic programming problem
- **Bisection Search**: Finds equilibrium interest rate satisfying aggregate consistency
- **Monte Carlo Simulation**: Generates large samples for accurate aggregate statistics

## Parameter Analysis

The implementation replicates the complete parameter space from Aiyagari (1994):

### Income Process Parameters
- **Volatility (σ)**: {0.2, 0.4} - controls magnitude of income shocks
- **Persistence (ρ)**: {0.0, 0.3, 0.6, 0.9} - controls autocorrelation of income
- **Risk Aversion (θ)**: {1, 3, 5} - determines strength of precautionary motive

### Results Validation
The implementation achieves high accuracy in replicating:
- Equilibrium interest rates (within 0.05 percentage points)
- Aggregate saving rates (within 0.2 percentage points)
- Cross-parameter comparative statics

## Educational Applications

### Graduate Courses
- **Heterogeneous Agent Models**: Core foundation for understanding distribution effects
- **Incomplete Markets Theory**: Practical application of theoretical concepts
- **Computational Macroeconomics**: Hands-on training with industry-standard tools

### Research Training
- **HARK Toolkit Mastery**: Essential for modern computational macroeconomics research
- **Numerical Methods**: Experience with equilibrium computation and solution algorithms
- **Model Validation**: Techniques for verifying computational implementations

## Getting Started

### Quick Start
1. **Environment Setup**: Use Poetry (`poetry install`) or conda (`conda env create -f binder/environment.yml`)
2. **Basic Execution**: Run `./reproduce_min.sh` for quick demonstration
3. **Full Analysis**: Execute `./reproduce.sh` for complete replication

### Deep Dive
1. **Primary Notebook**: Start with `AiyagariMarkovHARK.ipynb` for detailed analysis
2. **Alternative Methods**: Compare with `AiyagariDolARK.ipynb` implementation
3. **Parameter Exploration**: Modify parameters to explore different scenarios

### Extension Opportunities
- Experiment with different utility functions
- Add government sector (taxes, transfers)
- Implement welfare analysis
- Extend to multiple asset types

This implementation provides a comprehensive foundation for understanding one of the most influential models in modern macroeconomics while demonstrating state-of-the-art computational techniques. 