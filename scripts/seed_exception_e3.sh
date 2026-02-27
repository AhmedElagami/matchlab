#!/bin/bash
set -euo pipefail

cd /home/ubuntu/matchlab

bash scripts/load_fixture.sh fixtures/manual_exception_e3.json
