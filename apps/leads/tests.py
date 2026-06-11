from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Inquiry


class InquiryModelTests(TestCase):
    def test_str_includes_name(self):
        inquiry = Inquiry.objects.create(name="Jane Doe", email="jane@example.com", message="Hi")
        self.assertIn("Jane Doe", str(inquiry))

    def test_defaults(self):
        inquiry = Inquiry.objects.create(name="A", email="a@x.tz", message="m")
        self.assertEqual(inquiry.status, Inquiry.Status.NEW)


class QuotationViewTests(TestCase):
    def _data(self, **overrides):
        data = {
            "name": "Jane Doe",
            "company": "Acme Ltd",
            "email": "jane@example.com",
            "phone": "+255 700 000 000",
            "service_interest": "",
            "project_type": "Office fit-out",
            "message": "Please quote my electrical project.",
            "website": "",
        }
        data.update(overrides)
        return data

    def test_get_renders_form(self):
        response = self.client.get(reverse("leads:quote"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Request a Quotation")

    def test_valid_submission_saves_and_emails(self):
        response = self.client.post(reverse("leads:quote"), self._data())
        self.assertRedirects(response, reverse("leads:thanks"))
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("info@dieynem.co.tz", mail.outbox[0].to)

    def test_honeypot_blocks_submission(self):
        response = self.client.post(
            reverse("leads:quote"), self._data(website="http://spam.example")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_required_fields(self):
        self.client.post(reverse("leads:quote"), self._data(name="", message=""))
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_page_shows_trust_cues(self):
        response = self.client.get(reverse("leads:quote"))
        self.assertContains(response, "What happens next")
        self.assertContains(response, "Contact us directly")

    def test_thanks_page_renders(self):
        response = self.client.get(reverse("leads:thanks"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "your request has been received")
        self.assertContains(response, "View our projects")
