# Tester C - Ambiguity + Override + Auditability Checklist

## Overview
This checklist tracks completion of testing for:
- **Slices**: 5.10, 5.13, 9, 7 (sampling)
- **Focus**: Ambiguity detection, manual override workflow, auditability/explainability, performance sampling
- **Datasets**: C (primary), A (override in normal), B (override after exception)

## Pre-testing Setup
- [ ] Docker environment verified running
- [ ] Admin user available (admin / admin123)
- [ ] Test user available (mentee2 / test123)
- [ ] Test script reviewed
- [ ] Evidence collection folders created

## Slice 5.10 - Ambiguity Detection

### Identify Existing Ambiguities
- [ ] Navigate to Run 13 results
- [ ] Filter/scan for ambiguity_flag=true matches
- [ ] Verify 4 ambiguous matches visible
- [ ] Screenshots captured

### Inspect Ambiguity Reasons
- [ ] Examine ambiguity_reason for each flagged row
- [ ] Verify clear alternative candidate naming
- [ ] Confirm score gap and threshold inclusion
- [ ] Screenshots captured

### DB Verification of Ambiguity Storage
- [ ] Check DB for ambiguity_flag and ambiguity_reason
- [ ] Verify 4 matches with proper storage
- [ ] Screenshots captured

### Edge Case - No Alternatives
- [ ] Find/single-candidate scenario
- [ ] Run matching
- [ ] Verify no ambiguity flag
- [ ] Screenshots captured

## Slice 5.13 - Manual Override Workflow

### Override in Successful Run
- [ ] Access Run 13 override UI
- [ ] Select non-matched mentor/mentee
- [ ] Enter override reason
- [ ] Submit override
- [ ] Verify success and results update
- [ ] Screenshots captured

### Verify Uniqueness Constraint
- [ ] Check one-to-one matching preserved
- [ ] Confirm no participant duplication
- [ ] Screenshots captured

### DB Verification of Override Persistence
- [ ] Check DB for is_manual_override marker
- [ ] Verify override_reason populated
- [ ] Screenshots captured

### Negative Case - Validation Errors
- [ ] Test incomplete override submission
- [ ] Test duplicate matching attempt
- [ ] Verify clear validation errors
- [ ] Screenshots captured

## Section 9 - Auditability & Explainability

### Match Percent Plausibility
- [ ] Examine matches for score reasonableness
- [ ] Correlate with preferences/organizations
- [ ] Screenshots captured

### Exception Reason Clarity
- [ ] Find exception_flag=true matches
- [ ] Examine exception_reason clarity
- [ ] Screenshots captured

### Audit Trail Completeness
- [ ] Verify all audit fields present
- [ ] Confirm mentor/mentee identifiers
- [ ] Check organizations and scores
- [ ] Verify exception/ambiguity/override fields
- [ ] Screenshots captured

### Match Run Evidence
- [ ] Check match run metadata
- [ ] Verify objective_summary populated
- [ ] Confirm created_at and mode
- [ ] Screenshots captured

## Section 7 - Performance & Scalability Checks

### Runtime Measurement
- [ ] Measure EXCEPTION mode duration
- [ ] Note results page load time
- [ ] Verify ~10s expectation
- [ ] Screenshots captured

### DB Query Efficiency
- [ ] Monitor results page load (N=16)
- [ ] Record timing observations
- [ ] Screenshots captured

### Stress Testing
- [ ] Rapid repeat operations
- [ ] Apply filters and export
- [ ] Record delays/timeouts
- [ ] Screenshots captured

## Dataset Testing Coverage

### Dataset C (Primary - Pathological/Edge-case)
- [ ] Ambiguity detection validation
- [ ] Threshold logic verification
- [ ] Close score scenario testing
- [ ] Edge case coverage

### Dataset A (Override in Normal)
- [ ] Override workflow in Run 13
- [ ] Audit trail creation verification
- [ ] Constraint preservation testing
- [ ] Validation error handling

### Dataset B (Override After Exception)
- [ ] Override in exception context
- [ ] Behavior consistency check
- [ ] Same audit requirements verification
- [ ] Constraint enforcement testing

## Evidence Collection

### Screenshots
- [ ] Ambiguous matches and reasons
- [ ] Override workflow and results
- [ ] Audit fields in UI
- [ ] DB verification outputs
- [ ] Performance timing
- [ ] Validation errors

### Logs
- [ ] Ambiguity detection logs
- [ ] Override action recordings
- [ ] Performance timings
- [ ] DB query observations

### Database Snapshots
- [ ] Ambiguous match samples
- [ ] Manual override samples
- [ ] MatchRun metadata
- [ ] Export integrity verification

## Defect Documentation
- [ ] Defect template ready
- [ ] Severity classification guidelines reviewed
- [ ] Evidence capture procedure established

## Completion Criteria
- [ ] All checklist items completed
- [ ] Evidence bundle assembled
- [ ] Run log documented
- [ ] Final report drafted