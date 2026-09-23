#!/usr/bin/env python3
"""Check recent prediction-rate drift from stored production logs."""

from __future__ import annotations

from sqlalchemy import text

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.database import create_db_engine


def main() -> int:
    settings = load_settings()
    engine = create_db_engine(settings.database_url)
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT count(*) AS n, avg(prediction::double precision) AS late_rate
                FROM serving.prediction_logs
                WHERE created_at >= now() - interval '24 hours'
                """
            )
        ).mappings().one()
    n = int(row["n"])
    if n == 0:
        print("No predictions in the last 24 hours; drift cannot be evaluated.")
        return 0
    rate = float(row["late_rate"])
    delta = abs(rate - settings.baseline_predicted_late_rate)
    print(
        f"n={n} recent_late_rate={rate:.4f} "
        f"baseline={settings.baseline_predicted_late_rate:.4f} delta={delta:.4f}"
    )
    return 2 if delta > settings.prediction_rate_alert_abs_delta else 0


if __name__ == "__main__":
    raise SystemExit(main())
