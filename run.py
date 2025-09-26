#!/usr/bin/env python3
"""Cross-platform project runner.

Features:
  * Applies migrations
  * Optionally imports seed data if no App rows exist
  * Starts Django development server (autoreload)

Usage examples:
  python run.py                 # default 127.0.0.1:8000
  python run.py --port 9001     # custom port
  python run.py --skip-import   # skip data import check
  python run.py --host 0.0.0.0  # listen on all interfaces

Environment alternative (overrides CLI defaults if CLI arg not provided):
  RUN_HOST, RUN_PORT, NO_IMPORT=1

Exit codes:
  0 success
  1 generic failure
  2 argument error
"""
from __future__ import annotations
import argparse
import os
import sys
import textwrap

# Ensure project root (where manage.py resides)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(os.path.join(PROJECT_ROOT, 'manage.py')):
    print('[runner][ERROR] manage.py not found in project root.', file=sys.stderr)
    sys.exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')

# Hardcode database backend for this runner. This overrides any shell/env setting.
# Change to 'postgres' (and ensure a server is running) when you want to use Postgres.
os.environ['DJANGO_DB_BACKEND'] = 'sqlite'

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='python run.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Django helper runner (cross-platform)'
    )
    parser.add_argument('--host', default=os.environ.get('RUN_HOST', '127.0.0.1'), help='Host interface (default 127.0.0.1)')
    parser.add_argument('--port', default=os.environ.get('RUN_PORT', '8000'), help='Port (default 8000)')
    parser.add_argument('--skip-import', action='store_true', default=os.environ.get('NO_IMPORT') == '1', help='Skip seed data import check')
    parser.add_argument('--no-migrate', action='store_true', help='Skip applying migrations')
    return parser.parse_args()

def apply_migrations(args: argparse.Namespace) -> None:
    if args.no_migrate:
        print('[runner] Skipping migrations (--no-migrate).')
        return
    print('[runner] Applying migrations...')
    call_command('migrate', interactive=False, verbosity=1)

def maybe_import_data(args: argparse.Namespace) -> None:
    if args.skip_import:
        print('[runner] Skipping data import check (--skip-import).')
        return
    print('[runner] Checking for existing App rows...')
    from playstore.models import App  # local import after Django setup
    if App.objects.exists():
        print('[runner] Data already present; not importing.')
        return
    print('[runner] Running import_data (idempotent).')
    try:
        call_command('import_data')
    except Exception as e:  # noqa: BLE001
        print(f'[runner][WARN] import_data failed (non-fatal): {e}', file=sys.stderr)


def main() -> int:
    args = parse_args()
    print(f"[runner] Host={args.host} Port={args.port} SkipImport={args.skip_import} NoMigrate={args.no_migrate}")
    django.setup()
    apply_migrations(args)
    maybe_import_data(args)
    print(f"[runner] Starting Django dev server at http://{args.host}:{args.port}")
    call_command('runserver', f'{args.host}:{args.port}')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('\n[runner] Interrupted by user.')
        raise SystemExit(130)
