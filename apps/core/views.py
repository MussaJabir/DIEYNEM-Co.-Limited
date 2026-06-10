from django.utils import timezone
from django.views.generic import TemplateView

from apps.credentials.models import Certificate
from apps.projects.models import Project
from apps.services.models import Service

COMPANY_FOUNDED_YEAR = 2011


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_services"] = Service.objects.featured()
        context["featured_projects"] = Project.objects.featured()[:6]
        # Credibility numbers band (counted up on scroll).
        context["stats"] = {
            "years": timezone.localdate().year - COMPANY_FOUNDED_YEAR,
            "projects": Project.objects.filter(is_published=True).count(),
            "services": Service.objects.published().count(),
            "certificates": Certificate.objects.published().count(),
        }
        return context
