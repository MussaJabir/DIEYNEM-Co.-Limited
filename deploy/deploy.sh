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

# Recompile Tailwind from source. The output (static/css/tailwind.out.css) is
# gitignored, so it must be rebuilt on every deploy or template class changes
# would ship stale styles. Uses the standalone Tailwind CLI (no Node) installed
# at /usr/local/bin/tailwindcss — see deploy/README.md.
echo "==> Building Tailwind CSS"
if command -v tailwindcss >/dev/null 2>&1; then
    tailwindcss -i ./static/src/input.css -o ./static/css/tailwind.out.css --minify
else
    echo "ERROR: tailwindcss CLI not found — install it per deploy/README.md." >&2
    exit 1
fi

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Restarting Gunicorn"
sudo systemctl restart gunicorn-dieynem

echo "==> Deploy complete: $(git rev-parse --short HEAD)"
