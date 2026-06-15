import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django_otp import login as otp_login
from django_otp import match_token, user_has_device
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.core.models import Client, SiteSetting, Statistic, TeamMember
from apps.credentials.models import EXPIRY_WARNING_DAYS, Certificate
from apps.leads.models import Inquiry
from apps.media_center.models import Download, GalleryImage
from apps.projects.models import Project
from apps.services.models import Service

from .activity import recent_activity
from .forms import (
    CertificateForm,
    ClientForm,
    DownloadForm,
    GalleryImageForm,
    InquiryStatusForm,
    ProjectForm,
    ProjectImageFormSet,
    ProjectMilestoneFormSet,
    ProjectUpdateFormSet,
    ServiceForm,
    SiteSettingForm,
    StatisticForm,
    TeamMemberForm,
)
from .mixins import AdministratorRequiredMixin, DashboardAccessMixin
from .two_factor import issue_backup_tokens, qr_svg


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
        # Most urgent first (furthest overdue, then soonest to expire).
        attention = list(Certificate.objects.needs_attention().order_by("valid_to"))
        context["certs_attention"] = attention
        context["certs_attention_count"] = len(attention)
        context["certs_expired_count"] = sum(1 for c in attention if c.is_expired)
        context["certs_expiring_count"] = sum(1 for c in attention if not c.is_expired)
        context["new_inquiries_count"] = Inquiry.objects.filter(status=Inquiry.Status.NEW).count()
        context["recent_activity"] = recent_activity()
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


class ProjectInlineFormsetsMixin:
    """Binds the Project inline formsets (images, milestones, updates) to a view.

    Each entry maps a context key to ``(FormSet, prefix)``. The prefix matches
    the management-form id the dashboard's add-row Alpine helper bumps.
    """

    inline_formsets = {
        "image_formset": (ProjectImageFormSet, "images"),
        "milestone_formset": (ProjectMilestoneFormSet, "milestones"),
        "update_formset": (ProjectUpdateFormSet, "updates"),
    }

    def _build_formset(self, formset_cls, prefix, *, bind):
        if bind:
            return formset_cls(
                self.request.POST, self.request.FILES, instance=self.object, prefix=prefix
            )
        return formset_cls(instance=self.object, prefix=prefix)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bind = self.request.method == "POST"
        for key, (formset_cls, prefix) in self.inline_formsets.items():
            # setdefault keeps any already-validated formset passed by form_valid.
            context.setdefault(key, self._build_formset(formset_cls, prefix, bind=bind))
        return context

    def form_valid(self, form):
        formsets = {
            key: self._build_formset(formset_cls, prefix, bind=True)
            for key, (formset_cls, prefix) in self.inline_formsets.items()
        }
        if not all(fs.is_valid() for fs in formsets.values()):
            return self.render_to_response(self.get_context_data(form=form, **formsets))
        response = super().form_valid(form)
        for fs in formsets.values():
            fs.instance = self.object
            fs.save()
        return response


class ProjectCreateView(
    DashboardAccessMixin, ProjectInlineFormsetsMixin, SuccessMessageMixin, CreateView
):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/projects/form.html"
    success_url = reverse_lazy("dashboard:project_list")
    success_message = "Project created."
    object = None


