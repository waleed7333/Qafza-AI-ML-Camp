from fastapi.testclient import TestClient

import app.main as main_module
from src.qafza_mlops.monitoring import REQUESTS
from tests.integration.test_api import (
    FakeEngine,
    FakePredictionLogRepository,
    fake_bundle,
)


def patch_runtime(monkeypatch):
    monkeypatch.setattr(main_module, "load_model_bundle", lambda settings: fake_bundle())
    monkeypatch.setattr(main_module, "create_db_engine", lambda url: FakeEngine())
    monkeypatch.setattr(
        main_module,
        "PredictionLogRepository",
        FakePredictionLogRepository,
    )


def test_bad_request_is_rejected_by_schema(monkeypatch, sample_order):
    patch_runtime(monkeypatch)
    sample_order["total_price"] = -1

    counter = REQUESTS.labels(route="/predict", status="invalid")
    before = counter._value.get()

    with TestClient(main_module.app) as client:
        response = client.post("/predict", json=sample_order)

    assert response.status_code == 422
    assert counter._value.get() == before + 1


def test_impossible_estimated_delivery_window_is_rejected(monkeypatch, sample_order):
    patch_runtime(monkeypatch)
    sample_order["order_estimated_delivery_date"] = "2017-12-31T10:00:00"

    with TestClient(main_module.app) as client:
        response = client.post("/predict", json=sample_order)

    assert response.status_code == 422
