# Tester E Dataset Manifest

## Overview
This document describes the datasets generated for scale and combinatorial edge case testing.

## Dataset Generation Tool
- **Script**: `generate_E_dataset.py`
- **Location**: `artifacts/datasets/generate_E_dataset.py`
- **Usage**: Generates deterministic datasets with various adversarial patterns

## Scenario Datasets

### E1: Large Cohort Baseline
- **Description**: Standard large cohort with N=30 (60 participants total)
- **Characteristics**: 
  - All participants submitted
  - Random but valid preferences
  - Normal organization distribution
- **Generation Command**: 
  ```bash
  python generate_E_dataset.py --scenario E1 --size 30 --output fixture_E1.json
  ```

### E2: Very High Contention
- **Description**: Everyone ranks the same small top-k set
- **Characteristics**:
  - High contention preference patterns
  - Same top 3 candidates ranked by all
  - Tests tie-breaking behavior
- **Generation Command**:
  ```bash
  python generate_E_dataset.py --scenario E2 --size 30 --contention 3 --output fixture_E2.json
  ```

### E3: Sparse / Missing Preferences
- **Description**: Only partial preference submission
- **Characteristics**:
  - 30% of participants have preferences
  - 70% have empty/sparse rankings
  - Tests handling of incomplete data
- **Generation Command**:
  ```bash
  python generate_E_dataset.py --scenario E3 --size 30 --sparse 0.3 --output fixture_E3.json
  ```

### E4: Degenerate Ranks
- **Description**: Invalid and degenerate rank data
- **Characteristics**:
  - Duplicate ranks
  - Out-of-range values
  - Invalid rank formats
  - Tests input validation
- **Generation Command**:
  ```bash
  python generate_E_dataset.py --scenario E4 --size 20 --output fixture_E4.json
  ```

### E5: Many Cohorts Partial Submissions
- **Description**: Multiple cohorts with varied submission rates
- **Characteristics**:
  - 10 cohorts with 0%, 10%, 50%, 90%, 100% submission rates
  - Tests multi-cohort eligibility filtering
  - Validates resource isolation
- **Generation Command**:
  ```bash
  python generate_E_dataset.py --scenario E5 --cohorts 10 --submission-rates 0,10,50,90,100 --output-dir cohorts_E5/
  ```

## Reproducibility

All datasets are generated with deterministic seeding:
- **Default Seed**: 42
- **Custom Seed**: Use `--seed <value>` parameter
- **Consistency**: Same seed produces identical datasets

## Loading Datasets

### Single Cohort Loading
```bash
# Reset database
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml exec app python manage.py migrate

# Load fixture
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixture_E1.json
```

### Multi-Cohort Loading
```bash
# For E5 scenario, load each cohort fixture separately
for fixture in cohorts_E5/*.json; do
    docker compose -f docker-compose.dev.yml exec app python manage.py loaddata $fixture
done
```

## Validation Commands

### Check Dataset Integrity
```bash
# Count participants
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from apps.core.models import Participant
print(f'Total participants: {Participant.objects.count()}')
"

# Count preferences
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from apps.matching.models import Preference
print(f'Total preferences: {Preference.objects.count()}')
"
```

## Artifact Organization
```
artifacts/
├── datasets/
│   ├── E_dataset_manifest.md
│   ├── generate_E_dataset.py
│   ├── fixture_E1.json
│   ├── fixture_E2.json
│   ├── fixture_E3.json
│   ├── fixture_E4.json
│   └── cohorts_E5/
│       ├── fixture_E5_Multi_Cohort_#1_(0%_submitted)_id10.json
│       └── ... (9 more cohort fixtures)
├── evidence/
├── reports/
└── tickets/
```