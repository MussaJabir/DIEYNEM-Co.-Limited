from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.models import SiteSetting
from apps.services.models import Service

from .forms import ServiceForm, SiteSettingForm
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


# --- Services CRUD (Editor + Administrator) ---


class ServiceListView(DashboardAccessMixin, ListView):
    model = Service
    template_name = "dashboard/services/list.html"
    context_object_name = "services"


class ServiceCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "dashboard/services/form.html"
    success_url = reverse_lazy("dashboard:service_list")
    success_message = "Service created."


class ServiceUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "dashboard/services/form.html"
    success_url = reverse_lazy("dashboard:service_list")
    success_message = "Service updated."


class ServiceDeleteView(DashboardAccessMixin, DeleteView):
    model = Service
    template_name = "dashboard/services/confirm_delete.html"
    success_url = reverse_lazy("dashboard:service_list")
