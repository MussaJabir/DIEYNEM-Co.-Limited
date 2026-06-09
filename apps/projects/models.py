from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import SEOModel, TimeStampedModel


class ProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)

    def completed(self):
        return self.published().filter(status=Project.Status.COMPLETED)

    def ongoing(self):
        return self.published().filter(status=Project.Status.ONGOING)


class Project(TimeStampedModel, SEOModel):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        ONGOING = "ongoing", "Ongoing"

    class Role(models.TextChoices):
        PRIME = "prime", "Prime Contractor"
        SUB = "sub", "Sub-Contractor"
        JV = "jv", "Joint Venture Partner"
        NOMINATED = "nominated", "Nominated Sub-Contractor"

    class Sector(models.TextChoices):
        AVIATION = "aviation", "Aviation"
        GOVERNMENT = "government", "Government"
        EDUCATION = "education", "Education"
        HOUSING = "housing", "Housing"
        INSTITUTIONAL = "institutional", "Institutional"
        COMMERCIAL = "commercial", "Commercial"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)

    client_name = models.CharField("Client / employer", max_length=255, blank=True)
    main_contractor = models.CharField(max_length=255, blank=True)
    consultant = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, default="Tanzania")
    sector = models.CharField(max_length=20, choices=Sector.choices, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, blank=True)

    year_start = models.PositiveIntegerField(null=True, blank=True)
    year_end = models.PositiveIntegerField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    overview = models.TextField(blank=True)
    scope_of_work = models.TextField(blank=True, help_text="One item per line.")
    technical_highlights = models.TextField(blank=True, help_text="One item per line.")
    outcome = models.TextField(blank=True)

    contract_value = models.CharField(
        max_length=160,
        blank=True,
        help_text="As documented, e.g. 'TZS 1,739,536,075'.",
    )
    contract_value_visible = models.BooleanField(default=True)

    related_services = models.ManyToManyField(
        "services.Service", blank=True, related_name="projects"
    )

    hero_image = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage.")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-year_end", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:250] or "project"
            slug = base
            counter = 2
            while Project.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("projects:detail", kwargs={"slug": self.slug})

    @property
    def scope_list(self) -> list[str]:
        return [s.strip() for s in self.scope_of_work.splitlines() if s.strip()]

    @property
    def highlight_list(self) -> list[str]:
        return [h.strip() for h in self.technical_highlights.splitlines() if h.strip()]

    @property
    def year_display(self) -> str:
        if self.year_start and self.year_end and self.year_start != self.year_end:
            return f"{self.year_start}–{self.year_end}"
        return str(self.year_end or self.year_start or "")

    @property
    def show_value(self) -> bool:
        return self.contract_value_visible and bool(self.contract_value)


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=300, blank=True)
    date_taken = models.DateField(null=True, blank=True)
    show_in_gallery = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.caption or f"Image {self.pk}"
