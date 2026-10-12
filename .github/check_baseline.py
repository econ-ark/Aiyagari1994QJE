# Compare a regenerated baseline/ with the committed one.
#
#   python .github/check_baseline.py [--numbers-only] <committed baseline dir> <regenerated baseline dir>
#
# Fails if a number in numbers.json differs by more than 1e-4 relative, or (without
# --numbers-only) if any pixel of a PNG differs or a file is missing. Then lists the files
# whose bytes differ, without failing: the pixels are platform-independent, but the PNG
# compression (and so the file bytes) can vary with the zlib that wrote the file.
import hashlib
import json
import math
import sys
from pathlib import Path


def compare_numbers(a, b, path=""):
    """Differences between two numbers.json trees; the figures' descriptions are not compared."""
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted((a.keys() | b.keys()) - {"figures"}):
            yield from compare_numbers(a.get(key), b.get(key), f"{path}.{key}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            yield from compare_numbers(x, y, f"{path}[{i}]")
    elif isinstance(a, float) and isinstance(b, float):
        if not math.isclose(a, b, rel_tol=1e-4):
            yield f"numbers.json{path}: committed {a}, regenerated {b}"
    elif a != b:
        yield f"numbers.json{path}: committed {a!r}, regenerated {b!r}"


def main(args):
    numbers_only = "--numbers-only" in args
    committed, regenerated = (Path(a) for a in args if a != "--numbers-only")
    problems = list(compare_numbers(*(json.loads((d / "numbers.json").read_text()) for d in (committed, regenerated))))
    if numbers_only:
        print("\n".join(problems) or "numbers match the committed baseline")
        return 1 if problems else 0

    import numpy as np
    from PIL import Image

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
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
