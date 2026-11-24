# What the first version of AiyagariDolARK.ipynb got wrong: the output of first_version.py

Written by `.venv-dolark/bin/python dolark-environment/first_version.py`, the script beside this file, on 2026-11-24, on Linux (x86-64), before the script was first committed; the interest rates are in percent. "fails": dolark's `find_steady_state` returned no equilibrium.

| first version's model, solved by find_steady_state | σ = 0.2, ρ = 0.0, μ = 1 | σ = 0.2, ρ = 0.6, μ = 3 | σ = 0.4, ρ = 0.9, μ = 5 |
|---|---|---|---|
| first version, as it reported | 3.9451% | 3.5017% | 1.5019% |
| first version, the rate its households faced | 3.9456% | 3.5022% | 1.5082% |
| with the Euler equation corrected | 3.9456% | fails | 0.5057% |
| with Aiyagari's chain | 3.9447% | 3.4758% | 0.9569% |
| with both | 3.9447% | 3.4061% | -0.4352% |
