"""Pydantic request and response contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_count: int = Field(ge=1)
    unique_product_count: int = Field(ge=1)
    unique_seller_count: int = Field(ge=1)
    total_price: float = Field(ge=0)
    total_freight: float = Field(ge=0)
    mean_product_weight_g: float | None = Field(default=None, ge=0)
    mean_product_volume_cm3: float | None = Field(default=None, ge=0)
    mean_product_photos_qty: float | None = Field(default=None, ge=0)
    payment_count: int = Field(ge=1)
    payment_value: float = Field(ge=0)
    max_payment_installments: int = Field(ge=0)
    same_state_share: float | None = Field(default=None, ge=0, le=1)
    mean_customer_seller_distance_km: float | None = Field(default=None, ge=0)
    max_customer_seller_distance_km: float | None = Field(default=None, ge=0)
    customer_state: str
    dominant_product_category: str | None = None
    dominant_seller_state: str
    dominant_payment_type: str
    order_purchase_timestamp: datetime
    order_estimated_delivery_date: datetime


class PredictionResponse(BaseModel):
    prediction: int
    label: str
    probability: float
    model_version: str
    request_id: str


class BatchPredictionRequest(BaseModel):
    orders: list[OrderRequest]


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    name: str
    alias: str
    version: str
    run_id: str
    threshold: float
    transformed_feature_count: int
