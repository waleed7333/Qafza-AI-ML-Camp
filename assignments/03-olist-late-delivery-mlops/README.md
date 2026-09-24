# Assignment 03 — From Notebooks to Production

**Status: ✅ Completed**

Self-contained MLOps inference system for the Olist late-delivery classifier.

The verified local acceptance evidence is recorded in [`docs/acceptance-report.md`](docs/acceptance-report.md).

This assignment intentionally lives in the same Qafza repository as Assignments 01 and 02, but it does **not** depend on either one at runtime. It owns its own raw-data directory, PostgreSQL service, training notebooks, fitted artifacts, MLflow registry, API, tests, containers, CI/CD workflow, logging, and monitoring.

## Objective

Turn the notebook model into a reproducible inference service.

Input:

- one new order or a batch of new orders

Output:

- late / on-time classification
- positive-class probability
- registered model version

Training remains in the six notebooks. Production inference never calls `fit()`.

## Architecture

```text
Original Olist CSV files
        |
        v
Standalone PostgreSQL / raw schema
        |
        v
6 training notebooks
        |
        +--> fitted preprocessor
        +--> fitted LogisticRegression model
        +--> feature contract / metrics
        |
        v
MLflow Tracking + Model Registry
        |
   champion alias
        |
        v
FastAPI inference service
        |
        +--> Great Expectations validation
        +--> fitted preprocessor.transform()
        +--> registered model.predict_proba()
        +--> threshold
        +--> PostgreSQL prediction logs
        +--> Prometheus metrics
```

Artifact storage is provided by MinIO. Because upstream MinIO container registries are not relied on for reproducibility, `Dockerfile.minio` builds pinned MinIO server/client binaries from the official GitHub release assets and verifies the pinned SHA256 digests before installation. The local stack is orchestrated by Docker Compose.

## Repository structure

```text
03-olist-late-delivery-mlops/
├── app/                  # FastAPI routes and request/response schemas
├── config/               # versioned non-secret configuration
├── data/                 # original data location; raw files are DVC-managed
├── examples/             # sample API / CLI input
├── gx/                   # Great Expectations documentation
├── logs/                 # runtime logs
├── models/               # model policy; production loads from MLflow
├── monitoring/           # Prometheus config and alert policy
├── notebooks/            # six self-contained training notebooks
├── requirements/         # runtime, training, and development dependencies
├── scripts/              # bootstrap, ingestion, registry, parity, CLI, drift
├── sql/                  # standalone raw PostgreSQL schema
├── src/qafza_mlops/      # reusable production Python modules
├── tests/                # unit, data, model, and API integration tests
├── .dvc/                 # DVC remote configuration
├── .env.example
├── .pre-commit-config.yaml
├── compose.yaml
├── Dockerfile
├── Dockerfile.dev
├── Dockerfile.minio
├── Makefile
└── pyproject.toml
```

The GitHub Actions workflow is stored at repository root:

```text
.github/workflows/assignment-03-ci-cd.yml
```

It is path-filtered to Assignment 03 and does not run because files in Assignment 01 or 02 changed.

## Model contract

The production feature builder is the Python-module equivalent of Notebook 05.

Source request fields:

- 14 numeric purchase-time fields
- 4 categorical purchase-time fields
- purchase timestamp
- estimated delivery timestamp

The feature builder derives:

- `purchase_month`
- `purchase_weekday`
- `purchase_hour`
- `promised_window_days`
- `freight_price_ratio`
- `purchase_is_holiday`

This produces the same 24 pre-preprocessing fields as Notebook 05.

The fitted preprocessor then produces 135 transformed features.

The selected model remains:

```text
LogisticRegression
C = 1.0
class_weight = None
decision threshold = 0.15699537486646237
```

The service does not refit the model, imputers, scaler, or encoder.

## Prerequisites

For the complete local stack:

- Git
- Docker Engine / Docker Desktop
- Docker Compose v2
- the nine original Olist CSV files

No Python installation is required for the Docker-first path.

## 1. Prepare the assignment

From the repository root:

```bash
git switch assignment-03
cd assignments/03-olist-late-delivery-mlops
cp .env.example .env
```

