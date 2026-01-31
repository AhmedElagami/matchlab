# Tester C - Ambiguity + Override + Auditability Test Plan

## Overview
This test plan covers the vertical feature slices assigned to Tester C:
- **Slices**: 5.10, 5.13, 9, 7 (partial)
- **Focus Areas**: Ambiguity detection, manual override workflow, auditability/explainability, performance sampling
- **Primary Dataset**: C (Pathological/edge-case scenarios)
- **Secondary Dataset**: A (Override in normal conditions)
- **Tertiary Dataset**: B (Override after exception)

## Environment Information
- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: mentee2 / test123
- **Available Cohorts**:
  - Cohort 1: "Engineering Mentoring Program 2026" (Rich dataset with ambiguity)
  - Cohort 3: "Test Cohort 5x5 Not Ready" (For additional testing)

## Test Execution Strategy

We'll follow the vertical slice approach to validate end-to-end functionality, with special attention to ambiguity detection and manual override workflows.

### Slice 5.10 - Ambiguity Detection

#### Test Objectives:
1. Validate ambiguity flagging when score gaps are within threshold
2. Verify clear ambiguity reasoning with alternative candidates
3. Confirm threshold behavior (default ~5 or cohort-configured)
4. Test edge cases (no alternatives, threshold adjustments)

#### Dataset C Scenarios:
1. **Close Scores**: Construct scenarios with near-equal pair scores
2. **Threshold Testing**: Verify behavior at boundary conditions
3. **No Alternatives**: Confirm no ambiguity when only one feasible candidate
4. **Multiple Ambiguities**: Test cohort with several ambiguous matches

#### Test Steps:
1. Identify run with existing ambiguities (Run 13 has 4 ambiguous matches)
2. Filter/identify ambiguity_flag=true matches in results table
3. Inspect ambiguity_reason for each flagged row
4. Verify ambiguity_flag true when chosen pairing score within threshold of best alternative
5. Verify ambiguity_reason names alternative candidate and score gap
6. Confirm DB storage of ambiguity_flag and ambiguity_reason
7. Test edge cases (no alternative, threshold adjustment)

### Slice 5.13 - Manual Override Workflow

#### Test Objectives:
1. Validate manual override UI and workflow
2. Confirm constraint preservation (one-to-one uniqueness)
3. Verify audit trail persistence (is_manual_override, override_reason)
4. Test override validation and error handling

#### Dataset Scenarios:
1. **Normal Conditions** (Dataset A): Override in successful run
2. **After Exception** (Dataset B): Override following exception mode run
3. **Constraint Violation**: Override that breaks strict compliance

#### Test Steps:
1. Navigate to override UI for successful run (e.g., Run 13)
2. Select mentor and mentee not currently matched together
3. Provide override reason
4. Submit override
5. Verify results table reflects new pairing
6. Confirm uniqueness: no mentor or mentee matched twice
7. Verify DB updates with is_manual_override=true and override_reason
8. Test negative cases:
   - Submit without selections → inline error
   - Attempt duplicate matching → validation block
   - Non-strict-compliant override → violation indication

### Section 9 - Auditability & Explainability

#### Test Objectives:
1. Verify results are explainable and traceable
2. Confirm all match decisions have evidence
3. Validate audit trail completeness
4. Test export integrity of audit fields

#### Test Cases:
1. **Manual Verification**:
   - Match percent plausibility relative to preferences
   - Exception reason clarity for overridden matches
   - Ambiguity reason referencing alternatives and thresholds

2. **Evidence Requirements** (per match row):
   - Mentor + mentee identifiers
   - Organizations
   - Score percent (match_percent)
   - Exception fields (flag/type/reason)
   - Ambiguity fields (flag/reason)
   - Manual override markers (is_manual_override, override_reason)

3. **Match Run Evidence**:
   - Created_at, created_by, mode, status
   - Objective_summary (totals, counts, avg score)
   - Failure_report when FAILED
   - Input_signature for traceability

### Section 7 - Performance & Scalability Checks (Sampling)

#### Test Objectives:
1. Validate runtime expectations for N≤30
2. Confirm DB query efficiency
3. Test stress scenarios with dense preferences
4. Document observed performance characteristics

#### Test Cases:
1. **Runtime Measurement**:
   - End-to-end from "Run matching" to results page
   - Solver runtime and exception counts (from logs)
   - Compare STRICT (~5s) vs EXCEPTION (~10s) durations

2. **DB Efficiency**:
   - Check for N×N query patterns
   - Monitor results page load times
   - Observe export action performance

3. **Stress Testing**:
   - Use cohort with dense preferences
   - Rapid repeat operations (results view, filters, export)
   - Record durations and any timeouts/errors

## Dataset Testing Approach

### Dataset C (Primary - Pathological/Edge-case)
- **Focus**: Ambiguity detection and close score scenarios
- **Construction**: Dense preferences with near-equal scores
- **Expected**: Ambiguity flags triggered with sensible reasons
- **Validation**: Threshold logic and alternative candidate naming

### Dataset A (Override in Normal)
- **Focus**: Manual override in typical successful runs
- **Use**: Run 13 (EXCEPTION on Cohort 1) with 4 ambiguities
- **Expected**: Clean override workflow and audit persistence

### Dataset B (Override After Exception)
- **Focus**: Override following exception mode execution
- **Use**: Recent exception runs on Cohort 3 if successful
- **Expected**: Same override behavior regardless of preceding mode

## Evidence Collection Requirements

### Screenshots Needed:
1. Ambiguity-flagged results with reasons visible
2. Override UI workflow and confirmation
3. Manual override markers in results table
4. Audit fields in exported files
5. Performance timing measurements
6. Validation error messages

### Log Collection:
1. App logs around ambiguity detection
2. Override action recording and validation
3. Performance timing and solver duration
4. DB query pattern observations

### Database Evidence:
1. Match samples with ambiguity_flag=true
2. Match samples with is_manual_override=true
3. MatchRun samples with objective_summary
4. Export integrity verification (DB vs file)

## Defect Reporting Format
For each defect found:
- Title: `[Slice] [Dataset] Symptom`
- Steps to reproduce: exact sequence
- Observed vs expected
- Evidence: screenshots/log excerpt + DB snapshot description
- Severity:
  - Critical: missing audit trails, incorrect ambiguity detection, constraint violations
  - High: unclear explanations, export integrity issues, performance degradation
  - Medium/Low: UI inconsistencies, minor validation gaps, documentation mismatches