from django.views.generic import TemplateView

from apps.services.models import Service


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_services"] = Service.objects.featured()
        return context