Place the nine original Olist CSV files under:

```text
data/raw/
```

Expected names are listed in `data/README.md`.

Task 3 does not read the data directory of another assignment.

## 2. Start the complete stack

Run:

```bash
docker compose up --build
```

On the first run, the `bootstrap` service:

1. recreates and loads this assignment's PostgreSQL `raw` schema;
2. executes notebooks 01 through 06 in order;
3. recreates the fitted preprocessor and final model;
4. logs all candidate Logistic Regression configurations to MLflow;
5. logs the selected run, metrics, and artifacts;
6. registers the selected model;
7. assigns the registered-model alias `champion`.

Only after bootstrap succeeds does the API start.

Later starts are idempotent: if the configured `champion` alias already exists, bootstrap does not retrain unless `FORCE_BOOTSTRAP=1`. If raw data is missing and `data/raw.dvc` exists, bootstrap first attempts `dvc pull data/raw.dvc`.

## Services

Default local endpoints:

| Service | Address |
|---|---|
| FastAPI | http://localhost:8000 |
| FastAPI docs | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| MinIO API | http://localhost:9000 |
| MinIO console | http://localhost:9001 |
| Prometheus | http://localhost:9090 |
| PostgreSQL host port | localhost:5433 |

All defaults can be overridden through `.env`.

## API routes

### Health

```bash
curl http://localhost:8000/health
```

### Model information

```bash
curl http://localhost:8000/model-info
```

### Single prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  --data @examples/order.json
```

The response contains:

```json
{
  "prediction": 0,
  "label": "on_time",
  "probability": 0.12,
  "model_version": "1",
  "request_id": "..."
}
```

The probability above is illustrative; the real response comes from the registered model.

### Batch prediction

Use:

```text
POST /predict-batch
```

with:

```json
{
  "orders": [
    { "...": "first order" },
    { "...": "second order" }
  ]
}
```

The configured default maximum batch size is 500.

## Command-line inference

The same production Python path can be used without HTTP:

```bash
docker compose run --rm trainer \
  python scripts/predict_cli.py examples/order.json
```

## Validation

Validation occurs in two layers.

1. Pydantic/FastAPI validates the request structure and primitive constraints.
2. Great Expectations checks representative column types, required-value missingness, semantic ranges, and allowed categories before inference.

Bad data is rejected rather than allowed to crash the model.

## Testing

Install locally if desired:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install-dev
```

Then:

```bash
make lint
make format-check
make test
```

The suite contains:

- unit tests for deterministic feature construction;
- data/leakage contract tests;
- Great Expectations data tests;
- model/prediction tests;
- end-to-end FastAPI route tests with controlled test doubles.

## Notebook-to-production parity

After the first bootstrap, prove that the registered serving pipeline and the local notebook artifacts return the same probability for the same held-out row:

```bash
make parity
```

The command fails unless the two probabilities match to `1e-12` absolute tolerance.

## DVC

DVC is configured for S3-compatible storage.

For the local demonstration, MinIO provides the `qafza-dvc` bucket.

After the initial bootstrap:

```bash
make dvc-track
make dvc-push
make dvc-status
```

The Docker tool container does not mount the repository's parent `.git` directory. DVC therefore uses a Git-ignored local setting (`.dvc/config.local`) with `core.no_scm=true` inside the container, while the host Git repository still versions the generated `.dvc` pointer files and project configuration.

This versions:

- `data/raw`
- `artifacts`

The generated `.dvc` pointer files should be committed to Git; the large data itself should not.

For a true second-machine `dvc pull`, point the DVC remote to a durable S3-compatible endpoint reachable by both machines. The local MinIO volume proves the DVC workflow but is local to one Docker host. Once `data/raw.dvc` is committed and the remote is reachable, the bootstrap service automatically tries to pull the raw snapshot when `data/raw/` is absent.

## MLflow

MLflow tracks:

- all eight Logistic Regression candidate configurations;
- their validation PR-AUC and ROC-AUC;
- selected parameters and threshold;
- validation/test metrics;
- fitted model;
- fitted preprocessor;
- feature list;
- feature-selection metadata;
- evaluation summaries.

The API resolves:

```text
models:/olist_late_delivery@champion
```

