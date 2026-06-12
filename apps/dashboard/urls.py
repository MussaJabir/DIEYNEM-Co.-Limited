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
    # Inquiries / leads
    path("inquiries/", views.InquiryListView.as_view(), name="inquiry_list"),
    path("inquiries/<int:pk>/", views.InquiryUpdateView.as_view(), name="inquiry_detail"),
    path("inquiries/<int:pk>/delete/", views.InquiryDeleteView.as_view(), name="inquiry_delete"),
    # Statistics
    path("statistics/", views.StatisticListView.as_view(), name="statistic_list"),
    path("statistics/new/", views.StatisticCreateView.as_view(), name="statistic_create"),
    path("statistics/<int:pk>/edit/", views.StatisticUpdateView.as_view(), name="statistic_update"),
    path(
        "statistics/<int:pk>/delete/",
        views.StatisticDeleteView.as_view(),
        name="statistic_delete",
    ),
    # Clients / partners
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/new/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client_delete"),
    # Team members
    path("team/", views.TeamMemberListView.as_view(), name="team_list"),
    path("team/new/", views.TeamMemberCreateView.as_view(), name="team_create"),
    path("team/<int:pk>/edit/", views.TeamMemberUpdateView.as_view(), name="team_update"),
    path("team/<int:pk>/delete/", views.TeamMemberDeleteView.as_view(), name="team_delete"),
]
