# Tester B - Failure + Exception + Labeling Test Plan

## Overview
This test plan covers the vertical feature slices assigned to Tester B:
- **Slices**: 5.7, 5.8, 5.9, 6, 8
- **Focus Areas**: Strict failure reporting, exception matching execution, exception labeling correctness, solver-specific validation, failure mode testing
- **Primary Dataset**: B (Strict-infeasible scenarios)
- **Secondary Dataset**: C (Penalty ordering scenarios)
- **Baseline Dataset**: A (Happy-path for comparison)

## Environment Information
- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: mentor21 / test123, mentee21 / test123
- **Available Cohorts**:
  - Cohort 1: "Engineering Mentoring Program 2026" (Baseline)
  - Cohort 3: "Test Cohort 5x5 Not Ready" (Primary for failure testing)

## Test Execution Strategy

We'll follow the vertical slice approach to validate end-to-end functionality, with special attention to failure modes and exception handling.

### Slice 5.7 - Strict Failure Reporting

#### Test Objectives:
1. Validate strict mode failure detection
2. Verify meaningful failure reports
3. Confirm UI guidance for next steps
4. Test various failure scenarios

#### Dataset B Scenarios:
1. **Acceptability Infeasible**: No mutual acceptability edges exist
2. **Org Infeasible**: Org assignments make cross-org pairing impossible
3. **Mismatched Counts**: Unequal mentors/mentees
4. **Missing Organizations**: Participants without orgs

#### Test Steps:
1. Identify cohort with minimal preferences (Cohort 3)
2. Run STRICT mode matching
3. Observe failure response
4. Verify error message includes failure_report
5. Check UI provides clear next steps
6. Confirm DB state shows FAILED MatchRun with failure_report

### Slice 5.8 - Exception Matching Execution

#### Test Objectives:
1. Validate exception mode execution
2. Confirm complete assignment generation
3. Verify success handling
4. Test edge cases

#### Dataset B/C Scenarios:
1. Run EXCEPTION mode after strict failure
2. Run EXCEPTION mode explicitly on problematic cohort
3. Test with zero participants
4. Test with mismatched counts

#### Test Steps:
1. Run EXCEPTION mode for failing cohort
2. Verify success message
3. Check results show exception_count > 0
4. Confirm DB MatchRun created with mode=EXCEPTION, status=SUCCESS
5. Verify full set of Match rows created
6. Test edge cases (zero participants, mismatched counts)

### Slice 5.9 - Exception Labeling Correctness (E1/E2/E3)

#### Test Objectives:
1. Validate correct exception type assignment
2. Confirm penalty ordering compliance
3. Verify exception reasoning clarity
4. Test combined violations

#### Dataset B/C Construction for Specific Labels:
1. **E3 (Same Org)**: Force same-org pairings
2. **E2 (Neither Acceptable)**: No rankings between paired participants
3. **E1 (One-sided)**: Exactly one participant ranked the other
4. **Combined Violations**: Same org + acceptability issues

#### Test Steps:
1. For each matched pair in EXCEPTION results:
   - Determine org relationship
   - Assess acceptability status
   - Compare to UI's exception_flag/type/reason
2. Verify penalty ordering matches spec:
   - E3 dominates E2 and E1
   - E2 dominates E1
   - Within same type, maximize score
3. Confirm DB stores exception_flag, exception_type, exception_reason

### Section 6 - Solver-Specific Validation

#### Test Objectives:
1. Verify strict mode constraints never violated
2. Confirm exception mode always produces complete matching
3. Validate penalty ordering expectations
4. Test determinism and reproducibility

#### Test Cases:
1. **Strict Mode Constraints**:
   - No same-org matches
   - No non-mutually acceptable matches
   - Complete N matches for N mentors/mentees

2. **Exception Mode Guarantees**:
   - Always complete one-to-one matching
   - All violations flagged, typed, and explained

3. **Penalty Ordering**:
   - Construct scenario where org violation vs. acceptability tradeoff exists
   - Confirm solver chooses zero-org-violation solution

4. **Determinism**:
   - Run same mode twice without changes
   - Compare match_run totals and exact pairings

### Section 8 - Failure Mode & Resilience Testing

#### Test Objectives:
1. Validate bad input handling
2. Confirm partial data resilience
3. Test timeout behavior
4. Verify infeasible model reporting

#### Test Cases:
1. **Bad Input**:
   - Non-integer ranks
   - Duplicate preference edges
   - Missing required org fields
   - Invalid CSV uploads

2. **Partial Data**:
   - Mixed submitted/not submitted participants
   - Missing org fields for some participants
   - Incomplete preferences

3. **Timeouts**:
   - Scale toward N=30 with dense constraints
   - Confirm graceful failure or completion

4. **Infeasible Models**:
   - Strict infeasible scenarios produce FAILED MatchRun
   - Clear failure_report with actionable hints

## Dataset Testing Approach

### Dataset B (Primary) - Strict-infeasible
- **Cohort 3**: "Test Cohort 5x5 Not Ready"
- **Characteristics**: Minimal preferences, one unsubmitted mentee
- **Expected Outcome**: Strict mode fails, Exception mode succeeds with labeling

### Dataset C (Penalty ordering) 
- **Construction needed**: Will create scenarios forcing specific exception types
- **Approach**: Manipulate preferences to create E1/E2/E3 situations
- **Focus**: Verify penalty ordering in solver

### Dataset A (Baseline)
- **Cohort 1**: "Engineering Mentoring Program 2026"
- **Characteristics**: Existing successful runs
- **Use**: Compare behavior, validate no regression

## Evidence Collection Requirements

### Screenshots Needed:
1. Strict failure reports with error messages
2. Exception results with labeled violations
3. Run matching screen before/after execution
4. Comparison of STRICT vs EXCEPTION UI
5. Timeout/error handling screens
6. Validation error messages

### Log Collection:
1. App logs around failed match runs
2. Solver mode, duration, exception counts
3. Timeout scenarios and handling
4. Error reporting and recovery

### Database Evidence:
1. MatchRun samples (FAILED STRICT, SUCCESS EXCEPTION)
2. Match samples with different exception types (E1/E2/E3)
3. Preference and PairScore data for penalty verification
4. Cohort readiness state snapshots

## Defect Reporting Format
For each defect found:
- Title: `[Slice] [Dataset] Symptom`
- Steps to reproduce: exact sequence
- Observed vs expected
- Evidence: screenshots/log excerpt + DB snapshot description
- Severity:
  - Critical: strict constraint violation, incomplete matching, wrong labeling
  - High: incorrect penalty ordering, missing failure reports
  - Medium/Low: unclear error messages, UI inconsistencies