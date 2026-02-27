from django.test import TestCase
from ..forms import ParticipantProfileForm
from ..models import Cohort, Participant
from django.contrib.auth.models import User


class ParticipantProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")

    def test_form_valid_with_complete_data(self):
        form_data = {"display_name": "Test User", "organization": "Test Organization"}
        form = ParticipantProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_organization(self):
        form_data = {
            "display_name": "Test User",
            "organization": "",  # Empty organization
        }
        form = ParticipantProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization", form.errors)
        self.assertEqual(form.errors["organization"], ["Organization is required."])

    def test_form_invalid_without_display_name(self):
        form_data = {
            "display_name": "",  # Empty display name
            "organization": "Test Organization",
        }
        form = ParticipantProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("display_name", form.errors)
