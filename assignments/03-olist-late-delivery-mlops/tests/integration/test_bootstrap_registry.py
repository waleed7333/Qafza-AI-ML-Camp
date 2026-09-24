from types import SimpleNamespace

from scripts import bootstrap


class FakeClient:
    models = []
    aliases = {}

    def search_registered_models(self, *, filter_string, max_results):
        assert filter_string == "name='olist_late_delivery'"
        assert max_results == 1
        return self.models

    def get_registered_model(self, name):
        assert name == "olist_late_delivery"
        return SimpleNamespace(aliases=self.aliases)


def test_registered_model_exists_returns_false_without_model(monkeypatch):
    FakeClient.models = []
    FakeClient.aliases = {}
    monkeypatch.setattr(bootstrap, "MlflowClient", FakeClient)
    monkeypatch.setattr(bootstrap.mlflow, "set_tracking_uri", lambda uri: None)

    assert bootstrap.registered_model_exists() is False


def test_registered_model_exists_requires_champion_alias(monkeypatch):
    FakeClient.models = [SimpleNamespace(name="olist_late_delivery")]
    FakeClient.aliases = {"staging": "1"}
    monkeypatch.setattr(bootstrap, "MlflowClient", FakeClient)
    monkeypatch.setattr(bootstrap.mlflow, "set_tracking_uri", lambda uri: None)

    assert bootstrap.registered_model_exists() is False

    FakeClient.aliases = {"champion": "2"}
    assert bootstrap.registered_model_exists() is True


def test_run_dvc_enables_local_no_scm_before_command(monkeypatch):
    calls = []

    def fake_run(command, *, cwd, check):
        calls.append((command, cwd, check))

    monkeypatch.setattr(bootstrap.subprocess, "run", fake_run)

    bootstrap.run_dvc("pull", "data/raw.dvc")

    assert calls[0][0] == ["dvc", "config", "core.no_scm", "true", "--local"]
    assert calls[1][0] == ["dvc", "pull", "data/raw.dvc"]
    assert all(call[1] == bootstrap.ROOT for call in calls)
    assert all(call[2] is True for call in calls)
