from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class DashboardAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Any logged-in superuser, Administrator or Editor may use the dashboard."""

    def test_func(self) -> bool:
        user = self.request.user
        return (
            user.is_superuser or user.groups.filter(name__in=["Administrator", "Editor"]).exists()
        )


class AdministratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Administrator-only areas (settings, certificates, users)."""

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_superuser or user.groups.filter(name="Administrator").exists()
