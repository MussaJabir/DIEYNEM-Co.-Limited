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
