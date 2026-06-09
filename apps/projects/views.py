from django.views.generic import DetailView, ListView

from .models import Project


class ProjectListView(ListView):
    template_name = "public/projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.published().prefetch_related("related_services")
        status = self.request.GET.get("status")
        if status in {Project.Status.COMPLETED, Project.Status.ONGOING}:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_status"] = self.request.GET.get("status", "")
        return context


class ProjectDetailView(DetailView):
    template_name = "public/projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.published().prefetch_related("related_services", "images")
