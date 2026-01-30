from django.db import models
from django.contrib.auth.models import User


class Cohort(models.Model):
    """A grouping of mentors and mentees for matching."""

    name = models.CharField(max_length=200, unique=True)
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
        ("MATCHED", "Matched"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    cohort_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for scoring weights and thresholds",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Cohorts"


class Participant(models.Model):
    """A user participating in a cohort as either mentor or mentee."""

    ROLE_CHOICES = [
        ("MENTOR", "Mentor"),
        ("MENTEE", "Mentee"),
    ]

    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_in_cohort = models.CharField(max_length=10, choices=ROLE_CHOICES)
    display_name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cohort", "user")
        indexes = [
            models.Index(fields=["cohort", "role_in_cohort"]),
        ]
        verbose_name_plural = "Participants"

    def __str__(self):
        return f"{self.display_name} ({self.role_in_cohort}) - {self.cohort.name}"
