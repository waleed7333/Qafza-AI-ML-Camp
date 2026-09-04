# Assignment 02 — From Tables to Notebooks

Notebook-based machine learning workflow for predicting late Olist deliveries.

This assignment continues directly from **Assignment 01 — Olist Database Ingestion**.
Assignment 01 loads and validates the raw Olist dataset inside a local PostgreSQL database. Assignment 02 consumes those validated database tables and turns them into a reproducible machine learning workflow composed of six ordered Jupyter notebooks.

The objective is not only to train a model, but to build the full path from relational tables to a leakage-safe, reproducible first ML experiment.

---

## Project Context

The project currently follows this progression:

```text
Olist CSV Dataset
        │
        ▼
Assignment 01
Database ingestion and validation
        │
        ▼
Docker + PostgreSQL 16
olist database / raw schema
        │
        ▼
Assignment 02
Notebook ML workflow
        │
        ├── Join
        ├── Label
        ├── Split
        ├── EDA
        ├── Feature Engineering
        └── Train & Evaluate
```

Assignment 02 does **not** create a new database or Docker stack.

It reuses the PostgreSQL instance created by Assignment 01.

---

## Machine Learning Problem

The task is a binary classification problem:

> **At approximately purchase time, can we predict whether an order will arrive later than its estimated delivery date?**

Target definition:

```text
late = 1  → actual delivery date > estimated delivery date
late = 0  → actual delivery date <= estimated delivery date
```

Orders without a known actual delivery date cannot be assigned a reliable delivery outcome and are excluded from the supervised learning population.

---

## Prediction-Time Boundary

The prediction point is approximately:

```text
order_purchase_timestamp
```

This creates an important modeling rule:

> A model feature must represent information that would have been available when the order was placed.

Historical future information may be used to create the label, but it must not be used as a model input.

Examples of prohibited model information include:

* actual customer delivery timestamp
* carrier delivery timestamp
* post-delivery review information
* outcome-dependent order status
* delivery-duration values calculated from the final outcome
* other information generated only after the prediction point

The final feature set is therefore built from an explicit **purchase-time whitelist**, rather than simply removing a few known leakage columns.

---

## Repository Structure

```text
02-olist-late-delivery-ml/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── notebooks/
│   ├── 01_read_join_tables.ipynb
│   ├── 02_create_labels.ipynb
│   ├── 03_train_val_test_split.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_feature_engineering.ipynb
│   └── 06_train_tune_evaluate.ipynb
│
└── artifacts/
    ├── 01_joined/
    ├── 02_labeled/
    ├── 03_splits/
    ├── 04_eda/
    ├── 05_features/
    └── 06_model/
```

Generated datasets, fitted transformers, trained models, virtual environments, and other large reproducible files are excluded from Git.

Small metadata and result summaries remain versionable so the reasoning and outputs can be reviewed.

---

## Workflow

Each notebook has one responsibility and produces artifacts for the next step.

| Notebook                        | Responsibility                                                       | Main Output                           |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------------------- |
| `01_read_join_tables.ipynb`     | Read, inspect, aggregate, and safely join the nine PostgreSQL tables | Order-level ML table                  |
| `02_create_labels.ipynb`        | Construct and validate the late/on-time target                       | Labeled order table                   |
| `03_train_val_test_split.ipynb` | Create train, validation, and test partitions                        | Three split datasets                  |
| `04_eda.ipynb`                  | Perform detailed EDA on training data only                           | Figures and findings                  |
| `05_feature_engineering.ipynb`  | Build leakage-safe features and fit preprocessing                    | Model-ready features and preprocessor |
| `06_train_tune_evaluate.ipynb`  | Establish baseline, train, tune, and evaluate                        | Final model and metrics               |

The artifact flow is:

```text
PostgreSQL raw tables
        │
        ▼
Notebook 01
        │
        ▼
ml_orders.parquet
        │
        ▼
Notebook 02
        │
        ▼
labeled_orders.parquet
        │
        ▼
Notebook 03
        │
        ├── train.parquet
        ├── validation.parquet
        └── test.parquet
                │
                ▼
Notebook 04
        │
        ├── figures
        └── findings.md
                │
                ▼
Notebook 05
        │
        ├── transformed datasets
        ├── fitted preprocessor
        └── feature metadata
                │
                ▼
Notebook 06
        │
        ├── model
        ├── metrics
        └── evaluation summary
```

---

## Notebook 01 — Read and Join Tables

The first notebook reads and inspects all nine tables from the `raw` PostgreSQL schema:

