from django import forms
from django.forms import inlineformset_factory

from apps.core.models import SiteSetting
from apps.credentials.models import Certificate
from apps.projects.models import Project, ProjectImage
from apps.services.models import Service

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-amber-400"
)
CHECKBOX_CLASS = "h-4 w-4 rounded border-slate-300 text-navy-600 focus:ring-amber-400"
FILE_CLASS = "block w-full text-sm text-slate-600"


class StyledModelForm(forms.ModelForm):
    """ModelForm that applies the dashboard's Tailwind styling to all widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", CHECKBOX_CLASS)
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault("class", FILE_CLASS)
            else:
                widget.attrs.setdefault("class", INPUT_CLASS)
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)


class SiteSettingForm(StyledModelForm):
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


class ServiceForm(StyledModelForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "short_description",
            "full_description",
            "capabilities",
            "icon",
            "hero_image",
            "order",
            "is_featured",
            "is_published",
            "meta_title",
            "meta_description",
        ]


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "status",
            "client_name",
            "main_contractor",
            "consultant",
            "location",
            "country",
            "sector",
            "role",
            "year_start",
            "year_end",
            "completion_date",
            "overview",
            "scope_of_work",
            "technical_highlights",
            "outcome",
            "contract_value",
            "contract_value_visible",
            "related_services",
            "hero_image",
            "is_featured",
            "is_published",
            "order",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "completion_date": forms.DateInput(attrs={"type": "date"}),
        }


class ProjectImageForm(StyledModelForm):
    class Meta:
        model = ProjectImage
        fields = ["image", "caption", "date_taken", "show_in_gallery", "order"]
        widgets = {"date_taken": forms.DateInput(attrs={"type": "date"})}


ProjectImageFormSet = inlineformset_factory(
    Project,
    ProjectImage,
    form=ProjectImageForm,
    extra=2,
    can_delete=True,
)


class CertificateForm(StyledModelForm):
    class Meta:
        model = Certificate
        fields = [
            "name",
            "category",
            "issuer",
            "number",
            "description",
            "issue_date",
            "valid_to",
            "file",
            "display_image",
            "downloadable",
            "related_project",
            "is_published",
            "order",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "valid_to": forms.DateInput(attrs={"type": "date"}),
        }
