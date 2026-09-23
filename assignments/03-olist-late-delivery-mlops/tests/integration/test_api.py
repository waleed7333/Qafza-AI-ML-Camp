import numpy as np
from fastapi.testclient import TestClient

import app.main as main_module
from src.qafza_mlops.model_loader import ModelBundle


class FakeEngine:
    def dispose(self):
        pass


class FakePreprocessor:
    def transform(self, frame):
        return np.ones((len(frame), 2))


class FakeModel:
    def predict_proba(self, matrix):
        return np.column_stack(
            [np.full(len(matrix), 0.2), np.full(len(matrix), 0.8)]
        )


def fake_bundle():
    return ModelBundle(
        model=FakeModel(),
        preprocessor=FakePreprocessor(),
        threshold=0.5,
        feature_names=["a", "b"],
        registered_name="olist_late_delivery",
        alias="champion",
        version="99",
        run_id="test-run",
    )


def test_health_model_info_and_predict(monkeypatch, sample_order):
    monkeypatch.setattr(main_module, "load_model_bundle", lambda settings: fake_bundle())
    monkeypatch.setattr(main_module, "create_db_engine", lambda url: FakeEngine())
    monkeypatch.setattr(main_module, "initialize_serving_schema", lambda engine: None)
    monkeypatch.setattr(main_module, "store_prediction", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "src.qafza_mlops.prediction.validate_inference_frame",
        lambda frame, settings: None,
    )

    with TestClient(main_module.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["model_version"] == "99"

        info = client.get("/model-info")
        assert info.status_code == 200
        assert info.json()["alias"] == "champion"

        response = client.post("/predict", json=sample_order)
        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] == 1
        assert body["label"] == "late"
        assert body["probability"] == 0.8
        assert body["model_version"] == "99"
