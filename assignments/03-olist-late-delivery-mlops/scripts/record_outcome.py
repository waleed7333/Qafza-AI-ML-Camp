#!/usr/bin/env python3
"""Attach a realized delivery outcome to a previously stored prediction."""

from __future__ import annotations

import argparse

from sqlalchemy import text

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.database import create_db_engine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    parser.add_argument("actual_late", type=int, choices=[0, 1])
    args = parser.parse_args()

    engine = create_db_engine(load_settings().database_url)
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """
                UPDATE serving.prediction_logs
                SET actual_late = :actual_late, actual_recorded_at = now()
                WHERE request_id = :request_id
                """
            ),
            {
                "request_id": args.request_id,
                "actual_late": args.actual_late,
            },
        )
    if result.rowcount != 1:
        raise SystemExit(f"request_id not found or not unique: {args.request_id}")
    print("Outcome recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
