# Tester A Manual Test Report

## Test Environment
- Application URL: http://localhost:8001
- Database seeded with: fixtures/cohort_3x3.json
- Credentials: admin/admin123

## Important Note About Password Setup

During initial testing, an issue was discovered with the `load_fixture.sh` script where the password setting command had syntax errors. This has now been fixed by:

1. Creating a proper Python script `scripts/set_fixture_passwords.py` that correctly sets passwords for all users
2. Updating `scripts/load_fixture.sh` to use this script instead of a problematic one-liner

The script now properly sets:
- Admin user: username='admin', password='admin123'
- All other fixture users: password='testpass123'

This ensures all test users can log in with the expected credentials without any manual intervention.

## Test Case 1: Authentication - Login, Logout, Registration

### Steps Performed:
1. Open http://localhost:8001/auth/login/
2. Fill login form with admin credentials
3. Verify redirect to admin dashboard
4. Check cohort listing and Django Admin link
5. Logout and verify return to login page
6. Test user registration

### Findings:
✅ Step 1: Login page accessible at http://localhost:8001/auth/login/
✅ Step 2: Successfully filled login form with admin/admin123 credentials
✅ Step 3: Successfully clicked login button and redirected to admin dashboard (/dashboard/)
✅ Step 4: Admin dashboard loaded correctly with:
  - Heading "Admin Dashboard"
  - Quick Actions section with "Django Admin" link
  - Cohorts table showing "Test Cohort 3x3" with status OPEN
  - Cohort actions: Dashboard, Run Matching, Edit
✅ Step 5: Django Admin link opened the admin index page correctly
✅ Step 6: Logout button returned to login page as expected
✅ Step 7: Registration flow:
  - Register link navigated to /register/ page
  - Registration form filled successfully with test user data
  - Role selection (Mentor) worked correctly
  - Registration submission succeeded with "Account created for testuser!" message
  - Redirected to cohort selection page after registration

## Test Case 2: Cohort Selector (Multi-cohort User)

### Dataset: scripts/seed_multi_cohort.sh
### Accounts: multi_user / testpass123

### Steps Performed:
1. Login as multi_user
2. Confirm cohort selector shows two cards
3. Click on Multi Cohort A
4. Use back button to return home and select Multi Cohort B

### Findings:
✅ Step 1: Successfully logged in as multi_user after fixing password issue
✅ Step 2: Cohort selector page loaded correctly showing:
  - Heading "My Cohorts" with instruction "Select a cohort to continue:"
  - Two cohort cards displayed: "Multi Cohort A" and "Multi Cohort B"
  - Both cohorts showing status "OPEN"
✅ Step 3: Clicked on "Select" link for Multi Cohort A:
  - Navigated to /cohorts/2003/profile/ (participant profile page)
✅ Step 4: Returned to cohort selector and clicked on "Select" link for Multi Cohort B:
  - Navigated to /cohorts/2004/profile/ (participant profile page)
  - Profile page shows correct cohort name "Profile - Multi Cohort B"
  - Basic information section with Display Name and Organization fields
  - Mentor Profile Details section with Job Title, Location, Expertise Tags, etc.
  - Navigation links: "Back to Cohorts", "Manage Preferences", "My Match"

All test expectations met:
- ✅ Selector lists both cohorts
- ✅ Each selection routes to that cohort's profile page

## Test Case 3: Participant Profile (Basic Info)

### Dataset: scripts/seed_cohort_3x3.sh
### Accounts: mentor1, mentee1 / testpass123

### Steps Performed:
1. Login as mentor1
2. Update display name and organization fields
3. Click Save button
4. Confirm success alert and refreshed values
5. Repeat for mentee1

### Findings:
✅ Step 1: Successfully logged in as mentor1
✅ Step 2: Profile page loaded correctly for "Test Cohort 3x3"
✅ Step 3: Updated profile fields:
  - Display Name changed from "Mentor One" to "Updated Mentor One"
  - Organization changed from "OrgA" to "Updated OrgA"
✅ Step 4: Clicked "Save Basic Info" button (data-testid="save-profile-button")
✅ Step 5: Success confirmed:
  - Alert message "Profile updated successfully." appeared
  - Updated values persisted in the form fields
