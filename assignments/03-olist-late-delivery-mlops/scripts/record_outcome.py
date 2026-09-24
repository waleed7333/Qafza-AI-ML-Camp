#!/usr/bin/env python3
"""Attach a realized delivery outcome to a previously stored prediction."""

from __future__ import annotations

import argparse

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.data_access import PredictionLogRepository
from src.qafza_mlops.database import create_db_engine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    parser.add_argument("actual_late", type=int, choices=[0, 1])
    args = parser.parse_args()

    settings = load_settings()
    repository = PredictionLogRepository(create_db_engine(settings.database_url))
    updated = repository.record_outcome(args.request_id, args.actual_late)
    repository.close()

    if not updated:
        raise SystemExit(f"request_id not found: {args.request_id}")
    print("Outcome recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
