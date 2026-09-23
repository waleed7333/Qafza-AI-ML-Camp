import pandas as pd
import pytest

from src.qafza_mlops.features import FEATURE_WHITELIST, make_features


def test_make_features_matches_training_contract(sample_order):
    frame = pd.DataFrame([sample_order])
    result = make_features(frame)

    assert list(result.columns) == FEATURE_WHITELIST
    assert result.shape == (1, 24)
    assert result.loc[0, "purchase_month"] == 1
    assert result.loc[0, "purchase_weekday"] == 1
    assert result.loc[0, "purchase_hour"] == 10
    assert result.loc[0, "promised_window_days"] == pytest.approx(10.0)
    assert result.loc[0, "freight_price_ratio"] == pytest.approx(0.2)
