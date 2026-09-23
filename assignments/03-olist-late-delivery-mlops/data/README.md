# Data

This assignment is self-contained and does not read data from Assignment 01 or Assignment 02.

Place the nine original Olist CSV files under `data/raw/` before the first bootstrap:

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

The raw directory is intentionally not committed to Git. It is versioned with DVC when `make dvc-track` is run.

Generated notebook artifacts are written to `artifacts/` and are also versioned with DVC rather than Git.
