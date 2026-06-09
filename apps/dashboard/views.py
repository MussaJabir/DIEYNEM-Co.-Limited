from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from apps.core.models import SiteSetting

from .forms import SiteSettingForm
from .mixins import AdministratorRequiredMixin, DashboardAccessMixin


class OverviewView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/overview.html"


class SettingsView(AdministratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SiteSetting
    form_class = SiteSettingForm
    template_name = "dashboard/settings.html"
    success_url = reverse_lazy("dashboard:settings")
    success_message = "Site settings saved."

    def get_object(self, queryset=None):
        return SiteSetting.load()
