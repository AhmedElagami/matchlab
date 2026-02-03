#!/bin/bash
set -euo pipefail

cd /home/ubuntu/matchlab

echo "[B] Wiping DB (docker compose down -v)"
docker compose -f docker-compose.dev.yml down -v

echo "[B] Starting services"
docker compose -f docker-compose.dev.yml up -d

echo "[B] Waiting for DB"
sleep 8

echo "[B] Running migrations"
docker compose -f docker-compose.dev.yml exec app python manage.py migrate

echo "[B] Ensuring admin user"
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@example.com','admin123'); print('admin_ready', User.objects.filter(username='admin').exists())"

echo "[B] Loading fixtures"
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_not_ready.json
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_ready.json

echo "[B] Verifying seed counts"
docker compose -f docker-compose.dev.yml exec -T db psql -U matchlab -d matchlab -c "select count(*) as cohorts from core_cohort;" -c "select count(*) as participants from core_participant;" -c "select count(*) as preferences from matching_preference;" -c "select count(*) as users from auth_user;"

echo "[B] Reseed complete"
