#!/bin/bash

echo "=== MatchLab Tester E Environment Verification ==="

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
echo "4. Checking Python environment for data generation..."
cd /home/ubuntu/matchlab && python3 -c "import json, argparse, random" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python environment ready for data generation"
else
    echo "❌ Python environment missing required modules"
    exit 1
fi

echo ""
echo "5. Testing data generator script..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Data generator script is functional"
else
    echo "❌ Data generator script has issues"
    exit 1
fi

echo ""
echo "6. Creating artifacts directory structure..."
mkdir -p /home/ubuntu/matchlab/artifacts/datasets
mkdir -p /home/ubuntu/matchlab/artifacts/evidence
mkdir -p /home/ubuntu/matchlab/artifacts/reports
mkdir -p /home/ubuntu/matchlab/artifacts/tickets

if [ $? -eq 0 ]; then
    echo "✅ Artifacts directory structure created"
else
    echo "❌ Failed to create artifacts directory structure"
    exit 1
fi

echo ""
echo "7. Generating sample E1 dataset..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E1 --size 5 --output artifacts/datasets/sample_E1.json > /dev/null 2>&1
if [ $? -eq 0 ] && [ -f artifacts/datasets/sample_E1.json ]; then
    echo "✅ Sample E1 dataset generated successfully"
    # Clean up sample
    rm artifacts/datasets/sample_E1.json
else
    echo "❌ Failed to generate sample E1 dataset"
    exit 1
fi

echo ""
echo "=== Environment Verification Complete ==="
echo "✅ All systems ready for Tester E"
echo ""
echo "Next steps:"
echo "1. Review documentation in docs/testing/"
echo "2. Start with tester_e_plan.md"
echo "3. Follow tester_e_script.md for execution"
echo "4. Track progress with tester_e_checklist.md"
echo "5. Use artifacts/datasets/generate_E_dataset.py for data generation"