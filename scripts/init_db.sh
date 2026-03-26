#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Running migrations..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py migrate

echo "Ensuring admin user exists..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py shell -c "from django.contrib.auth.models import User; admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'}); admin.email = 'admin@example.com'; admin.is_staff = True; admin.is_superuser = True; admin.is_active = True; admin.set_password('admin123'); admin.save(); print('Admin ready: admin / admin123')"
