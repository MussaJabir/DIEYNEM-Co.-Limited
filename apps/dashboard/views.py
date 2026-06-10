from datetime import timedelta

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.models import SiteSetting
from apps.credentials.models import EXPIRY_WARNING_DAYS, Certificate
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


class FilterableListMixin:
    """Adds search, per-view filtering, pagination and HTMX partial rendering.

    Combine with an access mixin and ``ListView``. Set ``search_fields`` for
    a case-insensitive ``q`` search, override ``apply_filters`` for dropdown
    filters, and set ``partial_template_name`` so HTMX requests get only the
    results fragment (the page swaps it into ``#results``).
    """

    paginate_by = 12
    search_fields: list[str] = []
    partial_template_name: str | None = None

    def get_search_query(self):
        return self.request.GET.get("q", "").strip()

    def get_queryset(self):
        queryset = super().get_queryset()
        term = self.get_search_query()
        if term and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__icontains": term})
            queryset = queryset.filter(condition)
        return self.apply_filters(queryset)

    def apply_filters(self, queryset):
        return queryset

    def get_template_names(self):
        if self.partial_template_name and self.request.headers.get("HX-Request"):
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.get_search_query()
        # Querystring (minus page) so pagination links keep active filters.
        params = self.request.GET.copy()
        params.pop("page", None)
        context["querystring"] = params.urlencode()
        return context


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


class ServiceListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Service
    template_name = "dashboard/services/list.html"
    partial_template_name = "dashboard/services/_table.html"
    context_object_name = "services"
    search_fields = ["name", "short_description"]

    def apply_filters(self, queryset):
        published = self.request.GET.get("published")
        if published == "published":
            queryset = queryset.filter(is_published=True)
        elif published == "draft":
            queryset = queryset.filter(is_published=False)
        if self.request.GET.get("featured") == "1":
            queryset = queryset.filter(is_featured=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_published"] = self.request.GET.get("published", "")
        context["active_featured"] = self.request.GET.get("featured", "")
        return context


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


class ProjectListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Project
    template_name = "dashboard/projects/list.html"
    partial_template_name = "dashboard/projects/_table.html"
    context_object_name = "projects"
    search_fields = ["title", "location", "client_name"]

    def apply_filters(self, queryset):
        status = self.request.GET.get("status")
        if status in Project.Status.values:
            queryset = queryset.filter(status=status)
        sector = self.request.GET.get("sector")
        if sector in Project.Sector.values:
            queryset = queryset.filter(sector=sector)
        published = self.request.GET.get("published")
        if published == "published":
            queryset = queryset.filter(is_published=True)
        elif published == "draft":
            queryset = queryset.filter(is_published=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Project.Status.choices
        context["sectors"] = Project.Sector.choices
        context["active_status"] = self.request.GET.get("status", "")
        context["active_sector"] = self.request.GET.get("sector", "")
        context["active_published"] = self.request.GET.get("published", "")
        return context


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


class CertificateListView(FilterableListMixin, AdministratorRequiredMixin, ListView):
    model = Certificate
    template_name = "dashboard/certificates/list.html"
    partial_template_name = "dashboard/certificates/_table.html"
    context_object_name = "certificates"
    search_fields = ["name", "issuer", "number"]

    def apply_filters(self, queryset):
        category = self.request.GET.get("category")
        if category in Certificate.Category.values:
            queryset = queryset.filter(category=category)
        validity = self.request.GET.get("validity")
        today = timezone.localdate()
        horizon = today + timedelta(days=EXPIRY_WARNING_DAYS)
        if validity == "expired":
            queryset = queryset.filter(valid_to__isnull=False, valid_to__lt=today)
        elif validity == "expiring":
            queryset = queryset.filter(
                valid_to__isnull=False, valid_to__gte=today, valid_to__lte=horizon
            )
        elif validity == "current":
            queryset = queryset.filter(Q(valid_to__isnull=True) | Q(valid_to__gt=horizon))
        published = self.request.GET.get("published")
        if published == "published":
            queryset = queryset.filter(is_published=True)
        elif published == "draft":
            queryset = queryset.filter(is_published=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attention"] = Certificate.objects.needs_attention()
        context["categories"] = Certificate.Category.choices
        context["active_category"] = self.request.GET.get("category", "")
        context["active_validity"] = self.request.GET.get("validity", "")
        context["active_published"] = self.request.GET.get("published", "")
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


class InquiryListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Inquiry
    template_name = "dashboard/inquiries/list.html"
    partial_template_name = "dashboard/inquiries/_table.html"
    context_object_name = "inquiries"
    search_fields = ["name", "email", "company"]

    def apply_filters(self, queryset):
        queryset = queryset.select_related("service_interest")
        status = self.request.GET.get("status")
        if status in Inquiry.Status.values:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_status"] = self.request.GET.get("status", "")
        context["statuses"] = Inquiry.Status.choices
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
