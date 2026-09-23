import numpy as np
import pandas as pd
import pytest

from src.qafza_mlops.preprocessing import transform_with_fitted_preprocessor


class FakePreprocessor:
    def __init__(self, matrix):
        self.matrix = matrix

    def transform(self, features):
        return self.matrix


def test_transform_accepts_expected_finite_width():
    features = pd.DataFrame({"x": [1]})
    result = transform_with_fitted_preprocessor(
        FakePreprocessor(np.array([[1.0, 2.0]])),
        features,
        ["a", "b"],
    )
    assert result.shape == (1, 2)


def test_transform_rejects_wrong_width():
    features = pd.DataFrame({"x": [1]})
    with pytest.raises(RuntimeError, match="feature width"):
        transform_with_fitted_preprocessor(
            FakePreprocessor(np.array([[1.0]])),
            features,
            ["a", "b"],
        )


def test_transform_rejects_non_finite_values():
    features = pd.DataFrame({"x": [1]})
    with pytest.raises(RuntimeError, match="Non-finite"):
        transform_with_fitted_preprocessor(
            FakePreprocessor(np.array([[np.nan, 1.0]])),
            features,
            ["a", "b"],
        )
