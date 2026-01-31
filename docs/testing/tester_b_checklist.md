# Tester B - Failure + Exception + Labeling Checklist

## Overview
This checklist tracks completion of testing for:
- **Slices**: 5.7, 5.8, 5.9, 6, 8
- **Focus**: Strict failure reporting, exception execution, labeling correctness, solver validation, failure resilience
- **Datasets**: B (primary), C (penalty ordering), A (baseline)

## Pre-testing Setup
- [ ] Docker environment verified running
- [ ] Admin user available (admin / admin123)
- [ ] Test users available (mentor21 / test123, mentee21 / test123)
- [ ] Test script reviewed
- [ ] Evidence collection folders created

## Slice 5.7 - Strict Failure Reporting

### Acceptability Infeasible Failure
- [ ] Navigate to cohort 3 run-matching
- [ ] Observe cohort details (minimal preferences)
- [ ] Run STRICT mode
- [ ] Verify failure redirect with details
- [ ] Confirm error message includes failure_report
- [ ] Screenshots captured

### UI Next Steps Guidance
- [ ] Check for next steps guidance on failure page
- [ ] Verify clear options presented
- [ ] Screenshots captured

### DB State Verification
- [ ] Check MatchRun record for FAILED STRICT
- [ ] Verify failure_report populated
- [ ] Screenshots captured

## Slice 5.8 - Exception Matching Execution

### Exception Mode After Strict Failure
- [ ] Run EXCEPTION mode on cohort 3
- [ ] Verify success redirect
- [ ] Check results show exception_count > 0
- [ ] Screenshots captured

### DB State Verification for Exception
- [ ] Check MatchRun record for SUCCESS EXCEPTION
- [ ] Verify 5 matches created
- [ ] Screenshots captured

### Edge Case - Zero Participants
- [ ] Create or find cohort with no participants
- [ ] Run EXCEPTION mode
- [ ] Verify graceful failure handling
- [ ] Screenshots captured

## Slice 5.9 - Exception Labeling Correctness

### Verify Exception Types in Results
- [ ] Examine exception flags in cohort 3 results
- [ ] Identify E1 (one-sided) examples
- [ ] Identify E2 (neither acceptable) examples
- [ ] Note absence/presence of E3 (same org)
- [ ] Screenshots captured

### DB Verification of Exception Types
- [ ] Check Match records with exceptions
- [ ] Verify exception_type values
- [ ] Confirm exception_reason clarity
- [ ] Screenshots captured

### Construct E3 Scenario
- [ ] Modify organizations to force same-org pairing
- [ ] Run EXCEPTION mode
- [ ] Verify E3 labeling appears
- [ ] Screenshots captured

## Section 6 - Solver-Specific Validation

### Strict Mode Constraint Verification
- [ ] Find successful STRICT run
- [ ] Verify zero constraint violations
- [ ] Screenshots captured

### Exception Mode Completeness
- [ ] Find EXCEPTION run
- [ ] Verify complete matching (N matches for N participants)
- [ ] Screenshots captured

### Penalty Ordering Validation
- [ ] Construct penalty ordering scenario
- [ ] Run EXCEPTION mode
- [ ] Verify correct penalty dominance
- [ ] Screenshots captured

### Determinism Check
- [ ] Run EXCEPTION mode twice on same inputs
- [ ] Compare matchings are identical
- [ ] Screenshots captured

## Section 8 - Failure Mode & Resilience Testing

### Bad Input Handling
- [ ] Test non-integer rank entry
- [ ] Test duplicate preference submission
- [ ] Verify graceful error handling
- [ ] Screenshots captured

### Partial Data Resilience
- [ ] Test cohort 3 mixed submission states
- [ ] Verify only submitted participants considered
- [ ] Screenshots captured

### Timeout Behavior
- [ ] Document timeout settings
- [ ] Note expected behavior for large N
- [ ] Screenshots captured

### Infeasible Model Reporting
- [ ] Run strict on cohort 3
- [ ] Verify actionable failure_report
- [ ] Screenshots captured

## Dataset Testing Coverage

### Dataset B (Primary - Strict-infeasible)
- [ ] Acceptability infeasible testing
- [ ] Failure detection and reporting
- [ ] Exception fallback behavior
- [ ] Edge case handling

### Dataset C (Penalty ordering)
- [ ] E1/E2/E3 scenario construction
- [ ] Penalty ordering verification
- [ ] Combined violation testing
- [ ] Determinism validation

### Dataset A (Baseline - Happy-path)
- [ ] Regression testing
- [ ] Comparison with known good behavior
- [ ] Determinism baseline establishment
- [ ] Exception handling consistency

## Evidence Collection

### Screenshots
- [ ] Strict failure reports
- [ ] Exception results with labels
- [ ] Run matching before/after
- [ ] DB verification command output
- [ ] Error/validation messages
- [ ] UI guidance and next steps

### Logs
- [ ] Failed match run logs
- [ ] Solver mode and duration info
- [ ] Exception count reporting
- [ ] Timeout/error handling logs

### Database Snapshots
- [ ] FAILED STRICT MatchRun samples
- [ ] SUCCESS EXCEPTION MatchRun samples
- [ ] Match samples with E1/E2/E3 types
- [ ] Preference and PairScore for penalty verification

## Defect Documentation
- [ ] Defect template ready
- [ ] Severity classification guidelines reviewed
- [ ] Evidence capture procedure established

## Completion Criteria
- [ ] All checklist items completed
- [ ] Evidence bundle assembled
- [ ] Run log documented
- [ ] Final report drafted