#!/bin/bash
set -euo pipefail

cd /home/ubuntu/matchlab

bash scripts/load_fixture.sh fixtures/cohort_5x5_not_ready.json