* `category_translation`
* `customers`
* `geolocation`
* `order_items`
* `order_payments`
* `order_reviews`
* `orders`
* `products`
* `sellers`

Before joining, it checks:

* row counts
* keys
* uniqueness
* duplicates
* missing values
* table grain

Special care is taken with one-to-many tables such as `order_items` and `order_payments`.

These tables are aggregated before the final join to prevent row multiplication.

The resulting machine learning table satisfies:

```text
1 row = 1 order
```

Validated result:

```text
99,441 rows
99,441 unique order IDs
```

---

## Notebook 02 — Create the Target

The second notebook creates the binary delivery target using:

```text
order_delivered_customer_date
vs.
order_estimated_delivery_date
```

Orders without enough information to determine the actual delivery outcome are excluded.

Final labeled population:

| Class             |     Orders |    Share |
| ----------------- | ---------: | -------: |
| On time           |     89,941 | 93.2263% |
| Late              |      6,535 |  6.7737% |
| **Total labeled** | **96,476** | **100%** |

Unknown outcomes excluded:

```text
2,965 orders
```

The resulting on-time-to-late ratio is approximately:

```text
13.763 : 1
```

This confirms a meaningful class imbalance.

The label compares normalized calendar dates: delivery before or on the estimated date is on time, while delivery after it is late. There are 1,292 labeled orders (1.3392%) delivered after midnight on the same calendar date as the estimate. A raw timestamp comparison would mark them late; the calendar-date convention correctly changes all 1,292 to on time.

---

## Notebook 03 — Chronological Split

The data is split **before detailed exploratory analysis**.

A chronological split was selected instead of a random split because the real deployment scenario is temporal:

> train on historical orders and predict later orders.

The labeled dataset is deterministically sorted by purchase timestamp and then `order_id`, then divided approximately 70/15/15.

| Split      | Orders | Late Rate |
| ---------- | -----: | --------: |
| Train      | 67,533 |   7.8347% |
| Validation | 14,471 |   4.3121% |
| Test       | 14,472 |   4.2841% |

Temporal boundaries:

```text
Train ends:
2018-04-15 20:07:56

Validation ends:
2018-06-21 07:50:39

Test ends:
2018-08-29 15:00:37
```

The changing late-delivery rate across periods is retained rather than artificially corrected because it represents real temporal variation in the data.

---

## Notebook 04 — Exploratory Data Analysis

Detailed EDA is performed on the **training split only**.

The notebook investigates:

* data types
* dataset shape and memory usage
* missing values
* numerical distributions
* skew and outliers
* categorical cardinality
* rare categories
* relationships with the target
* purchase-time patterns
* seasonality
* Brazilian national purchase-holiday effects using the pinned `holidays` package
* suspicious coordinate ranges and explicit Brazil-bound checks
* customer state, seller state, and customer/seller same-state relationships
* ZIP-prefix cardinality
* validated item-level Haversine distance aggregated to order mean and maximum
* descriptive actual delivery timing, explicitly marked outcome-only
* train-only evidence for promised-window and freight/price derived candidates
* candidate model features
* leakage risks

The purpose of the EDA is not simply to create charts.

Its findings determine the feature-engineering decisions used in Notebook 05.

Outputs include:

```text
artifacts/04_eda/figures/
artifacts/04_eda/findings.md
```

---

## Notebook 05 — Feature Engineering

Feature engineering uses only information considered available at prediction time.

An explicit feature whitelist is used to prevent accidental leakage.

Preprocessing is fitted using:

```text
TRAIN ONLY
```

The fitted transformations are then reused unchanged for:

```text
Train
Validation
Test
```

The workflow includes, where applicable:

* numerical missing-value handling
* categorical missing-value handling
* categorical encoding
* numerical scaling
* purchase-time date features
* order-level aggregates
* geography-related features
* promised delivery-window information
* purchase-date Brazilian holiday indicator
* validated mean/max customer-to-seller distance and same-state share

The final preprocessing pipeline produces:

```text
135 transformed features
```

The fitted preprocessing object is saved so future data can be transformed using the same learned rules without fitting again.

---

## Notebook 06 — Baseline, Training, and Evaluation

A simple majority-class classifier is used first as a baseline.

### Majority Baseline — Validation

```text
PR-AUC:  0.0431
Recall:  0.0000
F1:      0.0000
Accuracy: 0.9569
```

The high accuracy is misleading because the baseline predicts the majority class and fails to identify late orders.

This demonstrates why accuracy alone is not appropriate for this imbalanced classification problem.

---

## Selected Model

The selected learned model is:

```text
Logistic Regression
C = 1.0
class weighting = none
```

