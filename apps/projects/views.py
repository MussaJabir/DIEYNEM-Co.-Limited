from django.views.generic import DetailView, ListView

from apps.services.models import Service

from .models import Project


class ProjectListView(ListView):
    template_name = "public/projects/list.html"
    partial_template_name = "public/projects/_grid.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.published().prefetch_related("related_services")
        status = self.request.GET.get("status")
        if status in Project.Status.values:
            queryset = queryset.filter(status=status)
        sector = self.request.GET.get("sector")
        if sector in Project.Sector.values:
            queryset = queryset.filter(sector=sector)
        service = self.request.GET.get("service")
        if service:
            queryset = queryset.filter(related_services__slug=service)
        country = self.request.GET.get("country")
        if country:
            queryset = queryset.filter(country=country)
        # ``service`` is a many-to-many join, so de-duplicate the rows.
        return queryset.distinct()

    def get_template_names(self):
        # HTMX requests get just the results grid to swap into ``#project-results``.
        if self.request.headers.get("HX-Request"):
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published = Project.objects.published()
        used_sectors = set(published.exclude(sector="").values_list("sector", flat=True))
        context["sectors"] = [
            (v, label) for v, label in Project.Sector.choices if v in used_sectors
        ]
        context["services"] = (
            Service.objects.published().filter(projects__is_published=True).distinct()
        )
        # Plain ``distinct()`` is defeated by the model's Meta ordering, so dedupe here.
        context["countries"] = sorted(set(published.values_list("country", flat=True)))
        context["active_status"] = self.request.GET.get("status", "")
        context["active_sector"] = self.request.GET.get("sector", "")
        context["active_service"] = self.request.GET.get("service", "")
        context["active_country"] = self.request.GET.get("country", "")
        context["has_filters"] = any(
            self.request.GET.get(key) for key in ("status", "sector", "service", "country")
        )
        return context


class OngoingProjectListView(ListView):
    """The living portfolio: ongoing projects with progress, milestones, updates."""

    template_name = "public/projects/ongoing.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.ongoing().prefetch_related("milestones", "updates")


class ProjectDetailView(DetailView):
    template_name = "public/projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.published().prefetch_related(
            "related_services", "images", "milestones", "updates"
        )
