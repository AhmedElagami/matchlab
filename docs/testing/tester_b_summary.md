# Tester B - Failure + Exception + Labeling Summary

## Assignment Overview
**Tester B** is responsible for validating the failure handling, exception processing, and labeling correctness aspects of MatchLab:
- **Vertical Slices**: 5.7, 5.8, 5.9, 6, 8
- **Focus Areas**: Strict failure reporting, exception matching execution, exception labeling correctness, solver validation, failure resilience
- **Primary Dataset**: B (Strict-infeasible scenarios)
- **Secondary Dataset**: C (Penalty ordering scenarios)
- **Baseline Dataset**: A (Happy-path for comparison)

## Key Documents for Tester B

1. **Test Plan**: `tester_b_plan.md`
   - Detailed testing approach and methodology
   - Evidence collection requirements
   - Defect reporting format

2. **Test Script**: `tester_b_script.md`
   - Step-by-step testing procedures
   - Specific test cases with expected outcomes
   - URL paths and navigation instructions

3. **Checklist**: `tester_b_checklist.md`
   - Progress tracking for all test cases
   - Completion verification
   - Evidence collection points

## Environment Information

- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: mentor21 / test123, mentee21 / test123
- **Available Cohorts**:
  - **Cohort 1**: "Engineering Mentoring Program 2026" (Baseline, 16 participants)
  - **Cohort 3**: "Test Cohort 5x5 Not Ready" (Primary for failure testing, 10 participants)

## Critical Validation Areas

### Failure Detection & Reporting (Highest Priority)
1. Strict mode infeasibility detection
2. Meaningful failure reports with actionable information
3. UI guidance for recovery paths
4. DB persistence of failure details

### Exception Processing & Labeling
1. EXCEPTION mode execution and success handling
2. Complete assignment generation (N matches for N participants)
3. Correct exception type assignment (E1/E2/E3)
4. Clear exception reasoning and justification

### Solver Behavior Validation
1. Strict mode constraint enforcement (never violated)
2. Exception mode completeness guarantee
3. Penalty ordering compliance (E3 > E2 > E1)
4. Deterministic behavior across identical runs

### Resilience & Error Handling
1. Bad input validation and rejection
2. Partial data scenario handling
3. Timeout behavior and reporting
4. Infeasible model detection and reporting

## Time Allocation Guidance

### Primary Focus (60% of time)
- Slice 5.7: Strict Failure Reporting
- Slice 5.8: Exception Matching Execution
- Slice 5.9: Exception Labeling Correctness

### Secondary Focus (25% of time)
- Section 6: Solver-Specific Validation
- Verification of penalty ordering
- Determinism testing

### Tertiary Focus (15% of time)
- Section 8: Failure Mode & Resilience Testing
- Dataset A baseline comparison
- Edge case validation

## Evidence Collection Requirements

### Must-have Evidence
1. Screenshots of strict failure reports
2. Exception results with labeled violations
3. DB verification of MatchRun states
4. Match samples with different exception types
5. Determinism comparison results

### Nice-to-have Evidence (if time permits)
1. Screenshots of UI guidance and next steps
2. Validation error messages
3. Timeout behavior documentation
4. Solver mode and duration logs
5. Infeasible model reporting examples

## Defect Prioritization

### Critical Issues (Report Immediately)
- Strict constraint violations in STRICT mode
- Incomplete matching in EXCEPTION mode
- Wrong exception type labeling
- Missing or misleading failure reports

### High Priority Issues
- Incorrect penalty ordering
- Non-deterministic solver behavior
- Poor error recovery guidance
- Data corruption in failure scenarios

### Medium Priority Issues
- Unclear exception reasons
- UI inconsistencies in failure reporting
- Minor validation gaps
- Performance degradation in error cases

## Available Test Scenarios

### Dataset B - Strict-infeasible (Cohort 3)
This cohort is ideal for failure testing:
- **5 Mentors**: All submitted
- **5 Mentees**: 4 submitted, 1 not submitted
- **Minimal Preferences**: Only one mutual pair (mentor21 ↔ mentee21)
- **Expected STRICT Behavior**: Fail due to insufficient mutual acceptability
- **Expected EXCEPTION Behavior**: Success with exception labeling

### Dataset C - Penalty Ordering (To be constructed)
Will need to create specific scenarios for:
- **E3 (Same Org)**: Force same-organization pairings
- **E2 (Neither Acceptable)**: Pair participants who didn't rank each other
- **E1 (One-sided)**: Pair where only one participant ranked the other

### Dataset A - Baseline (Cohort 1)
Existing cohort for regression testing:
- **9 Mentors**: All submitted
- **7 Mentees**: All submitted
- **Multiple Successful Runs**: Both STRICT and EXCEPTION
- **Use**: Compare behavior, validate no regression

## Getting Started

1. Review all three documents:
   - `tester_b_plan.md` (strategy)
   - `tester_b_script.md` (execution steps)
   - `tester_b_checklist.md` (progress tracking)

2. Start Docker environment if not already running:
   ```
   cd /home/ubuntu/matchlab
   docker compose -f docker-compose.dev.yml up -d
   ```

3. Begin with Slice 5.7 (Strict Failure Reporting) using Cohort 3

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

## Special Notes for Tester B

1. **Cohort 3 is your primary testing ground** - Its minimal preferences make it ideal for failure scenarios
2. **Focus on the difference between STRICT and EXCEPTION modes** - This is core to your assignment
3. **Pay special attention to exception labeling accuracy** - E1/E2/E3 must be correctly assigned
4. **Verify penalty ordering when constructing Dataset C scenarios** - E3 should always dominate
5. **Document determinism testing thoroughly** - Solver behavior should be predictable