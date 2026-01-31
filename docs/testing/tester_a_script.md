# Tester A - Manual Test Script

## Prerequisites
- Clean Docker environment (reset using `scripts/reset_testing_env.sh`)
- Admin user credentials: admin / admin123
- Web browser for UI testing
- Dataset generation capability for creating test data on demand

## Slice 5.1 - Authentication & Access Control Testing

### Test Case 1: Unauthenticated Access
1. Open incognito/private browser window
2. Navigate to: http://localhost:8000/dashboard/
3. Expected: Redirect to login page
4. Try accessing: http://localhost:8000/cohort/1/run-matching/
5. Expected: Redirect to login page
6. Try accessing: http://localhost:8000/match-run/1/results/
7. Expected: Redirect to login page
8. Take screenshot of redirect behavior

### Test Case 2: Non-Admin Access to Protected Pages
1. Log in as mentor1 with password test123
2. Navigate to: http://localhost:8000/dashboard/
3. Expected: Access denied or redirect to participant pages
4. Try accessing: http://localhost:8000/cohort/1/run-matching/
5. Expected: Access denied
6. Try accessing: http://localhost:8000/import/mentor-csv/
7. Expected: Access denied
8. Take screenshot of access denied behavior

### Test Case 3: Admin Access to All Pages
1. Log out if logged in
2. Navigate to: http://localhost:8000/auth/login/
3. Log in as admin with password admin123
4. Navigate to: http://localhost:8000/dashboard/
5. Expected: Admin dashboard loads successfully
6. Navigate to: http://localhost:8000/cohort/1/run-matching/
7. Expected: Run matching page loads successfully
8. Navigate to: http://localhost:8000/match-run/1/results/
9. Expected: Results page loads successfully
10. Take screenshots of successful page loads

### Test Case 4: IDOR Testing
1. Stay logged in as admin
2. Navigate to: http://localhost:8000/cohorts/1/profile/ (should work)
3. Try modifying URL to access non-existent cohort: http://localhost:8000/cohorts/999/profile/
4. Expected: Error page or redirect, not data exposure
5. Try to access another user's profile by ID if URL pattern is visible
6. Expected: Blocked access with error or redirect
7. Take screenshots of error/redirect behavior

### Test Case 5: CSRF Protection
1. Stay logged in as admin
2. Navigate to any form page (e.g., profile edit page)
3. View page source
4. Locate CSRF token in form
5. Verify token is present in forms requiring authentication
6. Take screenshot showing CSRF token in source

## Slice 5.2 - Cohort Creation & Configuration

### Test Case 1: Cohort Management Access
1. Stay logged in as admin
2. Navigate to Django admin: http://localhost:8000/admin/
3. Find "Core" section and click "Cohorts"
4. Expected: List of existing cohorts
5. Click "Add cohort" button
6. Fill in cohort name: "Test Cohort A"
7. Set status to "DRAFT"
8. Save cohort
9. Expected: Success message and cohort appears in list
10. Take screenshots of cohort creation process

### Test Case 2: Cohort Status Transitions
1. From cohort list, click on "Test Cohort A"
2. Change status from "DRAFT" to "OPEN"
3. Save changes
4. Expected: Success message
5. Change status from "OPEN" to "CLOSED"
6. Save changes
7. Expected: Success message
8. Take screenshots of status transitions

## Slice 5.3 - Participant Management

### Test Case 1: Participant Creation
1. Navigate to Django admin: http://localhost:8000/admin/
2. Find "Core" section and click "Participants"
3. Click "Add participant"
4. Select existing cohort (Engineering Mentoring Program 2026)
5. Select existing user or create new user first
6. Set role as "MENTOR" or "MENTEE"
7. Fill in display name and organization
8. Save participant
9. Expected: Success message
10. Take screenshots of participant creation

### Test Case 2: Participant Profile Editing
1. Log out as admin
2. Log in as mentor1 or mentee1
3. Navigate to profile page: http://localhost:8000/cohorts/1/profile/
4. Edit display name and organization
5. Save changes
6. Expected: Confirmation message
7. Try submitting with empty organization
8. Expected: Validation error
9. Take screenshots of profile editing and validation

