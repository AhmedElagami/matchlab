"""Domain logic layer - pure functions for business rules."""

from typing import Dict, Tuple, NamedTuple
from .data_prep import PreparedInputs


class ExceptionClassification(NamedTuple):
    """Result of exception classification."""

    exception_type: str  # "E1", "E2", "E3", or "" for no exception
    reason: str  # Human-readable explanation


class PenaltyInfo(NamedTuple):
    """Information about penalties for a pair."""

    penalty_value: int
    penalty_type: str  # "E1", "E2", "E3", or "" for no penalty


def classify_exception(
    mentor_id: int, mentee_id: int, inputs: PreparedInputs
) -> ExceptionClassification:
    """
    Classify a match as an exception based on prepared inputs.

    This is a pure function that operates only on in-memory data.

    Returns:
        ExceptionClassification with type and reason
    """
    # Check for E3: Same organization (highest severity)
    if inputs.same_org[(mentor_id, mentee_id)]:
        org_name = _get_org_name(mentor_id, inputs)  # Helper to get org name
        return ExceptionClassification("E3", f"Same organization: {org_name}")

    # Check acceptability
    acceptability = inputs.acceptability[(mentor_id, mentee_id)]

    # Check for E2: Neither accepts (large penalty)
    if acceptability == "NEITHER":
        return ExceptionClassification("E2", "Neither participant ranked the other")

    # Check for E1: One-sided acceptance (medium penalty)
    if acceptability == "ONE_SIDED_MENTOR_ONLY":
        return ExceptionClassification("E1", "Mentor did not rank mentee")
    elif acceptability == "ONE_SIDED_MENTEE_ONLY":
        return ExceptionClassification("E1", "Mentee did not rank mentor")

    # Mutual acceptability - no exception
    return ExceptionClassification("", "No exception")


def get_penalty_info(
    mentor_id: int, mentee_id: int, inputs: PreparedInputs
) -> PenaltyInfo:
    """
    Get penalty information for a pair based on exception classification.

    This function determines penalty values based on the refactor plan's priority ordering.
    """
    classification = classify_exception(mentor_id, mentee_id, inputs)

    if classification.exception_type == "E3":  # Same org - largest penalty
        return PenaltyInfo(inputs.config["penalty_org"], "E3")
    elif classification.exception_type == "E2":  # Neither accepts - large penalty
        return PenaltyInfo(inputs.config["penalty_neither"], "E2")
    elif classification.exception_type == "E1":  # One-sided - medium penalty
        return PenaltyInfo(inputs.config["penalty_one_sided"], "E1")
    else:
        return PenaltyInfo(0, "")  # No penalty


def get_exception_priority(exception_type: str) -> int:
    """
    Get priority level for exception type (higher = more severe).

    Returns:
        3 for E3 (same org - highest)
        2 for E2 (neither accepts - large)
        1 for E1 (one-sided - medium)
        0 for no exception
    """
    if exception_type == "E3":
        return 3
    elif exception_type == "E2":
        return 2
    elif exception_type == "E1":
        return 1
    return 0


def detect_ambiguity(matches: list, inputs: PreparedInputs) -> list:
    """
    Detect ambiguous matches based on score gaps.

    This is a pure function that operates on prepared inputs.
    """
    if not matches:
        return []

    # Create match lookup for quick access
    match_lookup = {(m["mentor_id"], m["mentee_id"]): m for m in matches}

    # For each participant, find their best alternative
    ambiguities = []

    # Check for each mentee
    for mentee_id in inputs.mentee_ids:
        # Find mentee's matched mentor
        matched_mentor_id = None
        for match in matches:
            if match["mentee_id"] == mentee_id:
                matched_mentor_id = match["mentor_id"]
                break

        if matched_mentor_id:
            # Get matched score
            matched_score = inputs.score[(matched_mentor_id, mentee_id)]

            # Find best alternative mentor for this mentee
            best_alt_score = -1
            best_alt_mentor_id = None

            for mentor_id in inputs.mentor_ids:
                if mentor_id != matched_mentor_id:  # Skip matched mentor
                    score = inputs.score[(mentor_id, mentee_id)]
                    if score > best_alt_score:
                        best_alt_score = score
                        best_alt_mentor_id = mentor_id

            # Check if gap is small enough to be ambiguous
            gap_threshold = inputs.config.get("ambiguity_gap_threshold", 5.0)
            if best_alt_mentor_id and (matched_score - best_alt_score) <= gap_threshold:
                ambiguities.append(
                    {
                        "participant_id": mentee_id,
                        "matched_with_id": matched_mentor_id,
                        "matched_score": matched_score,
                        "alternative_id": best_alt_mentor_id,
                        "alternative_score": best_alt_score,
                        "gap": matched_score - best_alt_score,
                        "reason": f"Matched score ({matched_score / 1000:.1f}) vs alternative ({best_alt_score / 1000:.1f}) gap is small ({(matched_score - best_alt_score) / 1000:.1f} <= {gap_threshold})",
                    }
                )

    # Check for each mentor (similar logic)
    for mentor_id in inputs.mentor_ids:
        # Find mentor's matched mentee
        matched_mentee_id = None
        for match in matches:
            if match["mentor_id"] == mentor_id:
                matched_mentee_id = match["mentee_id"]
                break

        if matched_mentee_id:
            # Get matched score
            matched_score = inputs.score[(mentor_id, matched_mentee_id)]

            # Find best alternative mentee for this mentor
            best_alt_score = -1
            best_alt_mentee_id = None

            for mentee_id in inputs.mentee_ids:
                if mentee_id != matched_mentee_id:  # Skip matched mentee
                    score = inputs.score[(mentor_id, mentee_id)]
                    if score > best_alt_score:
                        best_alt_score = score
                        best_alt_mentee_id = mentee_id

            # Check if gap is small enough to be ambiguous
            gap_threshold = inputs.config.get("ambiguity_gap_threshold", 5.0)
            if best_alt_mentee_id and (matched_score - best_alt_score) <= gap_threshold:
                # Check if we already recorded this ambiguity from the mentee perspective
                already_recorded = False
                for amb in ambiguities:
                    if (
                        amb["participant_id"] == matched_mentee_id
                        and amb["matched_with_id"] == mentor_id
                    ):
                        already_recorded = True
                        break

                if not already_recorded:
                    ambiguities.append(
                        {
                            "participant_id": mentor_id,
                            "matched_with_id": matched_mentee_id,
                            "matched_score": matched_score,
                            "alternative_id": best_alt_mentee_id,
                            "alternative_score": best_alt_score,
                            "gap": matched_score - best_alt_score,
                            "reason": f"Matched score ({matched_score / 1000:.1f}) vs alternative ({best_alt_score / 1000:.1f}) gap is small ({(matched_score - best_alt_score) / 1000:.1f} <= {gap_threshold})",
                        }
                    )

    return ambiguities


def _get_org_name(participant_id: int, inputs: PreparedInputs) -> str:
    """
    Helper to get organization name for a participant.
    In a pure function context, this would need to be passed in the inputs,
    but for now we'll return a placeholder.
    """
    # This is a simplification - in a real implementation, org info would be in inputs
    return "Same Organization"
