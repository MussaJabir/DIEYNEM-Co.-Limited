from django.urls import path

from . import views

app_name = "credentials"

urlpatterns = [
    path("", views.CertificationListView.as_view(), name="list"),
]
