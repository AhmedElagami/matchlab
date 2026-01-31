from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    role = forms.ChoiceField(
        choices=[("MENTOR", "Mentor"), ("MENTEE", "Mentee")],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
