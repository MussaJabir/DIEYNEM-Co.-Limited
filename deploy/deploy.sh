#!/usr/bin/env bash
#
# DIEYNEM production deploy. Run on the server — by CI over SSH on every merge
# to main, or by hand:  bash deploy/deploy.sh
#
# Pulls main, installs deps, migrates, collects static, restarts Gunicorn.
# Idempotent and safe to re-run. Content is (re)seeded automatically by the
# data migrations, so no separate seed step is needed.

set -euo pipefail
export DJANGO_SETTINGS_MODULE=config.settings.prod

# Move to the repository root regardless of where this script is invoked from.
REPO_ROOT="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Fetching latest main"
git fetch --prune origin
git reset --hard origin/main

echo "==> Installing dependencies"
# shellcheck disable=SC1091
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Applying database migrations (also seeds verified content)"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Restarting Gunicorn"
sudo systemctl restart gunicorn-dieynem

echo "==> Deploy complete: $(git rev-parse --short HEAD)"
