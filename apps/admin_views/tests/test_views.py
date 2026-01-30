from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import MentorProfile, MenteeProfile


class AdminViewsTest(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin_user = User.objects.create_user(
            "admin", "admin@example.com", "adminpass"
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.regular_user = User.objects.create_user(
            "regular", "regular@example.com", "regularpass"
        )

        # Create cohort
        self.cohort = Cohort.objects.create(name="Test Cohort")

        # Create participants
        self.mentor_participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.regular_user,
            role_in_cohort="MENTOR",
            display_name="Test Mentor",
            organization="Test Org",
        )

        self.mentee_participant = Participant.objects.create(
            cohort=self.cohort,
            user=User.objects.create_user("mentee", "mentee@example.com", "mentee123"),
            role_in_cohort="MENTEE",
            display_name="Test Mentee",
            organization="Test Org",
        )

        # Create clients
        self.client = Client()
        self.admin_client = Client()
        self.admin_client.login(username="admin", password="adminpass")

        self.regular_client = Client()
        self.regular_client.login(username="regular", password="regularpass")

    def test_download_csv_template_requires_admin(self):
        """Test that downloading CSV template requires admin access."""
        # Regular user should be redirected to login
        response = self.client.get(reverse("admin_views:download_csv_template"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.url)

        # Logged in regular user should be redirected to login (because of @user_passes_test)
        response = self.regular_client.get(reverse("admin_views:download_csv_template"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.url)

        # Admin user should get the CSV
        response = self.admin_client.get(reverse("admin_views:download_csv_template"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_import_mentor_csv_requires_admin(self):
        """Test that importing mentor CSV requires admin access."""
        # Regular user should be redirected to login
        response = self.client.get(reverse("admin_views:import_mentor_csv"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.url)

        # Logged in regular user should be redirected to login (because of @user_passes_test)
        response = self.regular_client.get(reverse("admin_views:import_mentor_csv"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.url)

        # Admin user should get the form
        response = self.admin_client.get(reverse("admin_views:import_mentor_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload CSV File")

    def test_mentee_desired_attributes_requires_login(self):
        """Test that mentee desired attributes requires login."""
        # Anonymous user should be redirected to login
        response = self.client.get(
            reverse("admin_views:mentee_desired_attributes", args=[self.cohort.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.url)

        # Logged in user should get the form
        response = self.regular_client.get(
            reverse("admin_views:mentee_desired_attributes", args=[self.cohort.id])
        )
        # But they're not a mentee, so they should get an error
        self.assertEqual(
            response.status_code, 302
        )  # Redirect to home with error message

        # Create a client for the mentee
        mentee_client = Client()
        mentee_client.login(username="mentee", password="mentee123")

        response = mentee_client.get(
            reverse("admin_views:mentee_desired_attributes", args=[self.cohort.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desired Mentor Attributes")

    def test_mentee_desired_attributes_post(self):
        """Test posting to mentee desired attributes."""
        # Create a client for the mentee
        mentee_client = Client()
        mentee_user = User.objects.get(username="mentee")
        mentee_client.login(username="mentee", password="mentee123")

        # Submit form data
        form_data = {
            "desired_tags": "backend,python,career growth",
            "notes": "Looking for experienced backend mentor",
            "desired_attr_same_organization_ok": True,
            "desired_attr_remote_ok": False,
        }

        response = mentee_client.post(
            reverse("admin_views:mentee_desired_attributes", args=[self.cohort.id]),
            data=form_data,
        )

        # Should redirect back to the same page with success message
        self.assertEqual(response.status_code, 302)

        # Check that the profile was updated
        mentee_profile = MenteeProfile.objects.get(participant=self.mentee_participant)
        self.assertEqual(mentee_profile.notes, "Looking for experienced backend mentor")
        self.assertTrue(mentee_profile.desired_attributes["same_organization_ok"])
        self.assertFalse(mentee_profile.desired_attributes["remote_ok"])
