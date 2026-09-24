<div align="center">

# Qafza AI & Machine Learning Camp

**Assignments · Applied Machine Learning · Deep Learning · MLOps**

A structured collection of hands-on assignments and engineering projects completed throughout the **Qafza AI & Machine Learning Camp**.

</div>

---

## About

This repository documents my practical work throughout the **Qafza AI & Machine Learning Camp**, with a focus on building reliable, reproducible, and well-documented AI/ML systems.

The repository follows the **actual assignments delivered during the program** rather than a predefined weekly sequence. Each assignment is maintained as a self-contained project with its own documentation, dependencies, configuration, implementation files, tests, and data policy.

The goal is not only to complete the required tasks, but also to apply sound engineering practices while progressing through the AI/ML and MLOps lifecycle.

---

## Repository Structure

```text
Qafza-AI-ML-Camp/
├── .github/
│   └── workflows/
├── assignments/
│   ├── 01-olist-database-ingestion/
│   ├── 02-olist-late-delivery-ml/
│   └── 03-olist-late-delivery-mlops/
├── LICENSE
└── README.md
```

Each assignment has its own structure based on its technical requirements. No fixed template is imposed when it does not serve the assignment, and later assignments do not rewrite the runtime boundaries of earlier ones.

---

## Assignments

| # | Assignment | Focus | Status |
|---:|---|---|:---:|
| 01 | [Olist Database Ingestion](assignments/01-olist-database-ingestion/) | PostgreSQL · Docker · Python · SQL · Data Ingestion | ✅ Completed |
| 02 | [Olist Late Delivery ML](assignments/02-olist-late-delivery-ml/) | Notebooks · EDA · Feature Engineering · Classification · Evaluation | ✅ Completed |
| 03 | [From Notebooks to Production](assignments/03-olist-late-delivery-mlops/) | FastAPI · DVC · Great Expectations · MLflow · Docker · CI/CD · Monitoring | ✅ Completed |

The table grows as new assignments are released during the camp. Each assignment README contains its own setup, implementation details, results, and limitations.

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
- **Reproducibility** — another developer should be able to recreate environments and results whenever practical.
- **Separation of concerns** — data, configuration, implementation, validation, serving, and documentation have distinct responsibilities.
- **Data safety** — local datasets, generated artifacts, credentials, secrets, caches, and runtime logs remain outside ordinary Git version control when appropriate.
- **Validation** — successful execution is verified with automated checks and assignment-specific acceptance evidence rather than assumed.
- **Meaningful Git history** — changes are organized into clear, intentional commits.
- **Scope discipline** — each assignment solves the released task without depending on unrelated projects or unreleased work.
- **Technical documentation** — important decisions, assumptions, limitations, and operational procedures are documented alongside the implementation.

---

## License

This repository is licensed under the terms provided in the [`LICENSE`](LICENSE) file.

Third-party datasets, libraries, models, course materials, and other external resources remain subject to their respective licenses and terms.
