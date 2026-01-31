#!/bin/bash

echo "=== MatchLab Tester B Environment Verification ==="

echo "1. Checking Docker containers..."
docker compose -f docker-compose.dev.yml ps | grep -E "(app|db)" | grep "Up"

if [ $? -eq 0 ]; then
    echo "✅ Docker containers are running"
else
    echo "❌ Docker containers are not running"
    exit 1
fi

echo ""
echo "2. Checking application availability..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auth/login/ | grep -q "200"

if [ $? -eq 0 ]; then
    echo "✅ Application is accessible"
else
    echo "❌ Application is not accessible"
    exit 1
fi

echo ""
echo "3. Checking admin user..."
cd /home/ubuntu/matchlab && docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.filter(username='admin', is_superuser=True); print('Admin user exists:', u.exists())" 2>/dev/null | grep -q "True"

if [ $? -eq 0 ]; then
    echo "✅ Admin user exists"
else
    echo "❌ Admin user not found"
    exit 1
fi

echo ""
echo "4. Checking test users for Tester B..."
cd /home/ubuntu/matchlab && docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from django.contrib.auth.models import User; print('Test users:', User.objects.filter(username__in=['mentor21', 'mentee21']).count())" 2>/dev/null | grep -q "2"

if [ $? -eq 0 ]; then
    echo "✅ Test users exist"
else
    echo "❌ Test users not found"
    exit 1
fi

echo ""
echo "5. Checking cohort data for Tester B..."
cd /home/ubuntu/matchlab && docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.core.models import Cohort; print('Cohorts:', Cohort.objects.count())" 2>/dev/null | grep -q "[1-9]"

if [ $? -eq 0 ]; then
    echo "✅ Cohort data loaded"
else
    echo "❌ No cohort data found"
    exit 1
fi

echo ""
echo "6. Verifying Cohort 3 (Test Cohort 5x5 Not Ready)..."
cd /home/ubuntu/matchlab && docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.core.models import Cohort, Participant; c = Cohort.objects.get(id=3); participants = Participant.objects.filter(cohort=c); print(f'Cohort 3 has {participants.count()} participants')" 2>/dev/null | grep -q "10"

if [ $? -eq 0 ]; then
    echo "✅ Cohort 3 available with 10 participants"
else
    echo "❌ Cohort 3 not properly loaded"
    exit 1
fi

echo ""
echo "=== Environment Verification Complete ==="
echo "✅ All systems ready for Tester B"
echo ""
echo "Next steps:"
echo "1. Review documentation in docs/testing/"
echo "2. Start with tester_b_plan.md"
echo "3. Follow tester_b_script.md for execution"
echo "4. Track progress with tester_b_checklist.md"