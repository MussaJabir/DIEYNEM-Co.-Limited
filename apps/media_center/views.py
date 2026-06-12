from django.views.generic import TemplateView

from apps.projects.models import ProjectImage

from .models import Download, GalleryImage


class GalleryView(TemplateView):
    """Global gallery: curated GalleryImages plus project photos flagged for it.

    Items are normalised to a common shape so the template renders one grid +
    lightbox regardless of source (BS §268). Curated images lead, then project
    photos. A ``?category=`` query narrows the grid.
    """

    template_name = "public/gallery.html"

    def get_items(self):
        items = []
        for image in GalleryImage.objects.active().select_related("related_project"):
            project = image.related_project
            published = bool(project and project.is_published)
            items.append(
                {
                    "image": image.image,
                    "src": image.image.url,
                    "caption": image.caption or image.title,
                    "category": image.category,
                    "project_title": project.title if published else "",
                    "project_url": project.get_absolute_url() if published else "",
                }
            )
        project_images = (
            ProjectImage.objects.filter(show_in_gallery=True, project__is_published=True)
            .select_related("project")
            .order_by("project__order", "order", "id")
        )
        for pi in project_images:
            items.append(
                {
                    "image": pi.image,
                    "src": pi.image.url,
                    "caption": pi.caption,
                    "category": pi.project.get_sector_display(),
                    "project_title": pi.project.title,
                    "project_url": pi.project.get_absolute_url(),
                }
            )
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_items()
        context["categories"] = sorted({i["category"] for i in items if i["category"]})
        active_category = self.request.GET.get("category", "")
        if active_category:
            items = [i for i in items if i["category"] == active_category]
        context["items"] = items
        context["active_category"] = active_category
        return context


class DownloadsView(TemplateView):
    """Public downloads page — documents grouped by category (BS §270)."""

    template_name = "public/downloads.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        downloads = list(Download.objects.public())
        groups = []
        for value, label in Download.Category.choices:
            group_files = [d for d in downloads if d.category == value]
            if group_files:
                groups.append({"label": label, "downloads": group_files})
        context["download_groups"] = groups
        return context
