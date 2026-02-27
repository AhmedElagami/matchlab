from django.test import TestCase
from apps.core.models import Cohort, Participant
from django.contrib.auth.models import User
from ..forms import MenteeDesiredAttributesForm


class MenteeDesiredAttributesFormTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.cohort = Cohort.objects.create(name="Test Cohort")
        self.participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee",
        )

    def test_mentee_desired_attributes_form_valid(self):
        """Test that the mentee desired attributes form is valid."""
        form_data = {
            "desired_tags": "backend,python",
            "notes": "Looking for experienced mentor",
            "desired_attr_same_organization_ok": True,
            "desired_attr_remote_ok": False,
            "desired_attr_industry_experience_required": True,
        }
        form = MenteeDesiredAttributesForm(data=form_data, participant=self.participant)
        self.assertTrue(form.is_valid())

    def test_mentee_desired_attributes_form_empty_valid(self):
        """Test that the mentee desired attributes form is valid when empty."""
        form_data = {}
        form = MenteeDesiredAttributesForm(data=form_data, participant=self.participant)
        self.assertTrue(form.is_valid())
