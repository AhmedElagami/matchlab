# Tester B - Manual Test Script

## Prerequisites
- Docker environment running (matchlab-app and matchlab-db containers)
- Admin user credentials: admin / admin123
- Test user credentials: mentor21 / test123, mentee21 / test123
- Web browser for UI testing

## Slice 5.7 - Strict Failure Reporting

### Test Case 1: Acceptability Infeasible Failure
1. Log in as admin
2. Navigate to: http://localhost:8000/cohort/3/run-matching/
3. Observe cohort details:
   - 5 mentors, 5 mentees
   - Only minimal preferences exist (one mutual pair)
   - One mentee not submitted
4. Select "STRICT" mode
5. Click "Run Matching" button
6. Expected: Redirect to run page with failure details
7. Verify error message includes failure_report
8. Take screenshot of failure report

### Test Case 2: UI Next Steps Guidance
1. On failure page, look for next steps guidance
2. Expected: Option to run exception mode or fix inputs
3. Take screenshot of UI guidance

### Test Case 3: DB State Verification
1. Check DB for MatchRun record:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun; mr = MatchRun.objects.last(); print(f'Mode: {mr.mode}, Status: {mr.status}'); print(f'Failure Report: {mr.failure_report}')"
   ```
2. Expected: mode=STRICT, status=FAILED, failure_report populated
3. Take screenshot of DB verification

## Slice 5.8 - Exception Matching Execution

### Test Case 1: Exception Mode After Strict Failure
1. On the same cohort 3 run-matching page
2. Select "EXCEPTION" mode
3. Click "Run Matching" button
4. Expected: Redirect to results page with success message
5. Verify results show exception_count > 0
6. Take screenshot of success message and results table

### Test Case 2: DB State Verification for Exception
1. Check DB for MatchRun record:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun, Match; mr = MatchRun.objects.last(); print(f'Mode: {mr.mode}, Status: {mr.status}'); print(f'Matches created: {Match.objects.filter(match_run=mr).count()}')"
   ```
2. Expected: mode=EXCEPTION, status=SUCCESS, 5 matches created
3. Take screenshot of DB verification

### Test Case 3: Edge Case - Zero Participants
1. Create temporary cohort with no participants (via Django admin)
2. Try running EXCEPTION mode
3. Expected: Graceful failure with explicit error
4. Take screenshot of error handling

## Slice 5.9 - Exception Labeling Correctness

### Test Case 1: Verify Exception Types in Results
1. On EXCEPTION results page for cohort 3
2. Examine each match row for exception flags
3. Identify matches with different exception types:
   - Look for E1 (one-sided acceptability)
   - Look for E2 (neither acceptable)
   - Note: E3 (same org) may not be present in current data
4. Check exception_reason for clarity
5. Take screenshot of labeled exceptions

### Test Case 2: DB Verification of Exception Types
1. Check DB for Match records with exceptions:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import Match; matches = Match.objects.filter(match_run__mode='EXCEPTION', exception_flag=True); [print(f'Match: {m.mentor.display_name} - {m.mentee.display_name}, Type: {m.exception_type}, Reason: {m.exception_reason}') for m in matches[:3]]"
   ```
2. Verify exception_type values (E1/E2/E3 or blank)
3. Verify exception_reason provides sufficient detail
4. Take screenshot of DB verification

### Test Case 3: Construct E3 Scenario (Same Org Violation)
1. We need to create a scenario where same-org pairing is forced
2. Via Django admin, modify participant organizations to create conflict
3. Or run matching on cohort where same-org pairing is unavoidable
4. Run EXCEPTION mode
5. Verify E3 labeling appears
6. Take screenshot of E3 labeling

## Section 6 - Solver-Specific Validation

### Test Case 1: Strict Mode Constraint Verification
1. Find a successful STRICT run from cohort 1:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun, Match; mr = MatchRun.objects.filter(mode='STRICT', status='SUCCESS').first(); matches = Match.objects.filter(match_run=mr); print(f'Checking {matches.count()} matches for STRICT constraints...'); violations = [m for m in matches if m.mentor.organization == m.mentee.organization or not m.is_mutually_acceptable]; print(f'Violations found: {len(violations)}')"
   ```
