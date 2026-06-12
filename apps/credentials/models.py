from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel

EXPIRY_WARNING_DAYS = 60


class CertificateQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def public(self):
        """Published certificates that are not expired (safe to show publicly)."""
        today = timezone.localdate()
        return self.published().filter(
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=today)
        )

    def expiring_soon(self):
        today = timezone.localdate()
        return self.published().filter(
            valid_to__isnull=False,
            valid_to__gte=today,
            valid_to__lte=today + timedelta(days=EXPIRY_WARNING_DAYS),
        )

    def expired(self):
        return self.published().filter(valid_to__isnull=False, valid_to__lt=timezone.localdate())

    def needs_attention(self):
        """Published certificates that are expired or expiring soon."""
        today = timezone.localdate()
        return self.published().filter(
            valid_to__isnull=False,
            valid_to__lte=today + timedelta(days=EXPIRY_WARNING_DAYS),
        )


class Certificate(TimeStampedModel):
    class Category(models.TextChoices):
        REGISTRATION = "registration", "Company Registration"
        TAX = "tax", "Tax & Financial Compliance"
        LICENSE = "license", "Trading License"
        ACCREDITATION = "accreditation", "Industry Accreditation"
        SAFETY = "safety", "Health, Safety & Welfare"
        COMPLETION = "completion", "Project Completion"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    issuer = models.CharField(max_length=200, blank=True)
    number = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=255, blank=True)

    issue_date = models.DateField(null=True, blank=True)
    valid_to = models.DateField(
        null=True, blank=True, help_text="Leave blank if it does not expire."
    )

    file = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True,
        help_text="The certificate scan/PDF (offered as download-on-demand).",
    )
    display_image = models.ImageField(upload_to="certificates/thumbs/", blank=True, null=True)
    downloadable = models.BooleanField(default=True)

    related_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificates",
    )

    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    objects = CertificateQuerySet.as_manager()

    class Meta:
        ordering = ["category", "order", "name"]

    def __str__(self) -> str:
        return self.name

    @property
    def status(self) -> str:
        if self.valid_to is None:
            return "current"
        today = timezone.localdate()
        if self.valid_to < today:
            return "expired"
        if self.valid_to <= today + timedelta(days=EXPIRY_WARNING_DAYS):
            return "expiring"
        return "current"

    @property
    def is_expired(self) -> bool:
        return self.status == "expired"

    @property
    def days_until_expiry(self) -> int | None:
        """Whole days until ``valid_to`` (negative if already expired).

        ``None`` when the certificate has no expiry date. Powers the
        dashboard expiry warnings ("expires in 12 days" / "expired 3 days ago").
        """
        if self.valid_to is None:
            return None
        return (self.valid_to - timezone.localdate()).days

    @property
    def can_download(self) -> bool:
        return self.downloadable and bool(self.file)
