"""Pydantic request and response contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


ORDER_EXAMPLE = {
    "item_count": 1,
    "unique_product_count": 1,
    "unique_seller_count": 1,
    "total_price": 100.0,
    "total_freight": 20.0,
    "mean_product_weight_g": 500.0,
    "mean_product_volume_cm3": 1000.0,
    "mean_product_photos_qty": 2.0,
    "payment_count": 1,
    "payment_value": 120.0,
    "max_payment_installments": 1,
    "same_state_share": 1.0,
    "mean_customer_seller_distance_km": 10.0,
    "max_customer_seller_distance_km": 10.0,
    "customer_state": "SP",
    "dominant_product_category": "health_beauty",
    "dominant_seller_state": "SP",
    "dominant_payment_type": "credit_card",
    "order_purchase_timestamp": "2018-01-02T10:00:00",
    "order_estimated_delivery_date": "2018-01-12T10:00:00",
}


class OrderRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": ORDER_EXAMPLE},
    )

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

    @model_validator(mode="after")
    def validate_estimated_delivery_window(self):
        if self.order_estimated_delivery_date < self.order_purchase_timestamp:
            raise ValueError(
                "order_estimated_delivery_date must not precede order_purchase_timestamp"
            )
        return self


class PredictionResponse(BaseModel):
    prediction: int
    label: str
    probability: float
    model_version: str
    request_id: str


class BatchPredictionRequest(BaseModel):
    orders: list[OrderRequest] = Field(min_length=1)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    name: str
    alias: str
    version: str
    run_id: str
    threshold: float
    transformed_feature_count: int
