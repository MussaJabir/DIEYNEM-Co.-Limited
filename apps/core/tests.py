from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.leads.models import Inquiry
from apps.services.models import Service

from .models import SiteSetting


class HomePageTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_brand(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "DIEYNEM")

    def test_footer_uses_site_settings(self):
        response = self.client.get(reverse("home"))
        # Seeded contact details should appear in the footer.
        self.assertContains(response, "info@dieynem.co.tz")
        self.assertContains(response, "P.O. Box 38075")

    def test_home_exposes_credibility_stats(self):
        response = self.client.get(reverse("home"))
        stats = response.context["stats"]
        self.assertEqual(stats["years"], timezone.localdate().year - 2011)
        self.assertEqual(stats["services"], Service.objects.published().count())
        # Count-up band + new sections render.
        self.assertContains(response, "data-count-to")
        self.assertContains(response, "Years in business")

    def test_home_has_why_and_cta_sections(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Why DIEYNEM")
        self.assertContains(response, "Have a project or tender")


class RoleGroupTests(TestCase):
    def test_role_groups_created_by_migration(self):
        self.assertTrue(Group.objects.filter(name="Administrator").exists())
        self.assertTrue(Group.objects.filter(name="Editor").exists())


class SiteSettingTests(TestCase):
    def test_seeded_by_migration(self):
        setting = SiteSetting.load()
        self.assertEqual(setting.company_name, "DIEYNEM Co. Limited")
        self.assertIn("info@dieynem.co.tz", setting.emails)

    def test_is_singleton(self):
        SiteSetting.load()
        # Saving another instance must not create a second row.
        SiteSetting(company_name="Other").save()
        self.assertEqual(SiteSetting.objects.count(), 1)
        self.assertEqual(SiteSetting.objects.first().pk, 1)

    def test_phone_and_email_lists(self):
        setting = SiteSetting.load()
        setting.phones = "+255 1\n  \n+255 2\n"
        setting.emails = "a@x.tz\nb@x.tz"
        self.assertEqual(setting.phone_list, ["+255 1", "+255 2"])
        self.assertEqual(setting.email_list, ["a@x.tz", "b@x.tz"])

    def test_social_links_only_includes_filled(self):
        setting = SiteSetting.load()
        setting.facebook_url = "https://facebook.com/dieynem"
        setting.linkedin_url = ""
        names = [name for name, _ in setting.social_links]
        self.assertEqual(names, ["Facebook"])


class DashboardShellTests(TestCase):
    """Sidebar badge context processor and role-based shell rendering."""

    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.administrator = User.objects.create_user("boss", password="pass12345")
        self.administrator.groups.add(Group.objects.get(name="Administrator"))

    def test_badge_counts_absent_on_public_pages(self):
        Inquiry.objects.create(name="A", email="a@x.tz", message="hi")
        response = self.client.get(reverse("home"))
        self.assertIsNone(response.context.get("new_inquiries_count"))

    def test_new_inquiry_count_available_to_dashboard_staff(self):
        Inquiry.objects.create(name="A", email="a@x.tz", message="hi")
        Inquiry.objects.create(name="B", email="b@x.tz", message="hi")
        # Read by a quoted inquiry should not be counted as "new".
        Inquiry.objects.create(name="C", email="c@x.tz", message="hi", status=Inquiry.Status.QUOTED)
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:project_list"))
        self.assertEqual(response.context["new_inquiries_count"], 2)

    def test_certificate_attention_is_administrator_only(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:project_list"))
        self.assertIsNone(response.context.get("certs_attention_count"))

        self.client.login(username="boss", password="pass12345")
        response = self.client.get(reverse("dashboard:project_list"))
        self.assertIn("certs_attention_count", response.context)

    def test_sidebar_hides_admin_links_for_editor(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:overview"))
        self.assertContains(response, "Projects")
        self.assertNotContains(response, "Site Settings")

    def test_sidebar_shows_admin_links_and_role_for_administrator(self):
        self.client.login(username="boss", password="pass12345")
        response = self.client.get(reverse("dashboard:overview"))
        self.assertContains(response, "Site Settings")
        self.assertContains(response, "Administrator")
