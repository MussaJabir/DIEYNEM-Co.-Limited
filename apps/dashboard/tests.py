import tempfile
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.core.models import SiteSetting
from apps.credentials.models import Certificate
from apps.dashboard.forms import (
    CertificateForm,
    ProjectForm,
    ProjectImageFormSet,
    ServiceForm,
    SiteSettingForm,
)
from apps.leads.models import Inquiry
from apps.projects.models import Project
from apps.services.models import Service


def _png_upload(name="photo.png"):
    """A valid in-memory PNG for ImageField uploads in tests."""
    buffer = BytesIO()
    Image.new("RGB", (2, 2), "navy").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


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

    def test_published_filter(self):
        Service.objects.all().delete()  # ignore migration-seeded content
        Service.objects.create(name="Live", is_published=True)
        Service.objects.create(name="Hidden", is_published=False)
        response = self.client.get(reverse("dashboard:service_list"), {"published": "draft"})
        names = [s.name for s in response.context["services"]]
        self.assertEqual(names, ["Hidden"])


class ProjectDashboardTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="pass12345")

    def _form_data(self, **overrides):
        data = {
            "title": "New Project",
            "status": "completed",
            "client_name": "",
            "main_contractor": "",
            "consultant": "",
            "location": "",
            "country": "Tanzania",
            "sector": "",
            "role": "",
            "year_start": "",
            "year_end": "",
            "completion_date": "",
            "overview": "",
            "scope_of_work": "",
            "technical_highlights": "",
            "outcome": "",
            "contract_value": "",
            "contract_value_visible": "on",
            "progress_percent": "",
            "last_updated_label": "",
            "order": 0,
            "meta_title": "",
            "meta_description": "",
            # Empty inline image formset
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            # Empty inline milestone formset
            "milestones-TOTAL_FORMS": "0",
            "milestones-INITIAL_FORMS": "0",
            "milestones-MIN_NUM_FORMS": "0",
            "milestones-MAX_NUM_FORMS": "1000",
            # Empty inline update formset
            "updates-TOTAL_FORMS": "0",
            "updates-INITIAL_FORMS": "0",
            "updates-MIN_NUM_FORMS": "0",
            "updates-MAX_NUM_FORMS": "1000",
        }
        data.update(overrides)
        return data

    def test_anonymous_redirected(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard:project_list"))
        self.assertEqual(response.status_code, 302)

    def test_editor_can_list(self):
        response = self.client.get(reverse("dashboard:project_list"))
        self.assertEqual(response.status_code, 200)

    def test_editor_can_create(self):
        response = self.client.post(reverse("dashboard:project_create"), self._form_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(title="New Project").exists())

    def test_editor_can_update(self):
        project = Project.objects.create(title="Old Project")
        response = self.client.post(
            reverse("dashboard:project_update", args=[project.pk]),
            self._form_data(title="Renamed Project"),
        )
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.title, "Renamed Project")

    def test_editor_can_delete(self):
        project = Project.objects.create(title="ToDelete")
        response = self.client.post(reverse("dashboard:project_delete", args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_image_form_has_preview_and_add_button(self):
        project = Project.objects.create(title="Has images")
        response = self.client.get(reverse("dashboard:project_update", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "imageFormset(")
        self.assertContains(response, "Add another image")
        self.assertContains(response, "__prefix__")  # empty-form template present
        self.assertContains(response, 'accept="image/*"')  # preview-style picker

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_create_project_with_gallery_image(self):
        data = self._form_data(
            **{
                "images-TOTAL_FORMS": "1",
                "images-0-order": "0",
                "images-0-show_in_gallery": "on",
                "images-0-image": _png_upload(),
            }
        )
        response = self.client.post(reverse("dashboard:project_create"), data)
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(title="New Project")
        self.assertEqual(project.images.count(), 1)

    def test_create_project_with_milestone_and_update(self):
        data = self._form_data(
            **{
                "status": "ongoing",
                "progress_percent": "45",
                "milestones-TOTAL_FORMS": "1",
                "milestones-0-title": "Cabling complete",
                "milestones-0-is_complete": "on",
                "milestones-0-order": "0",
                "updates-TOTAL_FORMS": "1",
                "updates-0-date": "2026-06-01",
                "updates-0-note": "Main panel energised.",
            }
        )
        response = self.client.post(reverse("dashboard:project_create"), data)
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(title="New Project")
        self.assertEqual(project.progress_percent, 45)
        self.assertEqual(project.milestones.count(), 1)
        self.assertTrue(project.milestones.first().is_complete)
        self.assertEqual(project.updates.count(), 1)
        self.assertEqual(project.updates.first().note, "Main panel energised.")

    def test_editor_shows_milestone_and_update_sections(self):
        project = Project.objects.create(title="Ongoing one", status=Project.Status.ONGOING)
        response = self.client.get(reverse("dashboard:project_update", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ongoing progress")
        self.assertContains(response, "Milestones")
        self.assertContains(response, "Add milestone")
        self.assertContains(response, "Project updates")
        self.assertContains(response, "Post an update")
        # Generic add-row Alpine helper is wired for the new formsets.
        self.assertContains(response, "inlineFormset(")

    def test_search_filters_projects(self):
        Project.objects.all().delete()  # ignore migration-seeded content
        Project.objects.create(title="Alpha Tower")
        Project.objects.create(title="Beta Bridge")
        response = self.client.get(reverse("dashboard:project_list"), {"q": "Alpha"})
        titles = [p.title for p in response.context["projects"]]
        self.assertEqual(titles, ["Alpha Tower"])

    def test_status_filter(self):
        Project.objects.all().delete()  # ignore migration-seeded content
        Project.objects.create(title="Done one", status=Project.Status.COMPLETED)
        Project.objects.create(title="Live one", status=Project.Status.ONGOING)
        response = self.client.get(
            reverse("dashboard:project_list"), {"status": Project.Status.ONGOING}
        )
        titles = [p.title for p in response.context["projects"]]
        self.assertEqual(titles, ["Live one"])

    def test_list_is_paginated(self):
        Project.objects.all().delete()  # ignore migration-seeded content
        for i in range(13):
            Project.objects.create(title=f"Project {i:02d}")
        page1 = self.client.get(reverse("dashboard:project_list"))
        self.assertEqual(page1.context["paginator"].count, 13)
        self.assertEqual(len(page1.context["projects"]), 12)
        page2 = self.client.get(reverse("dashboard:project_list"), {"page": 2})
        self.assertEqual(len(page2.context["projects"]), 1)

    def test_htmx_request_returns_table_fragment_only(self):
        response = self.client.get(reverse("dashboard:project_list"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/projects/_table.html")
        self.assertTemplateNotUsed(response, "dashboard/base.html")


class CertificateDashboardTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.administrator = User.objects.create_user("boss", password="pass12345")
        self.administrator.groups.add(Group.objects.get(name="Administrator"))

    def _form_data(self, **overrides):
        data = {
            "name": "New Certificate",
            "category": "registration",
            "issuer": "",
            "number": "",
            "description": "",
            "issue_date": "",
            "valid_to": "",
            "downloadable": "on",
            "related_project": "",
            "is_published": "on",
            "order": 0,
        }
        data.update(overrides)
        return data

    def test_editor_denied(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:certificate_list"))
        self.assertEqual(response.status_code, 403)

    def test_administrator_can_list(self):
        self.client.login(username="boss", password="pass12345")
        response = self.client.get(reverse("dashboard:certificate_list"))
        self.assertEqual(response.status_code, 200)

    def test_administrator_can_create(self):
        self.client.login(username="boss", password="pass12345")
        response = self.client.post(reverse("dashboard:certificate_create"), self._form_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Certificate.objects.filter(name="New Certificate").exists())

    def test_administrator_can_delete(self):
        self.client.login(username="boss", password="pass12345")
        cert = Certificate.objects.create(name="ToDelete", category="safety")
        response = self.client.post(reverse("dashboard:certificate_delete", args=[cert.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Certificate.objects.filter(pk=cert.pk).exists())

    def test_validity_filter_returns_only_expired(self):
        self.client.login(username="boss", password="pass12345")
        Certificate.objects.all().delete()  # ignore migration-seeded content
        today = timezone.localdate()
        Certificate.objects.create(
            name="Lapsed", category="safety", valid_to=today - timedelta(days=1)
        )
        Certificate.objects.create(
            name="Good", category="safety", valid_to=today + timedelta(days=365)
        )
        response = self.client.get(reverse("dashboard:certificate_list"), {"validity": "expired"})
        names = [c.name for c in response.context["certificates"]]
        self.assertEqual(names, ["Lapsed"])


class InquiryDashboardTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="pass12345")
        self.inquiry = Inquiry.objects.create(name="Lead", email="lead@x.tz", message="Hello")

    def test_anonymous_redirected(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard:inquiry_list"))
        self.assertEqual(response.status_code, 302)

    def test_editor_can_list(self):
        response = self.client.get(reverse("dashboard:inquiry_list"))
        self.assertEqual(response.status_code, 200)

    def test_editor_can_update_status(self):
        response = self.client.post(
            reverse("dashboard:inquiry_detail", args=[self.inquiry.pk]),
            {"status": "contacted", "internal_notes": "Called them."},
        )
        self.assertEqual(response.status_code, 302)
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.status, "contacted")
        self.assertEqual(self.inquiry.internal_notes, "Called them.")

    def test_editor_can_delete(self):
        response = self.client.post(reverse("dashboard:inquiry_delete", args=[self.inquiry.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Inquiry.objects.filter(pk=self.inquiry.pk).exists())

    def test_search_filters_inquiries(self):
        Inquiry.objects.create(name="Acme Corp", email="ops@acme.tz", message="Hi")
        response = self.client.get(reverse("dashboard:inquiry_list"), {"q": "acme"})
        names = [i.name for i in response.context["inquiries"]]
        self.assertEqual(names, ["Acme Corp"])


class DashboardFormLayoutTests(TestCase):
    """Two-column fieldset rendering for the dashboard forms."""

    def test_fieldsets_render_every_field(self):
        # Guards against a field being dropped from a form's ``fieldsets``.
        for form_cls in (ProjectForm, ServiceForm, CertificateForm, SiteSettingForm):
            form = form_cls()
            rendered = {
                item["field"].name
                for section in form.iter_fieldsets()
                for item in section["fields"]
            }
            self.assertEqual(
                rendered,
                set(form.fields),
                msg=f"{form_cls.__name__}.fieldsets must render every field",
            )

    def test_form_without_fieldsets_renders_one_section(self):
        SiteSettingForm.fieldsets, saved = [], SiteSettingForm.fieldsets
        try:
            sections = list(SiteSettingForm().iter_fieldsets())
        finally:
            SiteSettingForm.fieldsets = saved
        self.assertEqual(len(sections), 1)
        self.assertIsNone(sections[0]["legend"])

    def test_project_form_renders_grouped_sections(self):
        editor = User.objects.create_user("editor", password="pass12345")
        editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:project_create"))
        self.assertEqual(response.status_code, 200)
        # Section legends present.
        self.assertContains(response, "Basics")
        self.assertContains(response, "Story")
        # Every key input still rendered.
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="overview"')
        self.assertContains(response, 'name="meta_description"')
        # Sticky save bar with submit-spinner wiring.
        self.assertContains(response, "Save project")
        self.assertContains(response, "saving = true")
        # Collapsible accordion sections.
        self.assertContains(response, ':aria-expanded="open"')

    def test_image_fields_detected_excluding_plain_files(self):
        self.assertIn("hero_image", ProjectForm().image_fields)
        self.assertIn("display_image", CertificateForm().image_fields)
        # The certificate scan is a plain FileField, not an image preview.
        self.assertNotIn("file", CertificateForm().image_fields)
        self.assertEqual(SiteSettingForm().image_fields, {"logo", "default_og_image"})

    def test_image_formset_has_no_always_on_blank_rows(self):
        self.assertEqual(ProjectImageFormSet.extra, 0)

    def test_section_flags_errors_for_auto_open(self):
        # A bound form missing a required field marks that section so the
        # template can open it automatically.
        form = ProjectForm(data={"status": "completed", "country": "Tanzania", "order": "0"})
        self.assertFalse(form.is_valid())  # title is required
        sections = {s["legend"]: s["has_errors"] for s in form.iter_fieldsets()}
        self.assertTrue(sections["Basics"], "Basics holds the missing title")
        self.assertFalse(sections["Story"], "Story fields are all optional")
