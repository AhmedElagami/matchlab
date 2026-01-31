# Tester D - Manual Test Script

## Prerequisites
- Docker environment running (matchlab-app and matchlab-db containers)
- Admin user credentials: admin / admin123
- Test user credentials: sophiemuller / test123 (participant without cohort assignment)
- Web browser for UI testing

## Registration/Login + Cohort Selector

### Test Case 1: New User Registration
1. Open incognito/private browser window
2. Navigate to: http://localhost:8000/register/
3. Fill registration form with:
   - Username: newtestuser
   - Email: newtestuser@example.com
   - Password: TestPass123!
   - Confirm Password: TestPass123!
4. Submit form
5. Expected: Account created successfully, redirected to login or dashboard
6. Take screenshot of registration form and success message

### Test Case 2: Login Process
1. Navigate to: http://localhost:8000/auth/login/
2. Enter credentials: sophiemuller / test123
3. Click login
4. Expected: Successful login, redirected to appropriate dashboard
5. Try invalid credentials (sophiemuller / wrongpass)
6. Expected: Error message, login form remains
7. Take screenshots of both scenarios

### Test Case 3: Cohort Selection
1. Login as sophiemuller
2. If user has access to multiple cohorts, verify cohort selection UI
3. If user has single cohort, verify direct access
4. Expected: Proper redirection based on cohort access
5. Take screenshot of cohort selection or direct access

## Profile Pages (Mentor/Mentee)

### Test Case 1: Mentor Profile Editing
1. Login as admin
2. Assign sophiemuller to a cohort as MENTOR (if not already)
3. Logout as admin
4. Login as sophiemuller
5. Navigate to profile page: http://localhost:8000/cohorts/{cohort_id}/profile/
6. Edit mentor profile fields:
   - Display name
   - Organization
   - Additional mentor-specific fields
7. Save changes
8. Expected: Changes saved successfully, confirmation message
9. Take screenshots of profile form and success message

### Test Case 2: Mentee Profile Editing
1. Login as admin
2. Create or use existing mentee user
3. Navigate to mentee profile page
4. Edit mentee profile fields:
   - Display name
   - Organization
   - Additional mentee-specific fields
5. Save changes
6. Expected: Changes saved successfully
7. Take screenshots of profile editing

### Test Case 3: Profile Validation
1. On profile page, try submitting with missing required fields
2. Expected: Inline validation errors
3. Try entering invalid organization format (if validation exists)
4. Expected: Appropriate error messaging
5. Take screenshots of validation errors

## Preferences UI (Including Duplicate Ranks, Readonly States)

### Test Case 1: Preference Entry
1. Login as participant with cohort access
2. Navigate to preferences page: http://localhost:8000/cohorts/{cohort_id}/preferences/
3. Rank available candidates
4. Try assigning same rank to multiple candidates
5. Expected: System handles duplicate ranks appropriately
6. Take screenshots of ranking interface and any validation messages

### Test Case 2: Duplicate Rank Handling
1. Continue on preferences page
2. Deliberately create duplicate rank scenario
3. Attempt to save preferences
4. Expected: Clear messaging about duplicate ranks
5. Take screenshots of error handling

### Test Case 3: Readonly States
1. Submit preferences (if possible in current cohort state)
2. Return to preferences page
3. Verify readonly presentation
4. Expected: No editing controls, clear indication of submitted state
5. Take screenshots of readonly preferences

## Candidate Profile View

### Test Case 1: Profile Viewing
1. From preferences page, click on candidate to view profile
2. Expected: Candidate profile displays correctly
3. Verify back navigation works
4. Expected: Return to preferences page
5. Take screenshots of candidate profile view

### Test Case 2: Information Display
1. On candidate profile, verify appropriate information shown
2. Check role-specific information visibility
3. Verify organization display
4. Expected: Proper information filtering based on viewer role
5. Take screenshots of profile information

## Participant "My Match" Page After a Run

### Test Case 1: Match Display
1. Login as admin
2. Ensure at least one successful match run exists
3. Logout as admin
4. Login as participant who was matched
5. Navigate to match page: http://localhost:8000/cohort/{cohort_id}/my-match/
6. Expected: Own match pairing displayed
7. Take screenshots of match results

### Test Case 2: Privacy Controls
1. On match page, verify only own match visible
2. Try to access other participants' matches directly via URL
3. Expected: Access denied or redirected
4. Take screenshots of privacy enforcement

## CSV Import: Upload → Preview Errors → Confirm Apply → Verify Mentor Profile Fields

### Test Case 1: Upload Process
1. Login as admin
2. Navigate to CSV import: http://localhost:8000/import/mentor-csv/
3. Download CSV template
4. Expected: Template downloads successfully
5. Take screenshot of template download

### Test Case 2: Valid CSV Upload
1. Fill out CSV template with valid mentor data
2. Upload completed CSV
3. Expected: Upload successful, preview displayed
4. Take screenshots of upload process and preview

### Test Case 3: Error Preview
1. Create CSV with intentional errors:
   - Missing required fields
   - Invalid email formats
   - Duplicate usernames
2. Upload erroneous CSV
3. Expected: Errors highlighted in preview
4. Take screenshots of error highlighting

### Test Case 4: Import Confirmation
1. From preview (valid or corrected), confirm import
2. Expected: Import success message
3. Take screenshots of confirmation process

### Test Case 5: Data Verification
1. Check Postgres to verify imported data:
   ```bash
   docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "
   from apps.core.models import Participant
   from apps.matching.models import MentorProfile
   # Check imported participants
   participants = Participant.objects.filter(display_name__contains='CSV')
   print(f'CSV-imported participants: {participants.count()}')
   # Check mentor profiles
   mentor_profiles = MentorProfile.objects.filter(participant__in=participants)
   print(f'Mentor profiles: {mentor_profiles.count()}')
   "
   ```
2. Expected: Data properly stored in database
3. Take screenshots of DB verification

## Accessibility + Cross-Browser + Responsiveness Smoke

### Test Case 1: Keyboard Navigation
1. Navigate key pages using only keyboard (Tab, Enter, arrow keys)
2. Verify all interactive elements accessible
3. Expected: Complete keyboard operability
4. Take screenshots documenting navigation

### Test Case 2: Screen Reader Compatibility
1. Test with screen reader (if available) or check ARIA attributes
2. Verify form labels and descriptions
3. Expected: Proper semantic markup
4. Take screenshots of ARIA attributes

### Test Case 3: Cross-Browser Testing
1. Test key workflows in Chrome, Firefox, Safari (if available)
2. Verify consistent rendering
3. Expected: Same functionality across browsers
4. Take screenshots of browser differences

### Test Case 4: Responsive Design
1. Test key pages on different viewport sizes:
   - Desktop (>1024px)
   - Tablet (768px-1024px)
   - Mobile (<768px)
2. Verify layout adaptation
3. Expected: Proper responsive behavior
4. Take screenshots at different breakpoints

### Test Case 5: Color Contrast
1. Check key UI elements for color contrast compliance
2. Use accessibility tools or manual inspection
3. Expected: Minimum 4.5:1 contrast ratio for text
4. Take screenshots highlighting contrast issues

## Evidence Collection Points

Throughout testing, collect:
1. Screenshots of key workflows and error states
2. Playwright assertion results (automated testing)
3. Database verification queries and results
4. Browser compatibility comparisons
5. Responsive design variations
6. Accessibility testing results

## Defect Documentation

If defects found, document with:
- Clear title with area and browser/device reference
- Exact reproduction steps
- Observed vs expected behavior
- Supporting screenshots/assertion failures
- Severity classification (Critical/High/Medium/Low)