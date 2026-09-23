from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace

import joblib

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.model_loader import load_model_bundle


class FakeClient:
    def __init__(self, preprocessor_path, threshold_path, feature_list_path):
        self.preprocessor_path = preprocessor_path
        self.threshold_path = threshold_path
        self.feature_list_path = feature_list_path
        self.alias_request = None

    def get_model_version_by_alias(self, name, alias):
        self.alias_request = (name, alias)
        return SimpleNamespace(run_id="run-123", version="7")

    def download_artifacts(self, run_id, artifact_path, dst_path):
        assert run_id == "run-123"
        paths = {
            "preprocessor/preprocessor.joblib": self.preprocessor_path,
            "contract/threshold.json": self.threshold_path,
            "contract/feature_list.json": self.feature_list_path,
        }
        return str(paths[artifact_path])


def test_load_model_bundle_resolves_registry_alias_and_artifacts(monkeypatch, tmp_path):
    preprocessor_path = tmp_path / "preprocessor.joblib"
    threshold_path = tmp_path / "threshold.json"
    feature_list_path = tmp_path / "feature_list.json"

    preprocessor = {"kind": "fitted-preprocessor"}
    joblib.dump(preprocessor, preprocessor_path)
    threshold_path.write_text(json.dumps({"threshold": 0.156}), encoding="utf-8")
    feature_list_path.write_text(json.dumps(["feature_a", "feature_b"]), encoding="utf-8")

    fake_client = FakeClient(preprocessor_path, threshold_path, feature_list_path)
    fake_model = object()

    monkeypatch.setattr(
        "src.qafza_mlops.model_loader.MlflowClient",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        "src.qafza_mlops.model_loader.mlflow.set_tracking_uri",
        lambda uri: None,
    )
    monkeypatch.setattr(
        "src.qafza_mlops.model_loader.mlflow.sklearn.load_model",
        lambda uri: fake_model,
    )

    settings = replace(
        load_settings(),
        mlflow_tracking_uri="http://mlflow.test:5000",
        artifact_cache_dir=tmp_path / "cache",
    )
    bundle = load_model_bundle(settings)

    assert fake_client.alias_request == (
        settings.registered_model_name,
        settings.model_alias,
    )
    assert bundle.model is fake_model
    assert bundle.preprocessor == preprocessor
    assert bundle.threshold == 0.156
    assert bundle.feature_names == ["feature_a", "feature_b"]
    assert bundle.version == "7"
    assert bundle.run_id == "run-123"
