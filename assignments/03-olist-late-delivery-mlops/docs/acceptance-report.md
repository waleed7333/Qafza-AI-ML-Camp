# Assignment 03 acceptance report

## Status

**Local functional acceptance: passed. Final integration into `main`: passed.**

This report records the observed acceptance evidence for Assignment 03 on 2026-09-24. The functional acceptance baseline was commit:

```text
5ff62fc87f9d550b26ae7081a40b35341a7f6a87
```

The runtime integration commit was:

```text
7e196e519721d3ee4d42c050872c30faa9d40a66
```

It was fast-forwarded to `main` after branch acceptance. GitHub Actions run `36020844977` then passed on `main`, including quality, infrastructure/MLflow smoke, and production-image build validation. Container publication remained manual and was not performed by CI.

## Environment and orchestration

The complete Docker Compose stack was started from the Assignment 03 project and observed with:

- PostgreSQL healthy.
- MinIO healthy.
- MLflow healthy.
- FastAPI healthy.
- Prometheus running.
- `minio-init` exited with code 0 after creating the required buckets.
- `bootstrap` exited with code 0 after data ingestion, notebook execution, and model registration.

The bootstrap loaded all nine Olist CSV sources into this assignment's standalone PostgreSQL database and executed notebooks 01 through 06 successfully.

## Registered model contract

The serving API resolved the MLflow registered model:

```text
name: olist_late_delivery
alias: champion
version: 1
threshold: 0.15699537486646237
transformed_feature_count: 135
```

Production inference uses the registered model and fitted preprocessor; it does not refit them.

## API acceptance

Observed checks:

- `GET /health` returned `status=ok` and model version `1`.
- `GET /model-info` returned the expected registered model, alias, version, threshold, and 135 transformed features.
- `POST /predict` returned a valid classification, probability, model version, and request id.
- `POST /predict-batch` returned valid results for two orders.
- A negative `total_price` was rejected with HTTP 422 rather than crashing the service.
- Invalid request validation was exposed in Prometheus as `status="invalid"`.

## Notebook-to-production parity

The parity command completed successfully:

```text
Parity OK: probability=0.067299010902202
```

This verifies that the saved notebook-side artifacts and the registered serving pipeline returned the same probability for the parity sample at the configured tolerance.

## Logging and outcome tracking

Successful prediction requests were observed in:

- `logs/api.log`
- PostgreSQL table `serving.prediction_logs`

The persisted rows contained request id, prediction, probability, model version, latency, and timestamp.

Outcome tracking was also exercised by recording an observed outcome for a stored request. The database row was updated with `actual_late` and `actual_recorded_at`.

The serving schema enforces a unique index on `request_id`.

## Monitoring

Prometheus reported ready and successfully scraped the API target:

```text
up{job="qafza_assignment_03_api"} = 1
```

Observed application metrics included:

- prediction request counts by route/status;
- end-to-end prediction latency;
- prediction counts by label/model version;
- loaded-model information.

The drift command is intentionally gated by a minimum sample count. Small demonstration samples are reported as insufficient evidence rather than as operational drift. Once the minimum is reached, the configured baseline/delta rule is applied.

## DVC acceptance

DVC tracked:

- `data/raw`: 9 files, 126,144,332 bytes;
- `artifacts`: 28 files, 62,053,371 bytes.

The DVC push reported:

```text
39 files pushed
```

and the final remote check reported:

```text
Cache and remote 'minio' are in sync.
```

Git contains only the small `data/raw.dvc` and `artifacts.dvc` pointer files. Raw CSVs, generated artifacts, DVC cache/tmp files, local DVC config, `.env`, and runtime logs remain ignored.

### DVC portability boundary

The configured `minio` remote points to the MinIO service on the local Docker Compose network. This proves the DVC add/push/status workflow on the same Docker host, but it is **not** a durable cross-machine remote.

A true second-machine `dvc pull` requires an S3-compatible endpoint reachable by both machines plus credentials supplied outside Git. This limitation is documented rather than presented as completed evidence.

## Container-source resilience

MinIO server/client releases are pinned in `Dockerfile.minio` and downloaded from the official MinIO GitHub release assets with pinned SHA256 verification during the image build. This avoids depending on the continued anonymous availability of historical MinIO images in third-party container registries.

## CI evidence

The acceptance-baseline push triggered Assignment 03 CI/CD run `35998922506`, which completed successfully.

The quality job passed:

- dependency installation and `pip check`;
- Ruff lint;
- Ruff formatting check;
- pytest.

The Docker job passed:

- Docker Compose validation;
- external service image pulls;
- development/bootstrap image build;
- trainer direct-script imports;
- containerized DVC mode;
- PostgreSQL/MinIO/MLflow infrastructure smoke test;
- MLflow registry alias and artifact round trip;
- production API image build.

Container publication is intentionally outside CI. The workflow validates the production image build but never logs in to a registry or pushes an image. Releases are manual owner actions.

## Final integration result

The integration gate was completed:

- the accepted development branch was ahead of `main` with no missing `main` commits;
- the final branch CI passed;
- the reviewed diff contained only the intended repository documentation, Assignment 03 workflow, and Assignment 03 project files;
- no raw/generated data, local secrets, DVC cache/config, or runtime logs were committed;
- `main` was fast-forwarded to the accepted runtime commit;
- `main` CI run `36020844977` passed all quality, infrastructure, MLflow artifact/registry, and production-image build checks.

Any GHCR release remains a separate manual owner action. CI has no registry-login step, no package-write permission, and no image-push step.
