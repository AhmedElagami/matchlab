from django import forms
from django.db import transaction
from apps.core.models import Participant
from .models import Preference


class PreferencesForm(forms.Form):
    """Form for entering ranked preferences."""

    def __init__(self, *args, **kwargs):
        self.participant = kwargs.pop("participant")
        self.candidates = kwargs.pop("candidates")
        super().__init__(*args, **kwargs)

        # Create a field for each candidate
        for candidate in self.candidates:
            field_name = f"candidate_{candidate.id}"
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=1,
                widget=forms.NumberInput(
                    attrs={
                        "class": "form-control",
                        "data-testid": f"pref-rank-input-{candidate.id}",
                        "placeholder": "Enter rank",
                    }
                ),
            )

    def clean(self):
        cleaned_data = super().clean()
        ranks = {}

        # Collect all non-empty ranks
        for candidate in self.candidates:
            field_name = f"candidate_{candidate.id}"
            rank = cleaned_data.get(field_name)
            if rank is not None:
                if rank in ranks:
                    ranks[rank].append(candidate)
                else:
                    ranks[rank] = [candidate]

        # Check for duplicates
        duplicates = {
            rank: candidates
            for rank, candidates in ranks.items()
            if len(candidates) > 1
        }
        if duplicates:
            # We'll resolve these in the save method
            self.duplicates = duplicates

        return cleaned_data

    def save(self):
        """Save preferences and resolve duplicates if needed."""
        with transaction.atomic():
            # Delete existing preferences
            Preference.objects.filter(from_participant=self.participant).delete()

            # Collect all non-empty ranks with their candidates
            ranks_data = []
            for candidate in self.candidates:
                field_name = f"candidate_{candidate.id}"
                rank = self.cleaned_data.get(field_name)
                if rank is not None:
                    ranks_data.append((rank, candidate))

            # Sort by rank and then by candidate id for consistency
            ranks_data.sort(key=lambda x: (x[0], x[1].id))

            # Debug logging
            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"Saving preferences for participant {self.participant.id}")
            logger.info(f"Ranks data: {ranks_data}")

            # Sort by rank and then by candidate id (to ensure consistent ordering for duplicates)
            ranks_data.sort(key=lambda x: (x[0], x[1].id))

            # Resolve duplicates by renumbering
            normalized_ranks = {}
            current_rank = 1
            duplicate_warning = False

            i = 0
            while i < len(ranks_data):
                original_rank, candidate = ranks_data[i]
                if original_rank in normalized_ranks:
                    # This is a duplicate rank
                    duplicate_warning = True
                    normalized_ranks[current_rank] = candidate
                else:
                    normalized_ranks[current_rank] = candidate
                    # Check if there are more candidates with the same rank
                    j = i + 1
                    while j < len(ranks_data) and ranks_data[j][0] == original_rank:
                        # Found duplicate, increment current_rank for the duplicate
                        current_rank += 1
                        normalized_ranks[current_rank] = ranks_data[j][1]
                        duplicate_warning = True
                        j += 1
                    i = j - 1  # Skip the duplicates we just processed

                current_rank += 1
                i += 1

            # Create preference objects
            preferences_to_create = []
            for rank, candidate in normalized_ranks.items():
                preferences_to_create.append(
                    Preference(
                        from_participant=self.participant,
                        to_participant=candidate,
                        rank=rank,
                    )
                )

            # Bulk create all preferences
            Preference.objects.bulk_create(preferences_to_create)

            return duplicate_warning, normalized_ranks
