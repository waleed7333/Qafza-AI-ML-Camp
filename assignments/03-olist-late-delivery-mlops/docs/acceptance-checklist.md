# Assignment 03 re-verification checklist

The completed acceptance evidence is recorded in [`acceptance-report.md`](acceptance-report.md).

Assignment 03 is integrated into `main`. Use this checklist to reproduce or re-verify the completed system on another environment or against a specific reviewed commit.

## Prepare

- Switch to `main` and pull the latest reviewed state, or check out a specific reviewed commit for an exact reproduction.
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

`make drift` should report insufficient samples and exit successfully until the configured minimum sample count is reached; only sufficiently sized windows can trigger the drift-alert exit code.

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
- Temporarily introduce a failing pytest assertion and confirm the `quality` job fails and the dependent `production-image` validation job does not run. Revert the deliberate failure immediately.

## DVC snapshot

After successful bootstrap:

```bash
make dvc-track
make dvc-push
make dvc-status
```

The containerized DVC commands use the Git-ignored local setting `core.no_scm=true`
because the trainer mount does not include the repository's parent `.git` directory.
Review the generated `data/raw.dvc` and `artifacts.dvc` pointers before committing;
raw CSVs, generated artifacts, `.dvc/config.local`, `.env`, caches, and runtime logs
must remain ignored. `make dvc-status` should report the cache and remote in sync.

A local MinIO DVC remote is not sufficient for a different physical machine. For clean-machine recovery, configure a durable S3-compatible remote reachable by both machines and then verify `dvc pull`.

## Final Git review

For any future change or re-verification branch:

```bash
git status
git diff origin/main...HEAD
```

Do not commit raw CSV files, generated model artifacts, local DVC cache/config, `.env`, or runtime logs. Any future code change should pass the same CI gates before it is integrated into `main`.
