from django import forms
from django.db.models import ImageField
from django.forms import inlineformset_factory

from apps.core.models import SiteSetting
from apps.credentials.models import Certificate
from apps.leads.models import Inquiry
from apps.projects.models import Project, ProjectImage, ProjectMilestone, ProjectUpdate
from apps.services.models import Service

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-amber-400"
)
CHECKBOX_CLASS = "h-4 w-4 rounded border-slate-300 text-navy-600 focus:ring-amber-400"
FILE_CLASS = (
    "block w-full text-sm text-slate-600 cursor-pointer "
    "file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 "
    "file:text-sm file:font-semibold file:bg-navy-50 file:text-navy-700 "
    "hover:file:bg-navy-100 file:cursor-pointer"
)


class StyledModelForm(forms.ModelForm):
    """ModelForm that applies the dashboard's Tailwind styling to all widgets.

    Subclasses may declare ``fieldsets`` to render the form as grouped,
    two-column sections (see :meth:`iter_fieldsets`)::

        fieldsets = [
            ("Legend", {"fields": [...], "wide": [...], "description": "..."}),
        ]
    """

    fieldsets: list = []

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

        # Image-field names so templates can render a thumbnail + live preview
        # instead of a bare file input. (A plain FileField, e.g. a PDF scan,
        # is intentionally excluded and keeps the default download widget.)
        model_meta = self._meta.model._meta
        self.image_fields = set()
        for name in self.fields:
            try:
                model_field = model_meta.get_field(name)
            except Exception:
                continue
            if isinstance(model_field, ImageField):
                self.image_fields.add(name)

    def iter_fieldsets(self):
        """Yield section dicts for the template's grouped two-column layout.

        Each section is ``{"legend", "description", "fields": [{"field",
        "wide"}]}``. Without a ``fieldsets`` declaration the whole form is
        returned as one unlabelled section. Any field omitted from
        ``fieldsets`` is appended in a final "Other" section so a forgotten
        name can never silently drop an input.
        """
        if not self.fieldsets:
            yield {
                "legend": None,
                "description": None,
                "has_errors": False,
                "fields": [{"field": self[name], "wide": False} for name in self.fields],
            }
            return

        seen = set()
        for legend, opts in self.fieldsets:
            wide = set(opts.get("wide", []))
            names = opts.get("fields", [])
            seen.update(names)
            yield {
                "legend": legend,
                "description": opts.get("description"),
                "has_errors": any(self[name].errors for name in names),
                "fields": [{"field": self[name], "wide": name in wide} for name in names],
            }

        leftovers = [name for name in self.fields if name not in seen]
        if leftovers:
            yield {
                "legend": "Other",
                "description": None,
                "has_errors": any(self[name].errors for name in leftovers),
                "fields": [{"field": self[name], "wide": False} for name in leftovers],
            }


class SiteSettingForm(StyledModelForm):
    fieldsets = [
        (
            "Company identity",
            {
                "fields": ["company_name", "motto", "logo", "default_og_image"],
                "wide": ["default_og_image"],
                "description": "Shown across the public site and in the footer.",
            },
        ),
        (
            "Contact details",
            {
                "fields": ["po_box", "physical_address", "phones", "emails", "map_embed"],
                "wide": ["physical_address", "map_embed"],
            },
        ),
        (
            "Social & footer",
            {
                "fields": ["facebook_url", "instagram_url", "linkedin_url", "footer_text"],
                "wide": ["footer_text"],
            },
        ),
    ]

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
    fieldsets = [
        (
            "Service",
            {
                "fields": ["name", "short_description", "full_description", "capabilities"],
                "wide": ["short_description", "full_description", "capabilities"],
            },
        ),
        ("Media", {"fields": ["icon", "hero_image"]}),
        ("Publishing", {"fields": ["order", "is_featured", "is_published"]}),
        (
            "Search engine (SEO)",
            {"fields": ["meta_title", "meta_description"], "wide": ["meta_description"]},
        ),
    ]

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
    fieldsets = [
        (
            "Basics",
            {"fields": ["title", "status", "sector", "role", "location", "country"]},
        ),
        ("Parties", {"fields": ["client_name", "main_contractor", "consultant"]}),
        ("Timeline", {"fields": ["year_start", "year_end", "completion_date"]}),
        (
            "Ongoing progress",
            {
                "fields": ["progress_percent", "last_updated_label"],
                "description": "Ongoing projects only — drives the public progress bar and "
                '"last updated" label. Manage milestones and updates in the sections below.',
            },
        ),
        (
            "Story",
            {
                "fields": ["overview", "scope_of_work", "technical_highlights", "outcome"],
                "wide": ["overview", "scope_of_work", "technical_highlights", "outcome"],
                "description": "Narrative shown on the public case-study page.",
            },
        ),
        ("Commercial", {"fields": ["contract_value", "contract_value_visible"]}),
        (
            "Media & related services",
            {"fields": ["hero_image", "related_services"], "wide": ["related_services"]},
        ),
        ("Publishing", {"fields": ["is_featured", "is_published", "order"]}),
        (
            "Search engine (SEO)",
            {"fields": ["meta_title", "meta_description"], "wide": ["meta_description"]},
        ),
    ]

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
            "progress_percent",
            "last_updated_label",
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
            "last_updated_label": forms.DateInput(attrs={"type": "date"}),
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
    extra=0,  # rows are added on demand from the dashboard
    can_delete=True,
)


class ProjectMilestoneForm(StyledModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ["title", "is_complete", "date", "order"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


ProjectMilestoneFormSet = inlineformset_factory(
    Project,
    ProjectMilestone,
    form=ProjectMilestoneForm,
    extra=0,  # rows are added on demand from the dashboard
    can_delete=True,
)


class ProjectUpdateForm(StyledModelForm):
    class Meta:
        model = ProjectUpdate
        fields = ["date", "note", "image"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


ProjectUpdateFormSet = inlineformset_factory(
    Project,
    ProjectUpdate,
    form=ProjectUpdateForm,
    extra=0,  # rows are added on demand from the dashboard
    can_delete=True,
)


class CertificateForm(StyledModelForm):
    fieldsets = [
        (
            "Certificate",
            {
                "fields": ["name", "category", "issuer", "number", "description"],
                "wide": ["description"],
            },
        ),
        ("Validity", {"fields": ["issue_date", "valid_to"]}),
        (
            "Files",
            {
                "fields": ["file", "display_image", "downloadable"],
                "description": "Upload the scan as the downloadable file; the display image is the clean card shown publicly.",
            },
        ),
        ("Publishing", {"fields": ["related_project", "is_published", "order"]}),
    ]

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


class InquiryStatusForm(StyledModelForm):
    class Meta:
        model = Inquiry
        fields = ["status", "internal_notes"]
