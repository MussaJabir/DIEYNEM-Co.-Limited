from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .emails import send_lead_notification
from .forms import QuotationForm


class QuotationView(FormView):
    template_name = "public/quotation.html"
    form_class = QuotationForm
    success_url = reverse_lazy("leads:thanks")

    def form_valid(self, form):
        inquiry = form.save(commit=False)
        inquiry.source = "quote-form"
        inquiry.save()
        send_lead_notification(inquiry)
        return super().form_valid(form)


class QuotationThanksView(TemplateView):
    template_name = "public/quotation_thanks.html"
