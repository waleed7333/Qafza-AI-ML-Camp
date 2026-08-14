#!/usr/bin/env python3
"""Create the raw schema and bulk-copy all Olist CSV files into PostgreSQL."""

from __future__ import annotations

import argparse
from pathlib import Path

from db import ASSIGNMENT_DIR, connect


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ASSIGNMENT_DIR / "data" / "raw")
    return parser.parse_args()


def copy_csv(cursor, table: str, path: Path) -> int:
    copy_sql = f"COPY raw.{table} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '', ENCODING 'UTF8')"
    with path.open("rb") as source, cursor.copy(copy_sql) as copy:
        while chunk := source.read(1024 * 1024):
            copy.write(chunk)
    cursor.execute(f"SELECT count(*) FROM raw.{table}")
    return cursor.fetchone()[0]


def main() -> int:
    args = parse_args()
    paths = {table: args.data_dir / filename for table, filename in FILES.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise SystemExit("Missing required CSV files:\n  " + "\n  ".join(missing))

    schema_sql = (ASSIGNMENT_DIR / "sql" / "schema.sql").read_text(encoding="utf-8")
    print("Connecting to PostgreSQL...")
    with connect() as connection:
        with connection.cursor() as cursor:
            print("Recreating schema raw (repeatable full refresh)...")
            cursor.execute(schema_sql)
            for table, path in paths.items():
                print(f"Loading {path.name} -> raw.{table} ...", flush=True)
                count = copy_csv(cursor, table, path)
                print(f"  loaded {count:,} rows", flush=True)
        connection.commit()
    print("Ingestion complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
