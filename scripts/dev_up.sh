#!/usr/bin/env bash
set -euo pipefail

# dev_up.sh - Convenience script for local (non-Docker) startup.
# 1. Applies migrations
# 2. Optionally imports data if no App rows exist
# 3. Starts Django dev server on specified host/port
#
# Usage:
#   ./scripts/dev_up.sh              # defaults
#   PORT=9000 ./scripts/dev_up.sh    # custom port
#   NO_IMPORT=1 ./scripts/dev_up.sh  # skip data import check
#
# Environment Variables:
#   HOST (default 127.0.0.1)
#   PORT (default 8000)
#   NO_IMPORT=1  -> Skip import_data logic
#
# Requirements: run from project root (where manage.py lives)

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if [ ! -f manage.py ]; then
  echo "[ERROR] Run this script from the project root (manage.py not found)." >&2
  exit 1
fi

echo "[dev_up] Applying migrations..."
python manage.py migrate --noinput

if [ "${NO_IMPORT:-0}" != "1" ]; then
  echo "[dev_up] Checking if initial data import is needed..."
  if python - <<'PYCODE'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','project_config.settings')
django.setup()
from playstore.models import App
import sys
sys.exit(0 if App.objects.exists() else 1)
PYCODE
  then
    echo "[dev_up] Data already present – skipping import_data."
  else
    echo "[dev_up] Running import_data (idempotent)."
    if ! python manage.py import_data; then
      echo "[dev_up][WARN] import_data failed; continuing without seed data." >&2
    fi
  fi
else
  echo "[dev_up] NO_IMPORT=1 set – skipping data import check."
fi

echo "[dev_up] Starting Django development server at http://${HOST}:${PORT}"
exec python manage.py runserver ${HOST}:${PORT}
