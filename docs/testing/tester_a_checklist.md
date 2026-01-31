# Tester A - Security + Core Strict Flow Checklist

## Overview
This checklist tracks completion of testing for:
- **Slices**: 5.1, 5.2, 5.3, 5.6, 5.11, 5.12, 5.15
- **Datasets**: A (primary), B (access-control impacts), quick C sanity

## Pre-testing Setup
- [ ] Docker environment verified running
- [ ] Admin user password set (admin / admin123)
- [ ] Test script reviewed
- [ ] Evidence collection folders created

## Slice 5.1 - Authentication & Access Control

### Unauthenticated Access Tests
- [ ] Attempt access to dashboard (redirects to login)
- [ ] Attempt access to run-matching (redirects to login)
- [ ] Attempt access to results (redirects to login)
- [ ] Screenshots captured

### Non-Admin Access Tests
- [ ] Log in as mentor1
- [ ] Attempt access to admin dashboard (blocked)
- [ ] Attempt access to run-matching (blocked)
- [ ] Attempt access to import pages (blocked)
- [ ] Screenshots captured

### Admin Access Tests
- [ ] Log in as admin
- [ ] Access dashboard (success)
- [ ] Access run-matching (success)
- [ ] Access results pages (success)
- [ ] Screenshots captured

### IDOR Testing
- [ ] Attempt direct access to non-existent cohort (blocked)
- [ ] Attempt direct access to other user profiles (blocked)
- [ ] Screenshots captured

### CSRF Protection
- [ ] Verify CSRF tokens in forms
- [ ] Screenshot of page source showing tokens

## Slice 5.2 - Cohort Creation & Configuration

### Cohort Management
- [ ] Access Django admin cohorts
- [ ] Create new cohort
- [ ] Save successfully
- [ ] Screenshots captured

### Status Transitions
- [ ] Change cohort from DRAFT to OPEN
- [ ] Change cohort from OPEN to CLOSED
- [ ] Changes save successfully
- [ ] Screenshots captured

## Slice 5.3 - Participant Management

### Participant Creation
- [ ] Access Django admin participants
- [ ] Create new participant
- [ ] Save successfully
- [ ] Screenshots captured

### Profile Editing
- [ ] Log in as participant
- [ ] Edit profile successfully
- [ ] Test validation (empty org)
- [ ] Screenshots captured

### Access Control
- [ ] Test profile access restrictions
- [ ] Verify proper blocking
- [ ] Screenshots captured

## Slice 5.6 - Strict Matching Execution

### Strict Mode Run
- [ ] Navigate to run-matching page
- [ ] Select STRICT mode
- [ ] Execute matching
- [ ] Verify success redirect
- [ ] Screenshots captured

### Results Verification
- [ ] Check results table
- [ ] Verify no exceptions
- [ ] Confirm match completeness
- [ ] Screenshots captured

### Deterministic Behavior
- [ ] Re-run strict matching
- [ ] Compare results
- [ ] Verify consistency
- [ ] Screenshots captured

## Slice 5.11 - Run History & Detail Views

### Run History
- [ ] View recent runs list
- [ ] Verify newest-first ordering
- [ ] Screenshots captured

### Run Details
- [ ] Access multiple run results
- [ ] Verify data consistency
- [ ] Screenshots captured

## Slice 5.12 - CSV Export Correctness

### Export Functionality
- [ ] Export CSV from successful run
- [ ] Verify file download
- [ ] Screenshots captured

### Export Content
- [ ] Verify column headers
- [ ] Check row count
- [ ] Confirm flag data present
- [ ] Screenshots captured

### Export Restrictions
- [ ] Attempt export of failed run
- [ ] Verify proper blocking
- [ ] Screenshots captured

## Slice 5.15 - UI Consistency Across Modes

### UI Structure
- [ ] Compare STRICT results UI
- [ ] Compare EXCEPTION results UI
- [ ] Verify consistent structure
- [ ] Screenshots captured

### Export Format
- [ ] Compare STRICT CSV export
- [ ] Compare EXCEPTION CSV export
- [ ] Verify format consistency
- [ ] Screenshots captured

## Dataset Testing Coverage

### Dataset A (Primary)
- [ ] Authentication flows tested
- [ ] Core strict matching validated
- [ ] Export functionality verified
- [ ] UI consistency checked

### Dataset B (Access-Control Impacts)
- [ ] Privilege escalation attempts tested
- [ ] User isolation verified
- [ ] Admin boundary protection confirmed
- [ ] Cross-cohort access blocked

### Dataset C (Quick Sanity)
- [ ] Edge case quick checks (time permitting)
- [ ] Error handling verification
- [ ] Boundary condition testing

## Evidence Collection

### Screenshots
- [ ] Authentication flow screenshots
- [ ] Access denied/error screenshots
- [ ] Run matching screenshots
- [ ] Results table screenshots
- [ ] Export functionality screenshots
- [ ] Profile editing screenshots
- [ ] Admin interface screenshots

### Logs
- [ ] Match run execution logs
- [ ] Authentication logs
- [ ] Error logs (if any)

### Database Snapshots
- [ ] MatchRun samples (different modes/statuses)
- [ ] Match samples (with flags/reasons)
- [ ] Cohort/Participant relationship examples

## Defect Documentation
- [ ] Defect template ready
- [ ] Severity classification guidelines reviewed
- [ ] Evidence capture procedure established

## Completion Criteria
- [ ] All checklist items completed
- [ ] Evidence bundle assembled
- [ ] Run log documented
- [ ] Final report drafted