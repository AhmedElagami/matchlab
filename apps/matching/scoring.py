"""Scoring engine for mentor-mentee match percentages."""

import math
from typing import Dict, Any, Tuple
from django.db import models
from django.db.models import QuerySet, Max
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, MentorProfile, MenteeProfile, PairScore


# Default configuration values
DEFAULT_CONFIG = {
    "rank_weight": 0.6,
    "tag_overlap_weight": 0.2,
    "attribute_match_weight": 0.2,
    "min_options_strict": 3,
}


def get_cohort_config(cohort: Cohort) -> Dict[str, Any]:
    """Get cohort configuration with defaults."""
    config = DEFAULT_CONFIG.copy()
    config.update(cohort.cohort_config)
    return config


def compute_rank_score(rank: int, max_rank: int) -> float:
    """
    Compute score based on rank position.
    Higher ranks (lower numbers) get higher scores.
    """
    if rank <= 0 or max_rank <= 0:
        return 0.0

    # Linear scoring: rank 1 gets 100%, max_rank gets 0%
    return max(0.0, (max_rank - rank + 1) / max_rank * 100)


def compute_tag_overlap_score(mentor_tags: list, mentee_tags: list) -> float:
    """
    Compute score based on tag overlap between mentor and mentee.
    Uses Jaccard similarity coefficient.
    """
    if not mentor_tags or not mentee_tags:
        return 0.0

    set1 = set(tag.lower().strip() for tag in mentor_tags if tag.strip())
    set2 = set(tag.lower().strip() for tag in mentee_tags if tag.strip())

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return 0.0

    return (intersection / union) * 100


def compute_attribute_match_score(
    mentee_desired_attributes: Dict[str, Any], mentor_profile_data: Dict[str, Any]
) -> float:
    """
    Compute score based on mentee's desired attributes matching mentor's profile.
    Handles both boolean flags and string/value matches.
    """
    if not mentee_desired_attributes:
        return 0.0

    matched_count = 0
    total_count = 0

    # Handle boolean attributes (existing logic)
    for attr_key, desired_value in mentee_desired_attributes.items():
        if isinstance(desired_value, bool) and desired_value:
            total_count += 1
            # Check if mentor has this attribute
            mentor_value = mentor_profile_data.get(attr_key, False)
            if mentor_value:
                matched_count += 1
        elif isinstance(desired_value, str) and desired_value:
            # Handle string attributes like preferred_location, preferred_languages
            total_count += 1
            mentor_value = mentor_profile_data.get(
                attr_key.replace("preferred_", ""), ""
            )
            if isinstance(mentor_value, str) and mentor_value:
                # Simple string match for location
                if (
                    "location" in attr_key.lower()
                    and desired_value.lower() == mentor_value.lower()
                ):
                    matched_count += 1
                # For languages, check if preferred language is in mentor's languages
                elif "language" in attr_key.lower():
                    mentor_languages = mentor_profile_data.get("languages", [])
                    if (
                        isinstance(mentor_languages, list)
                        and desired_value in mentor_languages
                    ):
                        matched_count += 1
        elif isinstance(desired_value, list) and desired_value:
            # Handle list attributes like preferred_expertise
            total_count += 1
            mentor_value = mentor_profile_data.get(
                attr_key.replace("preferred_", ""), []
            )
            if isinstance(mentor_value, list) and mentor_value:
                # Compute overlap for lists (similar to tag overlap)
                set1 = set(
                    str(item).lower().strip()
                    for item in desired_value
                    if str(item).strip()
                )
                set2 = set(
                    str(item).lower().strip()
                    for item in mentor_value
                    if str(item).strip()
                )
                if set1 and set2:
                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    if union > 0:
                        # Add proportional match
                        matched_count += intersection / union

    if total_count == 0:
        return 0.0

    return (matched_count / total_count) * 100


def get_max_rank(participant: Participant) -> int:
    """Get the maximum rank for a participant's preferences."""
    max_rank = Preference.objects.filter(from_participant=participant).aggregate(
        max_rank=Max("rank")
    )["max_rank"]
    return max_rank or 0


