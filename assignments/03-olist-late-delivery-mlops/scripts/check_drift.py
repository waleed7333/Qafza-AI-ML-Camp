#!/usr/bin/env python3
"""Check recent prediction-rate drift from stored production logs."""

from __future__ import annotations

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.data_access import PredictionLogRepository
from src.qafza_mlops.database import create_db_engine


def main() -> int:
    settings = load_settings()
    repository = PredictionLogRepository(create_db_engine(settings.database_url))
    count, rate = repository.recent_prediction_stats(hours=24)
    repository.close()

    if count == 0 or rate is None:
        print("No predictions in the last 24 hours; drift cannot be evaluated.")
        return 0

    delta = abs(rate - settings.baseline_predicted_late_rate)
    print(
        f"n={count} recent_late_rate={rate:.4f} "
        f"baseline={settings.baseline_predicted_late_rate:.4f} delta={delta:.4f}"
    )
    return 2 if delta > settings.prediction_rate_alert_abs_delta else 0


if __name__ == "__main__":
    raise SystemExit(main())
