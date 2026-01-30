"""OR-Tools CP-SAT solver for mentor-mentee matching."""

import time
import logging
from typing import Dict, List, Tuple, Any
from ortools.sat.python import cp_model
from apps.core.models import Participant
from apps.matching.models import Preference, PairScore
from apps.matching.exceptions import classify_exception

logger = logging.getLogger(__name__)

# Time limits for solvers
STRICT_TIME_LIMIT = 5  # seconds
EXCEPTION_TIME_LIMIT = 10  # seconds

# Penalty values for exception mode (scaled to ensure priority ordering)
PENALTY_ORG = 1000000
PENALTY_ONE_SIDED = 100000
PENALTY_NEITHER = 300000
SCORE_SCALE = 1000


def get_strict_feasible_pairs(
    mentors: List[Participant], mentees: List[Participant]
) -> Dict[Tuple[int, int], bool]:
    """
    Determine which pairs are feasible in strict mode.

    A pair is feasible if:
    1. Different organizations
    2. Mutual acceptability (both ranked each other)
    """
    # Build preference lookup maps
    mentor_accepts = {}  # mentor_id -> set of mentee_ids
    mentee_accepts = {}  # mentee_id -> set of mentor_ids

    for mentor in mentors:
        mentor_accepts[mentor.id] = set()
        prefs = Preference.objects.filter(from_participant=mentor)
        for pref in prefs:
            mentor_accepts[mentor.id].add(pref.to_participant.id)

    for mentee in mentees:
        mentee_accepts[mentee.id] = set()
        prefs = Preference.objects.filter(from_participant=mentee)
        for pref in prefs:
            mentee_accepts[mentee.id].add(pref.to_participant.id)

    # Determine feasible pairs
    feasible = {}
    for mentor in mentors:
        for mentee in mentees:
            # Check organization constraint
            org_constraint = mentor.organization != mentee.organization

            # Check mutual acceptability
            mutual_acceptable = mentee.id in mentor_accepts.get(
                mentor.id, set()
            ) and mentor.id in mentee_accepts.get(mentee.id, set())

            feasible[(mentor.id, mentee.id)] = org_constraint and mutual_acceptable

    return feasible


def get_pair_scores(
    mentors: List[Participant], mentees: List[Participant], cohort
) -> Dict[Tuple[int, int], float]:
    """
    Get precomputed pair scores from database.
    """
    scores = {}

    # Get all pair scores for this cohort
    pair_scores = PairScore.objects.filter(cohort=cohort)

    # Create lookup dictionary
    score_lookup = {}
    for ps in pair_scores:
        score_lookup[(ps.mentor.id, ps.mentee.id)] = ps.score

    # Fill in scores matrix
    for mentor in mentors:
        for mentee in mentees:
            scores[(mentor.id, mentee.id)] = score_lookup.get(
                (mentor.id, mentee.id), 0.0
            )

    return scores


