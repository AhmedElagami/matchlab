#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Starting dev stack (docker-compose.dev.yml)..."
docker compose -f docker-compose.dev.yml up -d --build

echo "Dev stack is up."
