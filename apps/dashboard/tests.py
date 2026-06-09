from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


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

    def test_administrator_can_access_settings(self):
        self.client.login(username="boss", password="pass12345")
        response = self.client.get(reverse("dashboard:settings"))
        self.assertEqual(response.status_code, 200)
