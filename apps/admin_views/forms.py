from django import forms


class MenteeDesiredAttributesForm(forms.Form):
    """Form for mentee desired attributes."""

    desired_tags = forms.CharField(
        label="Desired Expertise Tags",
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "data-testid": "desired-tags-input",
                "placeholder": "e.g., backend, career growth, leadership",
            }
        ),
    )

    bio = forms.CharField(
        label="Bio",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Tell us about yourself, your goals, and what kind of guidance you need...",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.participant = kwargs.pop("participant", None)
        super().__init__(*args, **kwargs)
