from django.urls import path

from . import views

app_name = "media_center"

urlpatterns = [
    path("gallery/", views.GalleryView.as_view(), name="gallery"),
]
