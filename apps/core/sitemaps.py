from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.projects.models import Project
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    """Hand-listed static public pages."""

    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "about",
            "services:list",
            "projects:list",
            "ongoing_projects",
            "media_center:gallery",
            "media_center:downloads",
            "credentials:list",
            "leads:quote",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "home" else 0.6


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Project.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
}
