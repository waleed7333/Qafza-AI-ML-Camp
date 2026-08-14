#!/usr/bin/env python3
"""Read-only structural profiler for the local Olist CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


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

CANDIDATE_KEYS = {
    "customers": [("customer_id",)],
    "geolocation": [("geolocation_zip_code_prefix",)],
    "order_items": [("order_id", "order_item_id")],
    "order_payments": [("order_id", "payment_sequential")],
    "order_reviews": [("review_id",), ("order_id",)],
    "orders": [("order_id",)],
    "products": [("product_id",)],
    "sellers": [("seller_id",)],
    "category_translation": [("product_category_name",)],
}

TIMESTAMP_COLUMNS = {
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
}

NUMERIC_COLUMNS = {
    "geolocation_lat",
    "geolocation_lng",
    "order_item_id",
    "price",
    "freight_value",
    "payment_sequential",
    "payment_installments",
    "payment_value",
    "review_score",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
}

ZIP_COLUMNS = {
    "customer_zip_code_prefix",
    "geolocation_zip_code_prefix",
    "seller_zip_code_prefix",
}

RELATIONSHIP_COLUMNS = {
    "customers": {"customer_id"},
    "order_items": {"order_id", "product_id", "seller_id"},
    "order_payments": {"order_id"},
    "order_reviews": {"order_id"},
    "orders": {"order_id", "customer_id"},
    "products": {"product_id", "product_category_name"},
    "sellers": {"seller_id"},
    "category_translation": {"product_category_name"},
}


def parse_args() -> argparse.Namespace:
    assignment_dir = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=assignment_dir / "data" / "raw",
        help="directory containing the nine source CSV files",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser.parse_args()


def key_label(columns: tuple[str, ...]) -> str:
    return "+".join(columns)


def profile_file(table: str, path: Path) -> tuple[dict, dict[str, list[str]]]:
    keys = CANDIDATE_KEYS[table]
    key_counts = {key: Counter() for key in keys}
    missing: Counter[str] = Counter()
    maximum_lengths: Counter[str] = Counter()
    numeric_invalid: Counter[str] = Counter()
    timestamp_invalid: Counter[str] = Counter()
    zip_lengths: dict[str, Counter[int]] = {}
    zip_leading_zero: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}
    relationship_values = {
        column: [] for column in RELATIONSHIP_COLUMNS.get(table, set())
    }
    malformed_rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        for column in headers:
            samples[column] = []
            if column in ZIP_COLUMNS:
                zip_lengths[column] = Counter()

        row_count = 0
        for row in reader:
            row_count += 1
            if None in row or set(row) != set(headers):
                malformed_rows += 1
            clean_row = {column: row.get(column, "") or "" for column in headers}
            for column in relationship_values:
                relationship_values[column].append(clean_row[column])

            for column, value in clean_row.items():
                if value == "":
                    missing[column] += 1
                    continue
                maximum_lengths[column] = max(maximum_lengths[column], len(value))
                if len(samples[column]) < 3 and value not in samples[column]:
                    samples[column].append(value)
                if column in NUMERIC_COLUMNS:
                    try:
                        Decimal(value)
                    except InvalidOperation:
                        numeric_invalid[column] += 1
                if column in TIMESTAMP_COLUMNS:
                    try:
                        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        timestamp_invalid[column] += 1
                if column in ZIP_COLUMNS:
                    zip_lengths[column][len(value)] += 1
                    if value.startswith("0"):
                        zip_leading_zero[column] += 1

            for key in keys:
                key_counts[key][tuple(clean_row[column] for column in key)] += 1

    candidate_key_results = {}
    for key, counts in key_counts.items():
        duplicate_values = sum(1 for count in counts.values() if count > 1)
        duplicate_rows = sum(count - 1 for count in counts.values() if count > 1)
        candidate_key_results[key_label(key)] = {
            "distinct": len(counts),
            "duplicate_values": duplicate_values,
            "duplicate_rows": duplicate_rows,
            "max_occurrences": max(counts.values(), default=0),
            "null_key_rows": sum(
                count for values, count in counts.items() if any(value == "" for value in values)
            ),
        }

    result = {
        "file": path.name,
        "rows": row_count,
        "columns": headers,
        "malformed_rows": malformed_rows,
        "missing": {column: missing[column] for column in headers},
        "max_length": {column: maximum_lengths[column] for column in headers},
        "candidate_keys": candidate_key_results,
        "numeric_invalid": {
            column: numeric_invalid[column] for column in headers if column in NUMERIC_COLUMNS
        },
        "timestamp_invalid": {
            column: timestamp_invalid[column] for column in headers if column in TIMESTAMP_COLUMNS
        },
        "zip": {
            column: {
                "length_counts": dict(sorted(zip_lengths[column].items())),
                "leading_zero_rows": zip_leading_zero[column],
            }
            for column in zip_lengths
        },
        "samples": samples,
    }
    return result, relationship_values


def relationship_result(child_values, parent_values) -> dict:
    parent_set = {value for value in parent_values if value != ""}
    child_values = [value for value in child_values if value != ""]
    orphan_values = {value for value in child_values if value not in parent_set}
    return {
        "child_rows_checked": len(child_values),
        "orphan_rows": sum(value in orphan_values for value in child_values),
        "orphan_distinct_keys": len(orphan_values),
    }


def main() -> int:
    args = parse_args()
    missing_files = [name for name in FILES.values() if not (args.data_dir / name).is_file()]
    if missing_files:
        raise SystemExit(f"Missing required files: {', '.join(missing_files)}")

    profiles = {}
    relationship_values = {}
    for table, filename in FILES.items():
        profiles[table], relationship_values[table] = profile_file(
            table, args.data_dir / filename
        )

    relationships = {
        "orders.customer_id -> customers.customer_id": relationship_result(
            relationship_values["orders"]["customer_id"],
            relationship_values["customers"]["customer_id"],
        ),
        "order_items.order_id -> orders.order_id": relationship_result(
            relationship_values["order_items"]["order_id"],
            relationship_values["orders"]["order_id"],
        ),
        "order_payments.order_id -> orders.order_id": relationship_result(
            relationship_values["order_payments"]["order_id"],
            relationship_values["orders"]["order_id"],
        ),
        "order_reviews.order_id -> orders.order_id": relationship_result(
            relationship_values["order_reviews"]["order_id"],
            relationship_values["orders"]["order_id"],
        ),
        "order_items.product_id -> products.product_id": relationship_result(
            relationship_values["order_items"]["product_id"],
            relationship_values["products"]["product_id"],
        ),
        "order_items.seller_id -> sellers.seller_id": relationship_result(
            relationship_values["order_items"]["seller_id"],
            relationship_values["sellers"]["seller_id"],
        ),
        "products.product_category_name -> category_translation.product_category_name": relationship_result(
            relationship_values["products"]["product_category_name"],
            relationship_values["category_translation"]["product_category_name"],
        ),
    }

    review_order_counts = Counter(relationship_values["order_reviews"]["order_id"])
    profiles["order_reviews"]["order_relationship"] = {
        "distinct_orders": len(review_order_counts),
        "orders_with_multiple_reviews": sum(count > 1 for count in review_order_counts.values()),
        "max_reviews_per_order": max(review_order_counts.values(), default=0),
    }
    output = {"tables": profiles, "relationships": relationships}

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for table, profile in profiles.items():
            print(f"{table}: {profile['rows']:,} rows; {profile['malformed_rows']} malformed")
            print(f"  columns: {', '.join(profile['columns'])}")
            print(f"  missing: {profile['missing']}")
            print(f"  candidate keys: {profile['candidate_keys']}")
            if profile["numeric_invalid"]:
                print(f"  numeric parse failures: {profile['numeric_invalid']}")
            if profile["timestamp_invalid"]:
                print(f"  timestamp parse failures: {profile['timestamp_invalid']}")
            if profile["zip"]:
                print(f"  ZIP behavior: {profile['zip']}")
            if "order_relationship" in profile:
                print(f"  review/order behavior: {profile['order_relationship']}")
        print("relationships:")
        for relationship, result in relationships.items():
            print(f"  {relationship}: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
