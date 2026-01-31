# Tester C - Ambiguity + Override + Auditability Summary

## Assignment Overview
**Tester C** is responsible for validating the ambiguity detection, manual override workflows, and auditability aspects of MatchLab:
- **Vertical Slices**: 5.10, 5.13, 9, 7 (sampling)
- **Focus Areas**: Ambiguity detection, manual override workflow, auditability/explainability, performance sampling
- **Primary Dataset**: C (Pathological/edge-case scenarios)
- **Secondary Dataset**: A (Override in normal conditions)
- **Tertiary Dataset**: B (Override after exception)

## Key Documents for Tester C

1. **Test Plan**: `tester_c_plan.md` - Comprehensive test plan with methodology
2. **Test Script**: `tester_c_script.md` - Step-by-step execution guide
3. **Checklist**: `tester_c_checklist.md` - Progress tracking checklist
4. **Summary**: `tester_c_summary.md` - Executive summary and getting started guide

## Environment Information

- **Application URL**: http://localhost:8000
- **Admin Credentials**: admin / admin123
- **Test User Credentials**: mentee2 / test123
- **Available Cohorts**:
  - **Cohort 1**: "Engineering Mentoring Program 2026" (Rich dataset, 16 participants)
  - **Cohort 3**: "Test Cohort 5x5 Not Ready" (10 participants)

## Critical Validation Areas

### Ambiguity Detection (Highest Priority)
1. Proper ambiguity flagging when score gaps ≤ threshold (~5.0)
2. Clear ambiguity reasoning with alternative candidates named
3. Threshold behavior compliance and edge case handling
4. DB persistence of ambiguity_flag and ambiguity_reason

### Manual Override Workflow
1. Intuitive override UI and workflow
2. Constraint preservation (one-to-one uniqueness)
3. Audit trail persistence (is_manual_override, override_reason)
4. Validation and error handling for improper overrides

### Auditability & Explainability
1. Results explainability with clear match scoring
2. Complete audit trail for all match decisions
3. Export integrity of audit fields
4. Match run metadata completeness

### Performance Sampling
1. Runtime expectations compliance (STRICT ~5s, EXCEPTION ~10s)
2. DB query efficiency and scalability
3. Stress scenario handling
4. Response time consistency

## Time Allocation Guidance

### Primary Focus (50% of time)
- Slice 5.10: Ambiguity Detection
- Slice 5.13: Manual Override Workflow
- Use existing ambiguous matches (Run 13 has 4)

### Secondary Focus (30% of time)
- Section 9: Auditability & Explainability
- Complete audit trail verification
- Export integrity testing

### Tertiary Focus (20% of time)
- Section 7: Performance & Scalability Sampling
- Runtime measurements
- Stress testing observations

## Evidence Collection Requirements

### Must-have Evidence
1. Screenshots of ambiguous matches with reasons
2. Override workflow and confirmation
3. DB verification of audit fields
4. Performance timing measurements
5. Validation error messages

### Nice-to-have Evidence (if time permits)
1. Screenshots of audit trail completeness
2. Export samples with audit fields
3. Stress test operation recordings
4. Threshold boundary testing
5. Edge case scenario documentation

## Defect Prioritization

### Critical Issues (Report Immediately)
- Missing or incorrect ambiguity detection
- Constraint violations in overrides
- Incomplete audit trails
- Data corruption in override processing

### High Priority Issues
- Unclear ambiguity/exception reasons
- Export integrity failures
- Performance degradation
- Poor override validation

### Medium Priority Issues
- UI inconsistencies in override workflow
- Minor audit field omissions
- Documentation mismatches
- Usability concerns

## Available Test Scenarios

### Dataset C - Pathological/Edge-case (Primary Focus)
Leverage existing data with ambiguities:
- **Run 13**: EXCEPTION mode on Cohort 1
- **4 Ambiguous Matches**: Clear test cases available
- **Score Details**: 
  - John Doe - Grace Wilson: Score 46.5 vs alternative 46.9
  - Mike Johnson - Lisa Kumar: Score 36.9 vs alternative 41.2
  - Sarah Wilson - David Brown: Score 42.8 vs alternative 37.8

### Dataset A - Override in Normal Conditions
- **Use**: Run 13 (EXCEPTION on Cohort 1)
- **Expected**: Clean override workflow testing
- **Audit**: Complete trail verification

### Dataset B - Override After Exception
- **Potential**: Recent runs on Cohort 3
- **Focus**: Consistency of override behavior
- **Validation**: Same requirements regardless of preceding mode

## Getting Started

1. Review all three documents:
   - `tester_c_plan.md` (strategy)
   - `tester_c_script.md` (execution steps)
   - `tester_c_checklist.md` (progress tracking)

2. Start Docker environment if not already running:
   ```
   cd /home/ubuntu/matchlab
   docker compose -f docker-compose.dev.yml up -d
   ```

3. Begin with Slice 5.10 (Ambiguity Detection) using Run 13

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

## Special Notes for Tester C

1. **Run 13 is your golden test case** - It has 4 pre-existing ambiguous matches
2. **Focus on the audit trail completeness** - Every match decision must be explainable
3. **Validate constraint preservation rigorously** - No participant should ever be matched twice
4. **Document performance observations** - Even sampling can reveal important scalability insights
5. **Test both positive and negative override cases** - Success workflows and validation errors