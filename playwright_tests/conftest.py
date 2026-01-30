"""Pytest configuration for Playwright tests."""

import pytest
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure database for tests."""
    pass


@pytest.fixture
def admin_user(db):
    """Create admin user for tests."""
    user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )
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