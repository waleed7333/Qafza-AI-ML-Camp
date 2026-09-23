"""Incoming inference-data validation with Great Expectations."""

from __future__ import annotations

from uuid import uuid4

import great_expectations as gx
import pandas as pd

from src.qafza_mlops.config import Settings


class DataValidationError(ValueError):
    """Raised when semantic data validation fails."""


def validate_inference_frame(frame: pd.DataFrame, settings: Settings) -> None:
    """Validate ranges and allowed categories before model inference."""
    context = gx.get_context(mode="ephemeral")
    source = context.data_sources.add_pandas(name=f"inference_source_{uuid4().hex}")
    asset = source.add_dataframe_asset(name="orders")
    batch_definition = asset.add_batch_definition_whole_dataframe("request")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": frame})

    expectations = [
        gx.expectations.ExpectColumnValuesToBeBetween(column="item_count", min_value=1),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="unique_product_count", min_value=1
        ),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="unique_seller_count", min_value=1
        ),
        gx.expectations.ExpectColumnValuesToBeBetween(column="total_price", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(column="total_freight", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(column="payment_count", min_value=1),
        gx.expectations.ExpectColumnValuesToBeBetween(column="payment_value", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="max_payment_installments", min_value=0
        ),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="same_state_share", min_value=0, max_value=1
        ),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="customer_state", value_set=list(settings.allowed_states)
        ),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="dominant_seller_state", value_set=list(settings.allowed_states)
        ),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="dominant_payment_type",
            value_set=list(settings.allowed_payment_types),
        ),
    ]

    failures: list[str] = []
    for expectation in expectations:
        result = batch.validate(expectation)
        if not result.success:
            failures.append(expectation.__class__.__name__)

    if failures:
        raise DataValidationError("Great Expectations validation failed: " + ", ".join(failures))
