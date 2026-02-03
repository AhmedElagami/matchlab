#!/bin/bash
set -euo pipefail

cd /home/ubuntu/matchlab

printf "yes\n" | ./scripts/reset_testing_env.sh

docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_3x3.json
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_ready.json
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_not_ready.json

docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from django.contrib.auth.models import User;\nif not User.objects.filter(username='admin').exists():\n    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')\n\nfor username in ['mentor1','mentee1']:\n    u=User.objects.get(username=username); u.set_password('test123'); u.save()"

docker compose -f docker-compose.dev.yml exec db psql -U matchlab -d matchlab -c "SELECT 'users' AS table, COUNT(*) FROM auth_user UNION ALL SELECT 'cohorts', COUNT(*) FROM core_cohort UNION ALL SELECT 'participants', COUNT(*) FROM core_participant UNION ALL SELECT 'preferences', COUNT(*) FROM matching_preference;"
