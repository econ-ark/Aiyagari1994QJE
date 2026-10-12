#!/bin/bash

# Aiyagari (1994QJE) Model - Quick Reproduction Script for CI
# This script runs only baseline parameters for fast CI testing (~10 seconds)

set -e  # Exit on any error

echo "=== Aiyagari (1994QJE) Model - Quick CI Reproduction ==="
echo "Starting minimal reproduction at $(date)"

cd "$(dirname "$0")"

# Build the pinned environments from uv.lock; this test needs only the HARK one
./setup_envs.sh
PYTHON_CMD=".venv-hark/bin/python"

# Create a simple baseline test script
echo ""
echo "=== Creating baseline parameter test for CI ==="
cat > baseline_test.py << 'EOF'
# Baseline Aiyagari (1994) Model Test for CI
# Parameters: σ=0.2, ρ=0.6, μ=1 (single combination)

import sys
import time
import numpy as np
from copy import deepcopy
from scipy.optimize import brentq
from functools import lru_cache
import random
import warnings

# Replaying a stored shock history, HARK warns that it does not store the aggregate
# productivity level PlvlAgg; that level is constant here (PermGroFacAgg = 1).
warnings.filterwarnings("ignore", message="The option for reading shocks was activated")

# Import HARK modules
try:
    from HARK.ConsumptionSaving.ConsMarkovModel import MarkovConsumerType, markov_constructor_dict
    from HARK.distributions import DiscreteDistributionLabeled, make_tauchen_ar1
except ImportError as e:
    print(f"Error importing HARK: {e}")
    print("Please ensure HARK is installed: pip install econ-ark")
    sys.exit(1)

print("=== Baseline Aiyagari Model Test ===")
print("Parameters: σ=0.2, ρ=0.6, μ=1")

# Model parameters (baseline)
N = 7  # Number of Markov states (using 7 like in notebook)
T = 500  # Number of periods to simulate
T_sum = 300  # Periods to average over
δ = 0.08  # Depreciation rate
α = 0.36  # Capital share
σ = 0.2   # Income volatility
ρ = 0.6   # Income persistence  
μ = 1     # Risk aversion (CRRA)

# Utility functions
shock_sd = lambda rho, sigma: sigma*(1-rho**2)**0.5

# Production functions  
RFunc = lambda k : 1.0 + α * k ** (α - 1.0) - δ
wFunc = lambda k: (1.0 - α) * k ** (α)
RFunc_inv = lambda R : ((R - 1.0 + δ)/α)**(1.0/(α - 1.0))

AverageAggregateVar = lambda var: np.mean(np.sum(var[T-T_sum:T-1], axis=1))

# Agent parameters (exact copy from notebook)
AiyagariMarkovAgentDictionary = {
    "CRRA": 5.0,  # Coefficient of relative risk aversion
    "Rfree": [np.array(N * [1.03])],  # Interest factor on assets, for each labor endowment state
    "DiscFac": 0.96,  # Intertemporal discount factor
    "LivPrb": [np.array(N * [1.0])],  # Survival probability
    "AgentCount": 1000,  # Number of agents of this type (only matters for simulation)
    "kLogInitMean": 0.0,  # Mean of log initial assets (only matters for simulation)
    "kLogInitStd": 1.0,  # Standard deviation of log initial assets (only for simulation)
    "PermGroFacAgg": 1.0,  # Aggregate permanent income growth factor (only matters for simulation)
    "T_age": None,  # Age after which simulated agents are automatically killed
    "T_cycle": 1,  # Number of periods in the cycle for this agent type
    # Parameters for constructing the "assets above minimum" grid
    "aXtraMin": 0.001,  # Minimum end-of-period "assets above minimum" value
    "aXtraMax": 20,  # Maximum end-of-period "assets above minimum" value
    # Some other value of "assets above minimum" to add to the grid
    "aXtraExtra": np.array([0.005, 0.01]),
    "aXtraNestFac": 3,  # Exponential nesting factor when constructing "assets above minimum" grid
    "aXtraCount": 48,  # Number of points in the grid of "assets above minimum"
    "BoroCnstArt": 0.0,  # Artificial borrowing constraint; imposed minimum level of end-of period assets
    "CubicBool": False,  # Use cubic spline interpolation when True, linear interpolation when False
    "vFuncBool": False,  # Whether to calculate the value function during solution
    "global_markov": False,
    "cycles": 0,
    "PermGroFac": [
        np.array(N * [1.0])
    ],
    "MrkvPrbsInit": np.array(N * [1 / N]),  # Initial distribution of labor endowment states
    # The labor endowment process and its transition matrix are set below
    "constructors": {**markov_constructor_dict, "IncShkDstn": None, "MrkvArray": None},
}

