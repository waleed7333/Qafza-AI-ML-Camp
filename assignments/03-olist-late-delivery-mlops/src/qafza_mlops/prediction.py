"""Inference orchestration shared by CLI and API."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.qafza_mlops.config import Settings
from src.qafza_mlops.features import make_features
from src.qafza_mlops.model_loader import ModelBundle
from src.qafza_mlops.validation import validate_inference_frame


@dataclass(frozen=True)
class PredictionResult:
    prediction: int
    label: str
    probability: float
    model_version: str


class Predictor:
    def __init__(self, bundle: ModelBundle, settings: Settings):
        self.bundle = bundle
        self.settings = settings

    def predict_frame(self, frame: pd.DataFrame) -> list[PredictionResult]:
        validate_inference_frame(frame, self.settings)
        raw_features = make_features(frame)
        matrix = self.bundle.preprocessor.transform(raw_features)

        if matrix.shape[1] != len(self.bundle.feature_names):
            raise RuntimeError("Transformed feature width does not match saved feature contract")
        if not np.isfinite(matrix).all():
            raise RuntimeError("Non-finite values remain after fitted preprocessing")

        probabilities = self.bundle.model.predict_proba(matrix)[:, 1]
        predictions = (probabilities >= self.bundle.threshold).astype(int)

        return [
            PredictionResult(
                prediction=int(prediction),
                label="late" if int(prediction) == 1 else "on_time",
                probability=float(probability),
                model_version=self.bundle.version,
            )
            for prediction, probability in zip(predictions, probabilities, strict=True)
        ]
