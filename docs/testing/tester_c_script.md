# Tester C - Manual Test Script

## Prerequisites
- Docker environment running (matchlab-app and matchlab-db containers)
- Admin user credentials: admin / admin123
- Test user credentials: mentee2 / test123
- Web browser for UI testing

## Slice 5.10 - Ambiguity Detection

### Test Case 1: Identify Existing Ambiguities
1. Log in as admin
2. Navigate to existing run with ambiguities: http://localhost:8000/match-run/13/results/
3. Filter or scan for ambiguity_flag=true matches
4. Expected: 4 ambiguous matches visible with flags
5. Take screenshot of ambiguous matches highlighted

### Test Case 2: Inspect Ambiguity Reasons
1. For each ambiguous match, examine the ambiguity_reason field
2. Expected: Clear naming of alternative candidate and score gap
3. Example: "Matched score (46.5) vs alternative (46.9) gap is small (-0.4 <= 5.0)"
4. Verify reason includes:
   - Matched score
   - Alternative candidate score
   - Gap calculation
   - Threshold comparison
5. Take screenshot of detailed ambiguity reasons

### Test Case 3: DB Verification of Ambiguity Storage
1. Check DB for ambiguous matches:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import Match; mr = Match.objects.get(id=13).match_run; ambiguous = Match.objects.filter(match_run=mr, ambiguity_flag=True); print(f'Run {mr.id} has {ambiguous.count()} ambiguous matches'); [print(f'- {m.mentor.display_name} - {m.mentee.display_name}: {m.ambiguity_reason}') for m in ambiguous]"
   ```
2. Expected: 4 matches with ambiguity_flag=True and populated ambiguity_reason
3. Take screenshot of DB verification

### Test Case 4: Edge Case - No Alternatives
1. Find or construct scenario with participant having only one feasible match
2. Run matching
3. Expected: No ambiguity flag (no alternative to compare)
4. Take screenshot of single-candidate scenario

## Slice 5.13 - Manual Override Workflow

### Test Case 1: Override in Successful Run
1. Stay on Run 13 results page
2. Look for override action/button
3. Click to open override UI
4. Select a mentor and mentee NOT currently matched together
5. Enter override reason: "Testing override workflow"
6. Submit override
7. Expected: Success confirmation, results table updates
8. Take screenshots of:
   - Override UI
   - Confirmation message
   - Updated results table

### Test Case 2: Verify Uniqueness Constraint
1. After override, check that no participant appears twice
2. Expected: One-to-one matching preserved
3. Take screenshot of results showing uniqueness

### Test Case 3: DB Verification of Override Persistence
1. Check DB for manual override markers:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import Match; overrides = Match.objects.filter(is_manual_override=True); print(f'Manual overrides: {overrides.count()}'); [print(f'- {m.mentor.display_name} - {m.mentee.display_name}: {m.override_reason}') for m in overrides]"
   ```
2. Expected: Newly created override with is_manual_override=True and override_reason
3. Take screenshot of DB verification

### Test Case 4: Negative Case - Validation Errors
1. Try submitting override without selecting both mentor and mentee
2. Expected: Inline validation error
3. Try creating duplicate match (same mentor/mentee with someone else)
4. Expected: Clear validation message preventing violation
5. Take screenshots of validation errors

## Section 9 - Auditability & Explainability

### Test Case 1: Match Percent Plausibility
1. Examine several matches in Run 13 results
2. Correlate match_percent with visible preferences/organizations
3. Expected: Higher scores for compatible orgs/interests
4. Take screenshot of matches with varying scores

### Test Case 2: Exception Reason Clarity
1. Find matches with exception_flag=true in Run 13
2. Examine exception_reason field
3. Expected: Clear policy violation explanation
4. Take screenshot of exception explanations

### Test Case 3: Audit Trail Completeness
1. For each match row, verify presence of:
   - Mentor/mentee identifiers
   - Organizations
   - Match percent
   - Exception fields (flag/type/reason)
   - Ambiguity fields (flag/reason)
   - Manual override markers (is_manual_override, override_reason)
2. Take screenshot of complete audit fields

### Test Case 4: Match Run Evidence
1. View match run details:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from apps.matching.models import MatchRun; mr = MatchRun.objects.get(id=13); print(f'Run {mr.id}:'); print(f'  Mode: {mr.mode}'); print(f'  Status: {mr.status}'); print(f'  Objective Summary: {mr.objective_summary}'); print(f'  Created: {mr.created_at}')"
   ```
2. Expected: Complete metadata with objective_summary populated
3. Take screenshot of match run evidence

## Section 7 - Performance & Scalability Checks

### Test Case 1: Runtime Measurement
1. Navigate to cohort 1 run-matching: http://localhost:8000/cohort/1/run-matching/
2. Note current time
3. Run EXCEPTION mode again
4. Note results page load time
5. Expected: Completion within ~10s for EXCEPTION mode
6. Take screenshot of timing measurement

### Test Case 2: DB Query Efficiency
1. Monitor results page load for N=16 cohort
2. Expected: Reasonable load time (<5s)
3. Take screenshot of page load timing

### Test Case 3: Stress Testing
1. Rapidly repeat operations:
   - Open results page
   - Apply filters (ambiguity/exceptions)
   - Export CSV
2. Record any delays or timeouts
3. Take screenshot of stress test operations

## Dataset Testing Approach

### Dataset C (Primary - Pathological/Edge-case)
1. Focus on ambiguity detection with close scores
2. Use Run 13 which has 4 ambiguous matches
3. Verify threshold logic (5.0) compliance
4. Test edge cases with limited alternatives

### Dataset A (Override in Normal)
1. Use successful Run 13 for override workflow
2. Verify clean audit trail creation
3. Confirm constraint preservation
4. Test validation error handling

### Dataset B (Override After Exception)
1. If Cohort 3 has successful exception runs, use those
2. Confirm override behavior consistency
3. Verify same audit requirements apply
4. Test constraint enforcement

## Evidence Collection Points

Throughout testing, collect:
1. Screenshots of ambiguous matches and reasons
2. Screenshots of override workflow and results
3. Screenshots of audit fields in UI and exports
4. Log captures around ambiguity detection and overrides
5. Database snapshots of ambiguous and override matches
6. Performance timing measurements

## Defect Documentation

If defects found, document with:
- Clear title with slice and dataset reference
- Exact reproduction steps
- Observed vs expected behavior
- Supporting screenshots/logs
- Severity classification (Critical/High/Medium/Low)