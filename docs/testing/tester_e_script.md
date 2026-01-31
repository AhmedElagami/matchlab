# Tester E Script — Scale + Edge Cases

## Prereqs
- Clean DB reset
- Seeder/generator available (preferred) OR documented fixture import steps
- BASE_URL running

## Dataset sets to execute
You must run ALL of the following dataset scenarios (E1–E6).

### E1: Large cohort baseline
- Create 1 cohort with N participants (N = 30 mentors + 30 mentees = 60 total)
- All participants fully submitted
- Preferences: random but valid
Run:
- strict matching
Validate:
- UI: run completes, results render, export works
- DB: counts (participants, matches, match_run) consistent

### E2: Very high contention
- Same cohort size as E1 (N=60)
- Preferences: everyone ranks the same small top-k set (top 3 mentors/mentees)
Run:
- strict matching
Validate:
- no crash, stable tie-breaking behavior (as specified)
- determinism across 2 repeated runs (same seed)

### E3: Sparse / missing preferences
- Large cohort (N=60)
- Only 30% submitted preferences (but "submitted" status must reflect reality)
- Remaining have empty/sparse rankings
Run:
- strict matching
Validate:
- correct handling per spec (unmatched, penalty, or exclusion)
- no UI errors
- DB reflects correct flags/reasons

### E4: Degenerate ranks
- Medium/large cohort (N=40)
- Inject duplicates/out-of-range ranks and invalid forms via UI if possible; otherwise via seed artifact
Run:
- UI validations should block invalid inputs where intended
- If invalid data is possible in DB, run matching and verify graceful failure/exception handling
Validate:
- errors are user-friendly
- errors logged; no silent corruption

### E5: Many cohorts with partial submissions
- Create 10 cohorts
- submission ratios: 0%, 10%, 50%, 90%, 100% across cohorts
Run:
- matching per cohort (or global, depending on app design)
Validate:
- only submitted/eligible participants included in matching
- cohorts with 0% submitted behave as expected (no run or no matches; per spec)
- UI lists remain usable

### E6: Performance sampling
- Use E1 dataset
Run:
- strict match run 3 times
Validate:
- capture durations, query counts if available
- confirm no degradation across runs
Artifacts:
- timings report

## Required UI flows (Playwright MCP)
For each scenario E1–E6:
- login as admin
- navigate to cohort
- run matching (strict; then exception if required by failure mode)
- view results
- export CSV (if available)
- (optional) apply a small override and confirm audit entries (if applicable)

## Required DB assertions (Postgres MCP)
After each run:
- MatchRun created with correct mode/status
- Match row counts reasonable and consistent
- No orphaned rows; foreign keys intact
- Any flags/reasons fields set when degeneracy occurs
- For partial submissions: confirm excluded participants are not in matches

## Evidence outputs
- UI screenshots (run start, run complete, results, export)
- network/console logs
- DB query outputs
- exported CSVs
- timings log

## Implementation Steps

### Step 1: Environment Setup
1. Reset database:
   ```bash
   cd /home/ubuntu/matchlab
   docker compose -f docker-compose.dev.yml down -v
   docker compose -f docker-compose.dev.yml up -d
   docker compose -f docker-compose.dev.yml exec app python manage.py migrate
   ```

2. Verify application is running:
   ```bash
   curl -I http://localhost:8000/auth/login/
   ```

### Step 2: Data Generator Creation
Create `artifacts/datasets/generate_E_dataset.py` with:
- Deterministic seeding
- Configurable cohort parameters
- Adversarial pattern generation
- Fixture export capability

### Step 3: Scenario Execution
For each scenario E1-E6:
1. Generate dataset
2. Load into database
3. Execute Playwright UI flows
4. Perform Postgres assertions
5. Collect evidence artifacts

### Step 4: Evidence Collection
Maintain organized artifact structure:
```
artifacts/
├── datasets/
│   ├── E_dataset_manifest.md
│   ├── generate_E_dataset.py
│   └── reseed_E.sh
├── evidence/
│   ├── E1_*.png
│   ├── E2_*.png
│   └── E_evidence_index.md
├── reports/
│   └── E_test_report.md
└── tickets/
    └── E_tickets.md
```

## Test Execution Commands

### Database Operations
```bash
# Check cohort counts
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from apps.core.models import Cohort, Participant
from apps.matching.models import MatchRun, Match
print(f'Cohorts: {Cohort.objects.count()}')
print(f'Participants: {Participant.objects.count()}')
print(f'MatchRuns: {MatchRun.objects.count()}')
print(f'Matches: {Match.objects.count()}')
"

# Verify match run integrity
docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
from apps.matching.models import MatchRun
runs = MatchRun.objects.all()
for run in runs:
    print(f'Run {run.id}: {run.mode} {run.status}')
    print(f'  Matches: {run.match_set.count()}')
"
```

### Playwright Automation
Use Playwright to automate:
- Login flows
- Navigation sequences
- Form submissions
- Screenshot capture
- Network log collection

### Performance Monitoring
Capture timing metrics:
```bash
# Time match execution
time curl -X POST http://localhost:8000/cohort/1/run-matching/ -d "mode=STRICT"
```

## Validation Queries

### Data Integrity Checks
```sql
-- Check for orphaned matches
SELECT COUNT(*) FROM matching_match m 
LEFT JOIN matching_matchrun mr ON m.match_run_id = mr.id 
WHERE mr.id IS NULL;

-- Check participant submission consistency
SELECT c.name, 
       COUNT(CASE WHEN p.is_submitted THEN 1 END) as submitted,
       COUNT(*) as total
FROM core_cohort c
JOIN core_participant p ON c.id = p.cohort_id
GROUP BY c.id, c.name;
```

### Count Verification
After each run, verify:
- Participants: Expected count based on scenario
- Preferences: Expected count based on submission rates
- Matches: N matches for N mentors/mentees in successful runs
- MatchRun: One entry per execution with correct attributes