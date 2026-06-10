from .models import SiteSetting


def user_roles(request):
    """Expose role flags to templates (used by the dashboard shell)."""
    user = getattr(request, "user", None)
    is_administrator = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="Administrator").exists())
    )
    return {"is_administrator": is_administrator}


def site_settings(request):
    """Expose the singleton SiteSetting to all templates as ``site``."""
    return {"site": SiteSetting.load()}


def dashboard_badges(request):
    """Sidebar badge counts for the dashboard shell.

    Scoped to authenticated users on ``/dashboard/`` URLs so the public site
    never runs these queries. Certificate attention is administrator-only.
    """
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and request.path.startswith("/dashboard/")):
        return {}

    # Local imports keep ``core`` free of import-time coupling to other apps.
    from apps.credentials.models import Certificate
    from apps.leads.models import Inquiry

    data = {
        "new_inquiries_count": Inquiry.objects.filter(status=Inquiry.Status.NEW).count(),
    }
    is_administrator = user.is_superuser or user.groups.filter(name="Administrator").exists()
    if is_administrator:
        data["certs_attention_count"] = Certificate.objects.needs_attention().count()
    return data
