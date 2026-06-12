import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.projects.models import Project, ProjectImage

from .models import GalleryImage


def _png(name="photo.png"):
    buffer = BytesIO()
    Image.new("RGB", (2, 2), "navy").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class GalleryImageModelTests(TestCase):
    def test_active_queryset(self):
        GalleryImage.objects.create(image="x.jpg", is_active=True)
        GalleryImage.objects.create(image="y.jpg", is_active=False)
        self.assertEqual(GalleryImage.objects.active().count(), 1)

    def test_str_prefers_title_then_caption(self):
        self.assertEqual(str(GalleryImage(title="Solar farm")), "Solar farm")
        self.assertEqual(str(GalleryImage(caption="A caption")), "A caption")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class GalleryPageTests(TestCase):
    def test_page_returns_200(self):
        response = self.client.get(reverse("media_center:gallery"))
        self.assertEqual(response.status_code, 200)

    def test_merges_gallery_images_and_project_images(self):
        GalleryImage.objects.create(image=_png(), caption="Curated shot", category="Solar")
        project = Project.objects.create(title="Live Works", is_published=True)
        ProjectImage.objects.create(project=project, image=_png(), caption="Site photo")
        response = self.client.get(reverse("media_center:gallery"))
        self.assertContains(response, "Curated shot")
        self.assertContains(response, "Site photo")

    def test_excludes_inactive_and_unpublished_sources(self):
        GalleryImage.objects.create(image=_png(), caption="Hidden curated", is_active=False)
        draft = Project.objects.create(title="Draft", is_published=False)
        ProjectImage.objects.create(project=draft, image=_png(), caption="Draft photo")
        published = Project.objects.create(title="Published", is_published=True)
        ProjectImage.objects.create(
            project=published, image=_png(), caption="Not in gallery", show_in_gallery=False
        )
        response = self.client.get(reverse("media_center:gallery"))
        self.assertNotContains(response, "Hidden curated")
        self.assertNotContains(response, "Draft photo")
        self.assertNotContains(response, "Not in gallery")

    def test_category_filter(self):
        GalleryImage.objects.create(image=_png(), caption="Solar one", category="Solar")
        GalleryImage.objects.create(image=_png(), caption="Fire one", category="Fire")
        response = self.client.get(reverse("media_center:gallery"), {"category": "Solar"})
        self.assertContains(response, "Solar one")
        self.assertNotContains(response, "Fire one")

    def test_empty_state(self):
        response = self.client.get(reverse("media_center:gallery"))
        self.assertContains(response, "will appear here soon")
