"""Database helpers for production prediction logs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


DDL = """
CREATE SCHEMA IF NOT EXISTS serving;

CREATE TABLE IF NOT EXISTS serving.prediction_logs (
    id bigserial PRIMARY KEY,
    request_id text NOT NULL,
    created_at timestamptz NOT NULL,
    input_payload jsonb NOT NULL,
    prediction integer NOT NULL CHECK (prediction IN (0, 1)),
    probability double precision NOT NULL CHECK (probability >= 0 AND probability <= 1),
    model_version text NOT NULL,
    latency_ms double precision NOT NULL CHECK (latency_ms >= 0),
    actual_late integer CHECK (actual_late IN (0, 1)),
    actual_recorded_at timestamptz
);

CREATE INDEX IF NOT EXISTS prediction_logs_created_at_idx
    ON serving.prediction_logs (created_at);
"""


def create_db_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def initialize_serving_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        for statement in [part.strip() for part in DDL.split(";") if part.strip()]:
            connection.execute(text(statement))


def store_prediction(
    engine: Engine,
    *,
    request_id: str,
    payload: dict[str, Any],
    prediction: int,
    probability: float,
    model_version: str,
    latency_ms: float,
) -> None:
    statement = text(
        """
        INSERT INTO serving.prediction_logs (
            request_id, created_at, input_payload, prediction,
            probability, model_version, latency_ms
        )
        VALUES (
            :request_id, :created_at, CAST(:input_payload AS jsonb), :prediction,
            :probability, :model_version, :latency_ms
        )
        """
    )
    with engine.begin() as connection:
        connection.execute(
            statement,
            {
                "request_id": request_id,
                "created_at": datetime.now(timezone.utc),
                "input_payload": json.dumps(payload, default=str),
                "prediction": prediction,
                "probability": probability,
                "model_version": model_version,
                "latency_ms": latency_ms,
            },
        )
