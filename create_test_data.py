#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import MentorProfile, MenteeProfile


def create_test_data():
    print("Creating test data...")

    # Create cohorts
    cohort1, created = Cohort.objects.get_or_create(
        name="Engineering Mentoring Program 2026", defaults={"status": "OPEN"}
    )
    print(f"Created cohort: {cohort1.name}")

    # Create users
    users_data = [
        {
            "username": "mentor1",
            "email": "mentor1@example.com",
            "first_name": "Alice",
            "last_name": "Johnson",
        },
        {
            "username": "mentor2",
            "email": "mentor2@example.com",
            "first_name": "Bob",
            "last_name": "Smith",
        },
        {
            "username": "mentor3",
            "email": "mentor3@example.com",
            "first_name": "Carol",
            "last_name": "Williams",
        },
        {
            "username": "mentee1",
            "email": "mentee1@example.com",
            "first_name": "David",
            "last_name": "Brown",
        },
        {
            "username": "mentee2",
            "email": "mentee2@example.com",
            "first_name": "Emma",
            "last_name": "Davis",
        },
        {
            "username": "mentee3",
            "email": "mentee3@example.com",
            "first_name": "Frank",
            "last_name": "Miller",
        },
        {
            "username": "mentee4",
            "email": "mentee4@example.com",
            "first_name": "Grace",
            "last_name": "Wilson",
        },
    ]

    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
            },
        )
        # Set password for all users
        user.set_password("test123")
        user.save()
        users.append(user)
        print(f"Created user: {user.username}")

    # Create participants
    mentors = users[:3]  # First 3 users as mentors
    mentees = users[3:]  # Last 4 users as mentees

    # Create mentor participants
    mentor_participants = []
    for i, user in enumerate(mentors):
        participant, created = Participant.objects.get_or_create(
            cohort=cohort1,
            user=user,
            defaults={
                "role_in_cohort": "MENTOR",
                "display_name": f"{user.first_name} {user.last_name}",
                "organization": "TechCorp" if i % 2 == 0 else "InnovateInc",
                "is_submitted": True,
            },
        )
        mentor_participants.append(participant)
        print(f"Created mentor participant: {participant.display_name}")

        # Create mentor profile
        mentor_profile, created = MentorProfile.objects.get_or_create(
            participant=participant,
            defaults={
                "job_title": "Senior Engineer" if i % 2 == 0 else "Engineering Manager",
                "function": "Software Development"
                if i % 2 == 0
                else "Product Management",
                "expertise_tags": "python,django,javascript,react"
                if i == 0
                else "java,spring,aws,microservices"
                if i == 1
                else "python,data-science,machine-learning,tensorflow",
                "languages": "en,fr" if i == 0 else "en,es" if i == 1 else "en,de",
                "location": "New York"
                if i == 0
                else "San Francisco"
                if i == 1
                else "Berlin",
                "years_experience": 8 if i == 0 else 12 if i == 1 else 10,
                "coaching_topics": "career development,technical leadership"
                if i == 0
                else "cloud architecture,system design"
                if i == 1
                else "data science,ml algorithms",
                "bio": f"Experienced engineer with expertise in modern technologies.",
            },
        )
        print(f"Created mentor profile for: {participant.display_name}")

    # Create mentee participants
    mentee_participants = []
    for i, user in enumerate(mentees):
        participant, created = Participant.objects.get_or_create(
            cohort=cohort1,
            user=user,
            defaults={
                "role_in_cohort": "MENTEE",
                "display_name": f"{user.first_name} {user.last_name}",
                "organization": "TechCorp" if i % 2 == 0 else "StartupXYZ",
                "is_submitted": True,
            },
        )
        mentee_participants.append(participant)
        print(f"Created mentee participant: {participant.display_name}")

        # Create mentee profile
        mentee_profile, created = MenteeProfile.objects.get_or_create(
            participant=participant,
            defaults={
                "desired_attributes": {
                    "preferred_expertise": ["python", "javascript"]
                    if i == 0
                    else ["java", "aws"]
                    if i == 1
                    else ["data-science", "machine-learning"],
                    "preferred_location": "New York"
                    if i == 0
                    else "San Francisco"
                    if i == 1
                    else "Remote",
                    "preferred_languages": ["en"]
                    if i == 0
                    else ["en", "es"]
                    if i == 1
                    else ["en", "de"],
                },
                "notes": f"Looking for mentorship in {'software engineering' if i < 2 else 'data science'}",
            },
        )
        print(f"Created mentee profile for: {participant.display_name}")

    print("\nTest data creation completed!")
    print("\nUsers created:")
    for user in users:
        print(f"  - {user.username} (password: test123)")
    print(f"\nCohort: {cohort1.name}")
    print(f"Mentors: {len(mentor_participants)}")
    print(f"Mentees: {len(mentee_participants)}")


if __name__ == "__main__":
    create_test_data()