# Create income process
print("Creating income process...")
incomes, transition_matrix = make_tauchen_ar1(N, shock_sd(ρ, σ), ρ, 3)

# Set up agent
AiyagariMarkovAgentDictionaryCopy = deepcopy(AiyagariMarkovAgentDictionary)
AiyagariMarkovAgentDictionaryCopy["CRRA"] = μ
AiyagariMarkovAgentDictionaryCopy["MrkvArray"] = [transition_matrix]
AiyagariMarkovAgentDictionaryCopy["IncShkDstn"] = [
    [DiscreteDistributionLabeled(pmv=np.ones(1), atoms=np.array([[1.0], [np.exp(x)]]), var_names=["PermShk", "TranShk"]) for x in incomes]
]

AiyagariMarkovType = MarkovConsumerType(**AiyagariMarkovAgentDictionaryCopy)
AiyagariMarkovType.T_sim = T
AiyagariMarkovType.track_vars = ["aNrm", "cNrm", "TranShk"]

@lru_cache(maxsize=5)
def solve_and_simulate(R):
    AiyagariMarkovType.Rfree = [np.full(N, R)]
    AiyagariMarkovType.solve()
    AiyagariMarkovType.initialize_sim()
    AiyagariMarkovType.simulate()
    aAgg = AverageAggregateVar(AiyagariMarkovType.history["aNrm"])
    pAgg = AverageAggregateVar(AiyagariMarkovType.history["TranShk"])
    return aAgg, pAgg

# Define equilibrium function (exact copy from notebook)
def CalculateImpliedR(R):
    aNrm_agg, pNrm_agg = solve_and_simulate(R)
    wRte = wFunc(RFunc_inv(R))
    K = aNrm_agg * wRte
    L = pNrm_agg
    k = K / L
    return RFunc(k)

def EquilibriumFunc(R):
    calculated = CalculateImpliedR(R)
    print(f"Input R: {R: .6f} | Implied R: {calculated: .6f} | Diff: {calculated - R: .6e}")
    return calculated - R

# Generate shock history
print("Generating shock history...")
start_time = time.process_time()
AiyagariMarkovType.make_shock_history()
print(f"Time to generate shock history: {time.process_time() - start_time:.2f} seconds")

# Solve for equilibrium over the same bracket as the notebook
print("Solving for equilibrium interest rate...")
start_time = time.process_time()
R_star = brentq(EquilibriumFunc, 0.99, 1.05)
solve_time = time.process_time() - start_time

# Calculate results (exact copy from notebook)
cNrm_agg = AverageAggregateVar(AiyagariMarkovType.history["cNrm"])
aNrm_agg = AverageAggregateVar(AiyagariMarkovType.history["aNrm"])
pNrm_agg = AverageAggregateVar(AiyagariMarkovType.history["TranShk"])

income = (R_star - 1.0 + δ)*aNrm_agg + pNrm_agg
saving = (1 - cNrm_agg/income)*100
saving_rate = float("%.2f" % saving)

interest = (R_star - 1)*100
interest_rate = float("%.4f" % interest)

print(f"Equilibrium solving time: {solve_time:.2f} seconds")
print(f"σ: {σ} ρ: {ρ} μ: {μ} || Interest rate: {interest_rate}% || Aggregate saving rate: {saving_rate}%")

# Validation checks
if not (1.0 < R_star < 1.1):
    print(f"WARNING: Interest rate {R_star:.4f} outside expected range")
    sys.exit(1)

if not (20.0 < saving_rate < 30.0):
    print(f"WARNING: Saving rate {saving_rate:.2f}% outside expected range")
    sys.exit(1)

print("✓ Baseline Aiyagari model test completed successfully!")
print(f"✓ All validation checks passed")
EOF

echo "✓ Created baseline test script"

echo ""
echo "=== Executing baseline Aiyagari model (σ=0.2, ρ=0.6, μ=1) ==="
echo "Expected runtime: ~10 seconds"
$PYTHON_CMD baseline_test.py

# Clean up
rm -f baseline_test.py

echo ""
echo "=== Quick CI reproduction completed successfully at $(date) ==="
echo "Baseline model executed in ~10 seconds. Run reproduce.sh for full parameter sweep." 