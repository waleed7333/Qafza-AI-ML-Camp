"""FastAPI model-serving application."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from prometheus_client import make_asgi_app

from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelInfoResponse,
    OrderRequest,
    PredictionResponse,
)
from src.qafza_mlops.config import load_settings
from src.qafza_mlops.database import (
    create_db_engine,
    initialize_serving_schema,
    store_prediction,
)
from src.qafza_mlops.logging_config import configure_logging
from src.qafza_mlops.model_loader import load_model_bundle
from src.qafza_mlops.monitoring import LATENCY, MODEL_INFO, PREDICTIONS, REQUESTS
from src.qafza_mlops.prediction import Predictor
from src.qafza_mlops.validation import DataValidationError


LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    configure_logging(settings)
    engine = create_db_engine(settings.database_url)
    initialize_serving_schema(engine)
    bundle = load_model_bundle(settings)

    app.state.settings = settings
    app.state.engine = engine
    app.state.bundle = bundle
    app.state.predictor = Predictor(bundle, settings)

    MODEL_INFO.labels(
        model_name=bundle.registered_name, model_version=bundle.version
    ).set(1)
    LOGGER.info(
        "service_started model=%s version=%s alias=%s",
        bundle.registered_name,
        bundle.version,
        bundle.alias,
    )
    yield
    engine.dispose()


settings_for_metadata = load_settings()
app = FastAPI(
    title=settings_for_metadata.app_name,
    version=settings_for_metadata.app_version,
    lifespan=lifespan,
)
app.mount("/metrics", make_asgi_app())


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    bundle = request.app.state.bundle
    return {"status": "ok", "model_version": bundle.version}


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info(request: Request) -> ModelInfoResponse:
    bundle = request.app.state.bundle
    return ModelInfoResponse(
        name=bundle.registered_name,
        alias=bundle.alias,
        version=bundle.version,
        run_id=bundle.run_id,
        threshold=bundle.threshold,
        transformed_feature_count=len(bundle.feature_names),
    )


def _predict_one(request: Request, order: OrderRequest, request_id: str):
    started = time.perf_counter()
    payload = order.model_dump(mode="json")
    frame = pd.DataFrame([payload])
    result = request.app.state.predictor.predict_frame(frame)[0]
    latency_ms = (time.perf_counter() - started) * 1000

    store_prediction(
        request.app.state.engine,
        request_id=request_id,
        payload=payload,
        prediction=result.prediction,
        probability=result.probability,
        model_version=result.model_version,
        latency_ms=latency_ms,
    )
    PREDICTIONS.labels(
        label=result.label, model_version=result.model_version
    ).inc()
    LOGGER.info(
        "prediction request_id=%s input=%s output=%s probability=%.6f "
        "latency_ms=%.2f model_version=%s",
        request_id,
        payload,
        result.label,
        result.probability,
        latency_ms,
        result.model_version,
    )
    return result, latency_ms


@app.post("/predict", response_model=PredictionResponse)
def predict(request: Request, order: OrderRequest) -> PredictionResponse:
    request_id = uuid4().hex
    route = "/predict"
    try:
        with LATENCY.labels(route=route).time():
            result, _ = _predict_one(request, order, request_id)
        REQUESTS.labels(route=route, status="success").inc()
        return PredictionResponse(**result.__dict__, request_id=request_id)
    except DataValidationError as exc:
        REQUESTS.labels(route=route, status="invalid").inc()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        REQUESTS.labels(route=route, status="error").inc()
        LOGGER.exception("prediction_failed request_id=%s", request_id)
        raise


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(
    request: Request, body: BatchPredictionRequest
) -> BatchPredictionResponse:
    route = "/predict-batch"
    limit = request.app.state.settings.max_batch_size
    if not body.orders:
        raise HTTPException(status_code=422, detail="orders must not be empty")
    if len(body.orders) > limit:
        raise HTTPException(
            status_code=413, detail=f"batch size exceeds configured limit {limit}"
        )

    responses: list[PredictionResponse] = []
    try:
        with LATENCY.labels(route=route).time():
            for order in body.orders:
                request_id = uuid4().hex
                result, _ = _predict_one(request, order, request_id)
                responses.append(
                    PredictionResponse(**result.__dict__, request_id=request_id)
                )
        REQUESTS.labels(route=route, status="success").inc()
        return BatchPredictionResponse(predictions=responses)
    except DataValidationError as exc:
        REQUESTS.labels(route=route, status="invalid").inc()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        REQUESTS.labels(route=route, status="error").inc()
        LOGGER.exception("batch_prediction_failed")
        raise
