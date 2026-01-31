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
    print("Setting preferences for all mentors and mentees (fixed version)...")

    # Get the cohort
    cohort = Cohort.objects.get(name="Engineering Mentoring Program 2026")
    print(f"Using cohort: {cohort.name}")

    # Get all mentors and mentees
    mentors = list(Participant.objects.filter(cohort=cohort, role_in_cohort="MENTOR"))
    mentees = list(Participant.objects.filter(cohort=cohort, role_in_cohort="MENTEE"))

    print(f"Found {len(mentors)} mentors and {len(mentees)} mentees")

    # Create a mapping to identify unique participants
    mentor_users = {m.user.username: m for m in mentors}
    mentee_users = {m.user.username: m for m in mentees}

    print("\nMentors:")
    for username, mentor in mentor_users.items():
        print(f"  {username}: {mentor.display_name}")

    print("\nMentees:")
    for username, mentee in mentee_users.items():
        print(f"  {username}: {mentee.display_name}")

    # Clear existing preferences
    Preference.objects.all().delete()

    # Set preferences for mentors (ranking mentees)
    print("\nSetting preferences for mentors:")
    for username, mentor in mentor_users.items():
        # Shuffle mentees to create random rankings
        shuffled_mentees = list(mentee_users.values())
        random.shuffle(shuffled_mentees)

        # Create preferences (rank 1-4, some mentors may not rank all mentees)
        num_preferences = min(
            random.randint(2, len(shuffled_mentees)), len(shuffled_mentees)
        )
        for i in range(num_preferences):
            Preference.objects.update_or_create(
                from_participant=mentor,
                to_participant=shuffled_mentees[i],
                defaults={"rank": i + 1},
            )

        print(f"  {mentor.display_name}: Ranked {num_preferences} mentees")

    # Set preferences for mentees (ranking mentors)
    print("\nSetting preferences for mentees:")
    for username, mentee in mentee_users.items():
        # Shuffle mentors to create random rankings
        shuffled_mentors = list(mentor_users.values())
        random.shuffle(shuffled_mentors)

        # Create preferences (rank 1-3, some mentees may not rank all mentors)
        num_preferences = min(
            random.randint(2, len(shuffled_mentors)), len(shuffled_mentors)
        )
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

    # Verify mutual preferences exist
    print("\nChecking mutual preferences...")
    mutual_count = 0
    for pref in Preference.objects.filter(from_participant__role_in_cohort="MENTOR"):
        if Preference.objects.filter(
            from_participant=pref.to_participant, to_participant=pref.from_participant
        ).exists():
            mutual_count += 1
            print(
                f"  Mutual preference: {pref.from_participant.display_name} <-> {pref.to_participant.display_name}"
            )

    print(f"\nTotal mutual preferences: {mutual_count}")

    print("\nPreferences set successfully!")
    print("All participants marked as submitted and ready for matching.")


if __name__ == "__main__":
    set_preferences()