### Test Case 3: Access Control for Profiles
1. Stay logged in as mentor1
2. Try to access another participant's profile via URL manipulation
3. Expected: Access denied or redirect
4. Take screenshot of access control behavior

## Slice 5.6 - Strict Matching Execution

### Test Case 1: Strict Mode Execution
1. Log out if logged in
2. Log in as admin
3. Navigate to: http://localhost:8000/cohort/1/run-matching/
4. Take screenshot of run matching page with existing runs
5. Select "STRICT" mode
6. Click "Run Matching" button
7. Expected: Redirect to results page with success message
8. Take screenshot of success message and results table

### Test Case 2: Results Verification
1. On results page, verify:
   - All participants are matched (equal mentors/mentees)
   - No exception flags are true
   - Match percentages are reasonable
2. Count rows in results table
3. Expected: Number of matches = number of mentors (or mentees)
4. Take screenshot of results table

### Test Case 3: Deterministic Behavior
1. Go back to run matching page
2. Run STRICT mode again without changing inputs
3. Compare results with previous run
4. Expected: Same pairings (deterministic behavior)
5. Take screenshots of both runs for comparison

## Slice 5.11 - Run History & Detail Views

### Test Case 1: Run History Display
1. Navigate to: http://localhost:8000/cohort/1/run-matching/
2. Scroll to "Recent Runs" section
3. Verify runs are listed newest first
4. Expected: Run 13 should be at top (most recent)
5. Take screenshot of run history list

### Test Case 2: Run Detail Access
1. Click on different runs in the history list
2. Verify each run's results page loads correctly
3. Check that older runs still show consistent data
4. Take screenshots of different run results

## Slice 5.12 - CSV Export Correctness

### Test Case 1: Export Functionality
1. Navigate to a successful match run results page
2. Find and click the "Export CSV" button
3. Expected: File download prompt
4. Save the file
5. Take screenshot of export button and download

### Test Case 2: Export Content Verification
1. Open downloaded CSV file
2. Verify columns include:
   - Mentor/mentee names
   - Organizations
   - Match percentage
   - Flags (ambiguity, exception)
   - Manual override fields
3. Verify row count matches expected matches
4. Take screenshot of CSV content in spreadsheet app

### Test Case 3: Export Restrictions
1. Try to export a failed match run (Run 1)
2. Expected: Export should be disabled or show error
3. Take screenshot of behavior for failed runs

## Slice 5.15 - UI Consistency Across Modes

### Test Case 1: UI Structure Comparison
1. Navigate to a STRICT mode results page
2. Note the table structure and columns
3. Navigate to an EXCEPTION mode results page
4. Compare table structure
5. Expected: Same structure with additional exception columns in EXCEPTION mode
6. Take screenshots of both for comparison

### Test Case 2: Export Format Consistency
1. Export CSV from STRICT mode run
2. Export CSV from EXCEPTION mode run
3. Compare file structures
4. Expected: Same columns with additional data in EXCEPTION export
5. Take screenshots of both CSV files

## Dataset Testing Notes

### Dataset A (Primary) Testing
- Focus on existing cohort with 16 participants
- Verify strict mode works correctly with mixed orgs
- Confirm no exceptions in properly configured scenarios

### Dataset B (Access-Control) Testing
- Focus on authentication flows and privilege boundaries
- Test user isolation and cohort separation
- Verify admin-only actions are properly protected

### Dataset C (Quick Sanity) Testing
- Brief test of edge cases if time permits
- Quick validation of error handling
- Focus remaining on core security and strict flow

## Evidence Collection Points

Throughout testing, collect:
1. Screenshots of key UI states (login flows, access denied, results)
2. Exported CSV files from different run modes
3. Log captures around match executions
4. Database snapshots of match_run and match records

## Defect Documentation

If defects found, document with:
- Clear title with slice and dataset reference
- Exact reproduction steps
- Observed vs expected behavior
- Supporting screenshots/logs
- Severity classification (Critical/High/Medium/Low)