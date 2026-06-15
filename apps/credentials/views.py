from django.views.generic import TemplateView

from .models import Certificate


class CertificationListView(TemplateView):
    template_name = "public/certifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        certificates = list(Certificate.objects.public())
        groups = []
        for value, label in Certificate.Category.choices:
            items = [c for c in certificates if c.category == value]
            if items:
                groups.append({"label": label, "items": items})
        context["groups"] = groups
        return context
