from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import SEOModel, TimeStampedModel


class ServiceQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)


class Service(TimeStampedModel, SEOModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    full_description = models.TextField(blank=True)
    capabilities = models.TextField(blank=True, help_text="One capability per line.")
    icon = models.CharField(
        max_length=50, blank=True, help_text="Optional icon key (for future use)."
    )
    hero_image = models.ImageField(upload_to="services/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage.")
    is_published = models.BooleanField(default=True)

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200] or "service"
            slug = base
            counter = 2
            while Service.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("services:detail", kwargs={"slug": self.slug})

    @property
    def capability_list(self) -> list[str]:
        return [c.strip() for c in self.capabilities.splitlines() if c.strip()]
