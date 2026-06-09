from django import forms

from apps.core.models import SiteSetting

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-amber-400"
)


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            "company_name",
            "motto",
            "po_box",
            "physical_address",
            "phones",
            "emails",
            "map_embed",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "footer_text",
            "logo",
            "default_og_image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault("class", "block w-full text-sm text-slate-600")
            else:
                widget.attrs.setdefault("class", INPUT_CLASS)
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)
