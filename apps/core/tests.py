from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

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
