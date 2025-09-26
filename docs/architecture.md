# 🏗 Architecture & Component Design

This document provides a deeper look at the system architecture, data flow, and main components of the Play Store Review & Sentiment Dashboard.

## 1. High-Level Diagram

```
                +--------------------+
                |  CSV Datasets      | (googleplaystore.csv,
                |  (raw files)       |  googleplaystore_user_reviews.csv)
                +----------+---------+
                           |
                           | cleaning (Pandas)
                           v
                +--------------------+
                |  Cleaned CSVs      |
                |  *_clean.csv       |
                +----------+---------+
                           |
                           | import_data (Django mgmt cmd)
                           v
+------------------+   +------------------+
|  App Model       |   |  Review Model    |
| (metadata)       |   | (text + sentiment)|
+---------+--------+   +---------+--------+
          |                      |
          | ORM                  | ORM
          v                      v
                +--------------------+
                |   PostgreSQL / DB  |
                +--------------------+
                           |
                           | Django Views / Queries
                           v
                +--------------------+
                |   Web Interface    |
                | (Search, Detail,   |
                |  Reviews, Admin)   |
                +--------------------+
```

## 2. Components

### a. Data Layer
- `playstore/models.py`
  - `App`: Core metadata about a Play Store application.
  - `Review`: Cleaned + imported historical reviews (plus user-submitted & moderated reviews).
  - `ReviewApproval`: Captures supervisor approval actions.
  - `UserProfile`: Extends `auth.User` with a supervisor flag.

### b. Ingestion & Cleaning
- `scripts/clean_data.py`: Functions `clean_googleplaystore` & `clean_user_reviews` applied prior to loading.
- `import_data` command performs an idempotent load—skips if any `App` exists.

### c. Application Services (Views)
- Search: TF–IDF over `App.name` (in-memory per request; upgrade path = caching or vector DB).
- App Detail: Aggregates sentiment counts of approved reviews.
- Review Submission: Auth-only; enters moderation queue.
- Supervisor Moderation: Approve pending reviews; creates `ReviewApproval` entry.

### d. Auth & Profiles
- Standard Django auth for login/logout/register.
- Profile view powered by `UserProfile` model.

### e. Deployment / Runtime
- Docker container runs Gunicorn + Postgres (compose).
- `entrypoint.sh` ensures order: wait DB → migrate → conditional data import → serve.

## 3. Data Lifecycle
| Phase | Action | Tooling |
|-------|--------|---------|
| Raw Acquisition | Store CSVs in `playstore/migrations/csv_data/` | Manual / versioned |
| Cleaning | Normalize fields, handle nulls | `scripts/clean_data.py` |
| Import | Create rows in `App` & `Review` | `python manage.py import_data` |
| User Interaction | Submit / approve reviews | Django views & templates |
| Analytics (Basic) | Sentiment tallies on detail pages | ORM queries |

## 4. Extension Points
- Replace TF–IDF with persistent vector embeddings (FAISS, PGVector, etc.).
- Add Celery for async NLP enrichment (e.g., toxicity filtering, topic modeling).
- Introduce API layer (DRF) for programmatic access.
- Add caching (Redis) for heavy search queries.
- Expand moderation with rejection reasons + audit log.

## 5. Non-Functional Considerations
| Concern | Current State | Future Improvement |
|---------|---------------|--------------------|
| Performance | In-memory TF–IDF per request | Precompute & cache matrix |
| Security | Default Django protections | Add rate limiting & CSP |
| Observability | Minimal logging | Structured logs + metrics (Prometheus) |
| Testing | Deferred (none in repo yet) | Add unit + integration + data pipeline tests |
| CI/CD | None | GitHub Actions (lint, test, build) |

## 6. Risks / Trade-offs
- In-memory search scalability limited by dataset size.
- Import idempotence relies on presence of any `App`; partial loads aren't reconciled.
- Sentiment data is static from original dataset for imported reviews.

## 7. Suggested Next Architecture Steps
1. (Future) Add a `tests/` package and begin with model + search tests.
2. Introduce `poetry` or pin dependency versions for reproducibility.
3. Feature-flag an embeddings-based semantic search prototype.
4. Add DRF endpoints for `App` list/search and review submission.

---
Feel free to extend this document with diagrams (PlantUML, Mermaid) and ADRs (Architecture Decision Records) as complexity grows.
