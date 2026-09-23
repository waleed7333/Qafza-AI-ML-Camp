"""Application configuration loaded from TOML plus environment variables."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    max_batch_size: int
    log_level: str
    registered_model_name: str
    model_alias: str
    allowed_states: tuple[str, ...]
    allowed_payment_types: tuple[str, ...]
    baseline_predicted_late_rate: float
    prediction_rate_alert_abs_delta: float
    latency_alert_ms: float
    error_rate_alert: float
    log_file: Path
    artifact_cache_dir: Path
    database_url: str
    mlflow_tracking_uri: str


def load_settings() -> Settings:
    config_path = Path(os.getenv("QAFZA_CONFIG", PROJECT_ROOT / "config" / "settings.toml"))
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    return Settings(
        app_name=raw["app"]["name"],
        app_version=raw["app"]["version"],
        max_batch_size=int(raw["app"]["max_batch_size"]),
        log_level=os.getenv("LOG_LEVEL", raw["app"]["log_level"]),
        registered_model_name=os.getenv("MODEL_REGISTERED_NAME", raw["model"]["registered_name"]),
        model_alias=os.getenv("MODEL_ALIAS", raw["model"]["alias"]),
        allowed_states=tuple(raw["validation"]["allowed_states"]),
        allowed_payment_types=tuple(raw["validation"]["allowed_payment_types"]),
        baseline_predicted_late_rate=float(raw["monitoring"]["baseline_predicted_late_rate"]),
        prediction_rate_alert_abs_delta=float(raw["monitoring"]["prediction_rate_alert_abs_delta"]),
        latency_alert_ms=float(raw["monitoring"]["latency_alert_ms"]),
        error_rate_alert=float(raw["monitoring"]["error_rate_alert"]),
        log_file=PROJECT_ROOT / raw["paths"]["log_file"],
        artifact_cache_dir=Path(raw["paths"]["artifact_cache_dir"]),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://qafza:qafza_dev_password@localhost:5433/qafza_mlops",
        ),
        mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
    )
