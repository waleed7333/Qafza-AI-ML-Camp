#!/usr/bin/env python3
"""Predict one order from a JSON file using the same inference path as the API."""

from __future__ import annotations

import argparse
import json

import pandas as pd

from app.schemas import OrderRequest
from src.qafza_mlops.config import load_settings
from src.qafza_mlops.model_loader import load_model_bundle
from src.qafza_mlops.prediction import Predictor


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    args = parser.parse_args()

    payload = json.load(open(args.json_file, encoding="utf-8"))
    order = OrderRequest.model_validate(payload)
    settings = load_settings()
    predictor = Predictor(load_model_bundle(settings), settings)
    result = predictor.predict_frame(pd.DataFrame([order.model_dump(mode="json")]))[0]
    print(json.dumps(result.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
