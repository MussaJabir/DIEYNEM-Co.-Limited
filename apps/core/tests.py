import json
import tempfile
from io import BytesIO

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.leads.models import Inquiry
from apps.projects.models import Project
from apps.services.models import Service

from .models import Client, SiteSetting, Statistic, TeamMember


def _jpeg(name="photo.jpg", size=(1200, 800)):
    buffer = BytesIO()
    Image.new("RGB", size, "navy").save(buffer, "JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


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

    def test_home_uses_editable_statistics_when_present(self):
        Statistic.objects.create(label="Km of line", value=120, suffix=" km", order=1)
        Statistic.objects.create(label="Hidden one", value=9, is_active=False)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Km of line")
        self.assertContains(response, 'data-count-to="120"')
        # Inactive statistics and the computed fallback are not shown.
        self.assertNotContains(response, "Hidden one")
        self.assertNotContains(response, "Years in business")

    def test_home_falls_back_to_computed_stats_without_statistics(self):
        self.assertFalse(Statistic.objects.exists())
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Years in business")

    def test_home_shows_clients_band(self):
        Client.objects.create(name="Tanesco", order=1)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Clients &amp; partners")
        self.assertContains(response, "Tanesco")


class AboutPageTests(TestCase):
    def test_about_returns_200(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_about_shows_verified_overview_and_motto(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "Specialist Contractor, Class One")
        self.assertContains(response, "Milestones")
        # Motto comes from the (seeded) SiteSetting singleton.
        self.assertContains(response, "Quality is our Motto")

    def test_about_shows_seeded_leadership(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "Leadership &amp; technical team")
        self.assertContains(response, "Maulidy Ngaiwa Juma")
        self.assertContains(response, "Eng. Novatus Peter Lyimo")

    def test_about_groups_only_active_members(self):
        TeamMember.objects.create(
            name="Hidden Person", role="Intern", group=TeamMember.Group.SUPPORT, is_active=False
        )
        response = self.client.get(reverse("about"))
        self.assertNotContains(response, "Hidden Person")

    def test_about_exposes_years_in_operation(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.context["years_in_operation"], timezone.localdate().year - 2011)


class LeadershipSeedTests(TestCase):
    def test_three_leaders_seeded_by_migration(self):
        leaders = TeamMember.objects.filter(group=TeamMember.Group.LEADERSHIP)
        self.assertEqual(leaders.count(), 3)
        self.assertTrue(leaders.filter(name="Dickson Nathaniel Chungu").exists())


class AccessibilityTests(TestCase):
    """Structural a11y markers added in the accessibility pass.

    Colour-contrast itself is verified out-of-band with axe-core; these guard
    the markup affordances so they can't silently regress.
    """

    def test_skip_link_and_main_landmark(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="#main"')
        self.assertContains(response, "Skip to content")
        self.assertContains(response, 'id="main"')

    def test_focus_visible_styles_present(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, ":focus-visible")
        self.assertContains(response, "skip-link")

    def test_certifications_uses_no_misused_definition_list(self):
        # The cert cards' label/value lines were a <dl> of bare <div>s, which
        # axe flags as a broken definition list — now plain divs.
        from apps.credentials.models import Certificate

        Certificate.objects.create(
            name="CRB Class One", category="registration", issuer="CRB", number="99527"
        )
        response = self.client.get(reverse("credentials:list"))
        self.assertNotContains(response, "<dl")
        self.assertContains(response, "Issuer:")

    def test_gallery_lightbox_has_dialog_semantics(self):
        # The lightbox only renders when the gallery has at least one image.
        from apps.media_center.models import GalleryImage

        buffer = BytesIO()
        Image.new("RGB", (2, 2), "navy").save(buffer, "PNG")
        with tempfile.TemporaryDirectory() as media:
            with override_settings(MEDIA_ROOT=media):
                GalleryImage.objects.create(
                    image=SimpleUploadedFile("g.png", buffer.getvalue(), content_type="image/png"),
                    caption="Site photo",
                )
                response = self.client.get(reverse("media_center:gallery"))
        self.assertContains(response, 'role="dialog"')
        self.assertContains(response, 'aria-modal="true"')


class PwaTests(TestCase):
    """Installable PWA: manifest, service worker, offline page, link tags."""

    def test_manifest_served_as_json_with_icons(self):
        response = self.client.get("/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/manifest+json")
        data = json.loads(response.content)
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["start_url"], "/")
        self.assertEqual(len(data["icons"]), 3)
        self.assertTrue(any(i["purpose"] == "maskable" for i in data["icons"]))

    def test_service_worker_served_at_root_scope(self):
        response = self.client.get("/sw.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])
        body = response.content.decode()
        # Has the lifecycle + fetch handler (needed for installability) and
        # deliberately bypasses the dashboard/admin.
        self.assertIn('addEventListener("install"', body)
        self.assertIn('addEventListener("fetch"', body)
        self.assertIn("/dashboard/", body)
        self.assertIn("/offline/", body)

    def test_offline_page(self):
        response = self.client.get("/offline/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "offline")

    def test_pages_link_manifest_and_register_sw(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'rel="manifest"')
        self.assertContains(response, 'name="theme-color"')
        self.assertContains(response, "serviceWorker")


class PerformanceTests(TestCase):
    """Self-hosted fonts, LCP hint and version-keyed fragment caching."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def test_fonts_are_self_hosted(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "css/fonts.css")
        self.assertNotContains(response, "fonts.googleapis.com")
        self.assertNotContains(response, "fonts.gstatic.com")
        # The two above-the-fold faces are preloaded.
        self.assertContains(response, 'rel="preload"')
        self.assertContains(response, "manrope-800-latin.woff2")

    def test_hero_image_uses_fetchpriority(self):
        from apps.projects.models import Project

        Project.objects.create(
            title="Hero Project", is_featured=True, is_published=True, hero_image="projects/x.jpg"
        )
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'fetchpriority="high"')

    def test_content_save_bumps_cache_version(self):
        from apps.core.cache import get_cache_version
        from apps.services.models import Service

        before = get_cache_version()
        Service.objects.create(name="Cache Buster")
        self.assertGreater(get_cache_version(), before)

    def test_unrelated_model_does_not_bump_version(self):
        from django.contrib.auth.models import User

        from apps.core.cache import get_cache_version

        before = get_cache_version()
        User.objects.create_user("nobody", password="x")
        self.assertEqual(get_cache_version(), before)

    def test_home_exposes_cache_version_to_templates(self):
        response = self.client.get(reverse("home"))
        self.assertIn("cache_version", response.context)


class SeoTests(TestCase):
    def test_sitemap_lists_static_and_content_urls(self):
        Service.objects.create(name="SEO Service", is_published=True)
        Project.objects.create(title="SEO Project", is_published=True)
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        body = response.content.decode()
        self.assertIn("/about/", body)
        self.assertIn("/seo-service/", body)
        self.assertIn("/seo-project/", body)

    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        body = response.content.decode()
        self.assertIn("Disallow: /dashboard/", body)
        self.assertIn("Sitemap:", body)
        self.assertIn("/sitemap.xml", body)

    def test_home_has_organization_jsonld_and_og(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, "application/ld+json")
        payload = response.context["organization_jsonld"]
        data = json.loads(payload)
        self.assertEqual(data["@type"], "Organization")
        self.assertEqual(data["name"], "DIEYNEM Co. Limited")

    def test_service_detail_has_service_jsonld(self):
        service = Service.objects.create(name="Switchgear Service", is_published=True)
        response = self.client.get(service.get_absolute_url())
        self.assertContains(response, '"@type": "Service"')

    def test_project_detail_has_creativework_jsonld_and_article_og(self):
        project = Project.objects.create(title="Tower Wiring", is_published=True)
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, '"@type": "CreativeWork"')
        self.assertContains(response, 'content="article"')

    def test_dashboard_pages_skip_organization_jsonld(self):
        editor = User.objects.create_user("editor", password="pass12345")
        editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:overview"))
        self.assertIsNone(response.context.get("organization_jsonld"))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ResponsiveImageTagTests(TestCase):
    def _render(self, image, **kwargs):
        kw = " ".join(f'{k}="{v}"' for k, v in kwargs.items())
        template = Template("{% load media_extras %}{% responsive_image img " + kw + " %}")
        return template.render(Context({"img": image}))

    def test_renders_picture_with_webp_and_fallback(self):
        member = TeamMember.objects.create(name="Jane", role="MD", photo=_jpeg())
        html = self._render(member.photo, alt="Jane", sizes="50vw", ratio="1:1")
        self.assertIn("<picture>", html)
        self.assertIn('type="image/webp"', html)
        self.assertIn(".webp", html)
        # Fallback <img> keeps the original format and carries a width srcset.
        self.assertIn("<img", html)
        self.assertIn("480w", html)
        self.assertIn('alt="Jane"', html)
        self.assertIn('sizes="50vw"', html)

    def test_emits_width_and_height_to_prevent_layout_shift(self):
        # A 1200x800 source cropped 1:1 -> a square largest derivative; the
        # width/height attrs carry that intrinsic ratio so the box is reserved.
        member = TeamMember.objects.create(name="Sized", role="MD", photo=_jpeg(size=(1200, 800)))
        html = self._render(member.photo, alt="Sized", ratio="1:1")
        self.assertRegex(html, r'width="\d+"\s+height="\d+"')

    def test_no_image_renders_nothing(self):
        html = self._render("", alt="x").strip()
        self.assertEqual(html, "")

    def test_missing_source_file_falls_back_to_plain_img(self):
        # An ImageField pointing at a file that isn't on disk must not 500.
        member = TeamMember.objects.create(name="Ghost", role="X")
        member.photo = "team/does-not-exist.jpg"
        html = self._render(member.photo, alt="Ghost")
        self.assertIn("<img", html)
        self.assertNotIn("<picture>", html)


class StatisticModelTests(TestCase):
    def test_str_includes_prefix_and_suffix(self):
        stat = Statistic.objects.create(label="Line", value=120, prefix="~", suffix=" km")
        self.assertEqual(str(stat), "Line: ~120 km")

    def test_default_ordering_by_order(self):
        Statistic.objects.create(label="B", value=2, order=2)
        Statistic.objects.create(label="A", value=1, order=1)
        self.assertEqual([s.label for s in Statistic.objects.all()], ["A", "B"])


class TeamMemberModelTests(TestCase):
    def test_display_name_prepends_qualification(self):
        member = TeamMember.objects.create(name="Jane Doe", role="MD", qualification="Eng.")
        self.assertEqual(member.display_name, "Eng. Jane Doe")

    def test_display_name_without_qualification(self):
        member = TeamMember.objects.create(name="John Doe", role="Technician")
        self.assertEqual(member.display_name, "John Doe")


class ClientModelTests(TestCase):
    def test_default_type_is_client(self):
        client = Client.objects.create(name="Tanesco")
        self.assertEqual(client.type, Client.Type.CLIENT)


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

    def test_dashboard_has_dark_mode_toggle_and_no_flash_script(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("dashboard:overview"))
        # Toggle control, the pre-paint theme script and the scoped override.
        self.assertContains(response, 'aria-label="Toggle dark mode"')
        self.assertContains(response, "dz-theme")
        self.assertContains(response, "html.dark")

    def test_public_site_never_gets_dark_mode(self):
        # The override is dashboard-scoped; the public base must not ship it.
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "dz-theme")
        self.assertNotContains(response, "Toggle dark mode")

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
