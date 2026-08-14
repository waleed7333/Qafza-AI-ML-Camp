<div align="center">

# Qafza AI & Machine Learning Camp

**Assignments · Applied Machine Learning · Deep Learning · MLOps**

A structured collection of hands-on assignments and engineering projects completed throughout the **Qafza AI & Machine Learning Camp**.

</div>

---

## About

This repository documents my practical work throughout the **Qafza AI & Machine Learning Camp**, with a focus on building reliable, reproducible, and well-documented AI/ML systems.

The repository follows the **actual assignments delivered during the program** rather than a predefined weekly sequence. Each assignment is maintained as a self-contained project with its own documentation, environment-specific configuration, implementation files, and project-specific `.gitignore`.

The goal is not only to complete the required tasks, but also to apply sound engineering practices while progressing through the AI/ML and MLOps lifecycle.

---

## Repository Structure

```text
Qafza-AI-ML-Camp/
│
├── README.md
├── LICENSE
│
└── assignments/
    │
    └── 01-olist-database-ingestion/
        ├── README.md
        ├── .gitignore
        ├── .env.example
        ├── docker-compose.yml
        ├── requirements.txt
        │
        ├── data/
        │   └── README.md
        │
        ├── docs/
        │   └── data-model.md
        │
        ├── scripts/
        │   ├── db.py
        │   ├── ingest.py
        │   ├── profile_data.py
        │   └── validate.py
        │
        └── sql/
            ├── schema.sql
            ├── smoke_tests.sql
            └── relationship_checks.sql
```

Each assignment has its own structure based on its technical requirements. No fixed template is imposed when it does not serve the assignment.

---

## Assignments

| # | Assignment | Focus | Status |
|---:|---|---|:---:|
| 01 | [Olist Database Ingestion](assignments/01-olist-database-ingestion/) | PostgreSQL · Docker · Python · SQL · Data Ingestion | ✅ Completed |

The assignments table will grow as new tasks are released during the camp.

---

## Current Assignment

### 01 · Olist Database Ingestion

The first assignment establishes the relational data foundation for the **Brazilian E-Commerce Public Dataset by Olist**.

The project takes nine raw CSV files and builds a reproducible local PostgreSQL environment with:

- Dockerized PostgreSQL
- Explicit relational schema design
- Reproducible bulk data ingestion
- Structural source-data profiling
- Source-to-database row-count validation
- Candidate-key and relationship checks
- SQL smoke tests
- Real JOIN verification
- Technical documentation of the data model

The raw dataset itself is intentionally excluded from version control.

**[View Assignment 01 →](assignments/01-olist-database-ingestion/)**

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
- **Separation of concerns** — raw data, configuration, implementation, validation, and documentation have distinct responsibilities.
- **Data safety** — generated files, local datasets, credentials, and temporary artifacts remain outside version control when appropriate.
- **Validation** — successful execution should be verified rather than assumed.
- **Meaningful Git history** — changes should be organized into clear, intentional commits.
- **Scope discipline** — assignments should solve the required problem without unnecessary tooling or artificial complexity.
- **Technical documentation** — important decisions, assumptions, relationships, and limitations should be documented alongside the implementation.

---

## License

This repository is licensed under the terms provided in the [`LICENSE`](LICENSE) file.

Third-party datasets, libraries, models, course materials, and other external resources remain subject to their respective licenses and terms.
