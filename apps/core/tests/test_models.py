from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Cohort, Participant


class CohortModelTest(TestCase):
    def test_cohort_str_representation(self):
        cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")
        self.assertEqual(str(cohort), "TDP 2026")


class ParticipantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")

    def test_participant_str_representation(self):
        participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization="Test Org",
        )
        expected_str = "Test User (MENTOR) - TDP 2026"
        self.assertEqual(str(participant), expected_str)

    def test_participant_unique_constraint(self):
        # Create first participant
        Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization="Test Org",
        )

        # Attempt to create duplicate participant (same user and cohort)
        with self.assertRaises(Exception):
            Participant.objects.create(
                cohort=self.cohort,
                user=self.user,
                role_in_cohort="MENTEE",
                display_name="Test User 2",
                organization="Test Org 2",
            )

    def test_participant_can_be_created_with_empty_organization(self):
        # Create a new cohort to avoid conflicts
        cohort2 = Cohort.objects.create(name="TDP 2027", status="OPEN")
        # This should pass since we're handling validation in forms, not models
        participant = Participant.objects.create(
            cohort=cohort2,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization="",  # Empty organization should be allowed at model level
        )
        self.assertEqual(participant.organization, "")
