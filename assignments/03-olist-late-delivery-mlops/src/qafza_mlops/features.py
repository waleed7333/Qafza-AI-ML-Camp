"""Deterministic purchase-time feature construction.

This is the production equivalent of this assignment's Notebook 05. It intentionally
contains no fit operation. The fitted sklearn preprocessor is loaded separately.
"""

from __future__ import annotations

import holidays
import numpy as np
import pandas as pd

BASE_NUMERIC = [
    "item_count",
    "unique_product_count",
    "unique_seller_count",
    "total_price",
    "total_freight",
    "mean_product_weight_g",
    "mean_product_volume_cm3",
    "mean_product_photos_qty",
    "payment_count",
    "payment_value",
    "max_payment_installments",
    "same_state_share",
    "mean_customer_seller_distance_km",
    "max_customer_seller_distance_km",
]

BASE_CATEGORICAL = [
    "customer_state",
    "dominant_product_category",
    "dominant_seller_state",
    "dominant_payment_type",
]

DERIVED_NUMERIC = [
    "purchase_month",
    "purchase_weekday",
    "purchase_hour",
    "promised_window_days",
    "freight_price_ratio",
    "purchase_is_holiday",
]

FEATURE_WHITELIST = BASE_NUMERIC + BASE_CATEGORICAL + DERIVED_NUMERIC

SOURCE_COLUMNS = (
    BASE_NUMERIC
    + BASE_CATEGORICAL
    + [
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
    ]
)


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the exact 24 purchase-time features used by the fitted preprocessor."""
    missing = sorted(set(SOURCE_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing source columns: {missing}")

    features = frame.copy()
    purchase = pd.to_datetime(features["order_purchase_timestamp"], errors="raise")
    estimated = pd.to_datetime(features["order_estimated_delivery_date"], errors="raise")

    years = sorted(set(purchase.dt.year.astype(int).tolist()))
    brazil_holidays = holidays.Brazil(years=years)

    features["purchase_month"] = purchase.dt.month
    features["purchase_weekday"] = purchase.dt.weekday
    features["purchase_hour"] = purchase.dt.hour
    features["purchase_is_holiday"] = purchase.dt.date.map(
        lambda date: int(date in brazil_holidays)
    )
    features["promised_window_days"] = (estimated - purchase).dt.total_seconds() / 86_400
    features["freight_price_ratio"] = features["total_freight"] / features["total_price"].replace(
        0, np.nan
    )

    return features[FEATURE_WHITELIST]
