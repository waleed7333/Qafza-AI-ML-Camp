from fastapi.testclient import TestClient

import app.main as main_module
from tests.integration.test_api import (
    FakeEngine,
    fake_bundle,
)


def test_bad_request_is_rejected_by_schema(monkeypatch, sample_order):
    monkeypatch.setattr(main_module, "load_model_bundle", lambda settings: fake_bundle())
    monkeypatch.setattr(main_module, "create_db_engine", lambda url: FakeEngine())
    monkeypatch.setattr(main_module, "initialize_serving_schema", lambda engine: None)
    sample_order["total_price"] = -1

    with TestClient(main_module.app) as client:
        response = client.post("/predict", json=sample_order)
    assert response.status_code == 422
