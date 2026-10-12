# Compare a regenerated baseline/ with the committed one.
#
#   python .github/check_baseline.py <committed baseline dir> <regenerated baseline dir>
#
# Fails if a number in numbers.json differs by more than 1e-4 relative, or if any pixel of a
# PNG differs. Then lists the files whose bytes differ, without failing: the pixels are
# platform-independent, but the PNG compression (and so the file bytes) can vary with the
# zlib that wrote the file. Run it with the HARK environment's Python, which has Pillow.
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

committed, regenerated = map(Path, sys.argv[1:3])
problems = []


def compare(a, b, path):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            compare(a.get(key), b.get(key), f"{path}.{key}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, f"{path}[{i}]")
    elif isinstance(a, float) and isinstance(b, float):
        if not math.isclose(a, b, rel_tol=1e-4):
            problems.append(f"numbers.json{path}: committed {a}, regenerated {b}")
    elif a != b:
        problems.append(f"numbers.json{path}: committed {a!r}, regenerated {b!r}")


compare(json.loads((committed / "numbers.json").read_text()), json.loads((regenerated / "numbers.json").read_text()), "")

names = sorted({p.name for p in committed.iterdir()} | {p.name for p in regenerated.iterdir()})
for name in names:
    if not (committed / name).exists() or not (regenerated / name).exists():
        problems.append(f"{name}: present on only one side")
    elif name.endswith(".png"):
        a, b = (np.asarray(Image.open(d / name)) for d in (committed, regenerated))
        if a.shape != b.shape or not np.array_equal(a, b):
            problems.append(f"{name}: pixels differ")

print("\n".join(problems) or "numbers and pixels match the committed baseline")
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
different = [n for n in names if (committed / n).exists() and (regenerated / n).exists()
             and digest(committed / n) != digest(regenerated / n)]
print("files whose bytes differ:", ", ".join(different) or "none")
sys.exit(1 if problems else 0)