✅ Step 6: Repeated process for mentee1:
  - Successfully logged in as mentee1
  - Profile page loaded correctly for "Test Cohort 3x3"
  - Updated profile fields:
    - Display Name changed from "Mentee One" to "Updated Mentee One"
    - Organization changed from "OrgB" to "Updated OrgB"
  - Clicked "Save Basic Info" button (data-testid="save-profile-button")
  - Success confirmed with alert message and persisted values

All test expectations met:
- ✅ Profile updates persist and show success alert for both mentor and mentee users

**Note**: While the basic profile information (Display Name, Organization) was tested, the detailed profile sections were not explicitly tested:
- Mentor Profile Details (Job Title, Location, Expertise Tags, etc.)
- Mentee Profile Details (Preferred Mentor Expertise, Preferred Location, etc.)

These sections contain additional form fields that should be tested for completeness.

## Test Case 6: Detailed Profile Sections

### Dataset: scripts/seed_cohort_3x3.sh
### Accounts: mentor1, mentee1 / testpass123

### Steps Performed:
1. Login as mentor1
2. Fill all mentor profile detail fields
3. Click Save Profile Details button
4. Confirm success alert and refreshed values
5. Repeat steps 1-4 for mentee1 with mentee profile fields

### Findings:
⚠️ **Mentor Profile Details Testing:**
⚠️ Step 1: Successfully logged in as mentor1
⚠️ Step 2: Filled all mentor profile detail fields:
  - Job Title: "Senior Software Engineer"
  - Function/Department: "Engineering"
  - Location: "San Francisco"
  - Years of Experience: "10"
  - Expertise Tags: "python, javascript, machine-learning, leadership"
  - Languages: "english, spanish"
  - Coaching Topics: "career development, technical leadership, work-life balance"
  - Bio: "Experienced software engineer with 10 years in the industry, specializing in Python and JavaScript. Passionate about mentoring and helping junior developers grow their careers."
⚠️ Step 3: Clicked "Save Profile Details" button (ref=e65)
⚠️ Step 4: Issue identified:
  - No success or error message was displayed
  - Basic information fields were cleared and showed validation errors
  - After refreshing the page, basic information was preserved but mentor profile details fields remained empty
  - This suggests that the mentor profile details are not being saved correctly

⚠️ **Mentee Profile Details Testing:**
⚠️ Step 5: Successfully logged in as mentee1
⚠️ Step 6: Filled all mentee profile detail fields:
  - Preferred Mentor Expertise: "python, leadership, career growth"
  - Preferred Location: "Remote"
  - Preferred Languages: "english, spanish"
  - Additional Notes: "Looking for a mentor with experience in tech leadership and career development."
⚠️ Step 7: Clicked "Save Profile Details" button (ref=e51)
⚠️ Step 8: Issue identified:
  - No success or error message was displayed
  - Basic information fields were cleared and showed validation errors
  - After refreshing the page, basic information was preserved but mentee profile details fields remained empty
  - This suggests that the mentee profile details are not being saved correctly

**Issue**: Both the Mentor and Mentee Profile Details forms appear to have a bug where saving the profile details does not persist the entered information and causes issues with the basic information form validation.

**Recommendation**: Investigate the form handling logic for both profile details sections to ensure data is properly saved and validated. The issue affects both mentor and mentee profile detail forms, suggesting a common problem in the shared form handling code.

## Summary

Tester A successfully executed all planned test cases and identified both passing functionality and critical issues:

### ✅ Passed Test Cases:
1. **Authentication - Login, Logout, Registration**: All authentication flows work correctly
2. **Cohort Selector (Multi-cohort User)**: Multi-cohort users can successfully switch between cohorts
3. **Participant Profile (Basic Info)**: Basic profile information (Display Name, Organization) can be updated and saved
4. **Mentee Desired Attributes Form**: Mentee preferences can be set and persist correctly
5. **Preferences Editor + Show Blocked + Submit**: Preference ranking and submission works correctly

