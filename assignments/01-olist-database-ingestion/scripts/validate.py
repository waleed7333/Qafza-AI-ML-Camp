#!/usr/bin/env python3
"""Fail-fast validation for the ingested Olist raw schema."""

from __future__ import annotations

import csv
from pathlib import Path

from db import ASSIGNMENT_DIR, connect


FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

EXPECTED_PARSED_ROWS = {
    "customers": 99_441,
    "geolocation": 1_000_163,
    "order_items": 112_650,
    "order_payments": 103_886,
    "order_reviews": 100_000,
    "orders": 99_441,
    "products": 32_951,
    "sellers": 3_095,
    "category_translation": 71,
}

KEY_CHECKS = {
    "customers.customer_id": "SELECT count(*) - count(DISTINCT customer_id) FROM raw.customers",
    "orders.order_id": "SELECT count(*) - count(DISTINCT order_id) FROM raw.orders",
    "order_items.(order_id, order_item_id)": "SELECT count(*) - count(DISTINCT (order_id, order_item_id)) FROM raw.order_items",
    "order_payments.(order_id, payment_sequential)": "SELECT count(*) - count(DISTINCT (order_id, payment_sequential)) FROM raw.order_payments",
    "products.product_id": "SELECT count(*) - count(DISTINCT product_id) FROM raw.products",
    "sellers.seller_id": "SELECT count(*) - count(DISTINCT seller_id) FROM raw.sellers",
    "category_translation.product_category_name": "SELECT count(*) - count(DISTINCT product_category_name) FROM raw.category_translation",
}

ORPHAN_CHECKS = {
    "orders -> customers": "SELECT count(*) FROM raw.orders o LEFT JOIN raw.customers c ON c.customer_id=o.customer_id WHERE c.customer_id IS NULL",
    "items -> orders": "SELECT count(*) FROM raw.order_items i LEFT JOIN raw.orders o ON o.order_id=i.order_id WHERE o.order_id IS NULL",
    "items -> products": "SELECT count(*) FROM raw.order_items i LEFT JOIN raw.products p ON p.product_id=i.product_id WHERE p.product_id IS NULL",
    "items -> sellers": "SELECT count(*) FROM raw.order_items i LEFT JOIN raw.sellers s ON s.seller_id=i.seller_id WHERE s.seller_id IS NULL",
    "payments -> orders": "SELECT count(*) FROM raw.order_payments p LEFT JOIN raw.orders o ON o.order_id=p.order_id WHERE o.order_id IS NULL",
    "reviews -> orders": "SELECT count(*) FROM raw.order_reviews r LEFT JOIN raw.orders o ON o.order_id=r.order_id WHERE o.order_id IS NULL",
}


def csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.reader(handle)) - 1


def main() -> int:
    failures: list[str] = []
    raw_dir = ASSIGNMENT_DIR / "data" / "raw"
    source_counts = {table: csv_rows(raw_dir / filename) for table, filename in FILES.items()}

    with connect() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        print(f"PASS connection: database={cursor.fetchone()[0]}")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='raw'")
        actual_tables = {row[0] for row in cursor.fetchall()}
        missing_tables = set(FILES) - actual_tables
        if missing_tables:
            failures.append(f"missing tables: {sorted(missing_tables)}")
        else:
            print("PASS tables: all 9 raw tables exist")

        for table, expected in EXPECTED_PARSED_ROWS.items():
            source = source_counts[table]
            cursor.execute(f"SELECT count(*) FROM raw.{table}")
            database = cursor.fetchone()[0]
            if source != expected or database != source:
                failures.append(
                    f"{table} rows: expected={expected}, parsed_source={source}, database={database}"
                )
            else:
                print(f"PASS rows {table}: {database:,}")

        for label, query in KEY_CHECKS.items():
            cursor.execute(query)
            duplicates = cursor.fetchone()[0]
            if duplicates:
                failures.append(f"key {label}: {duplicates} excess duplicate rows")
            else:
                print(f"PASS key {label}: unique")

        cursor.execute("SELECT count(*) - count(DISTINCT review_id) FROM raw.order_reviews")
        review_duplicate_rows = cursor.fetchone()[0]
        if review_duplicate_rows != 827:
            failures.append(f"review_id duplicate excess rows: expected=827, actual={review_duplicate_rows}")
        else:
            print("PASS source caveat: review_id has the profiled 827 excess duplicate rows")

        for label, query in ORPHAN_CHECKS.items():
            cursor.execute(query)
            orphans = cursor.fetchone()[0]
            if orphans:
                failures.append(f"relationship {label}: {orphans} orphan rows")
            else:
                print(f"PASS relationship {label}: 0 orphans")

        cursor.execute(
            "SELECT count(*) FROM raw.orders o JOIN raw.customers c ON c.customer_id=o.customer_id"
        )
        joined = cursor.fetchone()[0]
        if joined != EXPECTED_PARSED_ROWS["orders"]:
            failures.append(f"orders/customers JOIN: expected=99441, actual={joined}")
        else:
            print(f"PASS JOIN orders -> customers: {joined:,} rows")

    if failures:
        print("\nVALIDATION FAILED")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nVALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
