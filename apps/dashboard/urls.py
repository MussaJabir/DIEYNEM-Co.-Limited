from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    # Services
    path("services/", views.ServiceListView.as_view(), name="service_list"),
    path("services/new/", views.ServiceCreateView.as_view(), name="service_create"),
    path("services/<int:pk>/edit/", views.ServiceUpdateView.as_view(), name="service_update"),
    path("services/<int:pk>/delete/", views.ServiceDeleteView.as_view(), name="service_delete"),
    # Projects
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/new/", views.ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project_update"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project_delete"),
    # Certificates (Administrator only)
    path("certificates/", views.CertificateListView.as_view(), name="certificate_list"),
    path("certificates/new/", views.CertificateCreateView.as_view(), name="certificate_create"),
    path(
        "certificates/<int:pk>/edit/",
        views.CertificateUpdateView.as_view(),
        name="certificate_update",
    ),
    path(
        "certificates/<int:pk>/delete/",
        views.CertificateDeleteView.as_view(),
        name="certificate_delete",
    ),
]
