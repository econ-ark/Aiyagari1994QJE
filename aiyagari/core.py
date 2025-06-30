import numpy as np
from copy import deepcopy
from scipy.optimize import brentq
import pandas as pd

from HARK.ConsumptionSaving.ConsMarkovModel import MarkovConsumerType
from HARK.distributions import make_tauchen_ar1, DiscreteDistributionLabeled

# --- Model Parameters ---
DEFAULT_PARAMS = {
    'N': 7,          # Number of income grid points
    'T': 1000,       # Number of periods to simulate
    'T_sum': 700,    # Periods to average over for steady state
    'α': 0.36,       # Capital share
    'δ': 0.08,       # Depreciation rate
}

# --- Utility and Production Functions ---
def shock_sd(rho, sigma):
    return sigma * (1 - rho**2)**0.5

def r_func(k, alpha, delta):
    return 1.0 + alpha * k**(alpha - 1.0) - delta

def w_func(k, alpha):
    return (1.0 - alpha) * k**alpha

def r_inv_func(R, alpha, delta):
    return ((R - 1.0 + delta) / alpha)**(1.0 / (alpha - 1.0))

def average_aggregate_var(var, T, T_sum):
    return np.mean(np.sum(var[T - T_sum:T - 1], axis=1))

# --- Agent Definition ---
def create_aiyagari_agent(μ, ρ, σ, N, T):
    """
    Creates a HARK MarkovConsumerType agent with Aiyagari model parameters.
    """
    incomes, transition_matrix = make_tauchen_ar1(N, shock_sd(ρ, σ), ρ, 3)
    
    agent_params = {
        "CRRA": μ,
        "Rfree": 1.03, # Placeholder, will be solved for
        "DiscFac": 0.96,
        "LivPrb": [np.array(N * [1.0])],
        "AgentCount": 1000,
        "aNrmInitMean": 0.0,
        "aNrmInitStd": 1.0,
        "PermGroFacAgg": 1.0,
        "T_age": None,
        "T_cycle": 1,
        "aXtraMin": 0.001,
        "aXtraMax": 20,
        "aXtraExtra": np.array([0.005, 0.01]),
        "aXtraNestFac": 3,
        "aXtraCount": 48,
        "UnempPrb": 0.0,
        "UnempPrbRet": 0.0,
        "IncUnemp": 0.0,
        "IncUnempRet": 0.0,
        "tax_rate": 0.0,
        "T_retire": 0,
        "BoroCnstArt": 0.0,
        "CubicBool": False,
        "vFuncBool": False,
        "global_markv": False,
        "cycles": 0,
        "PermGroFac": [np.array(N * [1.0])],
        "MrkvArray": [transition_matrix],
    }
    
    agent = MarkovConsumerType(**agent_params)
    agent.T_sim = T
    agent.track_vars = ["aNrm", "cNrm", "TranShk"]
    agent.MrkvPrbsInit = [1/N] * N
    agent.IncShkDstn = [
        [DiscreteDistributionLabeled(pmv=np.ones(1), atoms=np.array([[1.0], [np.exp(x)]]), var_names=["PermShk", "TranShk"]) for x in incomes]
    ]
    return agent

# --- Equilibrium Solver ---
def solve_equilibrium(agent, alpha, delta, T, T_sum):
    """
    Solves for the equilibrium interest rate for a given agent configuration.
    """
    
    def calculate_implied_R(R_guess):
        wRte = w_func(r_inv_func(R_guess, alpha, delta), alpha)
        agent.Rfree = np.array(np.array(agent.MrkvArray[0].shape[0] * [R_guess]))
        
        agent.make_shock_history()
        agent.solve()
        agent.initialize_sim()
        agent.simulate()
        
        aNrm_agg = average_aggregate_var(agent.history["aNrm"], T, T_sum)
        pNrm_agg = average_aggregate_var(agent.history["TranShk"], T, T_sum)
        
        K = aNrm_agg * wRte
        L = pNrm_agg
        k = K / L
        
        return r_func(k, alpha, delta)

    def equilibrium_func(R_guess):
        implied_r = calculate_implied_R(R_guess)
        print(f"Input R: {R_guess:.6f} || Implied R: {implied_r:.6f} || Difference: {implied_r - R_guess:.6e}")
        return implied_r - R_guess

    R_star = brentq(equilibrium_func, 0.99, 1.05)
    
    calculate_implied_R(R_star)
    
    cNrm_agg = average_aggregate_var(agent.history["cNrm"], T, T_sum)
    aNrm_agg = average_aggregate_var(agent.history["aNrm"], T, T_sum)
    pNrm_agg = average_aggregate_var(agent.history["TranShk"], T, T_sum)
    
    income = (R_star - 1.0 + delta) * aNrm_agg + pNrm_agg
    saving = (1 - cNrm_agg / income) * 100 if income != 0 else 0
    saving_rate = float("%.2f" % saving)
    
    interest_rate = (R_star - 1) * 100
    
    return interest_rate, saving_rate

# --- Main Replication Functions ---
def run_baseline_simulation():
    """
    Runs a single simulation with baseline parameters.
    """
    params = DEFAULT_PARAMS
    μ, ρ, σ = 3, 0.6, 0.2
    
    print(f"--- Running Baseline Simulation ---")
    print(f"Parameters: μ={μ}, ρ={ρ}, σ={σ}")
    
    agent = create_aiyagari_agent(μ, ρ, σ, params['N'], params['T'])
    interest_rate, saving_rate = solve_equilibrium(agent, params['α'], params['δ'], params['T'], params['T_sum'])
    
    print("\n--- Baseline Results ---")
    print(f"Equilibrium Interest Rate: {interest_rate:.4f}%")
    print(f"Aggregate Saving Rate: {saving_rate:.2f}%")
    return {"interest_rate": interest_rate, "saving_rate": saving_rate}

def run_full_replication():
    """
    Runs the full 24-parameter sweep from Aiyagari (1994) Table II.
    """
    params = DEFAULT_PARAMS
    σ_values = [0.2, 0.4]
    ρ_values = [0.0, 0.3, 0.6, 0.9]
    μ_values = [1, 3, 5]
    
    results = []
    print(f"--- Running Full Replication (24 parameter combinations) ---")

    for σ in σ_values:
        for ρ in ρ_values:
            for μ in μ_values:
                print(f"\n--- Solving for: σ={σ}, ρ={ρ}, μ={μ} ---")
                agent = create_aiyagari_agent(μ, ρ, σ, params['N'], params['T'])
                interest_rate, saving_rate = solve_equilibrium(agent, params['α'], params['δ'], params['T'], params['T_sum'])
                results.append({
                    'sigma': σ, 'rho': ρ, 'mu': μ,
                    'interest_rate': interest_rate,
                    'saving_rate': saving_rate
                })
    
    results_df = pd.DataFrame(results)
    print("\n--- Full Replication Results ---")
    print(results_df.to_string())
    return results_df 