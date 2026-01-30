from django.db import models
from apps.core.models import Participant


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
            f"{self.from_participant.display_name} -> "
            f"{self.to_participant.display_name} (rank {self.rank})"
        )
