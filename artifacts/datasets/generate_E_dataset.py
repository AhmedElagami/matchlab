#!/usr/bin/env python3
"""
MatchLab Dataset Generator for Scale + Edge Case Testing (Tester E)

Generates large and adversarial datasets for testing system behavior under:
- Very large cohorts (N=30)
- Extreme preference patterns
- Degenerate/adversarial data
- Partial submissions across many cohorts

Usage:
    python generate_E_dataset.py --scenario E1 --size 30 --output fixture_E1.json
    python generate_E_dataset.py --scenario E2 --size 30 --contention 3 --output fixture_E2.json
    python generate_E_dataset.py --scenario E3 --size 30 --sparse 0.3 --output fixture_E3.json
    python generate_E_dataset.py --scenario E4 --size 20 --degenerate --output fixture_E4.json
    python generate_E_dataset.py --scenario E5 --cohorts 10 --submission-rates 0,10,50,90,100 --output-dir cohorts_E5/
"""

import json
import argparse
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import sys

# Default parameters
DEFAULT_SIZE = 30  # N=30 as per technical spec
DEFAULT_CONTENTION = 3  # Top-k for high contention
DEFAULT_SPARSE_RATE = 0.3  # 30% sparse preferences
DEFAULT_ORGANIZATIONS = ["OrgA", "OrgB", "OrgC", "OrgD", "OrgE", "OrgF", "OrgG", "OrgH"]
DEFAULT_ROLES = ["MENTOR", "MENTEE"]