def solve_strict(
    mentors: List[Participant], mentees: List[Participant], cohort
) -> Tuple[bool, Dict[str, Any]]:
    """
    Solve strict matching problem using OR-Tools CP-SAT.

    Returns:
        Tuple of (success: bool, result: dict)
    """
    logger.info(
        f"Solving strict matching for {len(mentors)} mentors and {len(mentees)} mentees"
    )

    # Get feasible pairs
    feasible_pairs = get_strict_feasible_pairs(mentors, mentees)

    # Check if we have enough feasible pairs
    feasible_count = sum(1 for is_feasible in feasible_pairs.values() if is_feasible)
    logger.info(
        f"Found {feasible_count} feasible pairs out of {len(mentors) * len(mentees)} total"
    )

    # Get scores
    scores = get_pair_scores(mentors, mentees, cohort)

    # Create the model
    model = cp_model.CpModel()

    # Create variables
    x = {}  # x[i,j] = 1 if mentor i is matched to mentee j
    for i, mentor in enumerate(mentors):
        for j, mentee in enumerate(mentees):
            if feasible_pairs[(mentor.id, mentee.id)]:
                x[(i, j)] = model.NewBoolVar(f"x[{i},{j}]")
            # For infeasible pairs, we don't create variables (implicitly 0)

    # Assignment constraints
    # Each mentor matched exactly once
    for i, mentor in enumerate(mentors):
        feasible_mentee_indices = [
            j
            for j, mentee in enumerate(mentees)
            if feasible_pairs[(mentor.id, mentee.id)]
        ]
        if feasible_mentee_indices:
            model.AddExactlyOne(x[(i, j)] for j in feasible_mentee_indices)
        else:
            # If no feasible mentees, add explicit infeasible constraint (0 = 1)
            model.Add(sum([]) == 1)  # This makes the model infeasible

    # Each mentee matched exactly once
    for j, mentee in enumerate(mentees):
        feasible_mentor_indices = [
            i
            for i, mentor in enumerate(mentors)
            if feasible_pairs[(mentor.id, mentee.id)]
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
                x[(i, j)] * int(scores[(mentor.id, mentee.id)] * SCORE_SCALE)
                for (i, j), var in x.items()
                for mentor, mentee in [(mentors[i], mentees[j])]
            )
        )

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = STRICT_TIME_LIMIT

    start_time = time.time()
    status = solver.Solve(model)
    solve_time = time.time() - start_time

    logger.info(f"Solver status: {status}, time: {solve_time:.2f}s")

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # Extract solution
        matches = []
        total_score = 0

        for (i, j), var in x.items():
            if solver.Value(var) == 1:
                mentor = mentors[i]
                mentee = mentees[j]
                score = scores[(mentor.id, mentee.id)]
                matches.append({"mentor": mentor, "mentee": mentee, "score": score})
                total_score += score

        result = {
            "matches": matches,
            "total_score": total_score,
            "avg_score": total_score / len(matches) if matches else 0,
            "solve_time": solve_time,
        }

        logger.info(
            f"Found solution with {len(matches)} matches, total score: {total_score}"
        )
        return True, result

    else:
        # Infeasible or timeout
        failure_report = {
            "reason": "INFEASIBLE" if status == cp_model.INFEASIBLE else "TIMEOUT",
            "mentors_count": len(mentors),
            "mentees_count": len(mentees),
            "feasible_pairs_count": feasible_count,
            "solve_time": solve_time,
        }

        # Add diagnostics about blockers
        # Count mentors/mentees with zero feasible options
        zero_mentor_options = []
        for i, mentor in enumerate(mentors):
            feasible_count = sum(
                1
                for j, mentee in enumerate(mentees)
                if feasible_pairs[(mentor.id, mentee.id)]
            )
            if feasible_count == 0:
                zero_mentor_options.append(
                    {
                        "id": mentor.id,
                        "name": mentor.display_name,
                        "organization": mentor.organization,
                    }
                )

        zero_mentee_options = []
        for j, mentee in enumerate(mentees):
            feasible_count = sum(
                1
                for i, mentor in enumerate(mentors)
                if feasible_pairs[(mentor.id, mentee.id)]
            )
            if feasible_count == 0:
                zero_mentee_options.append(
                    {
                        "id": mentee.id,
                        "name": mentee.display_name,
                        "organization": mentee.organization,
                    }
                )

        failure_report["zero_mentor_options"] = zero_mentor_options
        failure_report["zero_mentee_options"] = zero_mentee_options

        logger.info(f"Strict solve failed: {failure_report['reason']}")
        return False, {"failure_report": failure_report}


