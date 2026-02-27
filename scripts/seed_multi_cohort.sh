#!/bin/bash
set -euo pipefail

cd /home/ubuntu/matchlab

bash scripts/load_fixture.sh fixtures/manual_multi_cohort.json
