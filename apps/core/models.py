from django.db import models


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