def detect_ambiguity(
    matches: List[Dict],
    mentors: List[Participant],
    mentees: List[Participant],
    scores: Dict[Tuple[int, int], float],
    gap_threshold: float = 5.0,
) -> List[Dict]:
    """
    Detect ambiguous matches based on score gaps.

    Args:
        matches: List of matched pairs
        mentors: All mentors
        mentees: All mentees
        scores: Precomputed pair scores
        gap_threshold: Threshold for ambiguity detection

    Returns:
        List of ambiguous matches with reasons
    """
    # Create match lookup for quick access
    match_lookup = {(m["mentor"].id, m["mentee"].id): m for m in matches}

    # For each participant, find their best alternative
    ambiguities = []

    # Check for each mentee
    for mentee in mentees:
        # Find mentee's matched mentor
        matched_mentor = None
        for match in matches:
            if match["mentee"].id == mentee.id:
                matched_mentor = match["mentor"]
                break

        if matched_mentor:
            # Get matched score
            matched_score = scores[(matched_mentor.id, mentee.id)]

            # Find best alternative mentor for this mentee
            best_alt_score = -1
            best_alt_mentor = None

            for mentor in mentors:
                if mentor.id != matched_mentor.id:  # Skip matched mentor
                    score = scores[(mentor.id, mentee.id)]
                    if score > best_alt_score:
                        best_alt_score = score
                        best_alt_mentor = mentor

            # Check if gap is small enough to be ambiguous
            if best_alt_mentor and (matched_score - best_alt_score) <= gap_threshold:
                ambiguities.append(
                    {
                        "participant": mentee,
                        "matched_with": matched_mentor,
                        "matched_score": matched_score,
                        "alternative": best_alt_mentor,
                        "alternative_score": best_alt_score,
                        "gap": matched_score - best_alt_score,
                        "reason": f"Matched score ({matched_score:.1f}) vs alternative ({best_alt_score:.1f}) gap is small ({matched_score - best_alt_score:.1f} <= {gap_threshold})",
                    }
                )

    # Check for each mentor (similar logic)
    for mentor in mentors:
        # Find mentor's matched mentee
        matched_mentee = None
        for match in matches:
            if match["mentor"].id == mentor.id:
                matched_mentee = match["mentee"]
                break

        if matched_mentee:
            # Get matched score
            matched_score = scores[(mentor.id, matched_mentee.id)]

            # Find best alternative mentee for this mentor
            best_alt_score = -1
            best_alt_mentee = None

            for mentee in mentees:
                if mentee.id != matched_mentee.id:  # Skip matched mentee
                    score = scores[(mentor.id, mentee.id)]
                    if score > best_alt_score:
                        best_alt_score = score
                        best_alt_mentee = mentee

            # Check if gap is small enough to be ambiguous
            if best_alt_mentee and (matched_score - best_alt_score) <= gap_threshold:
                # Check if we already recorded this ambiguity from the mentee perspective
                already_recorded = False
                for amb in ambiguities:
                    if (
                        amb["participant"].id == matched_mentee.id
                        and amb["matched_with"].id == mentor.id
                    ):
                        already_recorded = True
                        break

                if not already_recorded:
                    ambiguities.append(
                        {
                            "participant": mentor,
                            "matched_with": matched_mentee,
                            "matched_score": matched_score,
                            "alternative": best_alt_mentee,
                            "alternative_score": best_alt_score,
                            "gap": matched_score - best_alt_score,
                            "reason": f"Matched score ({matched_score:.1f}) vs alternative ({best_alt_score:.1f}) gap is small ({matched_score - best_alt_score:.1f} <= {gap_threshold})",
                        }
                    )

    return ambiguities


