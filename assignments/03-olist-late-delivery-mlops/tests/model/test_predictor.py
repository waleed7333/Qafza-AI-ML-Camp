import numpy as np
import pandas as pd

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.model_loader import ModelBundle
from src.qafza_mlops.prediction import Predictor


class FakePreprocessor:
    def transform(self, frame):
        return np.ones((len(frame), 2))


class FakeModel:
    def predict_proba(self, matrix):
        return np.column_stack(
            [np.full(len(matrix), 0.2), np.full(len(matrix), 0.8)]
        )


def test_predictor_returns_probability_threshold_and_version(monkeypatch, sample_order):
    monkeypatch.setattr(
        "src.qafza_mlops.prediction.validate_inference_frame",
        lambda frame, settings: None,
    )
    bundle = ModelBundle(
        model=FakeModel(),
        preprocessor=FakePreprocessor(),
        threshold=0.5,
        feature_names=["a", "b"],
        registered_name="test",
        alias="champion",
        version="7",
        run_id="run",
    )
    result = Predictor(bundle, load_settings()).predict_frame(
        pd.DataFrame([sample_order])
    )[0]

    assert result.prediction == 1
    assert result.label == "late"
    assert result.probability == 0.8
    assert result.model_version == "7"
