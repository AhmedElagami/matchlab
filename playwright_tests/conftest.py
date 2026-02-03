"""Pytest configuration for Playwright tests."""

import os
import pytest
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure database for tests."""
    pass


@pytest.fixture
def admin_user(db):
    """Create admin user for tests."""
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@test.com",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        user.set_password("testpass123")
    else:
        user.email = "admin@test.com"
        user.is_staff = True
        user.is_superuser = True
        user.set_password("testpass123")
    user.save()
    return user


@pytest.fixture
def test_cohort(db):
    """Create test cohort."""
    return Cohort.objects.create(name="Test Cohort")


@pytest.fixture
def mentor_user(db, test_cohort):
    """Create mentor user and participant."""
    user = User.objects.create_user(
        username="mentor",
        email="mentor@test.com",
        password="testpass123",
    )
    participant = Participant.objects.create(
        user=user,
        cohort=test_cohort,
        display_name="Test Mentor",
        role_in_cohort="MENTOR",
        organization="Test Org",
        is_submitted=True,
    )
    return user, participant


@pytest.fixture
def mentee_user(db, test_cohort):
    """Create mentee user and participant."""
    user = User.objects.create_user(
        username="mentee",
        email="mentee@test.com",
        password="testpass123",
    )
    participant = Participant.objects.create(
        user=user,
        cohort=test_cohort,
        display_name="Test Mentee",
        role_in_cohort="MENTEE",
        organization="Test Org",
        is_submitted=True,
    )
    return user, participant