def solve_exception(
    mentors: List[Participant], mentees: List[Participant], cohort
) -> Tuple[bool, Dict[str, Any]]:
    """
    Solve exception matching problem using OR-Tools CP-SAT.
    Allows all pairs but applies penalties for policy violations.

    Returns:
        Tuple of (success: bool, result: dict)
    """
    logger.info(
        f"Solving exception matching for {len(mentors)} mentors and {len(mentees)} mentees"
    )

    # Get scores
    scores = get_pair_scores(mentors, mentees, cohort)

    # Create the model
    model = cp_model.CpModel()

    # Create variables
    x = {}  # x[i,j] = 1 if mentor i is matched to mentee j
    for i, mentor in enumerate(mentors):
        for j, mentee in enumerate(mentees):
            x[(i, j)] = model.NewBoolVar(f"x[{i},{j}]")

    # Assignment constraints - each participant matched exactly once
    # Each mentor matched exactly once
    for i in range(len(mentors)):
        model.AddExactlyOne(x[(i, j)] for j in range(len(mentees)))

    # Each mentee matched exactly once
    for j in range(len(mentees)):
        model.AddExactlyOne(x[(i, j)] for i in range(len(mentors)))

    # Objective: maximize total score - penalties
    # We'll create penalty variables for each match
    penalty_vars = []
    penalty_coeffs = []

    for i, mentor in enumerate(mentors):
        for j, mentee in enumerate(mentees):
            # Apply penalties based on exception type
            exception_type, exception_reason = classify_exception(
                mentor, mentee, mentors, mentees
            )

            if exception_type == "E3":  # Same org - largest penalty
                penalty_var = model.NewIntVar(0, 1, f"penalty_e3_{i}_{j}")
                model.Add(penalty_var == x[(i, j)])  # penalty = 1 if matched
                penalty_vars.append(penalty_var)
                penalty_coeffs.append(PENALTY_ORG)
            elif exception_type == "E2":  # Neither accepts - large penalty
                penalty_var = model.NewIntVar(0, 1, f"penalty_e2_{i}_{j}")
                model.Add(penalty_var == x[(i, j)])  # penalty = 1 if matched
                penalty_vars.append(penalty_var)
                penalty_coeffs.append(PENALTY_NEITHER)
            elif exception_type == "E1":  # One-sided - medium penalty
                penalty_var = model.NewIntVar(0, 1, f"penalty_e1_{i}_{j}")
                model.Add(penalty_var == x[(i, j)])  # penalty = 1 if matched
                penalty_vars.append(penalty_var)
                penalty_coeffs.append(PENALTY_ONE_SIDED)

    # Objective: maximize score - penalties
    score_term = sum(
        x[(i, j)] * int(scores[(mentor.id, mentee.id)] * SCORE_SCALE)
        for (i, j), var in x.items()
        for mentor, mentee in [(mentors[i], mentees[j])]
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
    solver.parameters.max_time_in_seconds = EXCEPTION_TIME_LIMIT

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
                mentor = mentors[i]
                mentee = mentees[j]
                score = scores[(mentor.id, mentee.id)]

                # Check for exceptions
                exception_type, exception_reason = classify_exception(
                    mentor, mentee, mentors, mentees
                )
                is_exception = exception_type != ""

                if is_exception:
                    exception_count += 1
                    exception_summary[exception_type] += 1

                matches.append(
                    {
                        "mentor": mentor,
                        "mentee": mentee,
                        "score": score,
                        "exception_flag": is_exception,
                        "exception_type": exception_type,
                        "exception_reason": exception_reason,
                    }
                )
                total_score += score

        result = {
            "matches": matches,
            "total_score": total_score,
            "avg_score": total_score / len(matches) if matches else 0,
            "solve_time": solve_time,
            "exception_count": exception_count,
            "exception_summary": exception_summary,
        }

        logger.info(
            f"Exception matching completed with {len(matches)} matches, "
            f"{exception_count} exceptions, total score: {total_score}"
        )
        return True, result

    else:
        # Infeasible or timeout (should not happen with exception mode)
        failure_report = {
            "reason": "INFEASIBLE" if status == cp_model.INFEASIBLE else "TIMEOUT",
            "mentors_count": len(mentors),
            "mentees_count": len(mentees),
            "solve_time": solve_time,
        }

        logger.info(f"Exception solve failed: {failure_report['reason']}")
        return False, {"failure_report": failure_report}
