import pandas as pd
import pytest

from src.qafza_mlops.config import load_settings
from src.qafza_mlops.validation import DataValidationError, validate_inference_frame


def test_great_expectations_accepts_valid_order(sample_order):
    validate_inference_frame(pd.DataFrame([sample_order]), load_settings())


def test_great_expectations_rejects_unknown_state(sample_order):
    sample_order["customer_state"] = "XX"
    with pytest.raises(DataValidationError):
        validate_inference_frame(pd.DataFrame([sample_order]), load_settings())
