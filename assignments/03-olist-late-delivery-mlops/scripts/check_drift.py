#!/usr/bin/env python3
"""Check recent prediction-rate drift from stored production logs."""

from __future__ import annotations

from typing import Protocol

from src.qafza_mlops.config import Settings, load_settings
from src.qafza_mlops.data_access import PredictionLogRepository
from src.qafza_mlops.database import create_db_engine


class DriftSettings(Protocol):
    baseline_predicted_late_rate: float
    prediction_drift_min_samples: int
    prediction_rate_alert_abs_delta: float


def evaluate_drift(count: int, rate: float | None, settings: DriftSettings) -> int:
    """Return an operational exit code for the observed prediction distribution."""
    if count == 0 or rate is None:
        print("No predictions in the last 24 hours; drift cannot be evaluated.")
        return 0

    if count < settings.prediction_drift_min_samples:
        print(
            f"Insufficient samples for drift evaluation: n={count}, "
            f"minimum={settings.prediction_drift_min_samples}."
        )
        return 0

    delta = abs(rate - settings.baseline_predicted_late_rate)
    print(
        f"n={count} recent_late_rate={rate:.4f} "
        f"baseline={settings.baseline_predicted_late_rate:.4f} delta={delta:.4f}"
    )
    return 2 if delta > settings.prediction_rate_alert_abs_delta else 0


def main() -> int:
    settings: Settings = load_settings()
    repository = PredictionLogRepository(create_db_engine(settings.database_url))
    try:
        count, rate = repository.recent_prediction_stats(hours=24)
    finally:
        repository.close()

    return evaluate_drift(count, rate, settings)


if __name__ == "__main__":
    raise SystemExit(main())