class ProjectUpdateView(
    DashboardAccessMixin, ProjectInlineFormsetsMixin, SuccessMessageMixin, UpdateView
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

INQUIRY_SEARCH_FIELDS = ["name", "email", "company"]


def filtered_inquiries(params):
    """Inquiries narrowed by the ``q`` search and ``status`` filter.

    Shared by the list view and the CSV export so both honour the same filters.
    """
    queryset = Inquiry.objects.select_related("service_interest")
    term = params.get("q", "").strip()
    if term:
        condition = Q()
        for field in INQUIRY_SEARCH_FIELDS:
            condition |= Q(**{f"{field}__icontains": term})
        queryset = queryset.filter(condition)
    status = params.get("status")
    if status in Inquiry.Status.values:
        queryset = queryset.filter(status=status)
    return queryset


class InquiryListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Inquiry
    template_name = "dashboard/inquiries/list.html"
    partial_template_name = "dashboard/inquiries/_table.html"
    context_object_name = "inquiries"
    search_fields = INQUIRY_SEARCH_FIELDS

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
        # Pipeline overview: a stable count per status across all inquiries.
        counts = dict(Inquiry.objects.values_list("status").annotate(n=Count("id")))
        context["pipeline"] = [
            {"value": value, "label": label, "count": counts.get(value, 0)}
            for value, label in Inquiry.Status.choices
        ]
        context["pipeline_total"] = sum(counts.values())
        return context


class InquiryExportView(DashboardAccessMixin, View):
    """Stream the (optionally filtered) inquiries as a CSV download."""

    def get(self, request, *args, **kwargs):
        queryset = filtered_inquiries(request.GET).order_by("-created_at")
        stamp = timezone.localdate().isoformat()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="dieynem-inquiries-{stamp}.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Received",
                "Name",
                "Company",
                "Email",
                "Phone",
                "Service interest",
                "Project type",
                "Status",
                "Source",
                "Message",
                "Internal notes",
                "Last updated",
            ]
        )
        for inquiry in queryset:
            writer.writerow(
                [
                    inquiry.created_at.strftime("%Y-%m-%d %H:%M"),
                    inquiry.name,
                    inquiry.company,
                    inquiry.email,
                    inquiry.phone,
                    inquiry.service_interest.name if inquiry.service_interest else "",
                    inquiry.project_type,
                    inquiry.get_status_display(),
                    inquiry.source,
                    inquiry.message,
                    inquiry.internal_notes,
                    inquiry.updated_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )
        return response


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


# --- Statistics (Editor + Administrator) ---


class StatisticListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Statistic
    template_name = "dashboard/statistics/list.html"
    partial_template_name = "dashboard/statistics/_table.html"
    context_object_name = "statistics"
    search_fields = ["label"]

    def apply_filters(self, queryset):
        active = self.request.GET.get("active")
        if active == "active":
            queryset = queryset.filter(is_active=True)
        elif active == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_active"] = self.request.GET.get("active", "")
        return context


class StatisticCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = Statistic
    form_class = StatisticForm
    template_name = "dashboard/statistics/form.html"
    success_url = reverse_lazy("dashboard:statistic_list")
    success_message = "Statistic created."


class StatisticUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = Statistic
    form_class = StatisticForm
    template_name = "dashboard/statistics/form.html"
    success_url = reverse_lazy("dashboard:statistic_list")
    success_message = "Statistic updated."


class StatisticDeleteView(DashboardAccessMixin, DeleteView):
    model = Statistic
    template_name = "dashboard/statistics/confirm_delete.html"
    success_url = reverse_lazy("dashboard:statistic_list")


# --- Clients / partners (Editor + Administrator) ---


class ClientListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Client
    template_name = "dashboard/clients/list.html"
    partial_template_name = "dashboard/clients/_table.html"
    context_object_name = "clients"
    search_fields = ["name"]

    def apply_filters(self, queryset):
        client_type = self.request.GET.get("type")
        if client_type in Client.Type.values:
            queryset = queryset.filter(type=client_type)
        if self.request.GET.get("featured") == "1":
            queryset = queryset.filter(is_featured=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["types"] = Client.Type.choices
        context["active_type"] = self.request.GET.get("type", "")
        context["active_featured"] = self.request.GET.get("featured", "")
        return context


class ClientCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "dashboard/clients/form.html"
    success_url = reverse_lazy("dashboard:client_list")
    success_message = "Client created."


class ClientUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "dashboard/clients/form.html"
    success_url = reverse_lazy("dashboard:client_list")
    success_message = "Client updated."


class ClientDeleteView(DashboardAccessMixin, DeleteView):
    model = Client
    template_name = "dashboard/clients/confirm_delete.html"
    success_url = reverse_lazy("dashboard:client_list")


# --- Team members (Editor + Administrator) ---


class TeamMemberListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = TeamMember
    template_name = "dashboard/team/list.html"
    partial_template_name = "dashboard/team/_table.html"
    context_object_name = "members"
    search_fields = ["name", "role"]

    def apply_filters(self, queryset):
        group = self.request.GET.get("group")
        if group in TeamMember.Group.values:
            queryset = queryset.filter(group=group)
        active = self.request.GET.get("active")
        if active == "active":
            queryset = queryset.filter(is_active=True)
        elif active == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = TeamMember.Group.choices
        context["active_group"] = self.request.GET.get("group", "")
        context["active_active"] = self.request.GET.get("active", "")
        return context


class TeamMemberCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = "dashboard/team/form.html"
    success_url = reverse_lazy("dashboard:team_list")
    success_message = "Team member created."


class TeamMemberUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = "dashboard/team/form.html"
    success_url = reverse_lazy("dashboard:team_list")
    success_message = "Team member updated."


class TeamMemberDeleteView(DashboardAccessMixin, DeleteView):
    model = TeamMember
    template_name = "dashboard/team/confirm_delete.html"
    success_url = reverse_lazy("dashboard:team_list")


# --- Gallery (Editor + Administrator) ---


class GalleryImageListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = GalleryImage
    template_name = "dashboard/gallery/list.html"
    partial_template_name = "dashboard/gallery/_table.html"
    context_object_name = "images"
    search_fields = ["title", "caption", "category"]

    def get_queryset(self):
        return super().get_queryset().select_related("related_project")

    def apply_filters(self, queryset):
        active = self.request.GET.get("active")
        if active == "active":
            queryset = queryset.filter(is_active=True)
        elif active == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_active"] = self.request.GET.get("active", "")
        return context


class GalleryImageCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = GalleryImage
    form_class = GalleryImageForm
    template_name = "dashboard/gallery/form.html"
    success_url = reverse_lazy("dashboard:gallery_list")
    success_message = "Gallery image added."


class GalleryImageUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = GalleryImage
    form_class = GalleryImageForm
    template_name = "dashboard/gallery/form.html"
    success_url = reverse_lazy("dashboard:gallery_list")
    success_message = "Gallery image updated."


class GalleryImageDeleteView(DashboardAccessMixin, DeleteView):
    model = GalleryImage
    template_name = "dashboard/gallery/confirm_delete.html"
    success_url = reverse_lazy("dashboard:gallery_list")


# --- Downloads (Editor + Administrator) ---


class DownloadListView(FilterableListMixin, DashboardAccessMixin, ListView):
    model = Download
    template_name = "dashboard/downloads/list.html"
    partial_template_name = "dashboard/downloads/_table.html"
    context_object_name = "downloads"
    search_fields = ["title", "description"]

    def apply_filters(self, queryset):
        category = self.request.GET.get("category")
        if category in Download.Category.values:
            queryset = queryset.filter(category=category)
        public = self.request.GET.get("public")
        if public == "public":
            queryset = queryset.filter(is_public=True)
        elif public == "private":
            queryset = queryset.filter(is_public=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Download.Category.choices
        context["active_category"] = self.request.GET.get("category", "")
        context["active_public"] = self.request.GET.get("public", "")
        return context


class DownloadCreateView(DashboardAccessMixin, SuccessMessageMixin, CreateView):
    model = Download
    form_class = DownloadForm
    template_name = "dashboard/downloads/form.html"
    success_url = reverse_lazy("dashboard:download_list")
    success_message = "Download added."


class DownloadUpdateView(DashboardAccessMixin, SuccessMessageMixin, UpdateView):
    model = Download
    form_class = DownloadForm
    template_name = "dashboard/downloads/form.html"
    success_url = reverse_lazy("dashboard:download_list")
    success_message = "Download updated."


class DownloadDeleteView(DashboardAccessMixin, DeleteView):
    model = Download
    template_name = "dashboard/downloads/confirm_delete.html"
    success_url = reverse_lazy("dashboard:download_list")


# --- Account security: opt-in two-factor authentication (Editor + Administrator) ---


def _safe_next(request, default):
    """Validate a ``next`` redirect target against the current host."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return default


class SecurityView(DashboardAccessMixin, TemplateView):
    """Account security overview — shows 2FA status and entry points."""

    template_name = "dashboard/security.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["two_factor_enabled"] = user_has_device(self.request.user)
        return context


class TwoFactorEnableView(DashboardAccessMixin, View):
    """Enrol an authenticator app: show the QR, confirm with a code, then issue
    one-time backup tokens. Opt-in — a user only lands here by choosing to."""

    template_name = "dashboard/two_factor_enable.html"

    def _unconfirmed_device(self, user):
        # Reuse an in-progress device so the QR is stable across refreshes.
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        return device or TOTPDevice.objects.create(user=user, name="default", confirmed=False)

    def _enrol_page(self, request, device):
        return render(
            request,
            self.template_name,
            {"qr_svg": qr_svg(device.config_url), "secret": device.bin_key.hex()},
        )

    def get(self, request, *args, **kwargs):
        if user_has_device(request.user):
            return redirect("dashboard:security")
        return self._enrol_page(request, self._unconfirmed_device(request.user))

    def post(self, request, *args, **kwargs):
        if user_has_device(request.user):
            return redirect("dashboard:security")
        device = self._unconfirmed_device(request.user)
        if device.verify_token(request.POST.get("otp_token", "").strip()):
            device.confirmed = True
            device.save()
            tokens = issue_backup_tokens(request.user)
            messages.success(request, "Two-factor authentication is now on.")
            return render(request, "dashboard/two_factor_backup.html", {"backup_tokens": tokens})
        messages.error(request, "That code didn't match — try again.")
        return self._enrol_page(request, device)


class TwoFactorDisableView(DashboardAccessMixin, View):
    """Turn 2FA off — removes the authenticator and backup devices."""

    def post(self, request, *args, **kwargs):
        TOTPDevice.objects.filter(user=request.user).delete()
        StaticDevice.objects.filter(user=request.user).delete()
        messages.success(request, "Two-factor authentication is now off.")
        return redirect("dashboard:security")


class OtpChallengeView(DashboardAccessMixin, View):
    """Post-login code prompt for users who have 2FA enabled."""

    template_name = "dashboard/otp_challenge.html"

    def get(self, request, *args, **kwargs):
        if not user_has_device(request.user) or request.user.is_verified():
            return redirect(_safe_next(request, reverse("dashboard:overview")))
        return render(request, self.template_name, {"next": _safe_next(request, "")})

    def post(self, request, *args, **kwargs):
        token = request.POST.get("otp_token", "").strip()
        device = match_token(request.user, token)
        if device:
            otp_login(request, device)
            return redirect(_safe_next(request, reverse("dashboard:overview")))
        messages.error(request, "That code didn't match — try again.")
        return render(request, self.template_name, {"next": _safe_next(request, "")})
