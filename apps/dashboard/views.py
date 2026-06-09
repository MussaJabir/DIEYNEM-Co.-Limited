from django.views.generic import TemplateView

from .mixins import AdministratorRequiredMixin, DashboardAccessMixin


class OverviewView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/overview.html"


class SettingsView(AdministratorRequiredMixin, TemplateView):
    template_name = "dashboard/settings.html"
