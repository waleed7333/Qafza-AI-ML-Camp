#!/usr/bin/env python3
"""Execute the six training notebooks in their required order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb"))


def main() -> int:
    if len(NOTEBOOKS) != 6:
        raise SystemExit(f"Expected 6 notebooks, found {len(NOTEBOOKS)}")
    for notebook in NOTEBOOKS:
        print(f"Executing {notebook.name}", flush=True)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=900",
                str(notebook),
            ],
            cwd=ROOT,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
