"""Bump the public cache version whenever displayed content changes.

Connected for every model that feeds a cached public fragment, so an Editor
saving in the dashboard immediately invalidates the relevant fragments.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.cache import bump_cache_version
from apps.core.models import Client, SiteSetting, Statistic, TeamMember
from apps.credentials.models import Certificate
from apps.media_center.models import Download, GalleryImage
from apps.projects.models import Project, ProjectImage
from apps.services.models import Service

# Models whose changes should refresh public pages.
CACHED_CONTENT_MODELS = (
    Service,
    Project,
    ProjectImage,
    Certificate,
    SiteSetting,
    Statistic,
    Client,
    TeamMember,
    GalleryImage,
    Download,
)


@receiver(post_save)
@receiver(post_delete)
def invalidate_public_cache(sender, **kwargs):
    if sender in CACHED_CONTENT_MODELS:
        bump_cache_version()
