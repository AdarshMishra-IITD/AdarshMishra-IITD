
<div align="center">

# Play Store Review & Sentiment Dashboard

<em>Search, explore, and moderate Google Play Store app reviews with a lightweight Django + Postgres stack.</em>

<!-- Badges (placeholder examples) -->
<!--
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()
-->

</div>

## ✨ Features

- Fast fuzzy-ish search over app names (TF‑IDF + cosine similarity)
- App detail view with sentiment distribution of approved reviews
- User signup/login & role flag for supervisor moderation
- Review submission → pending approval workflow
- Idempotent CSV → DB import via custom management command
- Dockerized runtime (Gunicorn + Postgres) OR pure local dev
- Unified startup script (Docker `entrypoint.sh` supports dev & prod modes)
- Extensible model ready for future NLP enrichment (embeddings, topics)
 - Simple role elevation via Django Admin (grant Supervisor capability)

## 🧭 At a Glance

| Concern | Choice |
|---------|--------|
| Framework | Django 5.x |
| DB (default) | PostgreSQL (Docker) |
| Alt local DB | SQLite (manual tweak) |
| Frontend | Django templates |
| Search | In-memory TF‑IDF per request |
| Deployment style | Docker (Gunicorn) |

## 📂 Project Layout

```
playstore/               # Main app: models, views, urls, mgmt command
  management/commands/import_data.py
project_config/          # Project settings / wsgi / asgi
scripts/
  clean_data.py          # Data cleaning helpers
templates/               # UI templates
docs/                    # Detailed documentation
Dockerfile
docker-compose.yml
entrypoint.sh            # Container startup logic
```

More detail: `docs/code_overview.md`.

## 🧱 Architecture Flow

1. Raw CSVs in `playstore/migrations/csv_data/`
2. Cleaning functions produce normalized `_clean.csv` files
3. `import_data` loads Apps then Reviews (idempotent)
4. Users search → TF‑IDF ranks names → select app → view details
5. Auth users submit reviews (unapproved initially)
6. Supervisor approves → review becomes visible / counted

Extended breakdown: `docs/architecture.md` + data mapping: `docs/data_sources.md`.

## 🚀 Getting Started

### Option 1: Docker (Production style – Gunicorn)
```sh
docker compose up --build
```
Browse: http://localhost:8000

Rebuild fresh:
```sh
docker compose down -v
docker compose up --build
```

Exec a management command:
```sh
docker compose exec web python manage.py createsuperuser
```

### Option 2: Local Python Environment
```sh
pip install -r requirements.txt
python run.py            # will migrate + import (if needed) + runserver
```
Customizations:
```sh
python run.py --port 9001
NO_IMPORT=1 python run.py    # skip import check
RUN_HOST=0.0.0.0 RUN_PORT=8080 python run.py
```
Traditional direct commands still work if you prefer:
```sh
python manage.py migrate
python manage.py import_data
python manage.py runserver
```
Visit: http://127.0.0.1:8000 (or chosen port)

### Option 3: Docker Dev Mode (Runserver Inside Container)

Two equivalent ways:

