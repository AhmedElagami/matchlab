# Tester A - Security + Core Strict Flow Summary

## Assignment Overview
**Tester A** is responsible for validating the security and core strict flow aspects of MatchLab:
- **Vertical Slices**: 5.1, 5.2, 5.3, 5.6, 5.11, 5.12, 5.15
- **Focus Areas**: Authentication, access control, cohort/participant management, strict matching execution, run history, CSV exports, UI consistency
- **Primary Dataset**: A (Happy-path)
- **Secondary Dataset**: B (Access-control impacts)
- **Sanity Check**: Quick C validation

## Key Documents for Tester A

1. **Test Plan**: `tester_a_plan.md`
   - Detailed testing approach and methodology
   - Evidence collection requirements
   - Defect reporting format

2. **Test Script**: `tester_a_script.md`
   - Step-by-step testing procedures
   - Specific test cases with expected outcomes
   - URL paths and navigation instructions

3. **Checklist**: `tester_a_checklist.md`
   - Progress tracking for all test cases
   - Completion verification
   - Evidence collection points

## Environment Information

- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Starting Point**: Clean database with only admin user
- **Test Data**: Generated on-demand using dataset generators
- **Approach**: Start with zero data, generate datasets as needed for testing

## Critical Validation Areas

### Security Boundaries (Highest Priority)
1. Authentication enforcement on all protected pages
2. Role-based access control (admin vs participant)
3. IDOR prevention (direct object reference attacks)
4. CSRF protection on forms
5. Cross-cohort data isolation

### Core Strict Flow Validation
1. STRICT mode execution and success handling
2. Constraint enforcement (cross-org, mutual acceptability)
3. Deterministic matching behavior
4. Results completeness and correctness
5. Export functionality for STRICT runs

### Data Integrity Points
1. Cohort creation and configuration
2. Participant uniqueness constraints
3. Profile data validation
4. Run history immutability
5. Export data consistency

## Time Allocation Guidance

### Primary Focus (70% of time)
- Slice 5.1: Authentication & Access Control
- Slice 5.6: Strict Matching Execution
- Slice 5.12: CSV Export Correctness

### Secondary Focus (20% of time)
- Slice 5.2: Cohort Creation & Configuration
- Slice 5.3: Participant Management
- Slice 5.11: Run History & Detail Views

### Tertiary Focus (10% of time)
- Slice 5.15: UI Consistency Across Modes
- Dataset B access-control impact testing
- Quick Dataset C sanity checks

## Evidence Collection Requirements

### Must-have Evidence
1. Screenshots of key authentication flows
2. Access denied/error page screenshots
3. Successful STRICT mode run results
4. CSV export files from different modes
5. Database snapshots of match_run and match records

### Nice-to-have Evidence (if time permits)
1. Screenshots of admin interface operations
2. Profile editing validation errors
3. Run history consistency verification
4. UI structure comparisons
5. Log captures around match executions

## Defect Prioritization

### Critical Issues (Report Immediately)
- Any access control bypass
- STRICT mode constraint violations
- Data corruption or loss
- Missing matches in SUCCESS runs

### High Priority Issues
- Incorrect export content/format
- Non-deterministic matching behavior
- Authentication flow failures
- CSRF protection gaps

### Medium Priority Issues
- UI inconsistencies
- Minor validation gaps
- Usability concerns
- Documentation mismatches

## Deliverables for Tester A

1. **Run Log**
   - Dataset used
   - Match run IDs tested
   - Pass/fail status per slice

2. **Evidence Bundle**
   - Key screenshots (authentication, access control, results)
   - Exported CSV files (STRICT and EXCEPTION modes)
   - Relevant application logs
   - Database verification notes

3. **Defect Reports** (if any found)
   - Formatted per specification
   - Including steps to reproduce
   - With supporting evidence

## Getting Started

1. Review all three documents:
   - `tester_a_plan.md` (strategy)
   - `tester_a_script.md` (execution steps)
   - `tester_a_checklist.md` (progress tracking)

2. Start Docker environment if not already running:
   ```
   cd /home/ubuntu/matchlab
   docker compose -f docker-compose.dev.yml up -d
   ```

3. Begin with Slice 5.1 (Authentication & Access Control) testing

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