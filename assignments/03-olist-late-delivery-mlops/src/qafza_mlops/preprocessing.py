"""Apply the fitted preprocessing contract without refitting anything."""

from __future__ import annotations

import numpy as np
import pandas as pd


def transform_with_fitted_preprocessor(
    preprocessor: object,
    features: pd.DataFrame,
    expected_feature_names: list[str],
) -> np.ndarray:
    """Transform features and enforce the saved transformed-feature contract."""
    matrix = preprocessor.transform(features)
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()

    array = np.asarray(matrix)
    if array.ndim != 2:
        raise RuntimeError("Fitted preprocessor returned a non-2D matrix")
    if array.shape[1] != len(expected_feature_names):
        raise RuntimeError("Transformed feature width does not match saved feature contract")
    if not np.isfinite(array).all():
        raise RuntimeError("Non-finite values remain after fitted preprocessing")
    return array
