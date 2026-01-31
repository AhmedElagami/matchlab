# Tester A - Security + Core Strict Flow Test Plan

## Overview
This test plan covers the vertical feature slices assigned to Tester A:
- Slices: 5.1, 5.2, 5.3, 5.6, 5.11, 5.12, 5.15
- Datasets: A (primary), B (access-control impacts), quick C sanity

## Environment Setup
- Clean application environment (use `scripts/reset_testing_env.sh`)
- Admin user: admin / admin123
- Dataset generation on demand using custom generators
- No pre-loaded data - all test data created specifically for test scenarios

## Test Execution Order
We'll follow the vertical slice approach to validate end-to-end functionality.

### Slice 5.1 - Authentication & Access Control

#### Test Cases:
1. Unauthenticated access attempts to protected pages
2. Non-admin access to admin-only pages
3. Admin access to all pages
4. IDOR (Insecure Direct Object Reference) testing
5. CSRF protection verification

#### Steps:
1. Visit login page: http://localhost:8000/auth/login/
2. Try accessing admin pages without logging in:
   - http://localhost:8000/dashboard/
   - http://localhost:8000/cohort/1/run-matching/
   - http://localhost:8000/match-run/1/results/
3. Login as a non-admin user (mentor1/mentee1)
4. Try accessing admin pages with non-admin user
5. Login as admin user
6. Access admin pages with admin user
7. Try direct URL access to another cohort/participant data (IDOR test)
8. Verify CSRF tokens on POST forms

### Slice 5.2 - Cohort Creation & Configuration

#### Test Cases:
1. Admin creating new cohorts
2. Cohort status transitions
3. Cohort configuration settings

#### Steps:
1. Login as admin
2. Navigate to cohort management (Django admin or custom dashboard)
3. Create a new cohort
4. Set cohort configurations
5. Verify cohort appears in dashboard list
6. Test cohort status transitions (DRAFT → OPEN → CLOSED)

### Slice 5.3 - Participant Management

#### Test Cases:
1. Admin creating participants
2. Participant profile editing
3. Organization field validation
4. Unique constraint enforcement

#### Steps:
1. Login as admin
2. Add participants to cohort
3. Verify unique cohort-user constraint
4. Login as participant
5. Edit profile (display name, organization)
6. Verify required field validation
7. Try accessing another participant's profile (access control)

### Slice 5.6 - Strict Matching Execution

#### Test Cases:
1. Running strict mode matching
2. Success response handling
3. Results display
4. Match completeness verification

#### Steps:
1. Login as admin
2. Navigate to Run Matching page for cohort 1
3. Select STRICT mode
4. Execute matching
5. Verify success message
6. Check results table shows all matches
7. Verify no exceptions in strict mode results
8. Check deterministic behavior with re-runs

### Slice 5.11 - Run History & Detail Views

#### Test Cases:
1. Match run history display
2. Immutable run results
3. Access to older runs

#### Steps:
1. Login as admin
2. Navigate to run-matching page
3. View recent runs list
4. Access results pages for multiple runs
5. Verify runs are ordered newest-first
6. Compare results between runs to verify immutability

### Slice 5.12 - CSV Export Correctness

#### Test Cases:
1. CSV export functionality
2. Export content correctness
3. File naming convention
4. Column presence and data accuracy

#### Steps:
1. Login as admin
2. Navigate to successful match run results
3. Click Export CSV button
4. Save and inspect file:
   - Check column headers
   - Verify row count matches expected matches
   - Confirm flags and reasons are included
5. If XLSX export available, test that too
6. Verify export denied for failed runs

### Slice 5.15 - UI Consistency Across Modes

#### Test Cases:
1. UI consistency between strict and exception modes
2. Table structure uniformity
3. Field meaning consistency
4. Export format consistency

#### Steps:
1. Compare STRICT and EXCEPTION results pages:
   - Same table structure
   - Same columns
   - Consistent field meanings
2. Export both runs and compare formats:
   - Same headers
   - Same data structure
3. Verify mode indicators are clear
4. Check that exception fields only populate in exception mode

## Dataset Testing Approach

### Dataset A (Primary) - Happy-path
- Use existing cohort with mixed organizations
- Verify strict mode success with cross-org matching
- Confirm no exceptions in results

### Dataset B (Access-control impacts) 
- Focus on testing access control boundaries
- Test user privilege escalation attempts
- Verify proper isolation between cohorts/users

### Dataset C (Quick sanity)
- Brief test of pathological cases
- Quick check of edge conditions
- Main focus remains on security and strict flow

## Evidence Collection Requirements

### Screenshots Needed:
1. Login page and authentication flow
2. Access denied/error pages
3. Run-matching screen before and after execution
4. Results table with flags visible
5. Export download action and file presence
6. Profile edit screens with validation errors (if any)

### Log Collection:
1. App logs around match run start/end
2. Mode selection and duration information
3. Any error messages or warnings

### Database Evidence:
1. Snapshot of match_run row (mode, status, objective_summary/failure_report)
2. Sample match rows (flags, types, reasons, manual override fields)

## Defect Reporting Format
For each defect found:
- Title: `[Slice] [Dataset] Symptom`
- Steps to reproduce: exact sequence
- Observed vs expected
- Evidence: screenshots/log excerpt + DB snapshot description
- Severity:
  - Critical: access-control bypass, strict constraint violation, data corruption, missing matches on SUCCESS
  - High: incorrect exception labeling, incorrect exports, non-determinism without explanation
  - Medium/Low: UI inconsistencies, minor validation gaps