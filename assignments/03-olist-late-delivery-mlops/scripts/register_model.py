#!/usr/bin/env python3
"""Track the selected experiment and register the final fitted model in MLflow."""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException


ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = ROOT / "artifacts" / "05_features"
MODEL_DIR = ROOT / "artifacts" / "06_model"


def main() -> int:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    registered_name = os.getenv("MODEL_REGISTERED_NAME", "olist_late_delivery")
    alias = os.getenv("MODEL_ALIAS", "champion")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("qafza-assignment-03-olist-late-delivery")

    metrics = json.loads((MODEL_DIR / "metrics.json").read_text())
    selection = metrics["selection"]

    model = joblib.load(MODEL_DIR / "model.joblib")
    threshold_path = MODEL_DIR / "threshold.json"
    threshold_path.write_text(
        json.dumps({"threshold": selection["threshold"]}, indent=2)
    )

    with mlflow.start_run(run_name="selected-logistic-regression") as run:
        mlflow.log_params(
            {
                "model_type": "LogisticRegression",
                "C": selection["best_C"],
                "class_weight": selection["best_class_weight"],
                "threshold": selection["threshold"],
                "threshold_criterion": selection["threshold_criterion"],
            }
        )
        for name, value in selection["validation"].items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(f"validation_{name}", float(value))
        for name, value in metrics["final_model"]["test"].items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(f"test_{name}", float(value))

        mlflow.log_artifact(
            str(FEATURE_DIR / "preprocessor.joblib"), artifact_path="preprocessor"
        )
        mlflow.log_artifact(
            str(FEATURE_DIR / "feature_list.json"), artifact_path="contract"
        )
        mlflow.log_artifact(
            str(FEATURE_DIR / "feature_selection_metadata.json"),
            artifact_path="contract",
        )
        mlflow.log_artifact(str(threshold_path), artifact_path="contract")
        mlflow.log_artifact(str(MODEL_DIR / "metrics.json"), artifact_path="evaluation")
        mlflow.log_artifact(
            str(MODEL_DIR / "results_summary.md"), artifact_path="evaluation"
        )

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
        )
        model_version = mlflow.register_model(
            model_uri=model_info.model_uri,
            name=registered_name,
        )

    client = MlflowClient()
    client.set_registered_model_alias(
        registered_name, alias, model_version.version
    )
    client.set_model_version_tag(
        registered_name,
        model_version.version,
        "assignment",
        "03",
    )
    print(
        f"Registered {registered_name} version={model_version.version} "
        f"alias={alias} run_id={run.info.run_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
