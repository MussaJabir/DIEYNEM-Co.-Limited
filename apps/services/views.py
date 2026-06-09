from django.views.generic import DetailView, ListView

from .models import Service


class ServiceListView(ListView):
    template_name = "public/services/list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.published()


class ServiceDetailView(DetailView):
    template_name = "public/services/detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.published()
