def user_roles(request):
    """Expose role flags to templates (used by the dashboard shell)."""
    user = getattr(request, "user", None)
    is_administrator = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="Administrator").exists())
    )
    return {"is_administrator": is_administrator}
