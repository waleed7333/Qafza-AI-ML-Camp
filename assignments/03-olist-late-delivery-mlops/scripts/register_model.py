#!/usr/bin/env python3
"""Track candidate runs and register the selected fitted model in MLflow."""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient

ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = ROOT / "artifacts" / "05_features"
MODEL_DIR = ROOT / "artifacts" / "06_model"


def log_candidates(metrics: dict) -> None:
    for candidate in metrics["validation_candidates"]:
        with mlflow.start_run(run_name="candidate-logistic-regression"):
            mlflow.set_tag("run_role", "candidate")
            mlflow.log_params(
                {
                    "model_type": "LogisticRegression",
                    "C": candidate["C"],
                    "class_weight": candidate["class_weight"],
                }
            )
            mlflow.log_metric(
                "validation_average_precision",
                candidate["validation_average_precision"],
            )
            mlflow.log_metric(
                "validation_roc_auc",
                candidate["validation_roc_auc"],
            )


def main() -> int:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    registered_name = os.getenv("MODEL_REGISTERED_NAME", "olist_late_delivery")
    alias = os.getenv("MODEL_ALIAS", "champion")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("qafza-assignment-03-olist-late-delivery")

    metrics = json.loads((MODEL_DIR / "metrics.json").read_text())
    selection = metrics["selection"]
    log_candidates(metrics)

    model = joblib.load(MODEL_DIR / "model.joblib")
    threshold_path = MODEL_DIR / "threshold.json"
    threshold_path.write_text(json.dumps({"threshold": selection["threshold"]}, indent=2))

    with mlflow.start_run(run_name="selected-logistic-regression") as run:
        mlflow.set_tag("run_role", "selected")
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

        mlflow.log_artifact(str(FEATURE_DIR / "preprocessor.joblib"), artifact_path="preprocessor")
        mlflow.log_artifact(str(FEATURE_DIR / "feature_list.json"), artifact_path="contract")
        mlflow.log_artifact(
            str(FEATURE_DIR / "feature_selection_metadata.json"),
            artifact_path="contract",
        )
        mlflow.log_artifact(str(threshold_path), artifact_path="contract")
        mlflow.log_artifact(str(MODEL_DIR / "metrics.json"), artifact_path="evaluation")
        mlflow.log_artifact(str(MODEL_DIR / "results_summary.md"), artifact_path="evaluation")

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=registered_name,
            serialization_format="cloudpickle",
        )

    if model_info.registered_model_version is None:
        raise RuntimeError("MLflow did not return a registered model version")

    client = MlflowClient()
    version = str(model_info.registered_model_version)
    client.set_registered_model_alias(registered_name, alias, version)
    client.set_model_version_tag(registered_name, version, "assignment", "03")
    client.set_model_version_tag(registered_name, version, "validation_status", "passed")
    print(f"Registered {registered_name} version={version} alias={alias} run_id={run.info.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
