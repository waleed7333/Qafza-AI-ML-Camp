# Assignment 03 local acceptance checklist

Do not merge `assignment-03` into `main` until this checklist is completed on the target machine.

## Prepare

- Switch to branch `assignment-03`.
- Confirm the working tree is clean before adding local data.
- Copy `.env.example` to `.env`.
- Put the nine original Olist CSV files in `data/raw/`, or configure a durable DVC remote after the DVC pointer exists.

## Full-stack start

Run:

```bash
docker compose up --build
```

The first successful run must show:

- PostgreSQL healthy.
- MinIO available and both buckets created.
- MLflow healthy.
- Bootstrap exits successfully after data ingestion, six notebooks, and model registration.
- API healthy only after bootstrap succeeds.
- Prometheus starts after the API is healthy.

## Service demonstrations

Verify:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  --data @examples/order.json
```

Also submit a two-order request to `/predict-batch`.

The prediction response must include prediction, probability, model version, and request id.

## Required evidence

Run:

```bash
make parity
make drift
```

Inspect:

- FastAPI automatic docs at `/docs`.
- MLflow experiment runs and the registered `champion` alias.
- MinIO artifact bucket.
- Prometheus metrics.
- PostgreSQL `serving.prediction_logs`.
- `logs/api.log`.

## Failure demonstrations

- Submit a negative `total_price`; expect HTTP 422.
- Submit an estimated delivery timestamp before purchase; expect HTTP 422.
- Temporarily introduce a failing pytest assertion and confirm CI stops before Docker publication. Revert the deliberate failure immediately.

## DVC snapshot

After successful bootstrap:

```bash
make dvc-track
make dvc-push
```

Review the generated `data/raw.dvc`, `artifacts.dvc`, and `.gitignore` changes before committing them.

A local MinIO DVC remote is not sufficient for a different physical machine. For clean-machine recovery, configure a durable S3-compatible remote reachable by both machines and then verify `dvc pull`.

## Final Git review

Before merge:

```bash
git status
git diff main...assignment-03
```

Only after local end-to-end acceptance and the final review should Assignment 03 be merged into `main`.
