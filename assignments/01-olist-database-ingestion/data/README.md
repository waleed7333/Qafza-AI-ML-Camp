# Olist Dataset

This directory is reserved for the local source data used by **Assignment 01 — Olist Database Ingestion**.

The project uses the **Brazilian E-Commerce Public Dataset by Olist**, provided as multiple related CSV files.

---

## Dataset Placement

Create the following directory locally:

```text
data/raw/
```

Place the nine original CSV files inside it without renaming or modifying them:

```text
data/
│
├── README.md
│
└── raw/
    ├── olist_customers_dataset.csv
    ├── olist_geolocation_dataset.csv
    ├── olist_order_items_dataset.csv
    ├── olist_order_payments_dataset.csv
    ├── olist_order_reviews_dataset.csv
    ├── olist_orders_dataset.csv
    ├── olist_products_dataset.csv
    ├── olist_sellers_dataset.csv
    └── product_category_name_translation.csv
```

---

## Expected Files

| File | Represents |
|---|---|
| `olist_customers_dataset.csv` | Order-specific customer records and customer location information |
| `olist_geolocation_dataset.csv` | Brazilian ZIP-prefix geolocation observations |
| `olist_order_items_dataset.csv` | Individual items contained in orders |
| `olist_order_payments_dataset.csv` | Payment records associated with orders |
| `olist_order_reviews_dataset.csv` | Customer review records |
| `olist_orders_dataset.csv` | Orders and their lifecycle timestamps |
| `olist_products_dataset.csv` | Product attributes and category information |
| `olist_sellers_dataset.csv` | Seller records and locations |
| `product_category_name_translation.csv` | Portuguese-to-English product-category translations |

---

## Version-Control Policy

The raw dataset is a **local project input** and is intentionally excluded from Git.

The assignment `.gitignore` contains:

```gitignore
data/raw/
```

Therefore:

- Raw CSV files remain on the local machine.
- They must not be staged or committed.
- They must not be modified by the ingestion pipeline.
- Only this documentation file is tracked under `data/`.

This keeps the repository lightweight and separates source data from version-controlled implementation files.

---

## Verify the Dataset

From the assignment directory, run:

```bash
python scripts/profile_data.py
```

The profiler reads the files without modifying them and verifies their structural characteristics before database ingestion.

A successful setup should detect all nine required source files.

---

## Important Notes

The source files should be treated as the **raw layer** of the project.

Do not manually:

- rename columns,
- remove rows,
- fill missing values,
- modify timestamps,
- translate categories,
- aggregate records,
- or rewrite the CSV files.

Cleaning and feature-engineering decisions belong to later stages of the training workflow.

For the relational structure and known source-data characteristics, see:

[`../docs/data-model.md`](../docs/data-model.md)
