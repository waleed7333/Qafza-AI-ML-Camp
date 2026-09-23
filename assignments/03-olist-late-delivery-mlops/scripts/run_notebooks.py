#!/usr/bin/env python3
"""Execute the six training notebooks in their required order without modifying sources."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb"))


def main() -> int:
    if len(NOTEBOOKS) != 6:
        raise SystemExit(f"Expected 6 notebooks, found {len(NOTEBOOKS)}")

    with tempfile.TemporaryDirectory(prefix="qafza-notebooks-") as output_dir:
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
                    "--ExecutePreprocessor.timeout=900",
                    "--output-dir",
                    output_dir,
                    str(notebook),
                ],
                cwd=ROOT,
                check=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
