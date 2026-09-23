#!/usr/bin/env python3
"""Idempotently build data/artifacts and register the model for local production."""

from __future__ import annotations

import os
import subprocess
import sys

import mlflow
from mlflow import MlflowClient


def registered_model_exists() -> bool:
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    client = MlflowClient()
    try:
        client.get_model_version_by_alias(
            os.getenv("MODEL_REGISTERED_NAME", "olist_late_delivery"),
            os.getenv("MODEL_ALIAS", "champion"),
        )
    except Exception:
        return False
    return True


def run(script: str) -> None:
    subprocess.run([sys.executable, script], check=True)


def main() -> int:
    if registered_model_exists() and os.getenv("FORCE_BOOTSTRAP", "0") != "1":
        print("Registered champion model already exists; bootstrap is complete.")
        return 0

    run("scripts/ingest_raw.py")
    run("scripts/run_notebooks.py")
    run("scripts/register_model.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