It never loads `artifacts/06_model/model.joblib` directly.

## Logging and error handling

The API logs to both console and:

```text
logs/api.log
```

Every successful prediction records:

- request id;
- input;
- output;
- probability;
- latency;
- model version.

Successful prediction records are also persisted in PostgreSQL table:

```text
serving.prediction_logs
```

A later real outcome can be attached with:

```bash
docker compose run --rm trainer \
  python scripts/record_outcome.py REQUEST_ID 1
```

where `1` means actually late and `0` means actually on time.

## Monitoring

Prometheus scrapes `/metrics`.

The service exposes:

- request counts by route/status;
- prediction latency histogram;
- prediction counts by predicted class/model version;
- loaded-model information.

Recent prediction-distribution drift can be checked with:

```bash
make drift
```

Drift is not evaluated until at least 100 recent predictions are available. This avoids treating a tiny demonstration sample as operational evidence of distribution shift. After the minimum sample count is reached, the configured absolute deviation threshold is applied.

The initial alert policy is documented in `monitoring/ALERTS.md`.

## CI

The repository-root workflow is:

```text
.github/workflows/assignment-03-ci-cd.yml
```

The workflow is path-filtered to Assignment 03 and is organized for fast feedback:

1. `quality` and `infrastructure` start independently and run in parallel;
2. `quality` installs pinned dependencies, checks them with `pip check`, runs Ruff lint/format checks, and runs pytest;
3. `infrastructure` validates Compose first, builds the pinned MinIO tool image early, verifies external PostgreSQL/Prometheus images, builds the development image, validates trainer/DVC behavior, and performs the PostgreSQL/MinIO/MLflow registry-artifact smoke test;
4. `production-image` runs only after both jobs pass and verifies that the production FastAPI image builds successfully.

The CI **never publishes a container image** and has no package-write permission.

## Manual image release

Publishing is intentionally a manual owner action rather than a CI/CD side effect. When a release is desired, first choose an explicit release tag, build locally from the reviewed `main` commit, then authenticate and push it yourself.

Example build/tag flow:

```bash
docker build \
  -t ghcr.io/waleed7333/qafza-assignment-03:<release-tag> \
  assignments/03-olist-late-delivery-mlops
```

After authenticating to GHCR outside the repository, publish only the tag you selected:

```bash
docker push ghcr.io/waleed7333/qafza-assignment-03:<release-tag>
```

Credentials or tokens must never be written into repository files, shell scripts, Compose files, or documentation examples.

## Pre-commit

From this assignment directory, with the development environment active:

```bash
pre-commit install --config .pre-commit-config.yaml
```

The hooks run Ruff checks before a commit is created.

## Demonstrating failure handling

Bad API data:

```bash
cp examples/order.json /tmp/bad-order.json
# edit total_price to a negative value, then submit it
```

FastAPI/Pydantic returns HTTP 422.

A deliberately failing pytest test returns a non-zero exit code, and the GitHub Actions quality job stops before Docker publication.

## Acceptance evidence

The completed local acceptance run, observed results, CI evidence, and known DVC portability boundary are recorded in [`docs/acceptance-report.md`](docs/acceptance-report.md).

## Clean-machine acceptance

The reproducibility sequence is:

1. clone the repository;
2. switch to the intended Task 3 commit/branch;
3. obtain the DVC-managed raw data from a durable remote, or place the original nine CSV files under `data/raw`;
4. copy `.env.example` to `.env`;
5. run `docker compose up --build`;
6. verify `/health`, `/model-info`, `/predict`, and `/predict-batch`;
7. run `make parity`;
8. demonstrate rejection of bad input and confirm invalid requests are observable in metrics;
9. run `make dvc-status` after the local DVC snapshot is pushed;
10. demonstrate that a failing automated test blocks CI.

## Important boundary

Training belongs to the notebooks for this assignment.

The production inference path consists only of:

```text
request
  -> schema validation
  -> Great Expectations
  -> deterministic feature construction
  -> fitted preprocessor.transform()
  -> registered LogisticRegression.predict_proba()
  -> fixed threshold
  -> response + logs + metrics
```

No `fit()` occurs in the inference service.
