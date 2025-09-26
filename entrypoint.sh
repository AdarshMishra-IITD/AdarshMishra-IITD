#!/bin/sh
set -euo pipefail

# Unified entrypoint script for both Docker production-like usage (Gunicorn)
# and optional local development (Django runserver) to eliminate duplicate scripts.
#
# Modes (set APP_MODE):
#   prod (default) -> Gunicorn server (expects Postgres via env vars)
#   dev            -> Django runserver with auto-reload for quick iteration
#
# Environment Variables:
#   APP_MODE=prod|dev
#   DJANGO_DB_HOST / DJANGO_DB_PORT / credentials (for database wait logic)
#   GUNICORN_WORKERS (prod) default 3
#   GUNICORN_TIMEOUT (prod) default 120
#   DEV_HOST (dev) default 127.0.0.1
#   DEV_PORT (dev) default 8000
#   NO_IMPORT=1 -> skip initial data import check (both modes)
#
# Exit on error, treat unset vars as error, and fail on pipeline errors.

APP_MODE="${APP_MODE:-}"
if [ -z "$APP_MODE" ]; then
  # If not explicitly set, infer from DEBUG (common in docker-compose dev usage)
  if [ "${DEBUG:-0}" = "1" ]; then
    APP_MODE=dev
    echo "[entrypoint] APP_MODE not set; DEBUG=1 -> using dev mode"
  else
    APP_MODE=prod
  fi
fi
## In a container we almost always want to listen on 0.0.0.0 so the port mapping works.
## If someone really wants 127.0.0.1 they can still override DEV_HOST explicitly.
DEV_HOST="${DEV_HOST:-0.0.0.0}"
DEV_PORT="${DEV_PORT:-8000}"

echo "[entrypoint] Starting in mode: $APP_MODE"

# Function: wait for database if host provided (supports both modes)
wait_for_db() {
  if [ -n "${DJANGO_DB_HOST:-}" ]; then
    echo "[entrypoint] Waiting for database ${DJANGO_DB_HOST}:${DJANGO_DB_PORT:-5432} ..."
    until nc -z "$DJANGO_DB_HOST" "${DJANGO_DB_PORT:-5432}"; do
      sleep 1
    done
    echo "[entrypoint] Database is up."
  else
    echo "[entrypoint] No DJANGO_DB_HOST specified; skipping DB wait."
  fi
}

apply_migrations() {
  echo "[entrypoint] Applying migrations..."
  python manage.py migrate --noinput
}

maybe_import_data() {
  if [ "${NO_IMPORT:-0}" = "1" ]; then
    echo "[entrypoint] NO_IMPORT=1 set – skipping data import check."
    return 0
  fi
  if python - <<'PYCODE'
import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','project_config.settings')
django.setup()
from playstore.models import App
sys.exit(0 if App.objects.exists() else 1)
PYCODE
  then
    echo "[entrypoint] Data already present – skipping import_data."
  else
    echo "[entrypoint] Running import_data (idempotent)."
    python manage.py import_data || echo "[entrypoint][WARN] import_data failed (non-fatal)"
  fi
}

run_dev() {
  # For usability: if binding to 0.0.0.0 (inside container), display 127.0.0.1 so host users can click it.
  if [ "$DEV_HOST" = "0.0.0.0" ]; then
    DISPLAY_HOST="127.0.0.1"
  else
    DISPLAY_HOST="$DEV_HOST"
  fi
  echo "[entrypoint] Launching Django development server at http://${DISPLAY_HOST}:${DEV_PORT} (binding ${DEV_HOST}:${DEV_PORT})"
  exec python manage.py runserver "${DEV_HOST}:${DEV_PORT}"
}

run_prod() {
  echo "[entrypoint] Starting Gunicorn..."
  exec gunicorn project_config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}"
}

wait_for_db
apply_migrations
maybe_import_data

case "$APP_MODE" in
  dev)
    run_dev
    ;;
  prod|production)
    run_prod
    ;;
  *)
    echo "[entrypoint][ERROR] Unknown APP_MODE='$APP_MODE' (expected dev or prod)" >&2
    exit 1
    ;;
esac
