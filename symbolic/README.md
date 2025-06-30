# How to Use the Symbolic Aiyagari Model

This directory contains a serialized Python object (`model_expressions.pkl`) that holds the core mathematical equations of the Aiyagari (1994) model, represented as `sympy` symbolic objects.

## 1. Loading the Model

To load the symbolic model into your Python environment, use the `pickle` module. This will give you a dictionary of the expressions.

```python
import pickle

# Define the path to the file
file_path = 'Aiyagari1994QJE/symbolic/model_expressions.pkl'

# Load the dictionary of sympy expressions
with open(file_path, 'rb') as f:
    expressions = pickle.load(f)

# Now you can access the expressions by name
budget_constraint = expressions['budget_constraint']
```

## 2. Contents of the Model File

The loaded `expressions` object is a Python dictionary with the following keys:

| Key                   | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| `utility_function`    | The CRRA utility function `u(c)`.                                |
| `household_objective` | The full household objective function `E_0 * Sum(...)`.          |
| `budget_constraint`   | The household's budget constraint.                               |
| `borrowing_constraint`| The non-negative asset constraint.                               |
| `income_process`      | The AR(1) process for the log of the labor endowment.            |
| `firm_interest_rate`  | The equation for the interest rate `r` from the firm's problem. |
| `firm_wage_rate`      | The equation for the wage `w` from the firm's problem.          |

## 3. Sample Usage

Once loaded, you can use `sympy` functions to analyze and display the equations.

### Example: Pretty-Print the Budget Constraint

```python
from sympy import pprint

# Load the expressions (as shown above)
# ...

# Access the budget constraint
budget = expressions['budget_constraint']

# Pretty-print it in the console
pprint(budget, use_unicode=True)
```

**Expected Output:**

```text
cₜ + aₜ₊₁ = w⋅ℓₜ + (r + 1)⋅aₜ
```

### Example: Generate LaTeX for the Income Process

```python
from sympy import latex

# Load the expressions (as shown above)
# ...

# Access the income process equation
income_eq = expressions['income_process']

# Generate the LaTeX string
latex_code = latex(income_eq)
print(latex_code)
```

**Expected Output:**

```text
\log{\left(\ell_{t} \right)} = \rho \log{\left(\ell_{t - 1} \right)} + \sigma \sqrt{1 - \rho^{2}} \epsilon_{t}
```

## 4. Loading Symbol Descriptions

A second file, `symbol_descriptions.pkl`, contains human-readable descriptions for the core mathematical symbols (`sympy.Symbol` objects) used in the expressions.

```python
import pickle

# Define the path to the descriptions file
descriptions_path = 'Aiyagari1994QJE/symbolic/symbol_descriptions.pkl'

# Load the dictionary of descriptions
with open(descriptions_path, 'rb') as f:
    symbol_descriptions = pickle.load(f)

# You can now use this dictionary to look up descriptions
beta_symbol = expressions['household_objective'].free_symbols.intersection(symbol_descriptions.keys()).pop()
print(f"Description for {beta_symbol}: {symbol_descriptions[beta_symbol]}")
```

### Example: Combining Expressions and Descriptions

You can combine these two files to create a rich, self-documenting representation of the model.

```python
import pickle
from sympy import pprint, latex

# --- Load both files ---
with open('Aiyagari1994QJE/symbolic/model_expressions.pkl', 'rb') as f:
    expressions = pickle.load(f)
with open('Aiyagari1994QJE/symbolic/symbol_descriptions.pkl', 'rb') as f:
    descriptions = pickle.load(f)

# --- Analyze the interest rate equation ---
interest_rate_eq = expressions['firm_interest_rate']
print("Firm's interest rate equation:")
pprint(interest_rate_eq, use_unicode=True)

print("\\nSymbols in this equation and their meanings:")
for symbol in interest_rate_eq.free_symbols:
    if symbol in descriptions:
        print(f"  - {latex(symbol)}: {descriptions[symbol]}")
```

**Expected Output:**

```text
Firm's interest rate equation:
     α - 1
r = α⋅k      - δ

Symbols in this equation and their meanings:
  - r: Interest rate
  - k: Aggregate capital-to-labor ratio
  - α: Capital's share of income in the production function
  - δ: Depreciation rate of capital
```
