from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Cohort, Participant


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.cohort = Cohort.objects.create(name="TDP 2026", status="OPEN")
        self.participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test User",
            organization="Test Org",
        )

    def test_home_view_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("core:home"))
        self.assertRedirects(response, "/auth/login/?next=/")

    def test_home_view_accessible_to_logged_in_user(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse("core:profile", args=[self.cohort.id]))
        self.assertRedirects(
            response, f"/auth/login/?next=/cohorts/{self.cohort.id}/profile/"
        )

    def test_profile_view_shows_correct_data(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:profile", args=[self.cohort.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
        self.assertContains(response, "Test Org")

    def test_profile_form_validation(self):
        self.client.login(username="testuser", password="testpass123")
        # Try to submit form with empty organization
        response = self.client.post(
            reverse("core:profile", args=[self.cohort.id]),
            {
                "display_name": "Updated Name",
                "organization": "",  # Empty organization should cause validation error
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organization is required.")
