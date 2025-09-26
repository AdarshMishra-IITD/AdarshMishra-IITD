# 🚀 How to Run This Project

This project can be run in two ways:

1. Docker (fastest, reproducible – recommended)  
2. Local Python environment (fully manual, more flexible for quick experimentation)

Docker is optional, but it gives you a production‑like stack (Postgres + Gunicorn) with one command while keeping the host environment clean. If you just want to poke around the code quickly, skip to the Local Setup section.

For deeper background, see:
- `docs/code_overview.md`
- `docs/architecture.md`
- `docs/data_sources.md`

---

## ✅ Prerequisites
| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | Project currently targets 3.12 (see Dockerfile) |
| pip | Package installation |
| (Optional) Docker & Compose | Recommended for uniform environment |

---

## 🐳 Option A: Docker Quick Start (Recommended but Optional)

### Why Docker?
- Zero local dependency juggling
- Idempotent startup: migrations + data import handled automatically
- Mirrors a more production‑ready stack (Gunicorn instead of Django dev server)
- Easy teardown: remove volumes to reset data

### Start the Stack
```sh
docker compose up --build
```
Then visit: http://localhost:8000

Behind the scenes (`entrypoint.sh`):
1. Waits for database
2. Runs migrations
3. Imports seed data if no apps exist
4. Launches Gunicorn

### Common Tasks
Run a Django management command inside the container:
```sh
docker compose exec web python manage.py createsuperuser
```

Open a Django shell:
```sh
docker compose exec web python manage.py shell
```

Rebuild from scratch (wipe data):
```sh
docker compose down -v
docker compose up --build
```

### Environment Overrides
Adjust (or add) in `docker-compose.yml`:
- `GUNICORN_WORKERS`
- `GUNICORN_TIMEOUT`
- DB credentials (if pointing to an external Postgres)

---

## 🐍 Option B: Local (Python Environment)

### 1. Clone the Repository
```sh
git clone <repo-url>
cd AdarshMishra-IITD
```

### 2. Create & Activate Virtual Environment
```sh
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  (macOS/Linux)
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` (optional enhancement) or export env vars directly. For local experimentation you can keep defaults from `settings.py` (Postgres) or temporarily adapt to SQLite.

### 5. Database Setup
If you have Postgres running, ensure credentials match. Otherwise you may switch to SQLite by modifying `DATABASES` or exporting a custom settings module.
```sh
python manage.py migrate
```

### 6. Import Seed Data (Idempotent)
CSV files already reside in `playstore/migrations/csv_data/`.
```sh
python manage.py import_data
```
If apps already exist you'll see a skip notice.

### 7. Run Development Server
```sh
python manage.py runserver
```
Open http://127.0.0.1:8000

### (Alternative) Cross-Platform Helper (Python)
Use the new `run.py` script for an OS‑independent workflow (Windows / macOS / Linux):
```sh
python run.py           # migrate + import (if needed) + runserver
```
Customizations:
```sh
python run.py --port 9001
python run.py --host 0.0.0.0
NO_IMPORT=1 python run.py    # skip seed import
```
Environment variable overrides (if flags not supplied): `RUN_HOST`, `RUN_PORT`, `NO_IMPORT=1`.

Docker development mode (inside container, autoreload) still available:
```sh
APP_MODE=dev docker compose up --build
```
Custom dev container options:
```sh
APP_MODE=dev DEV_PORT=9001 NO_IMPORT=1 docker compose up
```
Then visit: http://localhost:9001

### 8. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```

---

## 🔁 Choosing Between Docker & Local
| Scenario | Use Docker | Use Local |
|----------|------------|-----------|
| Quick evaluation | ✅ (one command) | ✅ |
| Editing core Python only | ✅ | ✅ |
| Swapping DB engines | ✅ (adjust compose) | ✅ (edit settings) |
| Reproducible team onboarding | ✅ | ❌ (env drift risk) |
| Debugging library issues | ❌ (slower rebuild) | ✅ |

You can seamlessly switch: data imported via Docker is independent of any local SQLite experiment.

---

## 🔄 Data Refresh
To force a fresh import:
1. Flush DB (local):
	```sh
	python manage.py flush --noinput
	python manage.py import_data
	```
2. Docker approach (volume reset):
	```sh
	docker compose down -v
	docker compose up --build
	```

---

## 🧪 Run Tests (Deferred)
Automated tests have not been added yet. This section will be updated once an initial `tests/` package is introduced.

---

## 🔐 Authentication Flow
1. Register via /accounts/register/ (auto login after success)
2. View profile at /accounts/profile/
3. Submit a review on an app detail page (pending until supervisor approval)
4. Supervisor (user with `UserProfile.is_supervisor=True`) approves via the moderation dashboard

---

## 📚 Need Help?
Open an issue or check other docs in the `docs/` directory.

Happy building! 🚀
