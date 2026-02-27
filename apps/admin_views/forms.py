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

    # We'll dynamically add checkboxes for boolean attributes
    notes = forms.CharField(
        label="Additional Notes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Any additional information about your preferred mentor...",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.participant = kwargs.pop("participant", None)
        super().__init__(*args, **kwargs)

        # Add dynamic boolean attributes as checkboxes
        # In a real implementation, these would come from a configuration or database
        boolean_attributes = [
            ("same_organization_ok", "Okay with mentor from same organization"),
            ("remote_ok", "Okay with remote mentoring"),
            ("industry_experience_required", "Prefer mentor with industry experience"),
        ]

        for attr_key, attr_label in boolean_attributes:
            self.fields[f"desired_attr_{attr_key}"] = forms.BooleanField(
                label=attr_label,
                required=False,
                widget=forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                        "data-testid": f"desired-attr-{attr_key}",
                    }
                ),
            )