def get_mentor_profile_data(mentor: Participant) -> Dict[str, Any]:
    """Extract relevant data from mentor profile for scoring."""
    data = {}
    try:
        profile = mentor.mentor_profile
        data["expertise_tags"] = profile.get_expertise_tags_list()
        data["languages"] = profile.get_languages_list()
        data["coaching_topics"] = profile.get_coaching_topics_list()
        data["job_title"] = profile.job_title
        data["function"] = profile.function
        data["location"] = profile.location
        data["years_experience"] = profile.years_experience
    except MentorProfile.DoesNotExist:
        pass
    return data


def get_mentee_desired_attributes(mentee: Participant) -> Dict[str, Any]:
    """Get mentee's desired attributes."""
    try:
        profile = mentee.mentee_profile
        return profile.desired_attributes
    except MenteeProfile.DoesNotExist:
        return {}


def compute_pair_score(
    mentor: Participant, mentee: Participant, cohort: Cohort
) -> Tuple[float, Dict[str, float]]:
    """
    Compute match score between a mentor and mentee pair.

    Returns:
        Tuple of (overall_score, breakdown_dict)
    """
    config = get_cohort_config(cohort)

    # Get preferences
    try:
        mentor_pref = Preference.objects.get(
            from_participant=mentor, to_participant=mentee
        )
        mentee_pref = Preference.objects.get(
            from_participant=mentee, to_participant=mentor
        )
    except Preference.DoesNotExist:
        # If no mutual preferences, score is 0
        return 0.0, {"mutual_acceptability": 0.0}

    # Get max ranks for normalization
    mentor_max_rank = get_max_rank(mentor)
    mentee_max_rank = get_max_rank(mentee)

    # Compute rank scores
    mentor_rank_score = compute_rank_score(mentor_pref.rank, mentor_max_rank)
    mentee_rank_score = compute_rank_score(mentee_pref.rank, mentee_max_rank)
    avg_rank_score = (mentor_rank_score + mentee_rank_score) / 2

    # Get profile data
    mentor_data = get_mentor_profile_data(mentor)
    mentee_attrs = get_mentee_desired_attributes(mentee)

    # Compute tag overlap score
    mentor_expertise = mentor_data.get("expertise_tags", [])
    mentee_topics = mentee_attrs.get("preferred_expertise", [])
    tag_score = compute_tag_overlap_score(mentor_expertise, mentee_topics)

    # Compute attribute match score
    attr_score = compute_attribute_match_score(mentee_attrs, mentor_data)

    # Apply weights
    rank_component = avg_rank_score * config["rank_weight"]
    tag_component = tag_score * config["tag_overlap_weight"]
    attr_component = attr_score * config["attribute_match_weight"]

    # Calculate overall score
    overall_score = rank_component + tag_component + attr_component

    # Create breakdown
    breakdown = {
        "rank_score": round(avg_rank_score, 2),
        "rank_component": round(rank_component, 2),
        "tag_overlap_score": round(tag_score, 2),
        "tag_component": round(tag_component, 2),
        "attribute_match_score": round(attr_score, 2),
        "attribute_component": round(attr_component, 2),
        "overall_score": round(overall_score, 2),
    }

    return overall_score, breakdown


def compute_all_pair_scores(cohort: Cohort) -> None:
    """
    Compute and store scores for all mentor-mentee pairs in a cohort.
    """
    # Get all mentors and mentees in the cohort
    mentors = Participant.objects.filter(cohort=cohort, role_in_cohort="MENTOR")
    mentees = Participant.objects.filter(cohort=cohort, role_in_cohort="MENTEE")

    # Delete existing scores for this cohort
    PairScore.objects.filter(cohort=cohort).delete()

    # Compute scores for all pairs
    for mentor in mentors:
        for mentee in mentees:
            score, breakdown = compute_pair_score(mentor, mentee, cohort)

            # Store the score
            PairScore.objects.create(
                cohort=cohort,
                mentor=mentor,
                mentee=mentee,
                score=score,
                score_breakdown=breakdown,
            )
