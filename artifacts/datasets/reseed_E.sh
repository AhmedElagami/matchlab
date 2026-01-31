#!/bin/bash

# Tester E Dataset Reseeding Script
# Regenerates all E scenario datasets with default parameters

echo "=== Tester E Dataset Reseeding ==="
echo "This script regenerates all scale and edge case datasets"
echo ""

# Create datasets directory if it doesn't exist
mkdir -p /home/ubuntu/matchlab/artifacts/datasets

# Remove existing E datasets
echo "Removing existing E datasets..."
rm -f /home/ubuntu/matchlab/artifacts/datasets/fixture_E*.json
rm -rf /home/ubuntu/matchlab/artifacts/datasets/cohorts_E5/

echo "Generating E1: Large Cohort Baseline (N=30)..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E1 --size 30 --output artifacts/datasets/fixture_E1.json

echo "Generating E2: Very High Contention (N=30, k=3)..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E2 --size 30 --contention 3 --output artifacts/datasets/fixture_E2.json

echo "Generating E3: Sparse Preferences (N=30, 30% sparse)..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E3 --size 30 --sparse 0.3 --output artifacts/datasets/fixture_E3.json

echo "Generating E4: Degenerate Ranks (N=20)..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E4 --size 20 --output artifacts/datasets/fixture_E4.json

echo "Generating E5: Multi-Cohort Partial Submissions (10 cohorts)..."
cd /home/ubuntu/matchlab && python3 artifacts/datasets/generate_E_dataset.py --scenario E5 --cohorts 10 --submission-rates 0,10,50,90,100 --output-dir artifacts/datasets/cohorts_E5/

echo ""
echo "=== Dataset Generation Complete ==="
echo "Generated datasets:"
ls -la /home/ubuntu/matchlab/artifacts/datasets/fixture_E*.json
ls -la /home/ubuntu/matchlab/artifacts/datasets/cohorts_E5/ | head -10

echo ""
echo "To load a dataset:"
echo "  docker compose -f docker-compose.dev.yml exec app python manage.py loaddata artifacts/datasets/fixture_E1.json"