1. Override compose file (recommended):
```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

2. Environment variables inline:
```sh
APP_MODE=dev docker compose up --build
```

Because of the auto-detect added to `entrypoint.sh`, if `APP_MODE` is unset but `DEBUG=1`, the container will also default to dev mode.

Customizations:
```sh
DEV_PORT=9001 docker compose -f docker-compose.yml -f docker-compose.dev.yml up
NO_IMPORT=1 docker compose -f docker-compose.yml -f docker-compose.dev.yml up   # skip data import
```

Browse: http://localhost:8000 (or your chosen `DEV_PORT`).

## 🗄️ Data Pipeline

| Stage | Tool/File | Notes |
|-------|-----------|-------|
| Raw ingest | `csv_data/*.csv` | Bundled demo data |
| Clean | `scripts/clean_data.py` | Normalizes values |
| Import | `manage.py import_data` | Idempotent load |
| Persist | Postgres / SQLite | ORM access |
| Present | Django views/templates | Search / detail / moderation |

## 🔐 Configuration

Environment variables (Docker or local shell):
```
DJANGO_DB_HOST, DJANGO_DB_PORT, DJANGO_DB_NAME,
DJANGO_DB_USER, DJANGO_DB_PASSWORD,
DEBUG, GUNICORN_WORKERS, GUNICORN_TIMEOUT
```
Add a `.env` for convenience (not committed). Local SQLite experimentation can be enabled by adjusting `DATABASES` in `project_config/settings.py`.

### Authentication & Login Flow

The project uses Django's built‑in auth system plus a lightweight `UserProfile` extension model to flag supervisor users.

1. Registration: Navigate to `/accounts/register/` (link often available in UI) and submit the form (username, email, password twice). Successful registration automatically logs the user in and creates a `UserProfile` with `is_supervisor = False`.
2. Login: Use `/accounts/login/` (Django's default auth view — template provided) with your credentials.
3. Profile: Visit `/accounts/profile/` to view username, email, and whether you're a supervisor. From here you can log out (`/accounts/logout/`).
4. Adding Reviews: While authenticated, open an app detail page (e.g. `/app/<id>/`) and click Add Review. Your review is stored with `approved = False` until a supervisor approves it.

URLs (subset):
```
/                -> search view
/accounts/register/  -> registration form
/accounts/login/     -> login form (Django auth)
/accounts/profile/   -> profile (requires login)
/supervisor/reviews/ -> moderation queue (supervisor only)
```

### Assigning / Managing Supervisor Role

Supervisors can approve pending reviews and their actions are audit‑logged via the `ReviewApproval` model. To grant (or revoke) supervisor status:

Option A – Django Admin (recommended):
1. Create an admin user if none exists:
  ```sh
  python manage.py createsuperuser
  ```
2. Login at `/admin/`.
3. Open User Profiles, pick the target user's profile, tick `Is supervisor`, save.

Option B – One‑off shell (quick script / emergency):
```py
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from playstore.models import UserProfile
>>> u = User.objects.get(username="alice")
>>> prof, _ = UserProfile.objects.get_or_create(user=u)
>>> prof.is_supervisor = True
>>> prof.save()
```

Option C – SQL (not advised unless debugging): directly update `playstore_userprofile.is_supervisor`.

Option D – Dedicated management command (scriptable CI / infra friendly):
```sh
python manage.py create_supervisor alice --password S3cretPwd --email alice@example.com
```
Revoke:
```sh
python manage.py create_supervisor alice --remove
```
If you omit `--password` for a new user you'll be interactively prompted (unless `--no-input` is also given, which would error for safety).

After elevation the user immediately gains access to `/supervisor/reviews/` and each approval generates a `ReviewApproval` entry linking the supervisor and the review.

Supervisor Review Flow:
1. Supervisor visits `/supervisor/reviews/`.
2. Page lists all `approved = False` reviews + aggregate sentiment counts.
3. Clicking Approve (POST to `/supervisor/review/<id>/approve/`) sets `Review.approved = True` and creates a `ReviewApproval` record.
4. Approved reviews appear on the related App detail page and in counts / sentiment distribution.

Security Notes:
- Non‑supervisors attempting to access supervisor routes are redirected to search.
- Only approved reviews are shown publicly (preventing spam / abuse exposure).
- Minimal PII stored (email only) — extend cautiously if adding more fields.

### (Planned) Screenshot Examples

Place screenshots in `docs/images/` and reference here. Suggested shots:
- Registration form
- Supervisor review queue
- App detail with sentiment distribution

Placeholder (pending capture):
`![Supervisor Queue](docs/images/supervisor_queue.png)`

## 🧪 Testing (Deferred)

No automated tests yet while core flows stabilize. Planned initial suite: models, search, review submission & approval, data import. A `tests/` package + CI (GitHub Actions) will be introduced later.

## 🧭 Common Commands

| Command | Purpose |
|---------|---------|
| `python manage.py migrate` | Apply migrations |
| `python manage.py import_data` | Load cleaned data (skips if present) |
| `python manage.py createsuperuser` | Admin user |
| `python run.py` | Local dev: migrate → import (if needed) → runserver |
| `APP_MODE=dev docker compose up` | Docker dev: migrate → import → runserver |
| `docker compose up --build` | Full Docker stack |

## 👥 Contributing

See `CONTRIBUTING.md` for workflow & guidelines (testing section future‑dated). PRs welcome for: pagination, better search, improved data normalization, or an embeddings prototype.

## 🛠️ Roadmap (Excerpt)

- Semantic embeddings search (SentenceTransformers)
- Pagination & filtering (category, rating range)
- Real-time sentiment for new reviews
- Supervisor analytics dashboard
- Test suite + CI pipeline

## 📖 Further Reading

- `docs/how_to_run.md` – Detailed run modes (Docker vs local)
- `docs/architecture.md` – Architecture & extension points
- `docs/data_sources.md` – Dataset lineage & field mappings
- `docs/code_overview.md` – File-by-file explanations

## 📄 License

Add a license file (e.g. MIT) if external reuse is intended.

## 🙋 Author

Adarsh Mishra  
📧 adarshmishraiitd@gmail.com  
Focus: Generative AI · RAG · LLM Ops · Agent systems

---

Questions? Open an issue or start a discussion. Happy hacking! 🚀
