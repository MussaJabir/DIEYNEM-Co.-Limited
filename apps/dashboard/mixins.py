from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django_otp import user_has_device


class OtpGateMixin:
    """Force OTP verification for users who have opted into 2FA.

    Opt-in: only users with a confirmed device are gated. An enrolled user who
    hasn't yet entered their code this session is redirected to the challenge;
    everyone else passes straight through. The challenge view itself is exempt
    (otherwise it would redirect to itself).
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        match = request.resolver_match
        on_challenge = match and match.url_name == "otp_challenge"
        if user.is_authenticated and not on_challenge and user_has_device(user):
            if not user.is_verified():
                return redirect(f"{reverse('dashboard:otp_challenge')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)


class DashboardAccessMixin(OtpGateMixin, LoginRequiredMixin, UserPassesTestMixin):
    """Any logged-in superuser, Administrator or Editor may use the dashboard."""

    def test_func(self) -> bool:
        user = self.request.user
        return (
            user.is_superuser or user.groups.filter(name__in=["Administrator", "Editor"]).exists()
        )


class AdministratorRequiredMixin(OtpGateMixin, LoginRequiredMixin, UserPassesTestMixin):
    """Administrator-only areas (settings, certificates, users)."""

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_superuser or user.groups.filter(name="Administrator").exists()
