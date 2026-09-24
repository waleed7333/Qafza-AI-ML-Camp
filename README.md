<div align="center">

# Qafza AI & Machine Learning Camp

**Assignments · Applied Machine Learning · Deep Learning · MLOps**

A structured collection of hands-on assignments and engineering projects completed throughout the **Qafza AI & Machine Learning Camp**.

</div>

---

## About

This repository documents my practical work throughout the **Qafza AI & Machine Learning Camp**, with a focus on building reliable, reproducible, and well-documented AI/ML systems.

The repository follows the **actual assignments delivered during the program** rather than a predefined weekly sequence. Each assignment is maintained as a self-contained project with its own documentation, environment-specific configuration, implementation files, and project-specific data policy.

The goal is not only to complete the required tasks, but also to apply sound engineering practices while progressing through the AI/ML and MLOps lifecycle.

---

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

Each assignment has its own structure based on its technical requirements. No fixed template is imposed when it does not serve the assignment.

Assignment 03 remains in the same repository but is runtime-isolated from Assignments 01 and 02.

---

## Assignments

| # | Assignment | Focus | Status |
|---:|---|---|:---:|
| 01 | [Olist Database Ingestion](assignments/01-olist-database-ingestion/) | PostgreSQL · Docker · Python · SQL · Data Ingestion | ✅ Completed |
| 02 | [Olist Late Delivery ML](assignments/02-olist-late-delivery-ml/) | Notebooks · EDA · Feature Engineering · Classification · Evaluation | ✅ Completed |
| 03 | [From Notebooks to Production](assignments/03-olist-late-delivery-mlops/) | FastAPI · DVC · Great Expectations · MLflow · Docker · CI/CD · Monitoring | 🧪 Local acceptance |

The assignments table grows as new tasks are released during the camp.

---

## Current Assignment

### 03 · From Notebooks to Production

Assignment 03 converts the late-delivery notebook model into a self-contained MLOps inference system. It owns its raw-data location, PostgreSQL database, six training notebooks, fitted artifacts, MLflow registry, MinIO artifact storage, FastAPI service, automated tests, Docker Compose stack, CI/CD workflow, logging, and monitoring.

The production inference path never refits preprocessing or model objects. Final local acceptance is intentionally completed on the `assignment-03` branch before merge to `main`.

**[View Assignment 03 →](assignments/03-olist-late-delivery-mlops/)**

---

## Areas of Practice

Work throughout the camp may cover areas such as:

- Machine Learning
- Deep Learning
- Data Processing
- Relational Data Modeling
- Feature Engineering
- Model Development
- Model Evaluation
- APIs and Model Serving
- Containerization
- Data and Model Versioning
- Experiment Tracking
- Monitoring and Automation
- MLOps
- Production-oriented ML Engineering

The exact sequence follows the assignments and practical work delivered during the program.

---

## Engineering Principles

Projects in this repository aim to follow a consistent set of engineering principles:

- **Clarity** — project structure and intent should be easy to understand.
- **Reproducibility** — another developer should be able to recreate the environment and results whenever practical.
- **Separation of concerns** — data access, validation, feature construction, preprocessing, prediction, serving, and monitoring have distinct responsibilities.
- **Data safety** — generated files, local datasets, credentials, secrets, and temporary artifacts remain outside ordinary Git version control when appropriate.
- **Validation** — successful execution is verified with tests, parity checks, CI, and local end-to-end acceptance.
- **Meaningful Git history** — changes are organized into clear, intentional commits.
- **Scope discipline** — assignments solve the released task without depending on unreleased work or unrelated projects.
- **Technical documentation** — important decisions, assumptions, limitations, and operational procedures are documented alongside the implementation.

---

## License

This repository is licensed under the terms provided in the [`LICENSE`](LICENSE) file.

Third-party datasets, libraries, models, course materials, and other external resources remain subject to their respective licenses and terms.
