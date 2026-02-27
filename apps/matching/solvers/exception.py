"""Exception mode solver - pure OR-Tools model with penalties."""

import time
import logging
from typing import Dict, List, Tuple, Any, NamedTuple
from ortools.sat.python import cp_model
from ..data_prep import PreparedInputs
from ..domain import get_penalty_info

logger = logging.getLogger(__name__)


class ExceptionSolverResult(NamedTuple):
    """Result from exception solver."""

    success: bool
    matches: List[Dict[str, Any]]  # List of match dictionaries
    total_score: float
    avg_score: float
    solve_time: float
    exception_count: int
    exception_summary: Dict[str, int]  # Count by exception type
    failure_report: Dict[str, Any]  # Only populated when success=False


def solve_exception(inputs: PreparedInputs) -> ExceptionSolverResult:
    """
    Solve exception matching problem using OR-Tools CP-SAT.

    This is a pure function that operates only on in-memory data.
    Allows all pairs but applies penalties for policy violations.

    Returns:
        ExceptionSolverResult with solution or failure report
    """
    logger.info(
        f"Solving exception matching for {len(inputs.mentor_ids)} mentors and {len(inputs.mentee_ids)} mentees"
    )

    # Check for basic infeasibility conditions
    if len(inputs.mentor_ids) != len(inputs.mentee_ids):
        return ExceptionSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=0,
            exception_count=0,
            exception_summary={},
            failure_report={
                "reason": "COUNT_MISMATCH",
                "mentors_count": len(inputs.mentor_ids),
                "mentees_count": len(inputs.mentee_ids),
                "message": f"Unequal counts: {len(inputs.mentor_ids)} mentors vs {len(inputs.mentee_ids)} mentees",
            },
        )

    if len(inputs.mentor_ids) == 0:
        return ExceptionSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=0,
            exception_count=0,
            exception_summary={},
            failure_report={
                "reason": "NO_PARTICIPANTS",
                "message": "No submitted participants found",
            },
        )

    # Create the model
    model = cp_model.CpModel()

    # Create variables
    x = {}  # x[i,j] = 1 if mentor i is matched to mentee j
    mentor_index_map = {mid: i for i, mid in enumerate(inputs.mentor_ids)}
    mentee_index_map = {mid: j for j, mid in enumerate(inputs.mentee_ids)}

    for mentor_id in inputs.mentor_ids:
        i = mentor_index_map[mentor_id]
        for mentee_id in inputs.mentee_ids:
            j = mentee_index_map[mentee_id]
            x[(i, j)] = model.NewBoolVar(f"x[{i},{j}]")

    # Assignment constraints - each participant matched exactly once
    # Each mentor matched exactly once
    for i in range(len(inputs.mentor_ids)):
        model.AddExactlyOne(x[(i, j)] for j in range(len(inputs.mentee_ids)))

    # Each mentee matched exactly once
    for j in range(len(inputs.mentee_ids)):
        model.AddExactlyOne(x[(i, j)] for i in range(len(inputs.mentor_ids)))

    # Objective: maximize total score - penalties
    # We'll create penalty variables for each match
    penalty_vars = []
    penalty_coeffs = []

    for mentor_id in inputs.mentor_ids:
        i = mentor_index_map[mentor_id]
        for mentee_id in inputs.mentee_ids:
            j = mentee_index_map[mentee_id]

            # Apply penalties based on exception type
            penalty_info = get_penalty_info(mentor_id, mentee_id, inputs)

            if penalty_info.penalty_type:  # Has penalty
                penalty_var = model.NewIntVar(
                    0, 1, f"penalty_{penalty_info.penalty_type}_{i}_{j}"
                )
                model.Add(penalty_var == x[(i, j)])  # penalty = 1 if matched
                penalty_vars.append(penalty_var)
                penalty_coeffs.append(penalty_info.penalty_value)

    # Objective: maximize score - penalties
    score_term = sum(
        x[(i, j)] * inputs.score[(mentor_id, mentee_id)]
        for (i, j), var in x.items()
        for mentor_id, mentee_id in [(inputs.mentor_ids[i], inputs.mentee_ids[j])]
    )

    if penalty_vars:
        penalty_term = sum(
            penalty_var * penalty_coeff
            for penalty_var, penalty_coeff in zip(penalty_vars, penalty_coeffs)
        )
        model.Maximize(score_term - penalty_term)
    else:
        model.Maximize(score_term)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = inputs.config.get(
        "exception_time_limit", 10
    )

    start_time = time.time()
    status = solver.Solve(model)
    solve_time = time.time() - start_time

    logger.info(f"Exception solver status: {status}, time: {solve_time:.2f}s")

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # Extract solution
        matches = []
        total_score = 0
        exception_count = 0
        exception_summary = {"E1": 0, "E2": 0, "E3": 0}

        for (i, j), var in x.items():
            if solver.Value(var) == 1:
                mentor_id = inputs.mentor_ids[i]
                mentee_id = inputs.mentee_ids[j]
                score = inputs.score[(mentor_id, mentee_id)] / inputs.config.get(
                    "score_scale", 1000
                )

                # Check for exceptions
                from ..domain import classify_exception

                exception_classification = classify_exception(
                    mentor_id, mentee_id, inputs
                )
                is_exception = exception_classification.exception_type != ""

                if is_exception:
                    exception_count += 1
                    exception_summary[exception_classification.exception_type] += 1

                matches.append(
                    {
                        "mentor_id": mentor_id,
                        "mentee_id": mentee_id,
                        "score": score,
                        "exception_flag": is_exception,
                        "exception_type": exception_classification.exception_type,
                        "exception_reason": exception_classification.reason,
                    }
                )
                total_score += score

        avg_score = total_score / len(matches) if matches else 0

        logger.info(
            f"Exception matching completed with {len(matches)} matches, "
            f"{exception_count} exceptions, total score: {total_score}"
        )

        return ExceptionSolverResult(
            success=True,
            matches=matches,
            total_score=total_score,
            avg_score=avg_score,
            solve_time=solve_time,
            exception_count=exception_count,
            exception_summary=exception_summary,
            failure_report={},
        )

    else:
        # Infeasible or timeout (should not happen with exception mode)
        failure_report = {
            "reason": "INFEASIBLE" if status == cp_model.INFEASIBLE else "TIMEOUT",
            "mentors_count": len(inputs.mentor_ids),
            "mentees_count": len(inputs.mentee_ids),
            "solve_time": solve_time,
        }

        logger.info(f"Exception solve failed: {failure_report['reason']}")

        return ExceptionSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=solve_time,
            exception_count=0,
            exception_summary={},
            failure_report=failure_report,
        )
