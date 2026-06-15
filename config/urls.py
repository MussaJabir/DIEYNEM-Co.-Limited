"""URL configuration for the DIEYNEM project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import sitemaps
from apps.core.views import ManifestView, OfflineView, ServiceWorkerView, robots_txt
from apps.projects.views import OngoingProjectListView

urlpatterns = [
    # Django admin is kept for developer/superuser maintenance only.
    # The client-facing admin is the custom dashboard at /dashboard/.
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Language switcher endpoint (set_language).
    path("i18n/", include("django.conf.urls.i18n")),
    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    # PWA — root-scoped so the service worker controls the whole site.
    path("manifest.webmanifest", ManifestView.as_view(), name="manifest"),
    path("sw.js", ServiceWorkerView.as_view(), name="service_worker"),
    path("offline/", OfflineView.as_view(), name="offline"),
    path("dashboard/", include("apps.dashboard.urls")),
    path("services/", include("apps.services.urls")),
    # Top-level destination (a headline nav page), so it sits outside the
    # /projects/ include rather than nesting under it.
    path("ongoing-projects/", OngoingProjectListView.as_view(), name="ongoing_projects"),
    path("projects/", include("apps.projects.urls")),
    path("certifications/", include("apps.credentials.urls")),
    path("request-quotation/", include("apps.leads.urls")),
    path("", include("apps.media_center.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
