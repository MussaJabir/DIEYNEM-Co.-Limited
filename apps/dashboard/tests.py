from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import SiteSetting
from apps.services.models import Service


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.administrator = User.objects.create_user("boss", password="pass12345")
        self.administrator.groups.add(Group.objects.get(name="Administrator"))

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_editor_can_access_overview(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 200)

    def test_editor_denied_administrator_area(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:settings"))
        self.assertEqual(response.status_code, 403)

    def test_administrator_can_open_settings(self):
        self.client.login(username="boss", password="pass12345")
        response = self.client.get(reverse("dashboard:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Company identity")

    def test_administrator_can_save_settings(self):
        self.client.login(username="boss", password="pass12345")
        data = {
            "company_name": "DIEYNEM Co. Limited",
            "motto": "Quality is our Motto",
            "po_box": "P.O. Box 38075, Dar es Salaam, Tanzania",
            "physical_address": "Magomeni, Kinondoni, Dar es Salaam",
            "phones": "+255 22 2171512",
            "emails": "info@dieynem.co.tz",
            "map_embed": "",
            "facebook_url": "https://facebook.com/dieynem",
            "instagram_url": "",
            "linkedin_url": "",
            "footer_text": "Licensed Class One contractor.",
        }
        response = self.client.post(reverse("dashboard:settings"), data)
        self.assertEqual(response.status_code, 302)
        setting = SiteSetting.load()
        self.assertEqual(setting.footer_text, "Licensed Class One contractor.")
        self.assertEqual(setting.facebook_url, "https://facebook.com/dieynem")


class ServiceDashboardTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="pass12345")

    def _form_data(self, **overrides):
        data = {
            "name": "New Service",
            "short_description": "",
            "full_description": "",
            "capabilities": "",
            "icon": "",
            "order": 10,
            "is_published": "on",
            "meta_title": "",
            "meta_description": "",
        }
        data.update(overrides)
        return data

    def test_anonymous_redirected(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard:service_list"))
        self.assertEqual(response.status_code, 302)

    def test_editor_can_list(self):
        response = self.client.get(reverse("dashboard:service_list"))
        self.assertEqual(response.status_code, 200)

    def test_editor_can_create(self):
        response = self.client.post(reverse("dashboard:service_create"), self._form_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Service.objects.filter(name="New Service").exists())

    def test_editor_can_update(self):
        service = Service.objects.create(name="Old", order=5)
        response = self.client.post(
            reverse("dashboard:service_update", args=[service.pk]),
            self._form_data(name="Renamed", order=5),
        )
        self.assertEqual(response.status_code, 302)
        service.refresh_from_db()
        self.assertEqual(service.name, "Renamed")

    def test_editor_can_delete(self):
        service = Service.objects.create(name="ToDelete")
        response = self.client.post(reverse("dashboard:service_delete", args=[service.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Service.objects.filter(pk=service.pk).exists())