def generate_timestamp(offset_days: int = 0) -> str:
    """Generate ISO timestamp with optional offset"""
    dt = datetime.now() - timedelta(days=offset_days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def create_user(user_id: int, role: str, cohort_id: int) -> Dict[str, Any]:
    """Create a Django user object"""
    first_names = [
        "Alex",
        "Bailey",
        "Casey",
        "Drew",
        "Ellis",
        "Finley",
        "Harper",
        "Indigo",
        "Jordan",
        "Kai",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
    ]

    return {
        "model": "auth.user",
        "pk": user_id,
        "fields": {
            "username": f"{role.lower()}{user_id}",
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"{role.lower()}{user_id}@example.com",
            "password": "pbkdf2_sha256$600000$test$test==",
            "is_staff": False,
            "is_active": True,
            "is_superuser": False,
            "date_joined": generate_timestamp(30),
        },
    }


def create_cohort(cohort_id: int, name: str, status: str = "OPEN") -> Dict[str, Any]:
    """Create a cohort object"""
    return {
        "model": "core.cohort",
        "pk": cohort_id,
        "fields": {
            "name": name,
            "status": status,
            "created_at": generate_timestamp(30),
        },
    }


def create_participant(
    participant_id: int,
    cohort_id: int,
    user_id: int,
    role: str,
    submitted: bool = True,
    organization: str = "",
) -> Dict[str, Any]:
    """Create a participant object"""
    if not organization:
        organization = random.choice(DEFAULT_ORGANIZATIONS)

    first_names = [
        "Alex",
        "Bailey",
        "Casey",
        "Drew",
        "Ellis",
        "Finley",
        "Harper",
        "Indigo",
        "Jordan",
        "Kai",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
    ]

    display_name = f"{random.choice(first_names)} {random.choice(last_names)}"

    return {
        "model": "core.participant",
        "pk": participant_id,
        "fields": {
            "cohort": cohort_id,
            "user": user_id,
            "role_in_cohort": role,
            "display_name": display_name,
            "organization": organization,
            "is_submitted": submitted,
            "submitted_at": generate_timestamp(7) if submitted else None,
            "created_at": generate_timestamp(14),
            "updated_at": generate_timestamp(7),
        },
    }


def create_preferences(
    participant_id: int,
    target_ids: List[int],
    pattern: str = "random",
    contention_k: int = 3,
    sparse_rate: float = 0.0,
) -> List[Dict[str, Any]]:
    """Create preference objects with various patterns"""
    preferences = []

    if pattern == "contention":
        # Everyone ranks the same top-k participants
        top_targets = target_ids[:contention_k]
        for i, target_id in enumerate(top_targets):
            preferences.append(
                {
                    "model": "matching.preference",
                    "pk": None,  # Will be set later
                    "fields": {
                        "from_participant": participant_id,
                        "to_participant": target_id,
                        "rank": i + 1,
                    },
                }
            )
    elif pattern == "sparse":
        # Only create preferences for a subset of participants
        if (
            random.random() > sparse_rate and len(target_ids) > 0
        ):  # 70% chance of having preferences
            if len(target_ids) > 0:
                min_prefs = min(1, len(target_ids))
                max_prefs = min(5, len(target_ids))
                if min_prefs <= max_prefs:
                    num_prefs = random.randint(min_prefs, max_prefs)
                else:
                    num_prefs = min_prefs
                if num_prefs > 0:
                    selected_targets = random.sample(
                        target_ids, min(num_prefs, len(target_ids))
                    )
                    for i, target_id in enumerate(selected_targets):
                        preferences.append(
                            {
                                "model": "matching.preference",
                                "pk": None,  # Will be set later
                                "fields": {
                                    "from_participant": participant_id,
                                    "to_participant": target_id,
                                    "rank": i + 1,
                                },
                            }
                        )
    elif pattern == "degenerate":
        # Create some invalid/degenerate preferences
        num_prefs = random.randint(1, min(5, len(target_ids)))
        selected_targets = random.sample(target_ids, num_prefs)
        for i, target_id in enumerate(selected_targets):
            rank = i + 1
            # Occasionally create duplicate ranks or out-of-order ranks
            if random.random() < 0.2:  # 20% chance of degeneracy
                if random.random() < 0.5:
                    rank = random.randint(1, 3)  # Possible duplicate
                else:
                    rank = random.randint(10, 20)  # Out of order

            preferences.append(
                {
                    "model": "matching.preference",
                    "pk": None,  # Will be set later
                    "fields": {
                        "from_participant": participant_id,
                        "to_participant": target_id,
                        "rank": rank,
                    },
                }
            )
    else:  # random
        # Create random valid preferences
        if len(target_ids) == 0:
            return preferences
        min_prefs = min(3, len(target_ids))
        max_prefs = min(10, len(target_ids))
        if min_prefs <= max_prefs:
            num_prefs = random.randint(min_prefs, max_prefs)
        else:
            num_prefs = min_prefs
        if num_prefs > 0 and len(target_ids) > 0:
            selected_targets = random.sample(
                target_ids, min(num_prefs, len(target_ids))
            )
            for i, target_id in enumerate(selected_targets):
                preferences.append(
                    {
                        "model": "matching.preference",
                        "pk": None,  # Will be set later
                        "fields": {
                            "from_participant": participant_id,
                            "to_participant": target_id,
                            "rank": i + 1,
                        },
                    }
                )

    return preferences


def generate_E1_baseline(size: int = DEFAULT_SIZE) -> List[Dict[str, Any]]:
    """Generate E1: Large cohort baseline"""
    objects = []

    # Create cohort
    cohort_id = 1
    objects.append(create_cohort(cohort_id, f"E1 Large Cohort Baseline (N={size})"))

    # Create users and participants
    mentor_ids = list(range(1, size + 1))
    mentee_ids = list(range(size + 1, 2 * size + 1))
    participant_ids = list(range(1, 2 * size + 1))
    user_ids = list(range(1, 2 * size + 1))

    # Create users
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(create_user(user_ids[i], role, cohort_id))

    # Create participants (all submitted)
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(
            create_participant(
                participant_ids[i], cohort_id, user_ids[i], role, submitted=True
            )
        )

    # Create preferences (random valid)
    preference_pk = 1

    # Mentor preferences over mentees
    for mentor_idx in range(size):
        mentor_participant_id = participant_ids[mentor_idx]
        mentee_target_ids = participant_ids[size : 2 * size]
        prefs = create_preferences(mentor_participant_id, mentee_target_ids, "random")
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    # Mentee preferences over mentors
    for mentee_idx in range(size, 2 * size):
        mentee_participant_id = participant_ids[mentee_idx]
        mentor_target_ids = participant_ids[0:size]
        prefs = create_preferences(mentee_participant_id, mentor_target_ids, "random")
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    return objects


def generate_E2_contention(
    size: int = DEFAULT_SIZE, contention_k: int = DEFAULT_CONTENTION
) -> List[Dict[str, Any]]:
    """Generate E2: Very high contention"""
    objects = []

    # Create cohort
    cohort_id = 2
    objects.append(
        create_cohort(cohort_id, f"E2 High Contention (N={size}, k={contention_k})")
    )

    # Create users and participants
    mentor_ids = list(range(101, 101 + size))
    mentee_ids = list(range(101 + size, 101 + 2 * size))
    participant_ids = list(range(101, 101 + 2 * size))
    user_ids = list(range(101, 101 + 2 * size))

    # Create users
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(create_user(user_ids[i], role, cohort_id))

    # Create participants (all submitted)
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(
            create_participant(
                participant_ids[i], cohort_id, user_ids[i], role, submitted=True
            )
        )

    # Create preferences (high contention - everyone ranks same top-k)
    preference_pk = 1001

    # Top-k mentees that everyone will rank
    top_k_mentee_ids = participant_ids[size : size + contention_k]

    # Mentor preferences over mentees (high contention)
    for mentor_idx in range(size):
        mentor_participant_id = participant_ids[mentor_idx]
        prefs = create_preferences(
            mentor_participant_id, top_k_mentee_ids, "contention", contention_k
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    # Mentee preferences over mentors (high contention)
    top_k_mentor_ids = participant_ids[0:contention_k]
    for mentee_idx in range(size, 2 * size):
        mentee_participant_id = participant_ids[mentee_idx]
        prefs = create_preferences(
            mentee_participant_id, top_k_mentor_ids, "contention", contention_k
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    return objects


def generate_E3_sparse(
    size: int = DEFAULT_SIZE, sparse_rate: float = DEFAULT_SPARSE_RATE
) -> List[Dict[str, Any]]:
    """Generate E3: Sparse / missing preferences"""
    objects = []

    # Create cohort
    cohort_id = 3
    objects.append(
        create_cohort(
            cohort_id,
            f"E3 Sparse Preferences (N={size}, {int(sparse_rate * 100)}% sparse)",
        )
    )

    # Create users and participants
    mentor_ids = list(range(201, 201 + size))
    mentee_ids = list(range(201 + size, 201 + 2 * size))
    participant_ids = list(range(201, 201 + 2 * size))
    user_ids = list(range(201, 201 + 2 * size))

    # Create users
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(create_user(user_ids[i], role, cohort_id))

    # Create participants (all submitted)
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(
            create_participant(
                participant_ids[i], cohort_id, user_ids[i], role, submitted=True
            )
        )

    # Create preferences (sparse - only some participants have preferences)
    preference_pk = 2001

    # Mentor preferences over mentees (sparse)
    for mentor_idx in range(size):
        mentor_participant_id = participant_ids[mentor_idx]
        mentee_target_ids = participant_ids[size : 2 * size]
        prefs = create_preferences(
            mentor_participant_id, mentee_target_ids, "sparse", sparse_rate=sparse_rate
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    # Mentee preferences over mentors (sparse)
    for mentee_idx in range(size, 2 * size):
        mentee_participant_id = participant_ids[mentee_idx]
        mentor_target_ids = participant_ids[0:size]
        prefs = create_preferences(
            mentee_participant_id, mentor_target_ids, "sparse", sparse_rate=sparse_rate
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    return objects


def generate_E4_degenerate(size: int = 20) -> List[Dict[str, Any]]:
    """Generate E4: Degenerate ranks"""
    objects = []

    # Create cohort
    cohort_id = 4
    objects.append(create_cohort(cohort_id, f"E4 Degenerate Ranks (N={size})"))

    # Create users and participants
    mentor_ids = list(range(301, 301 + size))
    mentee_ids = list(range(301 + size, 301 + 2 * size))
    participant_ids = list(range(301, 301 + 2 * size))
    user_ids = list(range(301, 301 + 2 * size))

    # Create users
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(create_user(user_ids[i], role, cohort_id))

    # Create participants (all submitted)
    for i in range(2 * size):
        role = "MENTOR" if i < size else "MENTEE"
        objects.append(
            create_participant(
                participant_ids[i], cohort_id, user_ids[i], role, submitted=True
            )
        )

    # Create preferences (degenerate - with invalid ranks)
    preference_pk = 3001

    # Mentor preferences over mentees (degenerate)
    for mentor_idx in range(size):
        mentor_participant_id = participant_ids[mentor_idx]
        mentee_target_ids = participant_ids[size : 2 * size]
        prefs = create_preferences(
            mentor_participant_id, mentee_target_ids, "degenerate"
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    # Mentee preferences over mentors (degenerate)
    for mentee_idx in range(size, 2 * size):
        mentee_participant_id = participant_ids[mentee_idx]
        mentor_target_ids = participant_ids[0:size]
        prefs = create_preferences(
            mentee_participant_id, mentor_target_ids, "degenerate"
        )
        for pref in prefs:
            pref["pk"] = preference_pk
            preference_pk += 1
            objects.append(pref)

    return objects


def generate_E5_multi_cohort(
    num_cohorts: int = 10, submission_rates: List[int] = [0, 10, 50, 90, 100]
) -> Dict[int, List[Dict[str, Any]]]:
    """Generate E5: Many cohorts with partial submissions"""
    cohort_data = {}

    base_user_id = 1001
    base_participant_id = 1001
    base_preference_pk = 10001

    for cohort_idx in range(num_cohorts):
        objects = []
        cohort_id = 10 + cohort_idx

        # Determine submission rate for this cohort (cycle through provided rates)
        submission_rate = submission_rates[cohort_idx % len(submission_rates)]

        # Cohort name
        objects.append(
            create_cohort(
                cohort_id,
                f"E5 Multi Cohort #{cohort_idx + 1} ({submission_rate}% submitted)",
            )
        )

        # Size - vary slightly for realism
        size = max(10, DEFAULT_SIZE - (cohort_idx % 5))  # 25-30 participants

        # User and participant IDs for this cohort
        cohort_user_ids = list(range(base_user_id, base_user_id + 2 * size))
        cohort_participant_ids = list(
            range(base_participant_id, base_participant_id + 2 * size)
        )

        # Create users
        for i in range(2 * size):
            role = "MENTOR" if i < size else "MENTEE"
            objects.append(create_user(cohort_user_ids[i], role, cohort_id))

        # Create participants with specified submission rate
        for i in range(2 * size):
            role = "MENTOR" if i < size else "MENTEE"
            # Determine if this participant is submitted based on rate
            is_submitted = random.randint(1, 100) <= submission_rate
            objects.append(
                create_participant(
                    cohort_participant_ids[i],
                    cohort_id,
                    cohort_user_ids[i],
                    role,
                    submitted=is_submitted,
                )
            )

        # Create preferences for submitted participants only
        preference_pk = base_preference_pk

        # Mentor preferences over mentees
        for mentor_idx in range(size):
            mentor_participant_id = cohort_participant_ids[mentor_idx]
            mentor = next(
                (
                    obj
                    for obj in objects
                    if obj["model"] == "core.participant"
                    and obj["pk"] == mentor_participant_id
                ),
                None,
            )
            if mentor and mentor["fields"]["is_submitted"]:
                mentee_target_ids = cohort_participant_ids[size : 2 * size]
                # Filter to only submitted mentees
                submitted_mentee_ids = [
                    pid
                    for pid in mentee_target_ids
                    if any(
                        obj
                        for obj in objects
                        if obj["model"] == "core.participant"
                        and obj["pk"] == pid
                        and obj["fields"]["is_submitted"]
                    )
                ]
                if submitted_mentee_ids:
                    prefs = create_preferences(
                        mentor_participant_id, submitted_mentee_ids, "random"
                    )
                    for pref in prefs:
                        pref["pk"] = preference_pk
                        preference_pk += 1
                        objects.append(pref)

        # Mentee preferences over mentors
        for mentee_idx in range(size, 2 * size):
            mentee_participant_id = cohort_participant_ids[mentee_idx]
            mentee = next(
                (
                    obj
                    for obj in objects
                    if obj["model"] == "core.participant"
                    and obj["pk"] == mentee_participant_id
                ),
                None,
            )
            if mentee and mentee["fields"]["is_submitted"]:
                mentor_target_ids = cohort_participant_ids[0:size]
                # Filter to only submitted mentors
                submitted_mentor_ids = [
                    pid
                    for pid in mentor_target_ids
                    if any(
                        obj
                        for obj in objects
                        if obj["model"] == "core.participant"
                        and obj["pk"] == pid
                        and obj["fields"]["is_submitted"]
                    )
                ]
                if submitted_mentor_ids:
                    prefs = create_preferences(
                        mentee_participant_id, submitted_mentor_ids, "random"
                    )
                    for pref in prefs:
                        pref["pk"] = preference_pk
                        preference_pk += 1
                        objects.append(pref)

        cohort_data[cohort_id] = objects

        # Update base IDs for next cohort
        base_user_id += 2 * size
        base_participant_id += 2 * size
        base_preference_pk = preference_pk + 100  # Buffer for next cohort

    return cohort_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate MatchLab datasets for scale + edge case testing"
    )
    parser.add_argument(
        "--scenario",
        choices=["E1", "E2", "E3", "E4", "E5"],
        required=True,
        help="Scenario to generate (E1-E5)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=DEFAULT_SIZE,
        help=f"Cohort size (default: {DEFAULT_SIZE})",
    )
    parser.add_argument(
        "--contention",
        type=int,
        default=DEFAULT_CONTENTION,
        help=f"Top-k for high contention (default: {DEFAULT_CONTENTION})",
    )
    parser.add_argument(
        "--sparse",
        type=float,
        default=DEFAULT_SPARSE_RATE,
        help=f"Sparse rate 0.0-1.0 (default: {DEFAULT_SPARSE_RATE})",
    )
    parser.add_argument(
        "--degenerate", action="store_true", help="Generate degenerate ranks"
    )
    parser.add_argument(
        "--cohorts", type=int, default=10, help="Number of cohorts for E5 (default: 10)"
    )
    parser.add_argument(
        "--submission-rates",
        type=str,
        default="0,10,50,90,100",
        help="Comma-separated submission rates for E5 (default: 0,10,50,90,100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for single cohort scenarios",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for multi-cohort scenarios",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    # Set random seed for reproducibility
    random.seed(args.seed)

    print(f"Generating dataset for scenario {args.scenario} with seed {args.seed}")

    try:
        if args.scenario == "E1":
            data = generate_E1_baseline(args.size)
            output_file = args.output or f"fixture_E1_N{args.size}.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"E1 baseline dataset generated: {output_file}")
            print(f"  - Cohort size: {args.size}")
            print(
                f"  - Participants: {len([obj for obj in data if obj['model'] == 'core.participant'])}"
            )
            print(
                f"  - Preferences: {len([obj for obj in data if obj['model'] == 'matching.preference'])}"
            )

        elif args.scenario == "E2":
            data = generate_E2_contention(args.size, args.contention)
            output_file = (
                args.output or f"fixture_E2_N{args.size}_k{args.contention}.json"
            )
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"E2 high contention dataset generated: {output_file}")
            print(f"  - Cohort size: {args.size}")
            print(f"  - Contention top-k: {args.contention}")
            print(
                f"  - Participants: {len([obj for obj in data if obj['model'] == 'core.participant'])}"
            )
            print(
                f"  - Preferences: {len([obj for obj in data if obj['model'] == 'matching.preference'])}"
            )

        elif args.scenario == "E3":
            data = generate_E3_sparse(args.size, args.sparse)
            output_file = (
                args.output
                or f"fixture_E3_N{args.size}_sparse{int(args.sparse * 100)}.json"
            )
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"E3 sparse preferences dataset generated: {output_file}")
            print(f"  - Cohort size: {args.size}")
            print(f"  - Sparse rate: {args.sparse * 100}%")
            print(
                f"  - Participants: {len([obj for obj in data if obj['model'] == 'core.participant'])}"
            )
            print(
                f"  - Preferences: {len([obj for obj in data if obj['model'] == 'matching.preference'])}"
            )

        elif args.scenario == "E4":
            data = generate_E4_degenerate(args.size)
            output_file = args.output or f"fixture_E4_N{args.size}_degenerate.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"E4 degenerate ranks dataset generated: {output_file}")
            print(f"  - Cohort size: {args.size}")
            print(
                f"  - Participants: {len([obj for obj in data if obj['model'] == 'core.participant'])}"
            )
            print(
                f"  - Preferences: {len([obj for obj in data if obj['model'] == 'matching.preference'])}"
            )

        elif args.scenario == "E5":
            submission_rates = [int(x) for x in args.submission_rates.split(",")]
            cohort_data = generate_E5_multi_cohort(args.cohorts, submission_rates)

            output_dir = args.output_dir
            os.makedirs(output_dir, exist_ok=True)

            total_participants = 0
            total_preferences = 0

            for cohort_id, data in cohort_data.items():
                # Find cohort object to get name
                cohort_obj = next(
                    (obj for obj in data if obj["model"] == "core.cohort"), None
                )
                if cohort_obj:
                    cohort_name = (
                        cohort_obj["fields"]["name"].replace(" ", "_").replace("/", "_")
                    )
                    output_file = os.path.join(
                        output_dir, f"fixture_{cohort_name}_id{cohort_id}.json"
                    )
                    with open(output_file, "w") as f:
                        json.dump(data, f, indent=2)
                    print(f"E5 cohort {cohort_id} dataset generated: {output_file}")

                    participants = len(
                        [obj for obj in data if obj["model"] == "core.participant"]
                    )
                    preferences = len(
                        [obj for obj in data if obj["model"] == "matching.preference"]
                    )
                    total_participants += participants
                    total_preferences += preferences

                    print(f"  - Participants: {participants}")
                    print(f"  - Preferences: {preferences}")

            print(f"\nE5 multi-cohort generation complete:")
            print(f"  - Cohorts: {len(cohort_data)}")
            print(f"  - Total participants: {total_participants}")
            print(f"  - Total preferences: {total_preferences}")

    except Exception as e:
        print(f"Error generating dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
