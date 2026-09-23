#!/usr/bin/env python3
"""Prove production inference matches the saved notebook pipeline on one test row."""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.features import SOURCE_COLUMNS, make_features
from src.qafza_mlops.model_loader import load_model_bundle


def main() -> int:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    test = pd.read_parquet(root / "artifacts/03_splits/test.parquet").iloc[[0]]
    source = test[SOURCE_COLUMNS].copy()

    local_preprocessor = joblib.load(
        root / "artifacts/05_features/preprocessor.joblib"
    )
    local_model = joblib.load(root / "artifacts/06_model/model.joblib")
    local_matrix = local_preprocessor.transform(make_features(source))
    expected = float(local_model.predict_proba(local_matrix)[:, 1][0])

    bundle = load_model_bundle(load_settings())
    served_matrix = bundle.preprocessor.transform(make_features(source))
    actual = float(bundle.model.predict_proba(served_matrix)[:, 1][0])

    if not np.isclose(expected, actual, rtol=0, atol=1e-12):
        raise SystemExit(
            f"Parity FAILED: notebook={expected:.15f} serving={actual:.15f}"
        )
    print(f"Parity OK: probability={actual:.15f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
