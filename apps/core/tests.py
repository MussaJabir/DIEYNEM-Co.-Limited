from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_brand(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "DIEYNEM")


class RoleGroupTests(TestCase):
    def test_role_groups_created_by_migration(self):
        self.assertTrue(Group.objects.filter(name="Administrator").exists())
        self.assertTrue(Group.objects.filter(name="Editor").exists())
