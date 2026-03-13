#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Flushing database..."
docker compose -f docker-compose.dev.yml exec app python manage.py flush --no-input

echo "Running migrations..."
docker compose -f docker-compose.dev.yml exec app python manage.py migrate

echo "Loading fixture: fixtures/test_3x3_realistic.json"
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/test_3x3_realistic.json

echo "Setting passwords for fixture users..."
docker compose -f docker-compose.dev.yml exec app python manage.py shell <<EOF
from django.contrib.auth.models import User
users = User.objects.filter(username__in=['sarah.johnson', 'michael.chen', 'emily.rodriguez', 'david.kim', 'jessica.patel', 'alex.thompson'])
for user in users:
    user.set_password('testpass123')
    user.save()
print(f"Updated {users.count()} fixture users to testpass123")
EOF

echo "Ensuring admin user exists..."
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/admin_user.json

echo ""
echo "Admin ready: admin / admin123"