2. Expected: 0 violations
3. Take screenshot of verification

### Test Case 2: Exception Mode Completeness
1. Find an EXCEPTION run:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun, Match; from apps.core.models import Participant; mr = MatchRun.objects.filter(mode='EXCEPTION', status='SUCCESS').first(); cohort = mr.cohort; mentors = Participant.objects.filter(cohort=cohort, role_in_cohort='MENTOR', is_submitted=True); mentees = Participant.objects.filter(cohort=cohort, role_in_cohort='MENTEE', is_submitted=True); matches = Match.objects.filter(match_run=mr); print(f'Mentors: {mentors.count()}, Mentees: {mentees.count()}, Matches: {matches.count()}')"
   ```
2. Expected: Matches equal number of submitted mentors (or mentees)
3. Take screenshot of verification

### Test Case 3: Penalty Ordering Validation
1. We need to construct a scenario where penalty ordering is tested
2. Create preferences that would favor high-score same-org match vs. lower-score cross-org match
3. Run EXCEPTION mode
4. Verify solver chooses cross-org solution despite lower score
5. Take screenshot of results showing correct penalty ordering

### Test Case 4: Determinism Check
1. Run EXCEPTION mode twice on same cohort without changes
2. Compare results:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun, Match; runs = MatchRun.objects.filter(mode='EXCEPTION', status='SUCCESS').order_by('-created_at')[:2]; [print(f'Run {r.id}: {r.created_at}') for r in runs]; run1_matches = set((m.mentor.id, m.mentee.id) for m in Match.objects.filter(match_run=runs[0])); run2_matches = set((m.mentor.id, m.mentee.id) for m in Match.objects.filter(match_run=runs[1])); print(f'Matchings identical: {run1_matches == run2_matches}')"
   ```
3. Expected: Identical matchings
4. Take screenshot of comparison

## Section 8 - Failure Mode & Resilience Testing

### Test Case 1: Bad Input Handling
1. Try entering non-integer rank via preferences UI
2. Expected: Inline validation error
3. Try duplicate preference submission
4. Expected: DB constraint violation handled gracefully
5. Take screenshots of validation behavior

### Test Case 2: Partial Data Resilience
1. Find cohort with mixed submitted states (cohort 3 fits this)
2. Run matching and observe behavior
3. Expected: Only submitted participants considered
4. Take screenshot of handling

### Test Case 3: Timeout Simulation
1. This is harder to simulate directly
2. Document current timeout settings:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "print('Check for timeout settings in codebase')"
   ```
3. Note expected behavior: strict ~5s, exception ~10s
4. For large N, confirm graceful timeout handling

### Test Case 4: Infeasible Model Reporting
1. Use cohort 3 which should be infeasible for strict mode
2. Run strict and verify clear failure report
3. Expected: Actionable failure_report with hints
4. Take screenshot of report

## Dataset Testing Approach

### Dataset B (Primary) Testing - Cohort 3
1. Focus on "Test Cohort 5x5 Not Ready"
2. Verify strict failure with meaningful report
3. Confirm exception success with proper labeling
4. Test edge cases with partial submission

### Dataset C (Penalty Ordering) Testing
1. Need to construct scenarios for specific penalty types
2. May require modifying existing preferences
3. Focus on verifying E3 > E2 > E1 ordering
4. Test determinism with repeated runs

### Dataset A (Baseline) Testing - Cohort 1
1. Compare behavior with known good cohort
2. Verify no regression in exception handling
3. Confirm existing successful runs still work
4. Use for determinism baseline comparison

## Evidence Collection Points

Throughout testing, collect:
1. Screenshots of failure reports and error messages
2. Screenshots of exception-labeled results
3. Screenshots of DB verification commands and output
4. Log captures around failed executions
5. Database snapshots of MatchRun and Match records

## Defect Documentation

If defects found, document with:
- Clear title with slice and dataset reference
- Exact reproduction steps
- Observed vs expected behavior
- Supporting screenshots/logs
- Severity classification (Critical/High/Medium/Low)