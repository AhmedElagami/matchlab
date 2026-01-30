# Manual Validation Script - Phase 7

## Prerequisites
- Docker services running (`docker compose up -d`)
- Test data loaded
- Admin user created with username `admin` and password `admin123`
- Regular users with passwords `test123`

## Validation Steps

### 1. Set Match Run as Active

1. Navigate to http://localhost:8000/auth/login/
2. Login as admin (username: `admin`, password: `admin123`)
3. Go to the match results page for the successful match run (ID 2)
4. Click the "Set as Active" button [data-testid="set-active-btn"]
5. Verify success message appears
6. Verify the button now says "Active" or similar indication

### 2. Participant Views Their Match

1. Logout as admin
2. Login as a participant (e.g., username: `mentor11`, password: `test123`)
3. Select the "Test Cohort 5x5 Ready" cohort
4. Click on "My Match" link [data-testid="my-match-link"]
5. Verify the match details are displayed:
   - Mentor and mentee names
   - Organizations
   - Match percentage
   - Policy compliance status
   - Match card has [data-testid="my-match-card"]

### 3. Admin Performs Manual Override

1. Logout as participant
2. Login as admin again
3. Navigate to the match results page
4. Click "Manual Override" button
5. Select a mentor from the dropdown [data-testid="override-mentor-select"]
6. Select a mentee from the dropdown [data-testid="override-mentee-select"]
7. Enter an override reason in the textarea [data-testid="override-reason-textarea"]
8. Click "Create Override" button [data-testid="override-save-btn"]
9. Verify success message appears
10. Verify the match is marked as "Manual" in the matches table
11. Verify the override reason is stored and displayed

### 4. Verify Exception Handling

1. Try to create an override that would violate policies (same organization)
2. Leave the override reason blank
3. Click "Create Override"
4. Verify error message appears requiring override reason
5. Enter a reason and try again
6. Verify the match is created with exception flag

### 5. Verify Audit Trail

1. Check that the exported CSV includes:
   - is_manual_override column
   - override_reason column
   - exception_flag column
   - exception_type column
   - exception_reason column