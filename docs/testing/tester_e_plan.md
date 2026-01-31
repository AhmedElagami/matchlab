# Tester E Plan — Scale + Combinatorial Edge Cases

## Objective
Validate system correctness and UI stability under:
- very large cohorts
- extreme preference patterns
- degenerate/adversarial datasets
- partial submissions across many cohorts

Validation must include:
- Playwright MCP UI flows (admin run + results + export + override when applicable)
- Postgres MCP assertions after each run
- Evidence artifacts and reproducible dataset bundles

## In scope
- Dataset generation/loading for large and adversarial data
- Match run behavior: strict mode, exception behavior (if triggered), determinism checks
- Exports for large cohorts (CSV generation and content sanity)
- UI correctness under heavy tables/lists (rendering, paging, search/filter if present)
- Partial submission correctness

## Out of scope
- Deep accessibility beyond smoke checks
- Cross-browser testing (unless explicitly required)

## Pass criteria
- No console errors or failed network calls during runs/results for large datasets
- Matching results adhere to constraints in TECHNICAL_SPEC.md
- DB rows match expected counts and integrity invariants
- Determinism: repeated runs on identical seed produce identical results (where required)
- Partial submissions: only eligible participants included

## Test Strategy

### Dataset Generation Approach
1. **Custom Data Generator**: Create `artifacts/datasets/generate_E_dataset.py` 
   - Deterministic random seed support
   - Configurable cohort sizes (N=30 as maximum)
   - Various adversarial patterns
   - Fixture export capability

2. **Dataset Scenarios**:
   - E1: Large cohort baseline (N=30)
   - E2: Very high contention preferences
   - E3: Sparse/missing preferences
   - E4: Degenerate ranks
   - E5: Many cohorts with partial submissions
   - E6: Performance sampling

### Validation Methodology
1. **Playwright MCP UI Flows**:
   - Admin login and navigation
   - Run matching (strict and exception modes)
   - Results viewing and export
   - Override application (when applicable)

2. **Postgres MCP Assertions**:
   - MatchRun integrity validation
   - Match row count consistency
   - Flag/reason field correctness
   - Foreign key relationship integrity

3. **Evidence Collection**:
   - UI screenshots at key workflow steps
   - Network/console logs for error detection
   - Database query outputs for integrity verification
   - Exported CSVs for content validation
   - Performance timing reports

## Risk Areas

### Scale Risks
- UI rendering performance degradation
- Database query N×N explosion
- Memory consumption during matching
- Export generation timeouts

### Combinatorial Risks
- Tie-breaking determinism
- Preference validation edge cases
- Rank normalization boundary conditions
- Exception labeling accuracy under stress

### Data Integrity Risks
- Partial submission leakage
- Orphaned database records
- Inconsistent flag propagation
- Export data fidelity

## Test Environment Requirements
- Clean database state for each scenario
- Sufficient system resources for N=30 cohorts
- Playwright browser automation setup
- Postgres database access for assertions
- Artifact storage directory structure