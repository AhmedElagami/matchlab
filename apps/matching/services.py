"""Business logic services for matching operations."""

import hashlib
import json
import logging
import time
from typing import Dict, List, Any
from django.utils import timezone
from apps.core.models import Cohort, Participant
from apps.matching.models import MatchRun, Match, PairScore
from apps.matching.solver import (
    solve_strict,
    solve_exception,
    detect_ambiguity,
    get_pair_scores,
)

logger = logging.getLogger(__name__)


def get_input_signature(cohort: Cohort) -> str:
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


def run_strict_matching(cohort: Cohort, user) -> MatchRun:
    """
    Run strict matching for a cohort.

    Returns:
        MatchRun object with results
    """
    logger.info(f"Running strict matching for cohort {cohort.id}")
    start_time = time.time()

    # Create match run record
    match_run = MatchRun.objects.create(
        cohort=cohort,
        created_by=user,
        mode="STRICT",
        status="FAILED",  # Default to failed, update on success
        input_signature=get_input_signature(cohort),
    )

    try:
        # Get participants
        mentors = list(
            Participant.objects.filter(
                cohort=cohort, role_in_cohort="MENTOR", is_submitted=True
            )
        )
        mentees = list(
            Participant.objects.filter(
                cohort=cohort, role_in_cohort="MENTEE", is_submitted=True
            )
        )

        logger.info(f"Found {len(mentors)} mentors and {len(mentees)} mentees")

        # Check counts
        if len(mentors) != len(mentees):
            match_run.failure_report = {
                "reason": "COUNT_MISMATCH",
                "mentors_count": len(mentors),
                "mentees_count": len(mentees),
                "message": f"Unequal counts: {len(mentors)} mentors vs {len(mentees)} mentees",
            }
            match_run.save()
            return match_run

        if len(mentors) == 0:
            match_run.failure_report = {
                "reason": "NO_PARTICIPANTS",
                "message": "No submitted participants found",
            }
            match_run.save()
            return match_run

        # Solve
        success, result = solve_strict(mentors, mentees, cohort)

        if success:
            # Success case
            matches_data = result["matches"]
            total_score = result["total_score"]
            avg_score = result["avg_score"]
            solve_time = result["solve_time"]

            # Get scores for ambiguity detection
            scores = get_pair_scores(mentors, mentees, cohort)

            # Detect ambiguities
            ambiguities = detect_ambiguity(matches_data, mentors, mentees, scores)

            # Calculate total duration
            end_time = time.time()
            total_duration = end_time - start_time

            # Update match run
            match_run.status = "SUCCESS"
            match_run.objective_summary = {
                "total_score": total_score,
                "avg_score": avg_score,
                "match_count": len(matches_data),
                "ambiguity_count": len(ambiguities),
                "solve_time": solve_time,
                "total_duration": total_duration,
            }
            match_run.save()

            logger.info(f"Strict matching completed for cohort {cohort.id} in {total_duration:.2f}s with {len(matches_data)} matches")

            # Create match records
            for match_data in matches_data:
                mentor = match_data["mentor"]
                mentee = match_data["mentee"]
                score = match_data["score"]

                # Check if this match is ambiguous
                is_ambiguous = False
                ambiguity_reason = ""
                for amb in ambiguities:
                    if (
                        amb["participant"].id == mentor.id
                        and amb["matched_with"].id == mentee.id
                    ) or (
                        amb["participant"].id == mentee.id
                        and amb["matched_with"].id == mentor.id
                    ):
                        is_ambiguous = True
                        ambiguity_reason = amb["reason"]
                        break

                Match.objects.create(
                    match_run=match_run,
                    mentor=mentor,
                    mentee=mentee,
                    score_percent=int(round(score)),
                    ambiguity_flag=is_ambiguous,
                    ambiguity_reason=ambiguity_reason,
                    exception_flag=False,  # Strict mode has no exceptions
                    exception_type="",  # Empty for strict mode
                    exception_reason="",  # Empty for strict mode
                )

            logger.info(f"Strict matching succeeded with {len(matches_data)} matches")
        else:
            # Failure case
            match_run.status = "FAILED"
            match_run.failure_report = result["failure_report"]
            match_run.save()

            logger.info(f"Strict matching failed: {result['failure_report']['reason']}")

    except Exception as e:
        logger.error(f"Error during strict matching: {e}", exc_info=True)
        match_run.failure_report = {"reason": "INTERNAL_ERROR", "message": str(e)}
        match_run.save()

    return match_run


