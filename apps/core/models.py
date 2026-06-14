from django.db import models
from simple_history.models import HistoricalRecords


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SEOModel(models.Model):
    """Abstract base adding per-record SEO / social-share overrides."""

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True


class SiteSetting(models.Model):
    """Singleton holding company-wide settings shown across the site.

    Always stored as a single row (pk=1); edit it via the dashboard.
    """

    company_name = models.CharField(max_length=200, default="DIEYNEM Co. Limited")
    motto = models.CharField(max_length=200, default="Quality is our Motto")

    po_box = models.CharField("P.O. Box", max_length=150, blank=True)
    physical_address = models.TextField(blank=True)

    phones = models.TextField(blank=True, help_text="One phone number per line.")
    emails = models.TextField(blank=True, help_text="One email address per line.")

    map_embed = models.TextField(
        blank=True, help_text="Google Maps embed URL (the src of the iframe)."
    )

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    footer_text = models.TextField(blank=True)

    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    default_og_image = models.ImageField(
        upload_to="branding/",
        blank=True,
        null=True,
        help_text="Default image used when pages are shared on social media.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return self.company_name

    def save(self, *args, **kwargs):
        # Enforce the singleton: there is only ever one row.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSetting":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phone_list(self) -> list[str]:
        return [p.strip() for p in self.phones.splitlines() if p.strip()]

    @property
    def email_list(self) -> list[str]:
        return [e.strip() for e in self.emails.splitlines() if e.strip()]

    @property
    def social_links(self) -> list[tuple[str, str]]:
        pairs = [
            ("Facebook", self.facebook_url),
            ("Instagram", self.instagram_url),
            ("LinkedIn", self.linkedin_url),
        ]
        return [(name, url) for name, url in pairs if url]


class Statistic(TimeStampedModel):
    """An editable counter for the homepage numbers band (BS §6).

    Kept editable so figures stay honest as the portfolio grows — e.g.
    "120 km of line", "45+ transformers", "6 countries".
    """

    label = models.CharField(max_length=80)
    value = models.PositiveIntegerField()
    prefix = models.CharField(max_length=10, blank=True, help_text='e.g. "TZS " or "~".')
    suffix = models.CharField(max_length=10, blank=True, help_text='e.g. "+", " km" or "%".')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.label}: {self.prefix}{self.value}{self.suffix}"


class Client(TimeStampedModel):
    """A client, partner or main contractor shown in the homepage logo band."""

    class Type(models.TextChoices):
        CLIENT = "client", "Client"
        PARTNER = "partner", "Partner"
        MAIN_CONTRACTOR = "main_contractor", "Main Contractor"

    name = models.CharField(max_length=160)
    logo = models.ImageField(upload_to="clients/", blank=True, null=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.CLIENT)
    website = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Highlight in the homepage band.")

    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class TeamMember(TimeStampedModel):
    """A leadership / engineering / support staff member shown on the About page."""

    class Group(models.TextChoices):
        LEADERSHIP = "leadership", "Leadership"
        ENGINEER = "engineer", "Engineering"
        SUPPORT = "support", "Support"

    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    qualification = models.CharField(
        max_length=60, blank=True, help_text='Honorific / qualification, e.g. "Eng." or "CPA".'
    )
    group = models.CharField(max_length=20, choices=Group.choices, default=Group.LEADERSHIP)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    @property
    def display_name(self) -> str:
        """Name prefixed with the qualification, e.g. ``Eng. Jane Doe``."""
        return f"{self.qualification} {self.name}".strip()
