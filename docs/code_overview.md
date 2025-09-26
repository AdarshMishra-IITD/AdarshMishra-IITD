# 📦 Code Overview

This document explains the structure and purpose of each major file and folder in the project.

## Project Structure

- `playstore/` — Main Django app containing models, views, URLs, migrations, and management commands.
  - `models.py` — Defines the database models for apps and reviews.
  - `views.py` — Contains logic for handling web requests and rendering templates.
  - `urls.py` — URL routing for the app.
  - `migrations/` — Database migration files and `csv_data/` for raw and cleaned CSVs.
  - `management/commands/import_data.py` — Custom Django command to clean and import data from CSVs into the database.
- `project_config/` — Django project configuration (settings, URLs, WSGI/ASGI entry points).
- `scripts/clean_data.py` — Standalone script for robust cleaning of raw CSV data.
- `templates/` — HTML templates for rendering web pages.
- `.env` — Environment variables (e.g., secret key, debug mode).
- `requirements.txt` — Python dependencies for the project.
- `db.sqlite3` — SQLite database file (local development).

## Key Code Components

### Data Cleaning (`scripts/clean_data.py`)
- Cleans and preprocesses raw Google Play Store CSV data.
- Handles missing values, normalizes formats, and outputs cleaned CSVs.

### Data Import (`playstore/management/commands/import_data.py`)
- Cleans data (using the script above) and loads it into Django models.
- Can be run with `python manage.py import_data`.

### Django Models (`playstore/models.py`)
- `App` — Represents a Play Store app (name, category, rating, etc.).
- `Review` — Represents a user review (linked to an app and user).

### Views & Templates
- Handle search, app detail, review submission, and user authentication.

### Project Config (`project_config/`)
- `settings.py` — Django settings (database, installed apps, etc.).
- `urls.py` — Project-level URL routing.

---

For more details, see the inline comments in each file or ask for a specific code walkthrough! 🚀
