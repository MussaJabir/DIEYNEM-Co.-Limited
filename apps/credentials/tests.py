from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Certificate


class CertificateModelTests(TestCase):
    def setUp(self):
        Certificate.objects.all().delete()
        self.today = timezone.localdate()

    def _make(self, name, valid_to, **kwargs):
        return Certificate.objects.create(
            name=name, category="registration", valid_to=valid_to, **kwargs
        )

    def test_status_perpetual(self):
        self.assertEqual(self._make("Perpetual", None).status, "current")

    def test_status_expired(self):
        self.assertEqual(self._make("Old", self.today - timedelta(days=1)).status, "expired")

    def test_status_expiring(self):
        self.assertEqual(self._make("Soon", self.today + timedelta(days=30)).status, "expiring")

    def test_status_current_future(self):
        self.assertEqual(self._make("Future", self.today + timedelta(days=365)).status, "current")

    def test_public_excludes_expired(self):
        self._make("Old", self.today - timedelta(days=1))
        self._make("Good", self.today + timedelta(days=365))
        self._make("Perpetual", None)
        self.assertEqual(Certificate.objects.public().count(), 2)

    def test_needs_attention(self):
        self._make("Old", self.today - timedelta(days=1))
        self._make("Soon", self.today + timedelta(days=10))
        self._make("Fine", self.today + timedelta(days=365))
        self.assertEqual(Certificate.objects.needs_attention().count(), 2)

    def test_can_download_requires_file(self):
        cert = self._make("NoFile", None, downloadable=True)
        self.assertFalse(cert.can_download)


class CertificatePublicTests(TestCase):
    def test_list_page_shows_current_certs(self):
        response = self.client.get(reverse("credentials:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CRB Contractor Registration")

    def test_list_excludes_expired(self):
        # The seeded Tax Clearance (valid to 2025-12-31) is expired.
        response = self.client.get(reverse("credentials:list"))
        self.assertNotContains(response, "Tax Clearance Certificate")
