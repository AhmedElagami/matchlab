#!/usr/bin/env python
import os
import sys
import random
import django

# Setup Django environment
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import Cohort, Participant
from apps.matching.models import Preference


def set_preferences():
    print("Setting preferences for all mentors and mentees...")

    # Get the cohort
    cohort = Cohort.objects.get(name="Engineering Mentoring Program 2026")
    print(f"Using cohort: {cohort.name}")

    # Get all mentors and mentees
    mentors = list(Participant.objects.filter(cohort=cohort, role_in_cohort="MENTOR"))
    mentees = list(Participant.objects.filter(cohort=cohort, role_in_cohort="MENTEE"))

    print(f"Found {len(mentors)} mentors and {len(mentees)} mentees")

    # Set preferences for mentors (ranking mentees)
    print("\nSetting preferences for mentors:")
    for mentor in mentors:
        # Shuffle mentees to create random rankings
        shuffled_mentees = mentees.copy()
        random.shuffle(shuffled_mentees)

        # Create preferences (rank 1-4, some mentors may not rank all mentees)
        num_preferences = min(random.randint(2, len(mentees)), len(mentees))
        for i in range(num_preferences):
            Preference.objects.update_or_create(
                from_participant=mentor,
                to_participant=shuffled_mentees[i],
                defaults={"rank": i + 1},
            )

        print(f"  {mentor.display_name}: Ranked {num_preferences} mentees")

    # Set preferences for mentees (ranking mentors)
    print("\nSetting preferences for mentees:")
    for mentee in mentees:
        # Shuffle mentors to create random rankings
        shuffled_mentors = mentors.copy()
        random.shuffle(shuffled_mentors)

        # Create preferences (rank 1-3, some mentees may not rank all mentors)
        num_preferences = min(random.randint(2, len(mentors)), len(mentors))
        for i in range(num_preferences):
            Preference.objects.update_or_create(
                from_participant=mentee,
                to_participant=shuffled_mentors[i],
                defaults={"rank": i + 1},
            )

        print(f"  {mentee.display_name}: Ranked {num_preferences} mentors")

    # Mark all participants as submitted
    print("\nMarking all participants as submitted...")
    Participant.objects.filter(cohort=cohort).update(is_submitted=True)

    print("\nPreferences set successfully!")
    print("All participants marked as submitted and ready for matching.")


if __name__ == "__main__":
    set_preferences()
