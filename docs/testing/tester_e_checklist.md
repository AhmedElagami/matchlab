# Tester E Checklist — Scale + Edge Cases

## Setup
- [ ] MCP enumeration completed; Playwright + Postgres MCP mapped
- [ ] DB wiped (volumes removed) and migrations applied
- [ ] Services healthy and logs captured
- [ ] Base URL confirmed accessible
- [ ] Admin credentials verified (admin / admin123)

## Dataset Generator
- [ ] `artifacts/datasets/generate_E_dataset.py` created
- [ ] Deterministic seeding implemented
- [ ] Configurable cohort sizes (N=30 max)
- [ ] Adversarial pattern generation functions
- [ ] Fixture export capability
- [ ] Generator script tested and working

## Dataset Artifacts
- [ ] `artifacts/datasets/E_dataset_manifest.md` created
- [ ] `artifacts/datasets/reseed_E.sh` created and replays successfully
- [ ] `artifacts/datasets/E_db_snapshot.*` exported
- [ ] All scenario datasets generated and validated

## Scenarios

### E1: Large Cohort Baseline
- [ ] Generate N=30 cohort (60 participants)
- [ ] All participants submitted with valid preferences
- [ ] Execute strict matching via UI
- [ ] Validate UI completion and results rendering
- [ ] Export CSV and verify content
- [ ] Perform Postgres assertions
- [ ] Collect evidence artifacts
- [ ] Document timing metrics

### E2: Very High Contention
- [ ] Generate N=30 cohort with contention preferences
- [ ] All participants rank same top-k candidates
- [ ] Execute strict matching via UI
- [ ] Validate tie-breaking behavior
- [ ] Run twice with same seed for determinism check
- [ ] Perform Postgres assertions
- [ ] Collect evidence artifacts
- [ ] Document timing metrics

### E3: Sparse / Missing Preferences
- [ ] Generate N=30 cohort with 30% preference submission
- [ ] Mix of complete and sparse preference sets
- [ ] Execute strict matching via UI
- [ ] Validate handling per specification
- [ ] Check UI error status
- [ ] Perform Postgres assertions
- [ ] Collect evidence artifacts
- [ ] Document timing metrics

### E4: Degenerate Ranks
- [ ] Generate N=20 cohort with invalid rank data
- [ ] Include duplicates, out-of-range, and invalid ranks
- [ ] Test UI validation blocking
- [ ] If bypass possible, verify graceful failure
- [ ] Validate error messaging
- [ ] Perform Postgres assertions
- [ ] Collect evidence artifacts
- [ ] Document timing metrics

### E5: Many Cohorts Partial Submissions
- [ ] Generate 10 cohorts with varied submission rates
- [ ] Rates: 0%, 10%, 50%, 90%, 100%
- [ ] Execute matching for each cohort
- [ ] Validate eligibility filtering
- [ ] Check UI list usability
- [ ] Perform Postgres assertions
- [ ] Collect evidence artifacts
- [ ] Document timing metrics

### E6: Performance Sampling
- [ ] Use E1 dataset for performance testing
- [ ] Execute strict matching 3 times
- [ ] Capture duration metrics
- [ ] Monitor query counts if available
- [ ] Validate no performance degradation
- [ ] Document timing consistency
- [ ] Collect evidence artifacts

## Required UI Flows (Playwright MCP)
For each executed scenario:
- [ ] Admin login successful
- [ ] Cohort navigation working
- [ ] Matching execution completed
- [ ] Results viewing successful
- [ ] CSV export functional (when available)
- [ ] Override application tested (when applicable)
- [ ] Network/console logs captured
- [ ] UI screenshots collected

## Required DB Assertions (Postgres MCP)
After each run:
- [ ] MatchRun created with correct mode/status
- [ ] Match row counts reasonable and consistent
- [ ] No orphaned rows; foreign keys intact
- [ ] Flags/reasons fields set when degeneracy occurs
- [ ] Excluded participants not in matches (partial submissions)
- [ ] DB query outputs collected
- [ ] Integrity verification completed

## Evidence Outputs
- [ ] UI screenshots (run start, run complete, results, export)
- [ ] Network/console logs for each scenario
- [ ] DB query outputs for integrity checks
- [ ] Exported CSVs from successful runs
- [ ] Timing logs and performance reports
- [ ] `artifacts/evidence/E_evidence_index.md` created

## Reports
- [ ] `artifacts/tickets/E_tickets.md` created
- [ ] `artifacts/reports/E_test_report.md` created
- [ ] `artifacts/evidence/E_evidence_index.md` created
- [ ] MCP usage inventory included
- [ ] Performance analysis documented
- [ ] Determinism validation results

## Defect Documentation
- [ ] All defects logged with proper severity
- [ ] Reproduction steps documented
- [ ] Evidence artifacts linked
- [ ] Impact assessment completed
- [ ] Release blocking issues identified

## Final Validation
- [ ] All scenarios executed as planned
- [ ] All evidence artifacts collected
- [ ] All reports completed
- [ ] No critical/blocking issues found
- [ ] Performance within expected bounds
- [ ] Determinism requirements met
- [ ] Data integrity maintained