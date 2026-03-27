from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Cohort, Organization, Participant


class CohortModelTest(TestCase):
    def test_cohort_str_representation(self):
        cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")
        self.assertEqual(str(cohort), "TDP 2026")


class OrganizationModelTest(TestCase):
    def test_organization_str_representation(self):
        org = Organization.objects.create(name="Test Org")
        self.assertEqual(str(org), "Test Org")

    def test_organization_name_uniqueness(self):
        Organization.objects.create(name="Unique Org")
        with self.assertRaises(Exception):
            Organization.objects.create(name="Unique Org")

    def test_organization_default_ordering(self):
        Organization.objects.create(name="Charlie")
        Organization.objects.create(name="Alpha")
        Organization.objects.create(name="Bravo")
        orgs = list(Organization.objects.values_list("name", flat=True))
        self.assertEqual(orgs, ["Alpha", "Bravo", "Charlie"])


class ParticipantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")
        self.org = Organization.objects.create(name="Test Org")

    def test_participant_str_representation(self):
        participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization=self.org,
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
            organization=self.org,
        )

        # Attempt to create duplicate participant (same user and cohort)
        with self.assertRaises(Exception):
            Participant.objects.create(
                cohort=self.cohort,
                user=self.user,
                role_in_cohort="MENTEE",
                display_name="Test User 2",
                organization=self.org,
            )

    def test_participant_can_be_created_with_empty_organization(self):
        # Create a new cohort to avoid conflicts
        cohort2 = Cohort.objects.create(name="TDP 2027", status="OPEN")
        # NULL organization should be allowed at model level
        participant = Participant.objects.create(
            cohort=cohort2,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization=None,
        )
        self.assertIsNone(participant.organization)

    def test_organization_name_property_with_org(self):
        participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization=self.org,
        )
        self.assertEqual(participant.organization_name, "Test Org")

    def test_organization_name_property_without_org(self):
        cohort2 = Cohort.objects.create(name="TDP 2027", status="OPEN")
        participant = Participant.objects.create(
            cohort=cohort2,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization=None,
        )
        self.assertEqual(participant.organization_name, "")
