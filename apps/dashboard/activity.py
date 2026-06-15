"""Cross-model recent-activity feed, built from django-simple-history records.

Each tracked content model keeps its own ``historical_*`` table; this merges the
newest entries across them into one chronological feed for the dashboard
Overview, so staff can see who changed what and when (the audit trail).
"""

from apps.core.models import Client, SiteSetting, Statistic, TeamMember
from apps.credentials.models import Certificate
from apps.leads.models import Inquiry
from apps.media_center.models import Download, GalleryImage
from apps.projects.models import Project
from apps.services.models import Service

# (model, human label) for every history-tracked content model.
TRACKED_MODELS = [
    (Project, "Project"),
    (Service, "Service"),
    (Certificate, "Certificate"),
    (GalleryImage, "Gallery image"),
    (Download, "Download"),
    (Client, "Client"),
    (TeamMember, "Team member"),
    (Statistic, "Statistic"),
    (Inquiry, "Inquiry"),
    (SiteSetting, "Site settings"),
]


def recent_activity(limit=8):
    """Return the ``limit`` most recent changes across all tracked models.

    Each item is a dict: ``action`` (Created/Changed/Deleted), ``model`` label,
    ``name`` (object's str), ``user`` (or None for system changes) and ``when``.
    """
    records = []
    for model, label in TRACKED_MODELS:
        # Newest few per model; the global slice happens after the merge.
        for record in model.history.select_related("history_user")[:limit]:
            records.append(
                {
                    "action": record.get_history_type_display(),
                    "model": label,
                    "name": str(record.history_object),
                    "user": record.history_user,
                    "when": record.history_date,
                }
            )
    records.sort(key=lambda r: r["when"], reverse=True)
    return records[:limit]
