from django import forms
from .models import Participant


class ParticipantProfileForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["display_name", "organization"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "data-testid": "display-name-input"}
            ),
            "organization": forms.TextInput(
                attrs={"class": "form-control", "data-testid": "organization-input"}
            ),
        }
        labels = {
            "display_name": "Display Name",
            "organization": "Organization",
        }
        help_texts = {
            "display_name": "Your name as it will appear to others",
            "organization": "Your organization (required)",
        }

    def clean_organization(self):
        organization = self.cleaned_data.get("organization")
        if not organization:
            raise forms.ValidationError("Organization is required.")
        return organization
