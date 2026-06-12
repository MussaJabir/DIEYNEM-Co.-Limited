from pathlib import Path

from django.db import models

from apps.core.models import TimeStampedModel


class GalleryImageQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class GalleryImage(TimeStampedModel):
    """A standalone image for the global gallery.

    The public gallery is the union of these (active) and any ``ProjectImage``
    flagged ``show_in_gallery`` — see BS §268.
    """

    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=300, blank=True)
    category = models.CharField(
        max_length=80, blank=True, help_text='Optional grouping, e.g. "Solar" or "Switchgear".'
    )
    related_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_images",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    objects = GalleryImageQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self) -> str:
        return self.title or self.caption or f"Gallery image {self.pk}"


class DownloadQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_public=True)


class Download(TimeStampedModel):
    """A downloadable document — company profile, capability statement, brochure."""

    class Category(models.TextChoices):
        COMPANY_PROFILE = "company_profile", "Company Profile"
        CAPABILITY_STATEMENT = "capability_statement", "Capability Statement"
        BROCHURE = "brochure", "Brochure"

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300, blank=True)
    file = models.FileField(upload_to="downloads/")
    category = models.CharField(
        max_length=30, choices=Category.choices, default=Category.COMPANY_PROFILE
    )
    order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    objects = DownloadQuerySet.as_manager()

    class Meta:
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title

    @property
    def extension(self) -> str:
        """Upper-case file extension without the dot, e.g. ``PDF`` (``FILE`` if none)."""
        if not self.file:
            return ""
        suffix = Path(self.file.name).suffix.lstrip(".").upper()
        return suffix or "FILE"

    @property
    def size_display(self) -> str:
        """Human-readable file size, e.g. ``2.4 MB`` (empty if unavailable)."""
        if not self.file:
            return ""
        try:
            size = self.file.size
        except (OSError, ValueError):
            return ""
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return ""
