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
from apps.credentials.models import Certificate
from apps.leads.models import Inquiry
from apps.projects.models import Project
from apps.services.models import Service

from .forms import (
    CertificateForm,
    InquiryStatusForm,
    ProjectForm,
    ProjectImageFormSet,
    ServiceForm,
    SiteSettingForm,
)
from .mixins import AdministratorRequiredMixin, DashboardAccessMixin


class OverviewView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects_count"] = Project.objects.count()
        context["ongoing_count"] = Project.objects.ongoing().count()
        context["services_count"] = Service.objects.count()
        attention = Certificate.objects.needs_attention()
        context["certs_attention"] = attention
        context["certs_attention_count"] = attention.count()
        context["new_inquiries_count"] = Inquiry.objects.filter(status=Inquiry.Status.NEW).count()
        return context


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


# --- Projects CRUD (Editor + Administrator) ---


class ProjectListView(DashboardAccessMixin, ListView):
    model = Project
    template_name = "dashboard/projects/list.html"
    context_object_name = "projects"


class ProjectImageFormSetMixin:
    """Adds the ProjectImage inline formset to create/update views."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context["image_formset"] = ProjectImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix="images"
            )
        else:
            context["image_formset"] = ProjectImageFormSet(instance=self.object, prefix="images")
        return context

    def form_valid(self, form):
        formset = ProjectImageFormSet(
            self.request.POST, self.request.FILES, instance=self.object, prefix="images"
        )
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        response = super().form_valid(form)
        formset.instance = self.object
        formset.save()
        return response


class ProjectCreateView(
    DashboardAccessMixin, ProjectImageFormSetMixin, SuccessMessageMixin, CreateView
):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/projects/form.html"
    success_url = reverse_lazy("dashboard:project_list")
    success_message = "Project created."
    object = None


class ProjectUpdateView(
    DashboardAccessMixin, ProjectImageFormSetMixin, SuccessMessageMixin, UpdateView
):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/projects/form.html"
    success_url = reverse_lazy("dashboard:project_list")
    success_message = "Project updated."


class ProjectDeleteView(DashboardAccessMixin, DeleteView):
    model = Project
    template_name = "dashboard/projects/confirm_delete.html"
    success_url = reverse_lazy("dashboard:project_list")


# --- Certificates CRUD (Administrator only) ---


class CertificateListView(AdministratorRequiredMixin, ListView):
    model = Certificate
    template_name = "dashboard/certificates/list.html"
    context_object_name = "certificates"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attention"] = Certificate.objects.needs_attention()
        return context


class CertificateCreateView(AdministratorRequiredMixin, SuccessMessageMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = "dashboard/certificates/form.html"
    success_url = reverse_lazy("dashboard:certificate_list")
    success_message = "Certificate created."


class CertificateUpdateView(AdministratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Certificate
    form_class = CertificateForm
    template_name = "dashboard/certificates/form.html"
    success_url = reverse_lazy("dashboard:certificate_list")
    success_message = "Certificate updated."


class CertificateDeleteView(AdministratorRequiredMixin, DeleteView):
    model = Certificate
    template_name = "dashboard/certificates/confirm_delete.html"
    success_url = reverse_lazy("dashboard:certificate_list")


# --- Inquiries / leads (Editor + Administrator) ---


class InquiryListView(DashboardAccessMixin, ListView):
    model = Inquiry
    template_name = "dashboard/inquiries/list.html"
    context_object_name = "inquiries"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("service_interest")
        status = self.request.GET.get("status")
        if status in Inquiry.Status.values:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_status"] = self.request.GET.get("status", "")
        context["statuses"] = Inquiry.Status.choices
        context["new_count"] = Inquiry.objects.filter(status=Inquiry.Status.NEW).count()
        return context


class InquiryUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = Inquiry
    form_class = InquiryStatusForm
    template_name = "dashboard/inquiries/detail.html"
    success_url = reverse_lazy("dashboard:inquiry_list")
    success_message = "Inquiry updated."


class InquiryDeleteView(DashboardAccessMixin, DeleteView):
    model = Inquiry
    template_name = "dashboard/inquiries/confirm_delete.html"
    success_url = reverse_lazy("dashboard:inquiry_list")
