# Great Expectations

Incoming inference data is validated with Great Expectations in `src/qafza_mlops/validation.py`.

The validation contract checks types/ranges/categories after the FastAPI/Pydantic request schema has performed structural validation. Missing values that the fitted notebook preprocessor was explicitly trained to impute are allowed; structurally invalid or out-of-range values are rejected before model inference.
