from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Participant, Cohort


class Preference(models.Model):
    """A ranked preference from one participant to another in the same cohort."""

    from_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="given_preferences"
    )
    to_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="received_preferences"
    )
    rank = models.PositiveIntegerField()

    class Meta:
        unique_together = ("from_participant", "to_participant")
        ordering = ["from_participant", "rank"]
        indexes = [
            models.Index(fields=["from_participant", "rank"]),
        ]
        verbose_name_plural = "Preferences"

    def __str__(self):
        return (
            f"{self.from_participant.display_name} -> "  # type: ignore
            f"{self.to_participant.display_name} (rank {self.rank})"  # type: ignore
        )


class MentorProfile(models.Model):
    """Extended profile information for mentors."""

    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, related_name="mentor_profile"
    )
    job_title = models.CharField(max_length=200, blank=True)
    function = models.CharField(max_length=200, blank=True)
    expertise_tags = models.TextField(blank=True, help_text="Comma-separated tags")
    languages = models.TextField(blank=True, help_text="Comma-separated language codes")
    location = models.CharField(max_length=200, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    coaching_topics = models.TextField(blank=True, help_text="Comma-separated topics")
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Mentor Profiles"

    def __str__(self):
        return f"Mentor Profile: {self.participant.display_name}"  # type: ignore

    def get_expertise_tags_list(self):
        """Return expertise tags as a list."""
        if self.expertise_tags:
            return [tag.strip() for tag in self.expertise_tags.split(",")]  # type: ignore
        return []

    def get_languages_list(self):
        """Return languages as a list."""
        if self.languages:
            return [lang.strip() for lang in self.languages.split(",")]  # type: ignore
        return []

    def get_coaching_topics_list(self):
        """Return coaching topics as a list."""
        if self.coaching_topics:
            return [topic.strip() for topic in self.coaching_topics.split(",")]  # type: ignore
        return []


class MenteeProfile(models.Model):
    """Extended profile information for mentees."""

    participant = models.OneToOneField(
        Participant, on_delete=models.CASCADE, related_name="mentee_profile"
    )
    desired_attributes = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Mentee Profiles"

    def __str__(self):
        return f"Mentee Profile: {self.participant.display_name}"  # type: ignore


class ImportJob(models.Model):
    """Track CSV import jobs."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("PREVIEW", "Preview"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    file_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    total_rows = models.IntegerField(default=0)  # type: ignore
    processed_rows = models.IntegerField(default=0)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Import Jobs"

    def __str__(self):
        return f"Import Job: {self.name} ({self.status})"


class PairScore(models.Model):
    """Computed match scores between mentor-mentee pairs."""

    cohort = models.ForeignKey(
        "core.Cohort", on_delete=models.CASCADE, related_name="pair_scores"
    )
    mentor = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="mentor_scores"
    )
    mentee = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="mentee_scores"
    )
    score = models.FloatField(help_text="Overall match percentage (0-100)")
    score_breakdown = models.JSONField(
        default=dict, help_text="Detailed breakdown of score components"
    )
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("mentor", "mentee")
        verbose_name_plural = "Pair Scores"
        indexes = [
            models.Index(fields=["cohort", "-score"]),
            models.Index(fields=["mentor", "-score"]),
            models.Index(fields=["mentee", "-score"]),
        ]

    def __str__(self):
        return f"{self.mentor.display_name} <-> {self.mentee.display_name}: {self.score:.1f}%"


class MatchRun(models.Model):
    """A matching run execution."""

    MODE_CHOICES = [
        ("STRICT", "Strict"),
        ("EXCEPTION", "Exception"),
    ]

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    objective_summary = models.JSONField(
        default=dict, blank=True, help_text="Totals, exception counts, total score"
    )
    failure_report = models.JSONField(
        default=dict, blank=True, help_text="Failure diagnostics when status=FAILED"
    )
    input_signature = models.TextField(
        blank=True, help_text="Hash of relevant input for traceability"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Match Runs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Match Run {self.id} ({self.mode}, {self.status}) - {self.cohort.name}"


class Match(models.Model):
    """A single mentor-mentee match from a match run."""

    match_run = models.ForeignKey(MatchRun, on_delete=models.CASCADE, related_name="matches")
    mentor = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="mentor_matches")
    mentee = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="mentee_matches")
    
    # Match metrics
    score_percent = models.IntegerField(help_text="Match percentage (0-100)")
    
    # Ambiguity detection
    ambiguity_flag = models.BooleanField(default=False, help_text="Whether this match is ambiguous")
    ambiguity_reason = models.TextField(blank=True, help_text="Explanation of ambiguity if flagged")
    
    # Exception handling
    exception_flag = models.BooleanField(default=False, help_text="Whether this match violates policies")
    exception_type = models.CharField(max_length=20, blank=True, help_text="Type of exception if any")
    exception_reason = models.TextField(blank=True, help_text="Explanation of exception if flagged")
    
    # Manual overrides
    is_manual_override = models.BooleanField(default=False, help_text="Whether this was manually overridden")
    override_reason = models.TextField(blank=True, help_text="Reason for manual override if applicable")

    class Meta:
        verbose_name_plural = "Matches"
        unique_together = (
            ("match_run", "mentor"),
            ("match_run", "mentee"),
        )

    def __str__(self):
        return f"{self.mentor.display_name} <-> {self.mentee.display_name} ({self.score_percent}%)"


class ActiveMatchRun(models.Model):
    """The currently active match run for a cohort."""

    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE)
    match_run = models.ForeignKey(MatchRun, on_delete=models.CASCADE)
    set_by = models.ForeignKey(User, on_delete=models.CASCADE)
    set_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Active Match Runs"

    def __str__(self):
        return f"Active Match Run for {self.cohort.name}: {self.match_run.id}"
