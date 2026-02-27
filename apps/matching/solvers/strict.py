"""Strict mode solver - pure OR-Tools model with hard constraints."""

import time
import logging
from typing import Dict, List, Tuple, Any, NamedTuple
from ortools.sat.python import cp_model
from ..data_prep import PreparedInputs

logger = logging.getLogger(__name__)


class StrictSolverResult(NamedTuple):
    """Result from strict solver."""

    success: bool
    matches: List[Dict[str, Any]]  # List of match dictionaries
    total_score: float
    avg_score: float
    solve_time: float
    failure_report: Dict[str, Any]  # Only populated when success=False


def solve_strict(inputs: PreparedInputs) -> StrictSolverResult:
    """
    Solve strict matching problem using OR-Tools CP-SAT.

    This is a pure function that operates only on in-memory data.

    Returns:
        StrictSolverResult with solution or failure report
    """
    logger.info(
        f"Solving strict matching for {len(inputs.mentor_ids)} mentors and {len(inputs.mentee_ids)} mentees"
    )

    # Get feasible pairs based on strict constraints
    feasible_pairs = _get_strict_feasible_pairs(inputs)

    # Check if we have enough feasible pairs
    feasible_count = sum(1 for is_feasible in feasible_pairs.values() if is_feasible)
    logger.info(
        f"Found {feasible_count} feasible pairs out of {len(inputs.mentor_ids) * len(inputs.mentee_ids)} total"
    )

    # Check for basic infeasibility conditions
    if len(inputs.mentor_ids) != len(inputs.mentee_ids):
        return StrictSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=0,
            failure_report={
                "reason": "COUNT_MISMATCH",
                "mentors_count": len(inputs.mentor_ids),
                "mentees_count": len(inputs.mentee_ids),
                "message": f"Unequal counts: {len(inputs.mentor_ids)} mentors vs {len(inputs.mentee_ids)} mentees",
            },
        )

    if len(inputs.mentor_ids) == 0:
        return StrictSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=0,
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
            if feasible_pairs[(mentor_id, mentee_id)]:
                x[(i, j)] = model.NewBoolVar(f"x[{i},{j}]")
            # For infeasible pairs, we don't create variables (implicitly 0)

    # Assignment constraints
    # Each mentor matched exactly once
    for mentor_id in inputs.mentor_ids:
        i = mentor_index_map[mentor_id]
        feasible_mentee_indices = [
            mentee_index_map[mentee_id]
            for mentee_id in inputs.mentee_ids
            if feasible_pairs[(mentor_id, mentee_id)]
        ]
        if feasible_mentee_indices:
            model.AddExactlyOne(x[(i, j)] for j in feasible_mentee_indices)
        else:
            # If no feasible mentees, add explicit infeasible constraint (0 = 1)
            model.Add(sum([]) == 1)  # This makes the model infeasible

    # Each mentee matched exactly once
    for mentee_id in inputs.mentee_ids:
        j = mentee_index_map[mentee_id]
        feasible_mentor_indices = [
            mentor_index_map[mentor_id]
            for mentor_id in inputs.mentor_ids
            if feasible_pairs[(mentor_id, mentee_id)]
        ]
        if feasible_mentor_indices:
            model.AddExactlyOne(x[(i, j)] for i in feasible_mentor_indices)
        else:
            # If no feasible mentors, add explicit infeasible constraint (0 = 1)
            model.Add(sum([]) == 1)  # This makes the model infeasible

    # Objective: maximize total score
    if x:  # Only if we have variables
        model.Maximize(
            sum(
                x[(i, j)] * inputs.score[(mentor_id, mentee_id)]
                for (i, j), var in x.items()
                for mentor_id, mentee_id in [
                    (inputs.mentor_ids[i], inputs.mentee_ids[j])
                ]
            )
        )

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = inputs.config.get("strict_time_limit", 5)

    start_time = time.time()
    status = solver.Solve(model)
    solve_time = time.time() - start_time

    logger.info(f"Strict solver status: {status}, time: {solve_time:.2f}s")

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # Extract solution
        matches = []
        total_score = 0

        for (i, j), var in x.items():
            if solver.Value(var) == 1:
                mentor_id = inputs.mentor_ids[i]
                mentee_id = inputs.mentee_ids[j]
                score = inputs.score[(mentor_id, mentee_id)] / inputs.config.get(
                    "score_scale", 1000
                )
                matches.append(
                    {"mentor_id": mentor_id, "mentee_id": mentee_id, "score": score}
                )
                total_score += score

        avg_score = total_score / len(matches) if matches else 0

        logger.info(
            f"Strict matching completed with {len(matches)} matches, total score: {total_score}"
        )

        return StrictSolverResult(
            success=True,
            matches=matches,
            total_score=total_score,
            avg_score=avg_score,
            solve_time=solve_time,
            failure_report={},
        )

    else:
        # Infeasible or timeout
        failure_report = {
            "reason": "INFEASIBLE" if status == cp_model.INFEASIBLE else "TIMEOUT",
            "mentors_count": len(inputs.mentor_ids),
            "mentees_count": len(inputs.mentee_ids),
            "feasible_pairs_count": feasible_count,
            "solve_time": solve_time,
        }

        # Add diagnostics about blockers
        # Count mentors/mentees with zero feasible options
        zero_mentor_options = []
        for mentor_id in inputs.mentor_ids:
            feasible_count = sum(
                1
                for mentee_id in inputs.mentee_ids
                if feasible_pairs[(mentor_id, mentee_id)]
            )
            if feasible_count == 0:
                zero_mentor_options.append({"id": mentor_id})

        zero_mentee_options = []
        for mentee_id in inputs.mentee_ids:
            feasible_count = sum(
                1
                for mentor_id in inputs.mentor_ids
                if feasible_pairs[(mentor_id, mentee_id)]
            )
            if feasible_count == 0:
                zero_mentee_options.append({"id": mentee_id})

        failure_report["zero_mentor_options"] = zero_mentor_options
        failure_report["zero_mentee_options"] = zero_mentee_options

        logger.info(f"Strict solve failed: {failure_report['reason']}")

        return StrictSolverResult(
            success=False,
            matches=[],
            total_score=0,
            avg_score=0,
            solve_time=solve_time,
            failure_report=failure_report,
        )


def _get_strict_feasible_pairs(inputs: PreparedInputs) -> Dict[Tuple[int, int], bool]:
    """
    Determine which pairs are feasible in strict mode.

    A pair is feasible if:
    1. Different organizations
    2. Mutual acceptability (both ranked each other)
    """
    feasible = {}

    for mentor_id in inputs.mentor_ids:
        for mentee_id in inputs.mentee_ids:
            # Check organization constraint
            org_constraint = not inputs.same_org[(mentor_id, mentee_id)]

            # Check mutual acceptability
            mutual_acceptable = inputs.acceptability[(mentor_id, mentee_id)] == "MUTUAL"

            feasible[(mentor_id, mentee_id)] = org_constraint and mutual_acceptable

    return feasible
