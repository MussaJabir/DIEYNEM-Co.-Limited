from django import forms

from .models import Inquiry

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-amber-400"
)


class QuotationForm(forms.ModelForm):
    # Honeypot: real users never see or fill this; bots usually do.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
        label="Leave this field empty",
    )

    class Meta:
        model = Inquiry
        fields = [
            "name",
            "company",
            "email",
            "phone",
            "service_interest",
            "project_type",
            "message",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_interest"].required = False
        self.fields["service_interest"].empty_label = "— Select a service —"
        for name, field in self.fields.items():
            if name == "website":
                continue
            field.widget.attrs.setdefault("class", INPUT_CLASS)
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Your submission could not be processed.")
        return cleaned
