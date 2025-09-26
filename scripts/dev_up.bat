@echo off
REM dev_up.bat - Convenience script for local (non-Docker) startup on Windows.
REM 1. Applies migrations
REM 2. Optionally imports data if no App rows exist
REM 3. Starts Django dev server on specified host/port
REM
REM Usage:
REM   scripts\dev_up.bat
REM   set PORT=9000 && scripts\dev_up.bat
REM   set NO_IMPORT=1 && scripts\dev_up.bat
REM
REM Environment Variables:
REM   HOST (default 127.0.0.1)
REM   PORT (default 8000)
REM   NO_IMPORT=1  -> Skip import_data logic

setlocal ENABLEDELAYEDEXPANSION

IF NOT EXIST manage.py (
  echo [ERROR] Run this script from the project root (manage.py not found).
  exit /b 1
)

IF "%HOST%"=="" set HOST=127.0.0.1
IF "%PORT%"=="" set PORT=8000

echo [dev_up] Applying migrations...
python manage.py migrate --noinput

IF NOT "%NO_IMPORT%"=="1" (
  echo [dev_up] Checking if initial data import is needed...
  python - <<PYCODE
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','project_config.settings')
django.setup()
from playstore.models import App
import sys
sys.exit(0 if App.objects.exists() else 1)
PYCODE
  IF %ERRORLEVEL%==0 (
    echo [dev_up] Data already present – skipping import_data.
  ) ELSE (
    echo [dev_up] Running import_data (idempotent).
    python manage.py import_data || echo [dev_up][WARN] import_data failed; continuing without seed data.
  )
) ELSE (
  echo [dev_up] NO_IMPORT=1 set – skipping data import check.
)

echo [dev_up] Starting Django development server at http://%HOST%:%PORT%
python manage.py runserver %HOST%:%PORT%