Model selection is performed using validation data.

A validation-only threshold search selected:

```text
Decision threshold = 0.1570
```

The threshold was selected using validation F1 and was fixed before the final test evaluation.

---

## Validation Performance

| Metric    |  Score |
| --------- | -----: |
| PR-AUC    | 0.1374 |
| ROC-AUC   | 0.7742 |
| Precision | 0.1628 |
| Recall    | 0.3670 |
| F1        | 0.2255 |

The learned model substantially improves on the majority baseline for identifying late deliveries.

---

## Final Test Performance

The test set is evaluated only after feature selection, preprocessing, model configuration, and classification threshold have been fixed.

| Metric    |  Score |
| --------- | -----: |
| PR-AUC    | 0.0784 |
| ROC-AUC   | 0.6514 |
| Precision | 0.0646 |
| Recall    | 0.2742 |
| F1        | 0.1046 |

Performance decreases on the later test period.

This reduction is retained and reported rather than used to retune the model.

The difference between validation and test performance is consistent with the observed temporal change in target prevalence and suggests that the delivery-prediction problem may experience distribution drift over time.

More detailed values and confusion matrices are available after execution in:

```text
artifacts/06_model/metrics.json
artifacts/06_model/results_summary.md
```

---

## Environment Setup

Assignment 02 uses the PostgreSQL service from Assignment 01.

From the Assignment 02 directory, start or verify the existing database:

```bash
docker compose \
  -f ../01-olist-database-ingestion/docker-compose.yml \
  up -d
```

Check its status:

```bash
docker compose \
  -f ../01-olist-database-ingestion/docker-compose.yml \
  ps
```

The expected local development connection defaults are:

```text
POSTGRES_DB=olist
POSTGRES_USER=olist
POSTGRES_PASSWORD=olist_dev_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

These local development defaults—including the known development password literal—appear as notebook fallbacks and match Assignment 01. Environment variables can override every connection value for another environment; these defaults are not suitable production credentials.

---

## Python Environment

Create an isolated virtual environment from the Assignment 02 directory:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

The local `.venv` directory is ignored by Git.

---

## Running the Assignment

The notebooks must be executed in numerical order:

```text
01 → 02 → 03 → 04 → 05 → 06
```

They can be executed interactively using Jupyter, or sequentially from the command line.

Example:

```bash
export MPLCONFIGDIR=/tmp/olist-matplotlib

for notebook in notebooks/0{1..6}_*.ipynb; do
  .venv/bin/jupyter nbconvert \
    --to notebook \
    --execute \
    --inplace \
    --ExecutePreprocessor.timeout=900 \
    "$notebook" || exit 1
done
```

Each notebook reads the artifacts produced by the previous stage and recreates its own outputs.

---

## Reproducibility and Validation

The implementation was validated using a clean sequential notebook execution.

The validation checks include:

* PostgreSQL contains all nine expected raw tables
* `raw.orders` contains 99,441 rows
* final joined table contains one unique row per order
* label construction is manually and programmatically checked
* unknown outcomes are excluded rather than guessed
* train, validation, and test splits are non-overlapping
* detailed EDA reads training data only
* prediction-time feature whitelist prevents future-information leakage
* preprocessing is fitted on training rows only
* validation is used for model and threshold selection
* test is reserved for final evaluation
* generated artifacts are reproducible from the notebook sequence
* no additional PostgreSQL or Docker stack is created by Assignment 02

---

## Artifact and Git Policy

Generated artifacts are intentionally separated from source notebooks.

Large reproducible files such as:

```text
*.parquet
*.joblib
```

are ignored by Git.

The following remain reviewable where appropriate:

```text
validation.json
label_summary.json
split_summary.json
findings.md
feature_list.json
feature_selection_metadata.json
metrics.json
results_summary.md
```

This keeps the repository lightweight while preserving the important evidence, decisions, and results from the workflow.

---

## Key Takeaways

This assignment establishes the first complete machine learning workflow in the project:

```text
Relational data
      ↓
Correct analytical grain
      ↓
Validated target
      ↓
Chronological split
      ↓
Train-only EDA
      ↓
Leakage-safe feature engineering
      ↓
Reproducible preprocessing
      ↓
Baseline comparison
      ↓
Model selection
      ↓
Final held-out evaluation
```

The first model improves substantially over the trivial baseline, but its weaker performance on the later test period also shows that model quality cannot be judged from validation results alone.

The result is intentionally treated as a **first reproducible ML baseline**, not as a production-ready model.

Production scripts and later MLOps stages belong to subsequent assignments.
