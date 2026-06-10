from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.QuotationView.as_view(), name="quote"),
    path("thank-you/", views.QuotationThanksView.as_view(), name="thanks"),
]
