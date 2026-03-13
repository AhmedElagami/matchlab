#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant

# Clear existing data
print("Clearing existing data...")
Participant.objects.all().delete()
User.objects.all().delete()
Cohort.objects.all().delete()

# Load fixture
with open('fixtures/cohort_3x3.json', 'r') as f:
    data = json.load(f)

# Separate by model
cohorts = [obj for obj in data if obj['model'] == 'core.cohort']
users = [obj for obj in data if obj['model'] == 'auth.user']
participants = [obj for obj in data if obj['model'] == 'core.participant']

print(f"Loading {len(cohorts)} cohorts, {len(users)} users, {len(participants)} participants...")

# Load cohorts first
for obj in cohorts:
    Cohort.objects.create(
        id=obj['pk'],
        name=obj['fields']['name'],
        status=obj['fields']['status'],
        created_at=obj['fields']['created_at']
    )
    print(f"Created cohort: {obj['fields']['name']}")

# Load users
for obj in users:
    User.objects.create(
        id=obj['pk'],
        username=obj['fields']['username'],
        first_name=obj['fields']['first_name'],
        last_name=obj['fields']['last_name'],
        email=obj['fields']['email'],
        password=obj['fields']['password'],
        is_staff=obj['fields']['is_staff'],
        is_active=obj['fields']['is_active'],
        is_superuser=obj['fields']['is_superuser'],
        date_joined=obj['fields']['date_joined']
    )
    print(f"Created user: {obj['fields']['username']}")

# Load participants
for obj in participants:
    Participant.objects.create(
        id=obj['pk'],
        user_id=obj['fields']['user'],
        cohort_id=obj['fields']['cohort'],
        role_in_cohort=obj['fields']['role'],
        display_name=obj['fields'].get('display_name', ''),
        organization=obj['fields'].get('organization', ''),
        is_submitted=obj['fields'].get('preferences_submitted', False)
    )
        created_at=obj'['fields']['created_at'],
        updated_at=obj'['fields']['updated_at']
    print(f"Created participant: {obj['fields'].get('display_name', 'N/A')}")

# Set passwords for all users
print("\nSetting passwords...")
for user in User.objects.all():
    user.set_password('testpass123')
    user.save()
    print(f"Set password for: {user.username}")

# Create admin user
print("\nCreating admin user...")
admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(f"Created admin user")

print("\n✓ Fixture loaded successfully!")
print("Login credentials:")
print("  Admin: admin / admin123")
print("  Test users: mentor1, mentor2, mentor3, mentee1, mentee2, mentee3 / testpass123")
