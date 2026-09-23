#!/usr/bin/env python3
"""Idempotently build data/artifacts and register the model for local production."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import mlflow
from mlflow import MlflowClient

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT / "data" / "raw"
RAW_DATA_POINTER = ROOT / "data" / "raw.dvc"
EXPECTED_RAW_FILES = {
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
}


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


def raw_data_present() -> bool:
    return all((RAW_DATA_DIR / name).is_file() for name in EXPECTED_RAW_FILES)


def ensure_raw_data() -> None:
    if raw_data_present():
        return

    if RAW_DATA_POINTER.is_file():
        print("Raw data is missing; attempting DVC pull.", flush=True)
        subprocess.run(
            ["dvc", "pull", str(RAW_DATA_POINTER)],
            cwd=ROOT,
            check=True,
        )

    if not raw_data_present():
        raise SystemExit(
            "Raw Olist data is unavailable. Populate data/raw or configure the "
            "DVC remote so data/raw.dvc can be pulled."
        )


def run(script: str) -> None:
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def main() -> int:
    if registered_model_exists() and os.getenv("FORCE_BOOTSTRAP", "0") != "1":
        print("Registered champion model already exists; bootstrap is complete.")
        return 0

    ensure_raw_data()
    run("scripts/ingest_raw.py")
    run("scripts/run_notebooks.py")
    run("scripts/register_model.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
