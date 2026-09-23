"""Service-facing data access for prediction logs and realized outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.qafza_mlops.database import initialize_serving_schema, store_prediction


@dataclass
class PredictionLogRepository:
    """Encapsulate persistence used by the inference service and monitoring scripts."""

    engine: Engine

    def initialize(self) -> None:
        initialize_serving_schema(self.engine)

    def record(
        self,
        *,
        request_id: str,
        payload: dict[str, Any],
        prediction: int,
        probability: float,
        model_version: str,
        latency_ms: float,
    ) -> None:
        store_prediction(
            self.engine,
            request_id=request_id,
            payload=payload,
            prediction=prediction,
            probability=probability,
            model_version=model_version,
            latency_ms=latency_ms,
        )

    def record_outcome(self, request_id: str, actual_late: int) -> bool:
        statement = text(
            """
            UPDATE serving.prediction_logs
            SET actual_late = :actual_late, actual_recorded_at = now()
            WHERE request_id = :request_id
            """
        )
        with self.engine.begin() as connection:
            result = connection.execute(
                statement,
                {"request_id": request_id, "actual_late": actual_late},
            )
        return result.rowcount == 1

    def recent_prediction_stats(self, hours: int = 24) -> tuple[int, float | None]:
        if hours < 1:
            raise ValueError("hours must be at least 1")

        statement = text(
            """
            SELECT
                count(*) AS n,
                avg(prediction::double precision) AS late_rate
            FROM serving.prediction_logs
            WHERE created_at >= now() - (:hours * interval '1 hour')
            """
        )
        with self.engine.connect() as connection:
            row = connection.execute(statement, {"hours": hours}).mappings().one()

        count = int(row["n"])
        late_rate = None if row["late_rate"] is None else float(row["late_rate"])
        return count, late_rate

    def close(self) -> None:
        self.engine.dispose()