def run_exception_matching(cohort: Cohort, user) -> MatchRun:
    """
    Run exception matching for a cohort.
    Always produces complete matching and flags policy exceptions.

    Returns:
        MatchRun object with results
    """
    logger.info(f"Running exception matching for cohort {cohort.id}")
    start_time = time.time()

    # Create match run record
    match_run = MatchRun.objects.create(
        cohort=cohort,
        created_by=user,
        mode="EXCEPTION",
        status="FAILED",  # Default to failed, update on success
        input_signature=get_input_signature(cohort),
    )

    try:
        # Get participants
        mentors = list(
            Participant.objects.filter(
                cohort=cohort, role_in_cohort="MENTOR", is_submitted=True
            )
        )
        mentees = list(
            Participant.objects.filter(
                cohort=cohort, role_in_cohort="MENTEE", is_submitted=True
            )
        )

        logger.info(f"Found {len(mentors)} mentors and {len(mentees)} mentees")

        # Check counts
        if len(mentors) != len(mentees):
            match_run.failure_report = {
                "reason": "COUNT_MISMATCH",
                "mentors_count": len(mentors),
                "mentees_count": len(mentees),
                "message": f"Unequal counts: {len(mentors)} mentors vs {len(mentees)} mentees",
            }
            match_run.save()
            return match_run

        if len(mentors) == 0:
            match_run.failure_report = {
                "reason": "NO_PARTICIPANTS",
                "message": "No submitted participants found",
            }
            match_run.save()
            return match_run

        # Solve with exception mode
        success, result = solve_exception(mentors, mentees, cohort)

        if success:
            # Success case
            matches_data = result["matches"]
            total_score = result["total_score"]
            avg_score = result["avg_score"]
            solve_time = result["solve_time"]
            exception_count = result["exception_count"]
            exception_summary = result["exception_summary"]

            # Get scores for ambiguity detection
            scores = get_pair_scores(mentors, mentees, cohort)

            # Detect ambiguities (even in exception mode)
            ambiguities = detect_ambiguity(matches_data, mentors, mentees, scores)

            # Calculate total duration
            end_time = time.time()
            total_duration = end_time - start_time

            # Update match run
            match_run.status = "SUCCESS"
            match_run.objective_summary = {
                "total_score": total_score,
                "avg_score": avg_score,
                "match_count": len(matches_data),
                "ambiguity_count": len(ambiguities),
                "exception_count": exception_count,
                "exception_summary": exception_summary,
                "solve_time": solve_time,
                "total_duration": total_duration,
            }
            match_run.save()

            logger.info(f"Exception matching completed for cohort {cohort.id} in {total_duration:.2f}s with {len(matches_data)} matches and {exception_count} exceptions")

            # Create match records
            for match_data in matches_data:
                mentor = match_data["mentor"]
                mentee = match_data["mentee"]
                score = match_data["score"]
                exception_flag = match_data.get("exception_flag", False)
                exception_type = match_data.get("exception_type", "")
                exception_reason = match_data.get("exception_reason", "")

                # Check if this match is ambiguous
                is_ambiguous = False
                ambiguity_reason = ""
                for amb in ambiguities:
                    if (
                        amb["participant"].id == mentor.id
                        and amb["matched_with"].id == mentee.id
                    ) or (
                        amb["participant"].id == mentee.id
                        and amb["matched_with"].id == mentor.id
                    ):
                        is_ambiguous = True
                        ambiguity_reason = amb["reason"]
                        break

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

            logger.info(
                f"Exception matching succeeded with {len(matches_data)} matches, "
                f"{exception_count} exceptions"
            )
        else:
            # Failure case (should be rare for exception mode)
            match_run.status = "FAILED"
            match_run.failure_report = result["failure_report"]
            match_run.save()

            logger.info(
                f"Exception matching failed: {result['failure_report']['reason']}"
            )

    except Exception as e:
        logger.error(f"Error during exception matching: {e}", exc_info=True)
        match_run.failure_report = {"reason": "INTERNAL_ERROR", "message": str(e)}
        match_run.save()

    return match_run


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


def export_match_run_csv(match_run: MatchRun) -> str:
    """
    Export match run results to CSV format.

    Returns:
        CSV content as string
    """
    import csv
    import io

    results = get_match_run_results(match_run)

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "mentor_name",
            "mentor_email",
            "mentor_org",
            "mentee_name",
            "mentee_email",
            "mentee_org",
            "match_percent",
            "ambiguity_flag",
            "ambiguity_reason",
            "exception_flag",
            "exception_type",
            "exception_reason",
            "is_manual_override",
            "override_reason",
        ]
    )

    # Data rows
    for result in results:
        writer.writerow(
            [
                result["mentor_name"],
                result["mentor_email"],
                result["mentor_org"],
                result["mentee_name"],
                result["mentee_email"],
                result["mentee_org"],
                result["match_percent"],
                result["ambiguity_flag"],
                result["ambiguity_reason"],
                result["exception_flag"],
                result["exception_type"],
                result["exception_reason"],
                result["is_manual_override"],
                result["override_reason"],
            ]
        )

    return output.getvalue()
