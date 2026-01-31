# Tester D - Participant UX + CSV Import + UI Non-Functional Test Plan

## Overview
This test plan covers the vertical feature slices assigned to Tester D:
- **Focus Areas**: Participant user experience, CSV import workflow, UI non-functional qualities
- **Primary Goals**: Verify full non-admin experience and admin import workflow with Playwright assertions and Postgres validation

## Environment Information
- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: sophiemuller / test123 (participant without cohort assignment)
- **Available Cohorts**:
  - Cohort 1: "Engineering Mentoring Program 2026" (OPEN)
  - Cohort 3: "Test Cohort 5x5 Not Ready" (OPEN)

## Test Execution Strategy

### Registration/Login + Cohort Selector

#### Test Objectives:
1. Validate complete registration flow for new participants
2. Verify login process and session management
3. Test cohort selection for users in multiple cohorts
4. Confirm proper redirection and user state handling

#### Test Cases:
1. **New User Registration**:
   - Access registration page without login
   - Complete registration form with valid data
   - Verify account creation and email confirmation (if applicable)
   - Test validation errors (duplicate email, weak password, etc.)

2. **Login Process**:
   - Successful login with valid credentials
   - Failed login with invalid credentials
   - Session persistence across pages
   - Proper logout functionality

3. **Cohort Selection**:
   - Users with access to single cohort - direct access
   - Users with access to multiple cohorts - selection UI
   - Proper redirection based on cohort status
   - Access control for closed/matched cohorts

### Profile Pages (Mentor/Mentee)

#### Test Objectives:
1. Validate profile editing for both mentor and mentee roles
2. Verify required field validation and error handling
3. Test organization field normalization and validation
4. Confirm profile submission workflow

#### Test Cases:
1. **Mentor Profile**:
   - Access mentor-specific profile fields
   - Edit and save profile information
   - Test validation for required fields
   - Verify organization field handling

2. **Mentee Profile**:
   - Access mentee-specific profile fields
   - Edit and save profile information
   - Test validation for required fields
   - Verify organization field handling

3. **Profile Submission**:
   - Submit profile for matching
   - Confirm submission state change
   - Verify read-only behavior after submission
   - Test withdrawal/unsubmission if available

### Preferences UI (Including Duplicate Ranks, Readonly States)

#### Test Objectives:
1. Validate preference entry UI for both roles
2. Verify duplicate rank handling and validation
3. Test readonly states for submitted preferences
4. Confirm preference submission workflow

#### Test Cases:
1. **Preference Entry**:
   - Access preference ranking interface
   - Rank candidates with drag-and-drop or numeric entry
   - Test duplicate rank assignment
   - Verify real-time validation feedback

2. **Duplicate Rank Handling**:
   - Attempt to assign same rank to multiple candidates
   - Verify system response (allow/disallow with messaging)
   - Test rank normalization if implemented
   - Confirm data integrity after submission

3. **Readonly States**:
   - Access preferences after submission
   - Verify readonly presentation
   - Confirm no editing capabilities
   - Test print/view-only modes

### Candidate Profile View

#### Test Objectives:
1. Validate candidate profile viewing functionality
2. Verify proper information display based on user role
3. Test search and filtering capabilities
4. Confirm access control restrictions

#### Test Cases:
1. **Profile Viewing**:
   - Access candidate profile from preferences UI
   - View complete profile information
   - Test back navigation
   - Verify consistent styling

2. **Information Display**:
   - Role-specific information visibility
   - Organization display
   - Skills/interests presentation
   - Photo/avatar display (if applicable)

### Participant "My Match" Page After a Run

#### Test Objectives:
1. Validate match result display for participants
2. Verify proper information masking for privacy
3. Test export/download capabilities (if available)
4. Confirm responsive design and accessibility

#### Test Cases:
1. **Match Display**:
   - Access match results after run completion
   - View own match pairing
   - Verify information appropriate for participant role
   - Test error handling for unmatched participants

2. **Privacy Controls**:
   - Confirm only own match visible
   - Verify no access to other participants' matches
   - Test organization visibility rules
   - Confirm proper data masking

### CSV Import: Upload → Preview Errors → Confirm Apply → Verify Mentor Profile Fields

#### Test Objectives:
1. Validate complete CSV import workflow
2. Verify error detection and preview functionality
3. Test import confirmation and application
4. Confirm data integrity through Postgres validation

#### Test Cases:
1. **Upload Process**:
   - Access CSV import admin interface
   - Upload valid CSV template
   - Test invalid file type rejection
   - Verify file size limitations

2. **Error Preview**:
   - Upload CSV with intentional errors
   - Verify error highlighting and messaging
   - Test correction workflow
   - Confirm preview of valid rows

3. **Import Confirmation**:
   - Review import preview
   - Confirm import application
   - Verify success messaging
   - Test rollback/cancellation if available

4. **Data Verification**:
   - Query Postgres to verify imported data
   - Confirm profile field population
   - Validate data types and constraints
   - Test duplicate handling

### Accessibility + Cross-Browser + Responsiveness Smoke

#### Test Objectives:
1. Validate WCAG accessibility compliance
2. Verify cross-browser compatibility
3. Test responsive design across device sizes
4. Confirm keyboard navigation support

#### Test Cases:
1. **Accessibility**:
   - Keyboard navigation testing
   - Screen reader compatibility
   - Color contrast verification
   - ARIA attributes presence

2. **Cross-Browser**:
   - Chrome, Firefox, Safari, Edge compatibility
   - Consistent rendering and functionality
   - Form submission behavior
   - JavaScript-dependent features

3. **Responsiveness**:
   - Mobile, tablet, desktop layouts
   - Touch interaction support
   - Font scaling and readability
   - Orientation change handling

## Evidence Collection Requirements

### Playwright Assertions
1. Automated UI validation for key workflows
2. Cross-browser compatibility verification
3. Responsive design testing
4. Accessibility assertion checks

### Postgres Validation
1. Direct database queries to verify data integrity
2. Import data verification
3. Profile field population confirmation
4. Relationship integrity checks

### Screenshots Needed
1. Registration and login flows
2. Profile editing interfaces
3. Preference ranking UI
4. CSV import error previews
5. Match results display
6. Responsive design variations
7. Accessibility testing results

## Defect Reporting Format
For each defect found:
- Title: `[Area] [Browser/Device] Symptom`
- Steps to reproduce: exact sequence
- Observed vs expected
- Evidence: screenshots/assertion failures + DB query results
- Severity:
  - Critical: Registration/login blocking, data corruption, security issues
  - High: Import workflow failures, profile data loss, accessibility barriers
  - Medium/Low: UI inconsistencies, minor validation gaps, cosmetic issues