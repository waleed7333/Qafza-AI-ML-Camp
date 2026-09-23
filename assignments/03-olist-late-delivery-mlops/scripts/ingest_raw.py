#!/usr/bin/env python3
"""Create the standalone raw Olist schema and load the nine local CSV files."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"
FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
}


def connect():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB", "qafza_mlops"),
        user=os.getenv("POSTGRES_USER", "qafza"),
        password=os.getenv("POSTGRES_PASSWORD", "qafza_dev_password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )


def main() -> int:
    paths = {table: DATA_DIR / name for table, name in FILES.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        message = "Missing original Olist CSV files under data/raw:\n  "
        raise SystemExit(message + "\n  ".join(missing))

    schema_sql = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(schema_sql)
        for table, path in paths.items():
            sql = (
                f"COPY raw.{table} FROM STDIN "
                "WITH (FORMAT CSV, HEADER TRUE, NULL '', ENCODING 'UTF8')"
            )
            with path.open("rb") as source, cursor.copy(sql) as copy:
                while chunk := source.read(1024 * 1024):
                    copy.write(chunk)
            cursor.execute(f"SELECT count(*) FROM raw.{table}")
            print(f"{table}: {cursor.fetchone()[0]:,}")
        connection.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
