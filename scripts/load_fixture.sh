#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: scripts/load_fixture.sh <fixture_path>"
  echo "Example: scripts/load_fixture.sh fixtures/cohort_5x5_ready.json"
  exit 1
fi

FIXTURE_PATH="$1"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [ ! -f "$FIXTURE_PATH" ]; then
  echo "Fixture not found: $FIXTURE_PATH"
  exit 1
fi

echo "Flushing database..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py flush --noinput

echo "Running migrations..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py migrate

echo "Loading fixture: $FIXTURE_PATH"
docker compose -f docker-compose.dev.yml exec -T app python manage.py loaddata "$FIXTURE_PATH"

echo "Setting passwords for fixture users..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py shell < scripts/set_fixture_passwords.py
