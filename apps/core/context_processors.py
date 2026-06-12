import json

from django.utils.safestring import mark_safe

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


def structured_data(request):
    """Organization JSON-LD for the public site, exposed as ``organization_jsonld``.

    Skipped on dashboard/admin pages (not indexed). The JSON is escaped so it
    is safe to drop straight into a ``<script type="application/ld+json">``.
    """
    path = request.path
    if path.startswith("/dashboard/") or path.startswith("/admin/"):
        return {}

    site = SiteSetting.load()
    base = f"{request.scheme}://{request.get_host()}"
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site.company_name,
        "url": base + "/",
    }
    if site.logo:
        data["logo"] = base + site.logo.url
    if site.default_og_image:
        data["image"] = base + site.default_og_image.url
    if site.motto:
        data["slogan"] = site.motto
    if site.physical_address:
        data["address"] = {
            "@type": "PostalAddress",
            "streetAddress": site.physical_address,
            "addressCountry": "TZ",
        }
    if site.email_list:
        data["email"] = site.email_list[0]
    if site.phone_list:
        data["contactPoint"] = [
            {"@type": "ContactPoint", "telephone": phone, "contactType": "sales"}
            for phone in site.phone_list
        ]
    same_as = [url for _, url in site.social_links]
    if same_as:
        data["sameAs"] = same_as

    # Escape "<" so the payload can never break out of the <script> element.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return {"organization_jsonld": mark_safe(payload)}


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
