from src.qafza_mlops.features import FEATURE_WHITELIST, SOURCE_COLUMNS


FORBIDDEN = {
    "order_delivered_customer_date",
    "order_delivered_carrier_date",
    "order_approved_at",
    "order_status",
    "delivery_delta_hours",
    "late",
    "order_id",
    "customer_id",
    "customer_unique_id",
    "shipping_limit_date",
}


def test_feature_contract_is_purchase_time_only():
    assert len(SOURCE_COLUMNS) == 20
    assert len(FEATURE_WHITELIST) == 24
    assert not set(FEATURE_WHITELIST) & FORBIDDEN
    assert not any("review" in column for column in FEATURE_WHITELIST)
