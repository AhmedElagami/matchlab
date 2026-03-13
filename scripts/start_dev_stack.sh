#!/bin/bash
set -euo pipefail

cd /home/ekhekho/matchlab/matchlab

echo "Starting dev stack (docker-compose.dev.yml)..."
docker compose -f docker-compose.dev.yml up -d --build

echo "Dev stack is up."
