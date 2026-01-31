"""Unified matching service - orchestrates data prep, solvers, and persistence."""

import hashlib
import json
import logging
import time
from typing import Dict, List, Any
from django.utils import timezone
from django.db import transaction
from apps.core.models import Cohort, Participant
from .models import MatchRun, Match
from .data_prep import prepare_inputs
from .solvers.strict import solve_strict
from .solvers.exception import solve_exception
from .domain import detect_ambiguity

logger = logging.getLogger(__name__)


def run_matching(cohort: Cohort, user, mode: str = "STRICT") -> MatchRun:
    """
    Run matching for a cohort in specified mode.

    This is the unified orchestration function that handles:
    1. Input preparation (ORM isolation)
    2. Solver execution (pure functions)
    3. Result persistence
    4. Error handling

    Args:
        cohort: The cohort to match
        user: The user initiating the run
        mode: "STRICT" or "EXCEPTION"

    Returns:
        MatchRun object with results
    """
    logger.info(f"Running {mode} matching for cohort {cohort.id}")
    start_time = time.time()

    # Create match run record
    match_run = MatchRun.objects.create(
        cohort=cohort,
        created_by=user,
        mode=mode,
        status="FAILED",  # Default to failed, update on success
        input_signature=_get_input_signature(cohort),
    )

    try:
        # Step 1: Prepare inputs (ORM isolation layer)
        inputs = prepare_inputs(cohort)

        # Step 2: Solve with appropriate solver (pure functions)
        if mode == "STRICT":
            solver_result = solve_strict(inputs)
        elif mode == "EXCEPTION":
            solver_result = solve_exception(inputs)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        # Step 3: Handle results (persistence layer)
        if solver_result.success:
            _handle_successful_result(match_run, solver_result, inputs, start_time)
        else:
            _handle_failed_result(match_run, solver_result)

    except Exception as e:
        logger.error(f"Error during {mode} matching: {e}", exc_info=True)
        match_run.failure_report = {"reason": "INTERNAL_ERROR", "message": str(e)}
        match_run.save()

    return match_run


def _handle_successful_result(
    match_run: MatchRun, solver_result: object, inputs: object, start_time: float
) -> None:
    """Handle successful solver result by persisting matches."""
    # Calculate total duration
    end_time = time.time()
    total_duration = end_time - start_time

    # Detect ambiguities
    ambiguities = detect_ambiguity(solver_result.matches, inputs)

    # Update match run
    match_run.status = "SUCCESS"
    match_run.objective_summary = {
        "total_score": solver_result.total_score,
        "avg_score": solver_result.avg_score,
        "match_count": len(solver_result.matches),
        "ambiguity_count": len(ambiguities),
        "solve_time": solver_result.solve_time,
        "total_duration": total_duration,
    }

    # Add exception info if available
    if hasattr(solver_result, "exception_count"):
        match_run.objective_summary["exception_count"] = solver_result.exception_count
        match_run.objective_summary["exception_summary"] = (
            solver_result.exception_summary
        )

    match_run.save()

    logger.info(
        f"{match_run.mode} matching completed for cohort {match_run.cohort.id} in {total_duration:.2f}s "
        f"with {len(solver_result.matches)} matches"
    )

    # Create match records in a transaction
    with transaction.atomic():
        for match_data in solver_result.matches:
            mentor_id = match_data["mentor_id"]
            mentee_id = match_data["mentee_id"]
            score = match_data["score"]

            # Resolve participant objects
            mentor = Participant.objects.get(id=mentor_id)
            mentee = Participant.objects.get(id=mentee_id)

            # Check if this match is ambiguous
            is_ambiguous = False
            ambiguity_reason = ""
            for amb in ambiguities:
                if (
                    amb["participant_id"] == mentor_id
                    and amb["matched_with_id"] == mentee_id
                ) or (
                    amb["participant_id"] == mentee_id
                    and amb["matched_with_id"] == mentor_id
                ):
                    is_ambiguous = True
                    ambiguity_reason = amb["reason"]
                    break

            # Get exception info if available
            exception_flag = match_data.get("exception_flag", False)
            exception_type = match_data.get("exception_type", "")
            exception_reason = match_data.get("exception_reason", "")

            Match.objects.create(
                match_run=match_run,
                mentor=mentor,
                mentee=mentee,
                score_percent=int(round(score)),
                ambiguity_flag=is_ambiguous,
                ambiguity_reason=ambiguity_reason,
                exception_flag=exception_flag,
                exception_type=exception_type,
                exception_reason=exception_reason,
            )


def _handle_failed_result(match_run: MatchRun, solver_result: object) -> None:
    """Handle failed solver result by persisting failure report."""
    match_run.status = "FAILED"
    match_run.failure_report = solver_result.failure_report
    match_run.save()

    reason = solver_result.failure_report.get("reason", "UNKNOWN")
    logger.info(f"{match_run.mode} matching failed: {reason}")


def _get_input_signature(cohort: Cohort) -> str:
    """
    Generate a signature/hash of the current input state for traceability.

    This helps detect if inputs have changed between runs.
    """
    # Get all relevant data that affects matching
    participants = Participant.objects.filter(cohort=cohort).order_by("id")
    data_parts = []

    for participant in participants:
        data_parts.append(
            f"{participant.id}:{participant.role_in_cohort}:{participant.organization}"
        )

        # Add preferences
        prefs = participant.given_preferences.all().order_by("to_participant_id")
        for pref in prefs:
            data_parts.append(
                f"pref:{participant.id}->{pref.to_participant.id}:{pref.rank}"
            )

    # Add cohort config
    config_str = json.dumps(cohort.cohort_config, sort_keys=True)
    data_parts.append(f"config:{config_str}")

    # Create hash
    data_string = "|".join(data_parts)
    return hashlib.sha256(data_string.encode()).hexdigest()


def get_match_run_results(match_run: MatchRun) -> List[Dict[str, Any]]:
    """
    Get formatted results for a match run.

    Returns:
        List of match dictionaries with all relevant information
    """
    if match_run.status != "SUCCESS":
        return []

    matches = match_run.matches.select_related("mentor", "mentee").all()

    results = []
    for match in matches:
        results.append(
            {
                "mentor_name": match.mentor.display_name,
                "mentor_email": match.mentor.user.email,
                "mentor_org": match.mentor.organization,
                "mentee_name": match.mentee.display_name,
                "mentee_email": match.mentee.user.email,
                "mentee_org": match.mentee.organization,
                "match_percent": match.score_percent,
                "ambiguity_flag": match.ambiguity_flag,
                "ambiguity_reason": match.ambiguity_reason,
                "exception_flag": match.exception_flag,
                "exception_type": match.exception_type,
                "exception_reason": match.exception_reason,
                "is_manual_override": match.is_manual_override,
                "override_reason": match.override_reason,
            }
        )

    return results
