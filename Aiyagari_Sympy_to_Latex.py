import sympy
import pickle

# --- 1. Define all necessary symbols ---

# Parameters
beta = sympy.Symbol('β', positive=True)
mu = sympy.Symbol('μ', positive=True, real=True)
rho = sympy.Symbol('ρ', real=True)
sigma = sympy.Symbol('σ', positive=True)
delta = sympy.Symbol('δ', positive=True)
alpha = sympy.Symbol('α', positive=True)
k = sympy.Symbol('k')

# Time index
t = sympy.Symbol('t', integer=True, nonnegative=True)

# Economic variables (as indexed bases)
c = sympy.IndexedBase('c')
a = sympy.IndexedBase('a')
ell = sympy.IndexedBase('ℓ')

# Economic variables (as simple symbols)
w = sympy.Symbol('w')
r = sympy.Symbol('r')

# Innovation shock
epsilon_t = sympy.Symbol('ϵ_t')


# --- 2. Create metadata dictionary for symbol descriptions ---

symbol_descriptions = {
    beta: "Time preference factor (how much agents value the future)",
    mu: "Coefficient of relative risk aversion (how much agents dislike risk)",
    rho: "Persistence of the income shock",
    sigma: "Volatility of the income shock",
    delta: "Depreciation rate of capital",
    alpha: "Capital's share of income in the production function",
    k: "Aggregate capital-to-labor ratio"
}


# --- 3. Construct the mathematical expressions ---

# Household's Problem
utility = (c[t]**(1 - mu) - 1) / (1 - mu)
objective_sum = sympy.Sum(beta**t * utility, (t, 0, sympy.oo))
objective_func = sympy.Symbol('E_0') * objective_sum
budget_constraint = sympy.Eq(c[t] + a[t+1], w * ell[t] + (1 + r) * a[t])
borrowing_constraint = sympy.Ge(a[t], 0)

# Income Process
income_process_eq = sympy.Eq(
    sympy.log(ell[t]),
    rho * sympy.log(ell[t-1]) + sigma * sympy.sqrt(1 - rho**2) * epsilon_t
)
epsilon_dist = sympy.Symbol('\\epsilon_t \\sim N(0,1)')

# Utility Function Definition
utility_func_eq = sympy.Eq(sympy.Function('u')(sympy.Symbol('c')), (sympy.Symbol('c')**(1 - mu) - 1) / (1 - mu))

# General Equilibrium / Firm Equations
interest_rate_eq = sympy.Eq(r, alpha * k**(alpha - 1) - delta)
wage_rate_eq = sympy.Eq(w, (1 - alpha) * k**alpha)


# --- 4. Create a dictionary of all expressions ---

expressions_dict = {
    'utility_function': utility_func_eq,
    'household_objective': objective_func,
    'budget_constraint': budget_constraint,
    'borrowing_constraint': borrowing_constraint,
    'income_process': income_process_eq,
    'firm_interest_rate': interest_rate_eq,
    'firm_wage_rate': wage_rate_eq,
}


# --- 5. Serialize the objects to files ---

# Serialize the expressions dictionary
expressions_path = "Aiyagari1994QJE/symbolic/model_expressions.pkl"
with open(expressions_path, "wb") as f:
    pickle.dump(expressions_dict, f)
print(f"Successfully serialized symbolic model to {expressions_path}")

# Serialize the descriptions dictionary
descriptions_path = "Aiyagari1994QJE/symbolic/symbol_descriptions.pkl"
with open(descriptions_path, "wb") as f:
    pickle.dump(symbol_descriptions, f)
print(f"Successfully serialized symbol descriptions to {descriptions_path}")


# --- 6. Convert expressions to LaTeX strings for HTML output ---

# Manually adjust for better rendering
objective_latex = sympy.latex(objective_func).replace('E_0', 'E_{0}')
budget_latex = sympy.latex(budget_constraint)
borrowing_latex = sympy.latex(borrowing_constraint)
income_latex = sympy.latex(income_process_eq)
epsilon_latex = sympy.latex(epsilon_dist)
utility_latex = sympy.latex(utility_func_eq)


# --- 7. Generate an HTML file to display the results ---

html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>Aiyagari Model Equations (Sympy Output)</title>
<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
<style>
  body {{ font-family: sans-serif; margin: 2em; }}
  .equation {{ margin: 2em; }}
</style>
</head>
<body>

<h1>Symbolic Representation of the Aiyagari (1994) Model</h1>
<p>This document is generated from a Python script using Sympy to create and render the model's core mathematical equations.</p>

<h2>The Household's Maximization Problem</h2>
<p>The agent seeks to solve:</p>
<div class="equation">
\\[ \\max \\; {objective_latex} \\]
</div>
<p>Subject to:</p>
<div class="equation">
\\[ {budget_latex} \\]
</div>
<div class="equation">
\\[ {borrowing_latex} \\]
</div>

<h2>The Income Process</h2>
<p>The logarithm of the labor endowment shock follows an AR(1) process:</p>
<div class="equation">
\\[ {income_latex}, \\quad {epsilon_latex} \\]
</div>

<h2>Utility Function</h2>
<p>The period utility function is assumed to be CRRA:</p>
<div class="equation">
\\[ {utility_latex} \\]
</div>

</body>
</html>
"""

html_path = "Aiyagari1994QJE/Aiyagari_Equations.html"
with open(html_path, "w") as f:
    f.write(html_template)

print(f"Successfully generated {html_path}")
print("Please open this file in a web browser to view the rendered equations.") 