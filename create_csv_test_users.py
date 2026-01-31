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


def create_csv_test_users():
    print("Creating CSV test users...")

    # Get the existing cohort
    cohort = Cohort.objects.get(name="Engineering Mentoring Program 2026")
    print(f"Using cohort: {cohort.name}")

    # Users from the sample CSV that need to be created
    mentor_users_data = [
        {
            "username": "johndoe",
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
        },
        {
            "username": "janesmith",
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
        },
        {
            "username": "mikejohnson",
            "email": "mike.johnson@example.com",
            "first_name": "Mike",
            "last_name": "Johnson",
        },
        {
            "username": "sarahwilson",
            "email": "sarah.wilson@example.com",
            "first_name": "Sarah",
            "last_name": "Wilson",
        },
        {
            "username": "davidbrown",
            "email": "david.brown@example.com",
            "first_name": "David",
            "last_name": "Brown",
        },
    ]

    # Create mentor users
    mentor_users = []
    for user_data in mentor_users_data:
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
        mentor_users.append(user)
        status = "Created" if created else "Exists"
        print(f"{status} user: {user.username} ({user.email})")

    # Create mentor participants
    for i, user in enumerate(mentor_users):
        participant, created = Participant.objects.get_or_create(
            cohort=cohort,
            user=user,
            defaults={
                "role_in_cohort": "MENTOR",
                "display_name": f"{user.first_name} {user.last_name}",
                "organization": mentor_users_data[i]["email"]
                .split("@")[1]
                .split(".")[0]
                .capitalize()
                + " "
                + mentor_users_data[i]["email"].split("@")[1].split(".")[1].capitalize()
                if "." in mentor_users_data[i]["email"].split("@")[1]
                else mentor_users_data[i]["email"]
                .split("@")[1]
                .split(".")[0]
                .capitalize(),
                "is_submitted": False,
            },
        )
        status = "Created" if created else "Exists"
        print(f"{status} mentor participant: {participant.display_name}")

        # Create/update mentor profile
        mentor_profile, created = MentorProfile.objects.get_or_create(
            participant=participant,
            defaults={
                "job_title": "Senior Software Engineer"
                if i == 0
                else "Engineering Manager"
                if i == 1
                else "Data Science Lead"
                if i == 2
                else "Cloud Architect"
                if i == 3
                else "Security Engineer",
                "function": "Engineering"
                if i in [0, 1, 3]
                else "Management"
                if i == 1
                else "Data Science"
                if i == 2
                else "Infrastructure"
                if i == 3
                else "Security",
                "expertise_tags": "python,django,react,aws"
                if i == 0
                else "java,spring,kubernetes,azure"
                if i == 1
                else "python,tensorflow,sql,machine-learning"
                if i == 2
                else "aws,gcp,terraform,docker,kubernetes"
                if i == 3
                else "cybersecurity,networking,compliance,penetration-testing",
                "languages": "english,spanish"
                if i == 0
                else "english,french"
                if i == 1
                else "english,german"
                if i == 2
                else "english"
                if i == 3
                else "english,portuguese",
                "location": "San Francisco"
                if i == 0
                else "New York"
                if i == 1
                else "Berlin"
                if i == 2
                else "Austin"
                if i == 3
                else "London",
                "years_experience": 8
                if i == 0
                else 12
                if i == 1
                else 10
                if i == 2
                else 9
                if i == 3
                else 7,
                "coaching_topics": "career development,technical leadership,system design"
                if i == 0
                else "team leadership,project management,agile methodologies"
                if i == 1
                else "data science careers,ml algorithms,model deployment"
                if i == 2
                else "cloud migration,devops,infrastructure as code"
                if i == 3
                else "cybersecurity careers,secure coding,compliance frameworks",
                "bio": "Experienced software engineer with 8 years in web development and cloud technologies"
                if i == 0
                else "Seasoned engineering manager with expertise in building scalable distributed systems"
                if i == 1
                else "Data science expert with focus on machine learning and big data analytics"
                if i == 2
                else "Cloud specialist with deep experience in multi-cloud architectures and DevOps practices"
                if i == 3
                else "Information security professional with focus on application security and compliance",
            },
        )
        status = "Created" if created else "Updated"
        print(f"{status} mentor profile for: {participant.display_name}")

    # Users for mentees
    mentee_users_data = [
        {
            "username": "alexchen",
            "email": "alex.chen@example.com",
            "first_name": "Alex",
            "last_name": "Chen",
        },
        {
            "username": "mariagarcia",
            "email": "maria.garcia@example.com",
            "first_name": "Maria",
            "last_name": "Garcia",
        },
        {
            "username": "tomwalker",
            "email": "tom.walker@example.com",
            "first_name": "Tom",
            "last_name": "Walker",
        },
        {
            "username": "lisakumar",
            "email": "lisa.kumar@example.com",
            "first_name": "Lisa",
            "last_name": "Kumar",
        },
        {
            "username": "kevinlopez",
            "email": "kevin.lopez@example.com",
            "first_name": "Kevin",
            "last_name": "Lopez",
        },
        {
            "username": "sophiemuller",
            "email": "sophie.muller@example.com",
            "first_name": "Sophie",
            "last_name": "Muller",
        },
    ]

    # Create mentee users
    mentee_users = []
    for user_data in mentee_users_data:
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
        mentee_users.append(user)
        status = "Created" if created else "Exists"
        print(f"{status} user: {user.username} ({user.email})")

    # Create mentee participants
    organizations = [
        "StartupXYZ",
        "TechCorp",
        "InnovateInc",
        "DataDriven LLC",
        "CloudFirst Inc",
        "FinTech Solutions",
    ]
    for i, user in enumerate(mentee_users):
        participant, created = Participant.objects.get_or_create(
            cohort=cohort,
            user=user,
            defaults={
                "role_in_cohort": "MENTEE",
                "display_name": f"{user.first_name} {user.last_name}",
                "organization": organizations[i],
                "is_submitted": False,
            },
        )
        status = "Created" if created else "Exists"
        print(f"{status} mentee participant: {participant.display_name}")

        # Create/update mentee profile
        mentee_profile, created = MenteeProfile.objects.get_or_create(
            participant=participant,
            defaults={
                "desired_attributes": {
                    "preferred_expertise": ["python", "javascript", "react"]
                    if i == 0
                    else ["java", "spring", "aws"]
                    if i == 1
                    else ["data-science", "machine-learning", "python"]
                    if i == 2
                    else ["tensorflow", "sql", "statistics"]
                    if i == 3
                    else ["aws", "gcp", "devops"]
                    if i == 4
                    else ["cybersecurity", "networking"],
                    "preferred_location": "San Francisco"
                    if i == 0
                    else "New York"
                    if i == 1
                    else "Remote"
                    if i == 2
                    else "Berlin"
                    if i == 3
                    else "Austin"
                    if i == 4
                    else "London",
                    "preferred_languages": ["english", "chinese"]
                    if i == 0
                    else ["english", "spanish"]
                    if i == 1
                    else ["english"]
                    if i == 2
                    else ["english", "hindi"]
                    if i == 3
                    else ["english", "portuguese"]
                    if i == 4
                    else ["english", "german"],
                },
                "notes": "Looking for mentorship in full-stack web development"
                if i == 0
                else "Seeking guidance in enterprise Java development and cloud architectures"
                if i == 1
                else "Interested in data science and ML career growth"
                if i == 2
                else "Want to advance in data science and analytics"
                if i == 3
                else "Looking for cloud infrastructure mentorship"
                if i == 4
                else "Seeking expertise in information security",
            },
        )
        status = "Created" if created else "Updated"
        print(f"{status} mentee profile for: {participant.display_name}")

    print("\nAll CSV test users have been created!")
    print("You can now use the sample CSV files for import testing.")


if __name__ == "__main__":
    create_csv_test_users()
