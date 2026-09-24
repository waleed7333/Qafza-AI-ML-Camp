#!/usr/bin/env python3
"""Execute the six training notebooks in order without modifying source notebooks."""

from __future__ import annotations

import tempfile
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb"))


def execute_notebook(notebook: Path, output_dir: Path) -> None:
    """Execute one notebook from the project root and save only a temporary copy."""
    document = nbformat.read(notebook, as_version=4)
    executor = ExecutePreprocessor(timeout=900)
    executor.preprocess(
        document,
        resources={"metadata": {"path": str(ROOT)}},
    )
    nbformat.write(document, output_dir / notebook.name)


def main() -> int:
    if len(NOTEBOOKS) != 6:
        raise SystemExit(f"Expected 6 notebooks, found {len(NOTEBOOKS)}")

    with tempfile.TemporaryDirectory(prefix="qafza-notebooks-") as temporary_dir:
        output_dir = Path(temporary_dir)
        for notebook in NOTEBOOKS:
            print(f"Executing {notebook.name}", flush=True)
            execute_notebook(notebook, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
