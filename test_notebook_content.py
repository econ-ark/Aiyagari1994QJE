#!/usr/bin/env python3
"""
Test script to execute the AiyagariMarkovHARK_baseline notebook content step by step
"""

print("=== STEP 1: IMPORTS ===")
try:
    import time
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from copy import deepcopy
    from scipy.optimize import brentq

    from HARK.ConsumptionSaving.ConsMarkovModel import MarkovConsumerType
    from HARK.distribution import make_tauchen_ar1
    from HARK.distribution import DiscreteDistributionLabeled
    from HARK.utilities import plot_funcs
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

print("\n=== STEP 2: PARAMETER SETUP ===")
try:
    N = 7 # Number of income grid points
    σ = 0.2
    ρ = 0.6
    μ = 3

    shock_sd = lambda rho, sigma: sigma*(1-rho**2)**0.5
    incomes, transition_matrix = make_tauchen_ar1(N, shock_sd(ρ, σ), ρ, 3)
    print(f"✅ Tauchen discretization successful, got {len(incomes)} income states")
    print(f"Income range: [{np.min(incomes):.3f}, {np.max(incomes):.3f}]")
except Exception as e:
    print(f"❌ Parameter setup failed: {e}")
    exit(1)

print("\n=== STEP 3: AGENT SETUP ===")
try:
    T = 1000
    T_sum = 700

    AiyagariMarkovAgentDictionary = {
        "CRRA": 5.0,  # Coefficient of relative risk aversion
        "Rfree": 1.03,  # Interest factor on assets
        "DiscFac": 0.96,  # Intertemporal discount factor
        "LivPrb": [np.array(N * [1.0])],  # Survival probability
        "AgentCount": 1000,  # Number of agents of this type (only matters for simulation)
        "aNrmInitMean": 0.0,  # Mean of log initial assets (only matters for simulation)
        "aNrmInitStd": 1.0,  # Standard deviation of log initial assets (only for simulation)
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
        # Parameters describing the income process
        "UnempPrb": 0.0,  # Probability of unemployment while working
        "UnempPrbRet": 0.0,  # Probability of "unemployment" while retired
        "IncUnemp": 0.0,  # Unemployment benefits replacement rate
        "IncUnempRet": 0.0,  # "Unemployment" benefits when retired
        "tax_rate": 0.0,  # Flat income tax rate
        "T_retire": 0,  # Period of retirement (0 --> no retirement)
        "BoroCnstArt": 0.0,  # Artificial borrowing constraint; imposed minimum level of end-of period assets
        "CubicBool": False,  # Use cubic spline interpolation when True, linear interpolation when False
        "vFuncBool": False,  # Whether to calculate the value function during solution
        "global_markv": False,
        "cycles": 0,
        "PermGroFac": [np.array(N * [1.0])],
    }

    AiyagariMarkovAgentDictionaryCopy = deepcopy(AiyagariMarkovAgentDictionary)
    AiyagariMarkovAgentDictionaryCopy["CRRA"] = μ
    AiyagariMarkovAgentDictionaryCopy["MrkvArray"] = [transition_matrix]

    AiyagariMarkovType = MarkovConsumerType(**AiyagariMarkovAgentDictionaryCopy)
    AiyagariMarkovType.T_sim = T
    AiyagariMarkovType.track_vars = ["aNrm", "cNrm", "TranShk"]
    AiyagariMarkovType.MrkvPrbsInit = [1/N]*N

    # This defines the labor endowements that the agents will be transitioning between
    AiyagariMarkovType.IncShkDstn = [
        [DiscreteDistributionLabeled(pmv=np.ones(1), atoms=np.array([[1.0], [np.exp(x)]]), var_names=["PermShk", "TranShk"]) for x in incomes]
    ]
    print("✅ Agent setup successful")
except Exception as e:
    print(f"❌ Agent setup failed: {e}")
    exit(1)

print("\n=== STEP 4: SOLVE AND SIMULATE ===")
try:
    R = 1.03
    AverageAggregateVar = lambda var: np.mean(np.sum(var[T-T_sum:T-1], axis=1))

    AiyagariMarkovType.Rfree = np.array(N * [R])
    AiyagariMarkovType.solve()
    print("✅ Agent solved successfully")
    
    AiyagariMarkovType.make_shock_history()
    AiyagariMarkovType.initialize_sim()
    AiyagariMarkovType.simulate()
    print("✅ Simulation completed successfully")
    
    avg_assets = AverageAggregateVar(AiyagariMarkovType.history["aNrm"])
    print(f"Average normalized aggregate capital: {avg_assets:.4f}")
    
except Exception as e:
    print(f"❌ Solve/simulate failed: {e}")
    exit(1)

print("\n=== STEP 5: EQUILIBRIUM FUNCTIONS ===")
try:
    α = 0.36
    δ = 0.08
    RFunc = lambda k : 1.0 + α * k ** (α - 1.0) - δ
    wFunc = lambda k: (1.0 - α) * k ** (α)
    RFunc_inv = lambda R : ((R - 1.0 + δ)/α)**(1.0/(α - 1.0))

    # This function takes an interest rate, simulates an economy with such an interest rate, and calculates the interest rates implied by aggregate saving. 
    def CalculateImpliedR(R):
        wRte = wFunc(RFunc_inv(R))

        # Give the agents the proposed interest factor and calculate wage rate
        AiyagariMarkovType.Rfree = np.array(np.array(N * [R]))
        
        # Solve and simulate the agents
        AiyagariMarkovType.solve()
        AiyagariMarkovType.initialize_sim()
        AiyagariMarkovType.simulate()
        
        # Extract the agents' level of assets (capital holdings) and productivity at the end
        aNrm_agg = AverageAggregateVar(AiyagariMarkovType.history["aNrm"])
        pNrm_agg = AverageAggregateVar(AiyagariMarkovType.history["TranShk"])
        
        # Calculate aggregate capital and labor and take their ratio
        K = aNrm_agg*wRte # since assets are normalized, multiply by wage rate
        L = pNrm_agg
        k = K/L
        
        # Use the rule for determining Rfree to update the interest factor
        return RFunc(k)

    def EquilibriumFunc(R):
        calculated = CalculateImpliedR(R)
        print(f"Input R: {R:.6f} || Implied R: {calculated:.6f} || Difference {calculated - R:.6e}")
        return calculated - R
    
    print("✅ Equilibrium functions defined successfully")
except Exception as e:
    print(f"❌ Equilibrium function setup failed: {e}")
    exit(1)

print("\n=== STEP 6: FIND EQUILIBRIUM ===")
try:
    print("Finding equilibrium interest rate...")
    R_star = brentq(EquilibriumFunc, 0.99, 1.05)
    print(f"✅ Equilibrium found: R* = {R_star:.6f}")
except Exception as e:
    print(f"❌ Equilibrium finding failed: {e}")
    exit(1)

print("\n🎉 ALL TESTS PASSED! The notebook core functionality works correctly.")
