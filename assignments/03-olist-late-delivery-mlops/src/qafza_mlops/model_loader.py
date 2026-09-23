"""Load the registered model and fitted preprocessing artifact from MLflow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient

from src.qafza_mlops.config import Settings


@dataclass
class ModelBundle:
    model: object
    preprocessor: object
    threshold: float
    feature_names: list[str]
    registered_name: str
    alias: str
    version: str
    run_id: str


def load_model_bundle(settings: Settings) -> ModelBundle:
    """Resolve an MLflow alias and load all fitted inference artifacts."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    client = MlflowClient()
    version = client.get_model_version_by_alias(settings.registered_model_name, settings.model_alias)
    if not version.run_id:
        raise RuntimeError("Resolved MLflow model version has no run_id")

    model_uri = f"models:/{settings.registered_model_name}@{settings.model_alias}"
    model = mlflow.sklearn.load_model(model_uri)

    cache = settings.artifact_cache_dir
    cache.mkdir(parents=True, exist_ok=True)

    preprocessor_path = client.download_artifacts(
        version.run_id, "preprocessor/preprocessor.joblib", str(cache)
    )
    threshold_path = client.download_artifacts(
        version.run_id, "contract/threshold.json", str(cache)
    )
    features_path = client.download_artifacts(
        version.run_id, "contract/feature_list.json", str(cache)
    )

    threshold = float(json.loads(Path(threshold_path).read_text())["threshold"])
    feature_names = json.loads(Path(features_path).read_text())

    return ModelBundle(
        model=model,
        preprocessor=joblib.load(preprocessor_path),
        threshold=threshold,
        feature_names=feature_names,
        registered_name=settings.registered_model_name,
        alias=settings.model_alias,
        version=str(version.version),
        run_id=version.run_id,
    )
