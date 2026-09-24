from types import SimpleNamespace

from scripts import bootstrap


class FakeClient:
    models = []

    def search_registered_models(self, *, filter_string, max_results):
        assert filter_string == "name='olist_late_delivery'"
        assert max_results == 1
        return self.models


def test_registered_model_exists_returns_false_without_model(monkeypatch):
    FakeClient.models = []
    monkeypatch.setattr(bootstrap, "MlflowClient", FakeClient)
    monkeypatch.setattr(bootstrap.mlflow, "set_tracking_uri", lambda uri: None)

    assert bootstrap.registered_model_exists() is False


def test_registered_model_exists_requires_champion_alias(monkeypatch):
    FakeClient.models = [SimpleNamespace(aliases={"staging": "1"})]
    monkeypatch.setattr(bootstrap, "MlflowClient", FakeClient)
    monkeypatch.setattr(bootstrap.mlflow, "set_tracking_uri", lambda uri: None)

    assert bootstrap.registered_model_exists() is False

    FakeClient.models = [SimpleNamespace(aliases={"champion": "2"})]
    assert bootstrap.registered_model_exists() is True
