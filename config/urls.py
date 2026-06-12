"""URL configuration for the DIEYNEM project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

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
    path("dashboard/", include("apps.dashboard.urls")),
    path("services/", include("apps.services.urls")),
    # Top-level destination (a headline nav page), so it sits outside the
    # /projects/ include rather than nesting under it.
    path("ongoing-projects/", OngoingProjectListView.as_view(), name="ongoing_projects"),
    path("projects/", include("apps.projects.urls")),
    path("certifications/", include("apps.credentials.urls")),
    path("request-quotation/", include("apps.leads.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
