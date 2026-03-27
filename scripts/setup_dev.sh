#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

COMPOSE="docker compose -f docker-compose.dev.yml"

echo "=== MatchLab Dev Setup ==="
echo ""

# Step 1: Start services
echo "[1/4] Starting Docker services..."
$COMPOSE up -d
echo "  ✓ Services started"

# Step 2: Wait for Postgres
echo "[2/4] Waiting for database..."
for i in $(seq 1 15); do
    if $COMPOSE exec -T db pg_isready -U matchlab > /dev/null 2>&1; then
        echo "  ✓ Database ready"
        break
    fi
    if [ "$i" -eq 15 ]; then
        echo "  ✗ Database not ready after 15s"
        exit 1
    fi
    sleep 1
done

# Step 3: Migrations + admin user
echo "[3/4] Running migrations and creating admin user..."
$COMPOSE exec -T app python manage.py migrate --noinput
$COMPOSE exec -T app python manage.py shell -c "
from django.contrib.auth.models import User
admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
admin.email = 'admin@example.com'
admin.is_staff = True
admin.is_superuser = True
admin.is_active = True
admin.set_password('admin123')
admin.save()
print('  ✓ Admin ready: admin / admin123')
"

# Step 4: Load default fixture
FIXTURE="${1:-fixtures/cohort_5x5_ready.json}"
echo "[4/4] Loading fixture: $FIXTURE"
$COMPOSE exec -T app python manage.py flush --noinput
$COMPOSE exec -T app python manage.py migrate --noinput
$COMPOSE exec -T app python manage.py loaddata "$FIXTURE"
$COMPOSE exec -T app python manage.py shell < scripts/set_fixture_passwords.py
echo "  ✓ Fixture loaded"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "  App:   http://localhost:8001/auth/login/"
echo "  Admin: admin / admin123"
echo "  Users: testpass123 (all fixture users)"
echo ""
echo "Available fixtures:"
echo "  bash scripts/setup_dev.sh fixtures/cohort_3x3.json"
echo "  bash scripts/setup_dev.sh fixtures/cohort_5x5_ready.json (default)"
echo "  bash scripts/setup_dev.sh fixtures/cohort_5x5_not_ready.json"
echo "  bash scripts/setup_dev.sh fixtures/manual_exception_e1e2.json"
echo "  bash scripts/setup_dev.sh fixtures/manual_exception_e3.json"
echo "  bash scripts/setup_dev.sh fixtures/manual_multi_cohort.json"
echo "  bash scripts/setup_dev.sh fixtures/manual_profiles_scoring.json"
