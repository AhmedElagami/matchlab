#!/usr/bin/env python
import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from django.db import connection

print("Clearing existing data...")
Participant.objects.all().delete()
User.objects.all().delete()
Cohort.objects.all().delete()

# Reset sequences
with connection.cursor() as cursor:
    cursor.execute("ALTER SEQUENCE core_cohort_id_seq RESTART WITH 1")
    cursor.execute("ALTER SEQUENCE auth_user_id_seq RESTART WITH 1")
    cursor.execute("ALTER SEQUENCE core_participant_id_seq RESTART WITH 1")
print("✓ Sequences reset")

with open('fixtures/cohort_3x3.json', 'r') as f:
    data = json.load(f)

cohorts = [obj for obj in data if obj['model'] == 'core.cohort']
users = [obj for obj in data if obj['model'] == 'auth.user']
participants = [obj for obj in data if obj['model'] == 'core.participant']

print(f"\nLoading {len(cohorts)} cohorts, {len(users)} users, {len(participants)} participants...")

for obj in cohorts:
    c = Cohort.objects.create(name=obj['fields']['name'], status=obj['fields']['status'], created_at=obj['fields']['created_at'])
    print(f"✓ Cohort: {c.name} (ID: {c.id})")

for obj in users:
    u = User.objects.create(username=obj['fields']['username'], first_name=obj['fields']['first_name'], last_name=obj['fields']['last_name'], email=obj['fields']['email'], password=obj['fields']['password'], is_staff=obj['fields']['is_staff'], is_active=obj['fields']['is_active'], is_superuser=obj['fields']['is_superuser'], date_joined=obj['fields']['date_joined'])
    print(f"✓ User: {u.username} (ID: {u.id})")

for obj in participants:
    p = Participant.objects.create(user_id=obj['fields']['user'], cohort_id=obj['fields']['cohort'], role_in_cohort=obj['fields']['role_in_cohort'], display_name=obj['fields'].get('display_name', ''), organization=obj['fields'].get('organization', ''), is_submitted=obj['fields'].get('is_submitted', False), created_at=obj['fields']['created_at'], updated_at=obj['fields']['updated_at'])
    print(f"✓ Participant: {p.display_name}")

print("\nSetting passwords...")
for user in User.objects.all():
    user.set_password('testpass123')
    user.save()

admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

print("\n✅ SUCCESS! Database loaded with test data.")
print("\nLogin at: http://localhost:8000/auth/login/")
print("\nCredentials:")
print("  Admin: admin / admin123")
print("  Test users: mentor1, mentor2, mentor3, mentee1, mentee2, mentee3 / testpass123")
