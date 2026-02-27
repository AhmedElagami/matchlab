#!/bin/bash

# MatchLab Testing Environment Reset Script
# Resets database and prepares clean environment for testing

echo "=== MatchLab Testing Environment Reset ==="

# Confirm reset action
echo "WARNING: This will DELETE ALL DATA and reset to a clean state!"
read -p "Are you sure you want to proceed? (yes/no): " confirmation

if [[ ! "$confirmation" =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

echo ""
echo "1. Stopping Docker services..."
cd /home/ubuntu/matchlab
docker compose -f docker-compose.dev.yml down -v

if [ $? -eq 0 ]; then
    echo "✅ Docker services stopped and volumes removed"
else
    echo "❌ Failed to stop Docker services"
    exit 1
fi

echo ""
echo "2. Starting fresh Docker services..."
docker compose -f docker-compose.dev.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ Docker services started"
else
    echo "❌ Failed to start Docker services"
    exit 1
fi

echo ""
echo "3. Waiting for database to be ready..."
sleep 10

echo ""
echo "4. Running migrations..."
docker compose -f docker-compose.dev.yml exec app python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Database migrations applied"
else
    echo "❌ Failed to apply migrations"
    exit 1
fi

echo ""
echo "5. Creating admin user..."
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin / admin123')
else:
    print('Admin user already exists')
"

if [ $? -eq 0 ]; then
    echo "✅ Admin user ready"
else
    echo "❌ Failed to create admin user"
    exit 1
fi

echo ""
echo "6. Verifying clean state..."
cd /home/ubuntu/matchlab && docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from apps.core.models import Cohort, Participant
from apps.matching.models import MatchRun, Match
from django.contrib.auth.models import User
print('=== Clean State Verification ===')
print(f'Users: {User.objects.count()} (should be 1 for admin)')
print(f'Cohorts: {Cohort.objects.count()} (should be 0)')
print(f'Participants: {Participant.objects.count()} (should be 0)')
print(f'MatchRuns: {MatchRun.objects.count()} (should be 0)')
print(f'Matches: {Match.objects.count()} (should be 0)')
"

echo ""
echo "=== Environment Reset Complete ==="
echo "✅ Clean testing environment ready"
echo ""
echo "Next steps:"
echo "1. Each tester should generate their required datasets"
echo "2. Load datasets using: docker compose -f docker-compose.dev.yml exec app python manage.py loaddata <dataset.json>"
echo "3. Begin testing with clean, reproducible data"