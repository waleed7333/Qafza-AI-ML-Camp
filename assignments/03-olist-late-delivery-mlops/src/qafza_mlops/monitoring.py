"""Prometheus metrics for the inference service."""

from prometheus_client import Counter, Gauge, Histogram

REQUESTS = Counter(
    "qafza_prediction_requests_total",
    "Prediction requests received",
    ["route", "status"],
)
LATENCY = Histogram(
    "qafza_prediction_latency_seconds",
    "End-to-end prediction request latency",
    ["route"],
)
PREDICTIONS = Counter(
    "qafza_predictions_total",
    "Predictions emitted by class",
    ["label", "model_version"],
)
MODEL_INFO = Gauge(
    "qafza_model_loaded",
    "Whether a registered model is currently loaded",
    ["model_name", "model_version"],
)
