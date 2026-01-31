# Tester D - Participant UX + CSV Import + UI Non-Functional Summary

## Assignment Overview
**Tester D** is responsible for validating the participant user experience, CSV import workflows, and UI non-functional qualities of MatchLab:
- **Focus Areas**: Participant UX, CSV import workflow, UI non-functional qualities
- **Primary Goals**: Verify full non-admin experience and admin import workflow with Playwright assertions and Postgres validation
- **Key Workflows**: Registration/login, profile management, preferences UI, match viewing, CSV import, accessibility

## Key Documents for Tester D

1. **Test Plan**: `tester_d_plan.md` - Comprehensive test plan with methodology
2. **Test Script**: `tester_d_script.md` - Step-by-step execution guide
3. **Checklist**: `tester_d_checklist.md` - Progress tracking checklist
4. **Summary**: `tester_d_summary.md` - Executive summary and getting started guide

## Environment Information

- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: sophiemuller / test123 (participant without cohort assignment)
- **Available Cohorts**:
  - **Cohort 1**: "Engineering Mentoring Program 2026" (OPEN, 16 participants)
  - **Cohort 3**: "Test Cohort 5x5 Not Ready" (OPEN, 10 participants)

## Critical Validation Areas

### Participant User Experience (Highest Priority)
1. **End-to-End Participant Journey**:
   - Registration → Login → Cohort Selection → Profile Setup → Preferences → Matching → Results
2. **Profile Management**:
   - Mentor and mentee profile editing
   - Required field validation
   - Submission workflows
3. **Preferences Interface**:
   - Ranking mechanics
   - Duplicate rank handling
   - Read-only states after submission

### CSV Import Workflow
1. **Complete Import Process**:
   - Upload → Preview Errors → Confirm Apply → Verify Results
2. **Error Handling**:
   - Invalid data detection and highlighting
   - Correction workflow
   - Success/failure messaging
3. **Data Integrity**:
   - Postgres validation of imported data
   - Profile field population
   - Duplicate prevention

### UI Non-Functional Qualities
1. **Accessibility Compliance**:
   - WCAG guidelines adherence
   - Keyboard navigation support
   - Screen reader compatibility
2. **Cross-Browser Compatibility**:
   - Chrome, Firefox, Safari, Edge consistent behavior
   - Responsive design across browsers
3. **Responsive Design**:
   - Mobile, tablet, desktop layouts
   - Touch interaction support
   - Font scaling and readability

## Time Allocation Guidance

### Primary Focus (40% of time)
- Participant user experience workflows
- Registration/login through match viewing
- Profile and preferences UI validation

### Secondary Focus (35% of time)
- CSV import workflow validation
- Upload through Postgres verification
- Error handling and data integrity

### Tertiary Focus (25% of time)
- UI non-functional qualities
- Accessibility, cross-browser, responsiveness
- Playwright assertion validation

## Evidence Collection Requirements

### Must-have Evidence
1. Screenshots of key participant workflows
2. CSV import process and error handling
3. Playwright assertion results
4. Postgres validation queries and results
5. Accessibility and responsive design verification

### Nice-to-have Evidence (if time permits)
1. Cross-browser comparison screenshots
2. Keyboard navigation testing
3. Screen reader compatibility results
4. Color contrast analysis
5. Performance timing measurements

## Defect Prioritization

### Critical Issues (Report Immediately)
- Registration/login workflow blocking
- Profile data corruption or loss
- CSV import data integrity issues
- Accessibility barriers preventing usage

### High Priority Issues
- Preference ranking workflow failures
- Match result display errors
- Import error handling gaps
- Cross-browser functionality breaks

### Medium Priority Issues
- UI inconsistencies across devices
- Minor validation gaps
- Cosmetic issues affecting usability
- Documentation mismatches

## Available Test Scenarios

### Participant UX Testing
- **User**: sophiemuller (currently without cohort assignment)
- **Workflow**: Need to assign to cohort or create new participant journey
- **Existing Data**: Cohorts 1 and 3 available for testing
- **Match Runs**: Multiple existing runs for "my match" testing

### CSV Import Testing
- **Access**: Admin-only import interface at `/import/mentor-csv/`
- **Template**: Available for download with proper format
- **Validation**: Built-in error detection and preview
- **Verification**: Postgres queries to confirm data integrity

### UI Non-Functional Testing
- **Accessibility**: Built-in Bootstrap 5 components with ARIA attributes
- **Responsive**: Mobile-first Bootstrap grid system
- **Cross-Browser**: Modern browser support expected

## Getting Started

1. Review all three documents:
   - `tester_d_plan.md` (strategy)
   - `tester_d_script.md` (execution steps)
   - `tester_d_checklist.md` (progress tracking)

2. Start Docker environment if not already running:
   ```
   cd /home/ubuntu/matchlab
   docker compose -f docker-compose.dev.yml up -d
   ```

3. Begin with Registration/Login testing using sophiemuller user

4. Follow the test script for precise steps

5. Update checklist as you complete each test case

6. Collect evidence throughout the process

7. Report any defects immediately with proper formatting

## Support Information

If you encounter issues during testing:
- Check Docker container status: `docker compose -f docker-compose.dev.yml ps`
- Check application logs: `docker compose -f docker-compose.dev.yml logs app`
- Check database logs: `docker compose -f docker-compose.dev.yml logs db`
- Restart services if needed: `docker compose -f docker-compose.dev.yml restart`

## Special Notes for Tester D

1. **Focus on the participant journey** - This is the primary user experience
2. **Validate end-to-end workflows** - From registration to viewing matches
3. **Emphasize accessibility testing** - Critical for inclusive design
4. **Verify CSV import data integrity** - Use Postgres queries to confirm
5. **Test responsive behaviors** - Mobile usage is increasingly common
6. **Document Playwright assertions** - Automated validation is key for ongoing quality