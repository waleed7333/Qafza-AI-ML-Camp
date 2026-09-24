from types import SimpleNamespace

from scripts.check_drift import evaluate_drift


def settings():
    return SimpleNamespace(
        baseline_predicted_late_rate=0.10,
        prediction_drift_min_samples=100,
        prediction_rate_alert_abs_delta=0.05,
    )


def test_drift_skips_when_no_predictions(capsys):
    assert evaluate_drift(0, None, settings()) == 0
    assert "cannot be evaluated" in capsys.readouterr().out


def test_drift_skips_small_samples(capsys):
    assert evaluate_drift(4, 0.0, settings()) == 0
    output = capsys.readouterr().out
    assert "Insufficient samples" in output
    assert "minimum=100" in output


def test_drift_alerts_only_after_minimum_sample_size(capsys):
    assert evaluate_drift(100, 0.0, settings()) == 2
    output = capsys.readouterr().out
    assert "n=100" in output
    assert "delta=0.1000" in output


def test_drift_passes_when_distribution_is_within_threshold(capsys):
    assert evaluate_drift(250, 0.13, settings()) == 0
    assert "delta=0.0300" in capsys.readouterr().out
