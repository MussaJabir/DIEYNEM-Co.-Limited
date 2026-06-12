from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from apps.core.models import Client, Statistic, TeamMember
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
        # Editable numbers band, with computed fallbacks so the home page is
        # never empty before the client adds their own honest figures.
        context["statistics"] = Statistic.objects.filter(is_active=True)
        context["stats"] = {
            "years": timezone.localdate().year - COMPANY_FOUNDED_YEAR,
            "projects": Project.objects.filter(is_published=True).count(),
            "services": Service.objects.published().count(),
            "certificates": Certificate.objects.published().count(),
        }
        # Clients / partners logo band.
        context["clients"] = Client.objects.all()
        return context


class AboutView(TemplateView):
    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Partition active members into BS-ordered groups in a single query.
        members = list(TeamMember.objects.filter(is_active=True))
        groups = []
        for value, label in TeamMember.Group.choices:
            group_members = [m for m in members if m.group == value]
            if group_members:
                groups.append({"label": label, "members": group_members})
        context["team_groups"] = groups
        context["founded_year"] = COMPANY_FOUNDED_YEAR
        context["years_in_operation"] = timezone.localdate().year - COMPANY_FOUNDED_YEAR
        return context


def robots_txt(request):
    """Serve /robots.txt — crawlers welcome on the public site, not the admin."""
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
