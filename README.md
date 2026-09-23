<div align="center">

# Qafza AI & Machine Learning Camp

**Assignments · Applied Machine Learning · Deep Learning · MLOps**

A structured collection of hands-on assignments and engineering projects completed throughout the **Qafza AI & Machine Learning Camp**.

</div>

---

## About

This repository documents my practical work throughout the **Qafza AI & Machine Learning Camp**, following the actual assignments released during the program. Each assignment owns its code, documentation, dependencies, configuration, and local data policy.

## Repository Structure

```text
Qafza-AI-ML-Camp/
├── .github/
│   └── workflows/
│       └── assignment-03-ci-cd.yml
├── assignments/
│   ├── 01-olist-database-ingestion/
│   ├── 02-olist-late-delivery-ml/
│   └── 03-olist-late-delivery-mlops/
├── LICENSE
└── README.md
```

Assignment 03 remains in the same repository but is runtime-isolated from Assignments 01 and 02.

## Assignments

| # | Assignment | Focus | Status |
|---:|---|---|:---:|
| 01 | [Olist Database Ingestion](assignments/01-olist-database-ingestion/) | PostgreSQL · Docker · Python · SQL · Data Ingestion | ✅ Completed |
| 02 | [Olist Late Delivery ML](assignments/02-olist-late-delivery-ml/) | Notebooks · EDA · Feature Engineering · Classification · Evaluation | ✅ Completed |
| 03 | [From Notebooks to Production](assignments/03-olist-late-delivery-mlops/) | FastAPI · DVC · Great Expectations · MLflow · Docker · CI/CD · Monitoring | 🧪 Local acceptance |

## Current Assignment

### 03 · From Notebooks to Production

Assignment 03 converts the late-delivery notebook model into a self-contained MLOps inference system. It owns its raw-data location, PostgreSQL database, six training notebooks, fitted artifacts, MLflow registry, MinIO artifact storage, FastAPI service, automated tests, Docker Compose stack, CI/CD workflow, logging, and monitoring.

The production inference path never refits preprocessing or model objects. The final local acceptance is intentionally performed from the `assignment-03` branch before any merge to `main`.

**[View Assignment 03 →](assignments/03-olist-late-delivery-mlops/)**

## Engineering Principles

- **Clarity** — project structure and intent should be easy to understand.
- **Reproducibility** — environments and results should be recreatable whenever practical.
- **Separation of concerns** — data access, validation, feature construction, preprocessing, prediction, serving, and monitoring have distinct responsibilities.
- **Data safety** — raw data, secrets, generated artifacts, and local environments are not committed as ordinary Git files.
- **Validation** — execution is verified with tests, parity checks, CI, and local end-to-end acceptance.
- **Meaningful Git history** — changes are organized into focused commits.
- **Scope discipline** — each assignment solves the released task without depending on unreleased work.

## License

This repository is licensed under the terms provided in the [`LICENSE`](LICENSE) file.

Third-party datasets, libraries, models, course materials, and other external resources remain subject to their respective licenses and terms.
