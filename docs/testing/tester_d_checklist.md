# Tester D - Participant UX + CSV Import + UI Non-Functional Checklist

## Overview
This checklist tracks completion of testing for:
- **Focus**: Participant user experience, CSV import workflow, UI non-functional qualities
- **Goals**: Verify full non-admin experience and admin import workflow with Playwright assertions and Postgres validation

## Pre-testing Setup
- [ ] Docker environment verified running
- [ ] Admin user available (admin / admin123)
- [ ] Test user available (sophiemuller / test123)
- [ ] Test script reviewed
- [ ] Evidence collection folders created

## Registration/Login + Cohort Selector

### New User Registration
- [ ] Access registration page without login
- [ ] Complete registration form with valid data
- [ ] Verify account creation success
- [ ] Test validation errors (duplicate email, etc.)
- [ ] Screenshots captured

### Login Process
- [ ] Successful login with valid credentials
- [ ] Failed login with invalid credentials
- [ ] Session persistence across pages
- [ ] Proper logout functionality
- [ ] Screenshots captured

### Cohort Selection
- [ ] Single cohort access - direct access
- [ ] Multiple cohort access - selection UI
- [ ] Proper redirection based on cohort status
- [ ] Access control for closed/matched cohorts
- [ ] Screenshots captured

## Profile Pages (Mentor/Mentee)

### Mentor Profile Editing
- [ ] Access mentor-specific profile fields
- [ ] Edit and save profile information
- [ ] Test validation for required fields
- [ ] Verify organization field handling
- [ ] Screenshots captured

### Mentee Profile Editing
- [ ] Access mentee-specific profile fields
- [ ] Edit and save profile information
- [ ] Test validation for required fields
- [ ] Verify organization field handling
- [ ] Screenshots captured

### Profile Submission
- [ ] Submit profile for matching
- [ ] Confirm submission state change
- [ ] Verify read-only behavior after submission
- [ ] Screenshots captured

## Preferences UI (Including Duplicate Ranks, Readonly States)

### Preference Entry
- [ ] Access preference ranking interface
- [ ] Rank candidates with drag-and-drop or numeric entry
- [ ] Test duplicate rank assignment
- [ ] Verify real-time validation feedback
- [ ] Screenshots captured

### Duplicate Rank Handling
- [ ] Attempt to assign same rank to multiple candidates
- [ ] Verify system response (allow/disallow with messaging)
- [ ] Test rank normalization if implemented
- [ ] Confirm data integrity after submission
- [ ] Screenshots captured

### Readonly States
- [ ] Access preferences after submission
- [ ] Verify readonly presentation
- [ ] Confirm no editing capabilities
- [ ] Test print/view-only modes
- [ ] Screenshots captured

## Candidate Profile View

### Profile Viewing
- [ ] Access candidate profile from preferences UI
- [ ] View complete profile information
- [ ] Test back navigation
- [ ] Verify consistent styling
- [ ] Screenshots captured

### Information Display
- [ ] Role-specific information visibility
- [ ] Organization display
- [ ] Skills/interests presentation
- [ ] Photo/avatar display (if applicable)
- [ ] Screenshots captured

## Participant "My Match" Page After a Run

### Match Display
- [ ] Access match results after run completion
- [ ] View own match pairing
- [ ] Verify information appropriate for participant role
- [ ] Test error handling for unmatched participants
- [ ] Screenshots captured

### Privacy Controls
- [ ] Confirm only own match visible
- [ ] Verify no access to other participants' matches
- [ ] Test organization visibility rules
- [ ] Confirm proper data masking
- [ ] Screenshots captured

## CSV Import: Upload → Preview Errors → Confirm Apply → Verify Mentor Profile Fields

### Upload Process
- [ ] Access CSV import admin interface
- [ ] Upload valid CSV template
- [ ] Test invalid file type rejection
- [ ] Verify file size limitations
- [ ] Screenshots captured

### Error Preview
- [ ] Upload CSV with intentional errors
- [ ] Verify error highlighting and messaging
- [ ] Test correction workflow
- [ ] Confirm preview of valid rows
- [ ] Screenshots captured

### Import Confirmation
- [ ] Review import preview
- [ ] Confirm import application
- [ ] Verify success messaging
- [ ] Test rollback/cancellation if available
- [ ] Screenshots captured

### Data Verification
- [ ] Query Postgres to verify imported data
- [ ] Confirm profile field population
- [ ] Validate data types and constraints
- [ ] Test duplicate handling
- [ ] Screenshots captured

## Accessibility + Cross-Browser + Responsiveness Smoke

### Accessibility
- [ ] Keyboard navigation testing
- [ ] Screen reader compatibility
- [ ] Color contrast verification
- [ ] ARIA attributes presence
- [ ] Screenshots captured

### Cross-Browser
- [ ] Chrome compatibility
- [ ] Firefox compatibility
- [ ] Safari compatibility (if available)
- [ ] Edge compatibility (if available)
- [ ] Consistent rendering and functionality
- [ ] Screenshots captured

### Responsiveness
- [ ] Mobile layout testing (<768px)
- [ ] Tablet layout testing (768px-1024px)
- [ ] Desktop layout testing (>1024px)
- [ ] Touch interaction support
- [ ] Font scaling and readability
- [ ] Screenshots captured

## Evidence Collection

### Playwright Assertions
- [ ] Automated UI validation results
- [ ] Cross-browser compatibility verification
- [ ] Responsive design testing results
- [ ] Accessibility assertion checks

### Postgres Validation
- [ ] Direct database queries for data integrity
- [ ] Import data verification results
- [ ] Profile field population confirmation
- [ ] Relationship integrity checks

### Screenshots
- [ ] Registration and login flows
- [ ] Profile editing interfaces
- [ ] Preference ranking UI
- [ ] CSV import error previews
- [ ] Match results display
- [ ] Responsive design variations
- [ ] Accessibility testing results

## Defect Documentation
- [ ] Defect template ready
- [ ] Severity classification guidelines reviewed
- [ ] Evidence capture procedure established

## Completion Criteria
- [ ] All checklist items completed
- [ ] Evidence bundle assembled
- [ ] Run log documented
- [ ] Final report drafted