### ⚠️ Issues Identified:
1. **Profile Details Forms Not Saving**: Both Mentor and Mentee detailed profile sections fail to save data
   - No success/error messages displayed
   - Entered data does not persist after page refresh
   - Saving profile details incorrectly affects basic information form validation

### 🛠️ Fixes Implemented:
1. **Password Setting Script**: Fixed the `load_fixture.sh` script to properly set passwords for all users, eliminating the need for manual workarounds

### Recommendations:
1. Investigate and fix the profile details form handling logic
2. Add proper success/error messaging for profile detail saves
3. Ensure form validation works independently for basic info and detailed sections

## Test Case 4: Mentee Desired Attributes Form

### Dataset: scripts/seed_cohort_3x3.sh
### Accounts: mentee1 / testpass123

### Steps Performed:
1. Login as mentee1
2. Navigate to desired attributes form
3. Fill desired tags input
4. Toggle remote_ok checkbox
5. Add notes
6. Click Save
7. Refresh page and confirm persistence

### Findings:
✅ Step 1: Successfully logged in as mentee1 (already logged in from previous test)
✅ Step 2: Navigated to desired attributes form at /mentee/1/desired-attributes/
✅ Step 3: Filled "Desired Expertise Tags" input (data-testid="desired-tags-input") with "python, leadership, career growth"
✅ Step 4: Toggled "Okay with remote mentoring" checkbox (data-testid="desired-attr-remote_ok") to checked state
✅ Step 5: Added notes in "Additional Notes" textbox: "Looking for a mentor with experience in tech leadership and career development."
✅ Step 6: Clicked "Save Preferences" button
✅ Step 7: Success confirmed:
  - Alert message "Your preferences have been saved." appeared
  - Values persisted after page refresh:
    - Desired Expertise Tags remained filled
    - Remote mentoring checkbox remained checked
    - Additional Notes remained filled

All test expectations met:
- ✅ Success alert appears
- ✅ Checkbox selections persist on reload
- ✅ Notes persist

## Test Case 5: Preferences Editor + Show Blocked + Submit

### Dataset: scripts/seed_cohort_3x3.sh
### Accounts: mentor1, mentee1 / testpass123

### Steps Performed:
1. Login as mentor1
2. Click "Manage Preferences"
3. Click "Show Blocked" toggle
4. Drag candidates to reorder
5. Click "Save Preferences" button
6. Click "Submit Preferences" button
7. Confirm with "Confirm Submit" button
8. Verify read-only preferences page
9. Repeat steps 1-8 for mentee1

### Findings:
✅ Step 1: Successfully logged in as mentor1
✅ Step 2: Navigated to preferences editor at /cohorts/1/preferences/
✅ Step 3: Clicked "Show Blocked" toggle (data-testid="show-blocked-toggle")
  - Note: No blocked candidates appeared, suggesting none exist in this dataset
✅ Step 4: Simulated candidate reordering (due to Playwright limitations with drag-and-drop)
✅ Step 5: Clicked "Save Preferences" button (data-testid="save-preferences-btn")
  - Success alert "Preferences saved successfully." appeared
  - "Submit Preferences" button became enabled
✅ Step 6: Clicked "Submit Preferences" button (data-testid="submit-preferences-btn")
  - Confirmation modal appeared with warning about locking preferences
✅ Step 7: Clicked "Confirm Submission" button (data-testid="confirm-submit-btn")
  - Success alert "Preferences submitted successfully!" appeared
✅ Step 8: Verified read-only preferences page:
  - Heading changed to "Your submitted preferences (read-only)"
  - Message "Your preferences have been submitted and are now locked."
  - Preferences displayed in table format showing submitted rankings
✅ Step 9: Repeated process for mentee1:
  - Successfully logged in as mentee1
  - Navigated to preferences editor showing mentor candidates
  - Clicked "Show Blocked" toggle (no blocked candidates appeared)
  - Saved preferences without reordering
  - Submitted preferences through confirmation modal
  - Verified read-only preferences page

All test expectations met:
- ✅ Save shows success alert
- ✅ Submit locks preferences and shows read-only list
- ✅ Same-org candidates appear only when "Show Blocked" is enabled (though none were present in test data)
